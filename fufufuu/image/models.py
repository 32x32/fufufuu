from django.db import models
from fufufuu.core.uploads import image_upload_to, disabled_upload_to


class Image(models.Model):

    transformation = models.TextField(null=False, blank=False)
    source = models.FileField(upload_to=disabled_upload_to)
    output = models.FileField(upload_to=image_upload_to)

    class Meta:
        db_table = 'image'
