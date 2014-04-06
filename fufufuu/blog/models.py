from django.db import models
from fufufuu.account.models import User
from fufufuu.core.utils import slugify


class BlogEntry(models.Model):

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    markdown = models.TextField()
    html = models.TextField()

    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'blog_entry'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)[:200] or '-'
        super().save(*args, **kwargs)
