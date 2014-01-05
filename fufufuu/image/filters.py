from fufufuu.image.models import Image


def image(source, key_type, key_id):
    key_type = key_type.upper()
    try:
        image = Image.objects.get(key_type=key_type, key_id=key_id)
    except Image.DoesNotExist:
        image = Image(key_type=key_type, key_id=key_id)
        image.save(source)
    return image.file.url
