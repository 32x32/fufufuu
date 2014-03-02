from django.core.cache import cache
from django.db.models.fields.files import FieldFile
from django.db.utils import IntegrityError

from fufufuu.image.models import Image, get_cache_key


IMAGE_CACHE_TIMEOUT = 60 * 60 # 60 minutes


def image_resize(file_field, key_type, key_id):
    """
    key_type should be one of ImageKeyType.choices
    """

    if not file_field or not isinstance(file_field, FieldFile):
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
            image.save(file_field)
        except IntegrityError:
            image = Image.objects.only('file').get(key_type=key_type, key_id=key_id)

    cache.set(cache_key, image.file.url, IMAGE_CACHE_TIMEOUT)
    return image.file.url
