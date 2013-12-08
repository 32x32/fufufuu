from django.db import models
from fufufuu.account.models import User
from fufufuu.core.languages import Language
from fufufuu.core.models import BaseAuditableModel
from fufufuu.core.uploads import tag_cover_upload_to
from fufufuu.core.utils import slugify
from fufufuu.tag.enums import TagType


class Tag(models.Model):

    tag_type = models.CharField(max_length=20, choices=TagType.choices, db_index=True)

    class Meta:
        db_table = 'tag'


class TagData(BaseAuditableModel):

    tag = models.ForeignKey(Tag)
    language = models.CharField(max_length=20, choices=Language.choices, db_index=True)

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, db_index=True)
    markdown = models.TextField(blank=True)
    html = models.TextField(blank=True)
    cover = models.FileField(upload_to=tag_cover_upload_to, null=True)

    class Meta:
        db_table = 'tag_data'
        unique_together = (('tag', 'language'),)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)[:100] or '-'
        super().save(*args, **kwargs)


class TagDataHistory(models.Model):

    tag_data = models.ForeignKey(TagData)

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, db_index=True)
    markdown = models.TextField(blank=True)
    html = models.TextField(blank=True)
    cover = models.FileField(upload_to=tag_cover_upload_to, null=True)

    created_by = models.ForeignKey(User)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tag_data_history'


class TagAlias(BaseAuditableModel):

    tag = models.ForeignKey(TagData)

    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, db_index=True)

    class Meta:
        db_table = 'tag_alias'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)[:100] or '-'
        super().save(*args, **kwargs)
