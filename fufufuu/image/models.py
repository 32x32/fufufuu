from django.db import models
from fufufuu.core.uploads import image_upload_to
from fufufuu.image.enums import ImageKeyType
from fufufuu.image.utils import ImageTransformer


class Image(models.Model):

    key_type = models.CharField(max_length=20, choices=ImageKeyType.choices)
    key_id = models.IntegerField()

    file = models.FileField(upload_to=image_upload_to)

    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'image'
        unique_together = [('key_type', 'key_id')]

    def save(self, source, *args, **kwargs):
        self.file = ImageTransformer.transform(self.key_type, source)
        super().save(*args, **kwargs)
