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


class TagData(BaseAuditableModel):

    tag = models.ForeignKey(Tag)
    language = models.CharField(max_length=20, choices=Language.choices, db_index=True)

    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, db_index=True)
    markdown = models.TextField(blank=True)
    html = models.TextField(blank=True)
    cover = models.FileField(upload_to=tag_cover_upload_to, null=True)

    class Meta:
        db_table = 'tag_data'
        unique_together = (('tag', 'language'),)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)[:50] or '-'
        super().save(*args, **kwargs)


class TagDataHistory(models.Model):

    tag_data = models.ForeignKey(TagData)

    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, db_index=True)
    markdown = models.TextField(blank=True)
    html = models.TextField(blank=True)
    cover = models.FileField(upload_to=tag_cover_upload_to, null=True)

    created_by = models.ForeignKey(User)
    created_on = models.DateTimeField()

    class Meta:
        db_table = 'tag_data_history'


class TagAlias(BaseAuditableModel):

    tag = models.ForeignKey(TagData)

    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=50, db_index=True)

    class Meta:
        db_table = 'tag_alias'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)[:50] or '-'
        super().save(*args, **kwargs)


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


