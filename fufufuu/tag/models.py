from django.db import models
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from fufufuu.account.models import User
from fufufuu.core.languages import Language
from fufufuu.core.models import BaseAuditableModel
from fufufuu.core.uploads import tag_cover_upload_to
from fufufuu.core.utils import slugify
from fufufuu.tag.enums import TagType


class Tag(models.Model):

    tag_type = models.CharField(max_length=20, choices=TagType.choices, db_index=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tag'


class TagBase(models.Model):

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, db_index=True)
    markdown = models.TextField(blank=True)
    html = models.TextField(blank=True)
    cover = models.FileField(upload_to=tag_cover_upload_to, null=True)

    class Meta:
        abstract = True


class TagData(TagBase, BaseAuditableModel):

    tag = models.ForeignKey(Tag)
    language = models.CharField(max_length=20, choices=Language.choices, db_index=True)
    alias = models.ForeignKey('self', null=True, related_name='alias_set')

    class Meta:
        db_table = 'tag_data'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)[:100] or '-'
        super().save(*args, **kwargs)


class TagDataHistory(TagBase):

    tag_data = models.ForeignKey(TagData)

    created_by = models.ForeignKey(User)
    created_on = models.DateTimeField()

    class Meta:
        db_table = 'tag_data_history'


#-------------------------------------------------------------------------------
# signals
#-------------------------------------------------------------------------------


@receiver(post_delete, sender=TagData)
def tag_data_post_delete(instance, **kwargs):
    for field in ['cover']:
        field = getattr(instance, field)
        if field: field.storage.delete(field.path)


@receiver(post_delete, sender=TagDataHistory)
def tag_data_history_post_delete(instance, **kwargs):
    for field in ['cover']:
        field = getattr(instance, field)
        if field: field.storage.delete(field.path)


