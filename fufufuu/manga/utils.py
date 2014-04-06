import os
import tempfile
import zipfile
from io import BytesIO

from django.core.cache import cache
from django.core.files.base import File
from django.core.files.uploadedfile import UploadedFile
from django.utils.translation import ugettext as _
from PIL import Image

from fufufuu.core.models import DeletedFile
from fufufuu.core.utils import get_image_extension
from fufufuu.image.enums import ImageKeyType
from fufufuu.image.filters import image_resize
from fufufuu.manga.models import MangaPage, MangaArchive


MAX_TOTAL_SIZE          = 200 * 1024 * 1024
MAX_IMAGE_FILE_SIZE     = 8 * 1024 * 1024
MAX_IMAGE_DIMENSION     = (8000, 8000)
MANGA_PAGE_LIMIT        = 100
SUPPORTED_IMAGE_FORMATS = ['JPEG', 'PNG']


def process_images(manga, file_list, user):
    # TODO: handle maximum total size
    errors = []
    manga_page_list = []
    process_list = []

    page_num = MangaPage.objects.filter(manga=manga).count()

    for i, f in enumerate(file_list, start=1):
        if page_num >= MANGA_PAGE_LIMIT:
            errors.append(_('There are currently {} images; All other uploaded image files were ignored.').format(MANGA_PAGE_LIMIT))
            break

        if f.size > MAX_IMAGE_FILE_SIZE:
            errors.append(_('{} is over 10MB in size.'.format(f.name)))
            continue

        try:
            Image.open(f).verify()
            f.seek(0)
        except Exception as e:
            errors.append(_('{} failed to verify as an image file.').format(f.name))
            continue

        im = Image.open(f)

        if im.format not in SUPPORTED_IMAGE_FORMATS:
            errors.append(_('{} is not a supported image type.').format(f.name))
            continue

        if im.size[0] > MAX_IMAGE_DIMENSION[0] or im.size[1] > MAX_IMAGE_DIMENSION[1]:
            errors.append(_('{} is larger than 8000x8000 pixels.').format(f.name))
            continue

        manga_page = MangaPage(
            manga=manga,
            page=page_num+i,
            image=f,
            name=f.name[:100],
            double=im.size[0] > im.size[1],
        )
        manga_page_list.append(manga_page)

        if not manga.cover:
            manga.cover = f
            manga.save(updated_by=user)
            process_list.append((manga.cover.path, ImageKeyType.MANGA_COVER, manga.id))

    MangaPage.objects.bulk_create(manga_page_list)

    # pre-generate image cache for speed
    manga_page_list = MangaPage.objects.filter(manga=manga, page__in=[mp.page for mp in manga_page_list])
    for mp in manga_page_list:
        image_key_type = mp.double and ImageKeyType.MANGA_PAGE_DOUBLE or ImageKeyType.MANGA_PAGE
        process_list.append((mp.image.path, image_key_type, mp.id))
        process_list.append((mp.image.path, ImageKeyType.MANGA_THUMB, mp.id))

    for args in process_list: image_resize(*args)

    return errors


def process_zipfile(manga, file, user):
    if not zipfile.is_zipfile(file):
        return [_('The uploaded file is not a valid zip file.')]

    file_list, errors = [], []
    with zipfile.ZipFile(file, 'r') as zip:
        zipinfo_list = sorted(zip.infolist(), key=lambda zipinfo: zipinfo.filename)
        if len(zipinfo_list) > MANGA_PAGE_LIMIT:
            errors.append(_('The zip archive contains more than 100 images, some images were ignored.'))

        for zipinfo in zipinfo_list[:MANGA_PAGE_LIMIT]:
            if zipinfo.filename.endswith(os.sep):
                continue
            temp_dir = tempfile.TemporaryDirectory()
            file = File(open(zip.extract(zipinfo, temp_dir.name), 'rb'), name=zipinfo.filename.split('/')[-1])
            file_list.append(file)

        errors.extend(process_images(manga, file_list, user))

    return errors


class MangaArchiveGenerator:

    LOCK_KEY = 'generate-manga-archive-lock-{}'
    LOCK_TIMEOUT = 30

    @classmethod
    def acquire_lock(cls, manga):
        if cache.get(cls.LOCK_KEY.format(manga.id)):
            return False

        cache.set(cls.LOCK_KEY.format(manga.id), True, cls.LOCK_TIMEOUT)
        return True

    @classmethod
    def release_lock(cls, manga):
        cache.delete(cls.LOCK_KEY.format(manga.id))

    @classmethod
    def generate(cls, manga):
        """
        This method is locked for up to 30 seconds (per manga) until it returns.
        This prevents the server from falling over due to stampede effect.
        """

        if not cls.acquire_lock(manga): return

        try:
            manga_archive = MangaArchive.objects.get(manga=manga)
            DeletedFile.objects.create(path=manga_archive.file.path)
        except MangaArchive.DoesNotExist:
            manga_archive = MangaArchive(manga=manga)

        manga_zip_file = BytesIO()
        manga_zip = zipfile.ZipFile(manga_zip_file, 'w')

        # write manga pages into zip file
        for page in MangaPage.objects.filter(manga=manga).order_by('page'):
            if not page.image: continue
            extension = get_image_extension(page.image)
            manga_zip.write(page.image.path, '{:03d}.{}'.format(page.page, extension))

        # write info.txt into zip file
        info_text = manga.info_text
        manga_zip.writestr('info.txt', info_text)
        manga_zip.close()

        manga_archive.name = manga.archive_name
        manga_archive.file = UploadedFile(manga_zip_file, 'archive.zip')
        manga_archive.save()

        manga_zip_file.close()

        cls.release_lock(manga)

        return manga_archive
