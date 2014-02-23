import os
import tempfile
import zipfile
from io import BytesIO
from django.core.files.base import File
from django.core.files.uploadedfile import UploadedFile
from django.utils.translation import ugettext as _
from PIL import Image
from fufufuu.core.models import DeletedFile
from fufufuu.core.templates import TEMPLATE_ENV
from fufufuu.core.utils import get_image_extension
from fufufuu.manga.enums import MangaStatus
from fufufuu.manga.models import MangaPage, MangaArchive
from fufufuu.tag.models import Tag


MAX_TOTAL_SIZE          = 200 * 1024 * 1024
MAX_IMAGE_FILE_SIZE     = 8 * 1024 * 1024
MAX_IMAGE_DIMENSION     = (8000, 8000)
MANGA_PAGE_LIMIT        = 100
SUPPORTED_IMAGE_FORMATS = ['JPEG', 'PNG']


def process_images(manga, file_list, user):
    # TODO: handle maximum total size
    errors, manga_page_list = [], []
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

    MangaPage.objects.bulk_create(manga_page_list)
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


def generate_manga_archive(manga):
    if manga.status != MangaStatus.PUBLISHED:
        raise RuntimeError('generate_manga_archive should only be used with published manga')

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
    info_text = TEMPLATE_ENV.get_template('manga/manga-archive-info.txt').render({'manga': manga})
    manga_zip.writestr('info.txt', info_text)
    manga_zip.close()

    manga_archive.name = manga.archive_name
    manga_archive.file = UploadedFile(manga_zip_file, 'archive.zip')
    manga_archive.save()

    manga_zip_file.close()

    return manga_archive


def attach_revision_tags(revision_list):
    """
    sets the value of revision.tag to be (old_tags, new_tags) where
    old_tags, new_tags are sets of tag object
    """

    tag_id_list = []
    for revision in revision_list:
        if 'tags' not in revision.diff: continue
        ts1, ts2 = revision.diff['tags']
        tag_id_list.extend(ts1)
        tag_id_list.extend(ts2)

    tag_list = Tag.objects.filter(id__in=tag_id_list).values('id', 'name', 'tag_type')
    tag_dict = dict([(t['id'], (t['tag_type'], t['name'])) for t in tag_list])
    for revision in revision_list:
        if 'tags' not in revision.diff: continue
        ts1, ts2 = revision.diff['tags']
        revision.tags = (set([tag_dict[tid] for tid in ts1]), set([tag_dict[tid] for tid in ts2]))
