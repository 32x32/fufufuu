from django.db import models
from fufufuu.core.uploads import tag_image_upload_to
from fufufuu.core.utils import slugify
from fufufuu.tag.enums import TagType


class Tag(models.Model):

    tag_type        = models.CharField(max_length=20, choices=TagType.choices, db_index=True)

    name            = models.CharField(max_length=100)
    slug            = models.SlugField(max_length=100)
    markdown        = models.TextField(blank=True)
    html            = models.TextField(blank=True)
    manga_count     = models.PositiveIntegerField(default=0)
    image           = models.FileField(upload_to=tag_image_upload_to, null=True)

    created_on      = models.DateTimeField(auto_now_add=True)
    updated_on      = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '{}: {} - {}'.format(self.id, self.tag_type, self.name)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)[:100] or '-'
        super(Tag, self).save(*args, **kwargs)
