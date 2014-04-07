from django.db import models

from fufufuu.core.models import BaseAuditableModel
from fufufuu.core.utils import slugify


class BlogEntry(BaseAuditableModel):

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    markdown = models.TextField()
    html = models.TextField()

    class Meta:
        db_table = 'blog_entry'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)[:200] or '-'
        super().save(*args, **kwargs)
