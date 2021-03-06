import os

from django.utils import timezone
from django.utils.http import int_to_base36

from fufufuu.core.utils import get_image_extension


def get_timestamp():
    return timezone.now().strftime('%Y%m%d%H%M%S')


def user_avatar_upload_to(instance, filename):
    filename = '{}.{}'.format(int_to_base36(instance.id), get_image_extension(instance.avatar))
    dirs = int_to_base36(instance.id)[:-1]
    return os.sep.join(['user-avatar'] + list(dirs) + [filename])


def manga_cover_upload_to(instance, filename):
    filename = '{}-{}.{}'.format(int_to_base36(instance.id), get_timestamp(), get_image_extension(instance.cover))
    dirs = int_to_base36(instance.id)[:-1]
    return os.sep.join(['manga-cover'] + list(dirs) + [filename])


def manga_archive_upload_to(instance, filename):
    manga = instance.manga
    filename = '{}-{}.zip'.format(int_to_base36(manga.id), get_timestamp())
    dirs = int_to_base36(manga.id)[:-1]
    return os.sep.join(['manga-archive'] + list(dirs) + [filename])


def manga_page_upload_to(instance, filename):
    filename = '{}-{}.{}'.format(instance.page, get_timestamp(), get_image_extension(instance.image))
    dirs = int_to_base36(instance.manga.id)
    return os.sep.join(['manga-page'] + list(dirs) + [filename])


def tag_cover_upload_to(instance, filename):
    filename = '{}-{}.{}'.format(int_to_base36(instance.id), get_timestamp(), get_image_extension(instance.cover))
    dirs = int_to_base36(instance.id)[:-1]
    return os.sep.join(['tag-cover'] + list(dirs) + [filename])


def image_upload_to(instance, filename):
    """
    random_key is used to prevent scraping of the website
    """

    key = int(timezone.now().strftime('%Y%m%d%H%M%S%f'))
    key = int_to_base36(key)
    filename = '{}-{}.jpg'.format(int_to_base36(instance.key_id), key)
    dirs = int_to_base36(instance.key_id)[:-1]
    return os.sep.join(['image', instance.key_type.lower()] + list(dirs) + [filename])


def disabled_upload_to(instance, filename):
    raise RuntimeError('This filefield cannot be uploaded to.')
