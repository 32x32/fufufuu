from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch.dispatcher import receiver
from fufufuu.account.models import User
from fufufuu.core.languages import Language
from fufufuu.core.models import BaseAuditableModel
from fufufuu.core.uploads import tag_cover_upload_to
from fufufuu.core.utils import slugify
from fufufuu.image.enums import ImageKeyType
from fufufuu.image.filters import image_resize
from fufufuu.image.models import Image
from fufufuu.tag.enums import TagType


class Tag(BaseAuditableModel):

    tag_type = models.CharField(max_length=20, choices=TagType.choices)
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100)
    cover = models.FileField(upload_to=tag_cover_upload_to, blank=True, null=True, max_length=255)

    class Meta:
        db_table = 'tag'
        unique_together = [('tag_type', 'name')]

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)[:100] or '-'
        super().save(*args, **kwargs)

    def set_default_cover(self):
        from fufufuu.manga.models import Manga

        if self.tag_type not in [TagType.TANK, TagType.COLLECTION]:
            return
        if self.tag_type == TagType.TANK:
            filter_dict = {
                'tank_id': self.id,
                'cover__isnull': False,
            }
            order_attr = 'tank_chapter'
        elif self.tag_type == TagType.COLLECTION:
            filter_dict = {
                'collection_id': self.id,
                'cover__isnull': False,
            }
            order_attr = 'collection_part'

        manga_list = Manga.published.filter(**filter_dict).order_by(order_attr).only('cover')
        cover_list = [manga.cover.path for manga in manga_list if manga.cover]
        if cover_list:
            self.cover = SimpleUploadedFile('cover', open(cover_list[0], 'rb').read())
            self.save(None)

    @property
    def cover_url(self):
        return image_resize(self.cover, ImageKeyType.TAG_COVER, self.id)


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

    class Meta:
        db_table = 'tag_data'
        unique_together = [('tag', 'language')]


#-------------------------------------------------------------------------------
# signals
#-------------------------------------------------------------------------------


@receiver(post_delete, sender=Tag)
def tag_post_delete(instance, **kwargs):
    Image.objects.filter(key_type=ImageKeyType.TAG_COVER, key_id=instance.id).delete()
    for field in ['cover']:
        field = getattr(instance, field)
        if field: field.storage.delete(field.path)

@receiver(post_save, sender=Tag)
def manga_post_save(instance, **kwargs):
    Image.objects.filter(key_type=ImageKeyType.TAG_COVER, key_id=instance.id).delete()
