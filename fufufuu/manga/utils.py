import os
import tempfile
import zipfile
from django.core.files.base import File
from django.utils.translation import ugettext as _
from PIL import Image
from fufufuu.manga.models import MangaPage


MAX_IMAGE_FILE_SIZE     = 10 * 1024 * 1024
MAX_IMAGE_DIMENSION     = (8000, 8000)
MANGA_PAGE_LIMIT        = 100
SUPPORTED_IMAGE_FORMATS = ['JPEG', 'PNG']


def process_images(manga, file_list):
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
            manga.save()

    MangaPage.objects.bulk_create(manga_page_list)
    return errors


def process_zipfile(manga, file):
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

        errors.extend(process_images(manga, file_list))

    return errors
