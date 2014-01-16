import os
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch.dispatcher import receiver
from fufufuu.core.uploads import image_upload_to
from fufufuu.image.enums import ImageKeyType
from fufufuu.image.utils import ImageTransformer
from fufufuu.manga.models import Manga


class Image(models.Model):

    key_type = models.CharField(max_length=20, choices=ImageKeyType.choices)
    key_id = models.IntegerField()

    file = models.FileField(upload_to=image_upload_to)

    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'image'
        unique_together = [('key_type', 'key_id')]

    def save(self, source, *args, **kwargs):
        path = None
        if self.file: path = self.file.path

        file_content = ImageTransformer.transform(self.key_type, source)
        self.file.save('', SimpleUploadedFile('', file_content.getvalue()), save=False)
        super().save(*args, **kwargs)

        if path: os.remove(path)    # delete the old file that was associated with this instance


#-------------------------------------------------------------------------------
# model signals
#-------------------------------------------------------------------------------


@receiver(post_delete, sender=Image)
def image_post_delete(instance, **kwargs):
    for field in ['file']:
        field = getattr(instance, field)
        if field: field.storage.delete(field.path)


@receiver(post_save, sender=Manga)
def manga_post_save(instance, **kwargs):
    Image.objects.filter(key_type=ImageKeyType.MANGA_COVER, key_id=instance.id).delete()
    cache.delete('image-{}-{}'.format(ImageKeyType.MANGA_COVER.lower(), instance.id))
