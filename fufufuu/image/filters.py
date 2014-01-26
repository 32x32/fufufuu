from django.core.cache import cache
from django.core.files.base import File
from django.db.utils import IntegrityError
from fufufuu.image.models import Image, get_cache_key


def image(source, key_type, key_id):
    """
    key_type should be one of ImageKeyType.choices
    """

    if not source or not isinstance(source, File):
        return ''

    key_type = key_type.upper()

    cache_key = get_cache_key(key_type, key_id)
    url = cache.get(cache_key)
    if url: return url

    try:
        image = Image.objects.only('file').get(key_type=key_type, key_id=key_id)
    except Image.DoesNotExist:
        image = Image(key_type=key_type, key_id=key_id)
        try:
            image.save(source)
        except IntegrityError:
            image = Image.objects.only('file').get(key_type=key_type, key_id=key_id)

    cache.set(cache_key, image.file.url)
    return image.file.url
