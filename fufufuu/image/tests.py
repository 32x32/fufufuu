from django.db import models


class Image(models.Model):

    transformation = models.TextField(null=False, blank=False)
    source_image = models.FileField()
    output_image = models.FileField()

    class Meta:
        db_table = 'image'
