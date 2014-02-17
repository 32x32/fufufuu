from django.db import models
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from fufufuu.account.models import User
from fufufuu.core.languages import Language
from fufufuu.core.models import BaseAuditableModel
from fufufuu.core.uploads import tag_cover_upload_to
from fufufuu.core.utils import slugify
from fufufuu.tag.enums import TagType


class Tag(BaseAuditableModel):

    tag_type = models.CharField(max_length=20, choices=TagType.choices)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, db_index=True)

    class Meta:
        db_table = 'tag'
        unique_together = [('tag_type', 'name')]

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)[:100] or '-'
        super().save(*args, **kwargs)


class TagAlias(models.Model):

    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    language = models.CharField(max_length=20, choices=Language.choices)
    name = models.CharField(max_length=100)

    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, blank=True, related_name='+', on_delete=models.SET_NULL, db_index=True)

    class Meta:
        db_table = 'tag_alias'
        unique_together = [('tag', 'language', 'name')]


class TagData(BaseAuditableModel):

    tag = models.ForeignKey(Tag)
    language = models.CharField(max_length=20, choices=Language.choices)
    markdown = models.TextField(blank=True)
    html = models.TextField(blank=True)
    cover = models.FileField(upload_to=tag_cover_upload_to, null=True)

    class Meta:
        db_table = 'tag_data'
        unique_together = [('tag', 'language')]


#-------------------------------------------------------------------------------
# signals
#-------------------------------------------------------------------------------


@receiver(post_delete, sender=TagData)
def tag_data_post_delete(instance, **kwargs):
    for field in ['cover']:
        field = getattr(instance, field)
        if field: field.storage.delete(field.path)
