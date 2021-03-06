from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch.dispatcher import receiver

from fufufuu.account.models import User
from fufufuu.core.languages import Language
from fufufuu.core.models import BaseAuditableModel
from fufufuu.core.uploads import manga_cover_upload_to, manga_archive_upload_to, manga_page_upload_to
from fufufuu.core.utils import slugify
from fufufuu.image.enums import ImageKeyType
from fufufuu.image.models import Image
from fufufuu.manga.enums import MangaCategory, MangaStatus
from fufufuu.manga.mixins import MangaMixin
from fufufuu.tag.models import Tag


class MangaManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().exclude(status=MangaStatus.DELETED)


class MangaPublishedManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(status=MangaStatus.PUBLISHED).order_by('-published_on')


class MangaPublicManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(status__in=[MangaStatus.PUBLISHED, MangaStatus.DMCA])


class Manga(BaseAuditableModel, MangaMixin):

    title               = models.CharField(max_length=100, default='Untitled', db_index=True)
    slug                = models.SlugField(max_length=100)
    markdown            = models.TextField(blank=True)
    html                = models.TextField(blank=True)
    cover               = models.FileField(upload_to=manga_cover_upload_to, null=True, max_length=255)
    status              = models.CharField(max_length=20, choices=MangaStatus.choices, default=MangaStatus.DRAFT, db_index=True)
    category            = models.CharField(max_length=20, choices=MangaCategory.choices, default=MangaCategory.OTHER, db_index=True)
    language            = models.CharField(max_length=20, choices=Language.choices, default=Language.ENGLISH, db_index=True)
    uncensored          = models.BooleanField(default=False)

    tags                = models.ManyToManyField(Tag, blank=True)
    tank                = models.ForeignKey(Tag, null=True, blank=True, related_name='+', on_delete=models.SET_NULL)
    collection          = models.ForeignKey(Tag, null=True, blank=True, related_name='+', on_delete=models.SET_NULL)
    tank_chapter        = models.CharField(max_length=20, null=True, blank=True)
    collection_part     = models.CharField(max_length=20, null=True, blank=True)
    favorite_users      = models.ManyToManyField(User, related_name='manga_favorites', blank=True)

    published_on        = models.DateTimeField(null=True, db_index=True)

    objects             = MangaManager()
    published           = MangaPublishedManager()
    public              = MangaPublicManager()
    all                 = models.Manager()

    class Meta:
        db_table = 'manga'

    def save(self, updated_by, *args, **kwargs):
        self.slug = slugify(self.title)[:100] or '-'
        super().save(updated_by, *args, **kwargs)

    def delete(self, updated_by=None, force_delete=False, *args, **kwargs):
        if self.status == MangaStatus.DRAFT or force_delete:
            super().delete(*args, **kwargs)
        else:
            self.status = MangaStatus.DELETED
            self.save(updated_by, *args, **kwargs)

    def is_favorited_by(self, user):
        return user.is_authenticated() and MangaFavorite.objects.filter(manga=self, user=user).exists()


class MangaPage(models.Model):

    manga = models.ForeignKey(Manga, on_delete=models.CASCADE)
    double = models.BooleanField(default=False)
    page = models.PositiveIntegerField()
    image = models.FileField(upload_to=manga_page_upload_to, max_length=255)
    name = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'manga_page'
        ordering = ('page',)


class MangaArchive(models.Model):

    manga = models.ForeignKey(Manga, unique=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to=manga_archive_upload_to, max_length=255)
    downloads = models.PositiveIntegerField(default=0)

    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'manga_archive'


#-------------------------------------------------------------------------------
# unmanaged join tables
#-------------------------------------------------------------------------------


class MangaTag(models.Model):

    manga = models.ForeignKey(Manga)
    tag = models.ForeignKey(Tag)

    class Meta:
        managed = False
        db_table = 'manga_tags'


class MangaFavorite(models.Model):

    manga = models.ForeignKey(Manga)
    user = models.ForeignKey(User)

    class Meta:
        managed = False
        db_table = 'manga_favorite_users'


#-------------------------------------------------------------------------------
# model signals
#-------------------------------------------------------------------------------


@receiver(post_delete, sender=Manga)
def manga_post_delete(instance, **kwargs):
    Image.safe_delete(key_type=ImageKeyType.MANGA_COVER, key_id=instance.id)
    for field in ['cover']:
        field = getattr(instance, field)
        if field: field.storage.delete(field.path)


@receiver(post_delete, sender=MangaPage)
def manga_page_post_delete(instance, **kwargs):
    key_type = instance.double and ImageKeyType.MANGA_PAGE_DOUBLE or ImageKeyType.MANGA_PAGE
    Image.safe_delete(key_type=key_type, key_id=instance.id)
    Image.safe_delete(key_type=ImageKeyType.MANGA_THUMB, key_id=instance.id)
    for field in ['image']:
        field = getattr(instance, field)
        if field: field.storage.delete(field.path)


@receiver(post_delete, sender=MangaArchive)
def manga_archive_post_delete(instance, **kwargs):
    for field in ['file']:
        field = getattr(instance, field)
        if field: field.storage.delete(field.path)


@receiver(post_save, sender=Manga)
def manga_post_save(instance, **kwargs):
    Image.safe_delete(key_type=ImageKeyType.MANGA_COVER, key_id=instance.id)
