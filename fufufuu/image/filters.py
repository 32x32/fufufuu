from django.core.cache import cache
from django.db.utils import IntegrityError
from fufufuu.image.models import Image


def image(source, key_type, key_id):
    """
    key_type should be one of ImageKeyType.choices
    """

    if not source:
        return ''

    key_type = key_type.upper()

    cache_key = 'image-{}-{}'.format(key_type.lower(), key_id)
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
