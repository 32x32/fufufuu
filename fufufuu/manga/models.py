from django.db import models
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from fufufuu.account.models import User
from fufufuu.core.languages import Language
from fufufuu.core.models import BaseAuditableModel
from fufufuu.core.uploads import manga_cover_upload_to, manga_archive_upload_to, manga_page_upload_to
from fufufuu.core.utils import slugify
from fufufuu.manga.enums import MangaCategory, MangaStatus
from fufufuu.manga.mixins import MangaMixin
from fufufuu.tag.models import Tag


class MangaManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().exclude(status=MangaStatus.DELETED)


class MangaPublishedManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(status=MangaStatus.PUBLISHED).order_by('-published_on')


class Manga(BaseAuditableModel, MangaMixin):

    title               = models.CharField(max_length=100, default='Untitled')
    slug                = models.SlugField(max_length=100)
    markdown            = models.TextField(blank=True)
    html                = models.TextField(blank=True)
    cover               = models.FileField(upload_to=manga_cover_upload_to, null=True)
    status              = models.CharField(max_length=20, choices=MangaStatus.choices, default=MangaStatus.DRAFT, db_index=True)
    category            = models.CharField(max_length=20, choices=MangaCategory.choices, default=MangaCategory.OTHER, db_index=True)
    language            = models.CharField(max_length=20, choices=Language.choices, default=Language.ENGLISH)
    uncensored          = models.BooleanField(default=False)

    tags                = models.ManyToManyField(Tag, blank=True)
    tank                = models.ForeignKey(Tag, null=True, blank=True, related_name='+')
    collection          = models.ForeignKey(Tag, null=True, blank=True, related_name='+')
    tank_chapter        = models.CharField(max_length=20, null=True, blank=True)
    collection_part     = models.CharField(max_length=20, null=True, blank=True)
    favorite_users      = models.ManyToManyField(User, related_name='manga_favorites', blank=True)

    published_on        = models.DateTimeField(null=True, db_index=True)

    objects             = MangaManager()
    published           = MangaPublishedManager()
    all                 = models.Manager()

    class Meta:
        db_table = 'manga'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)[:100] or '-'
        super().save(*args, **kwargs)

    def delete(self, force_delete=False, *args, **kwargs):
        if self.status == MangaStatus.DRAFT or force_delete:
            super().delete(*args, **kwargs)
        else:
            self.status = MangaStatus.DELETED
            self.save(*args, **kwargs)


class MangaHistory(models.Model, MangaMixin):

    manga               = models.ForeignKey(Manga)

    title               = models.CharField(max_length=100, default='Untitled')
    slug                = models.SlugField(max_length=100)
    markdown            = models.TextField(blank=True)
    html                = models.TextField(blank=True)
    cover               = models.FileField(upload_to=manga_cover_upload_to, null=True)
    category            = models.CharField(max_length=20, choices=MangaCategory.choices, default=MangaCategory.VANILLA, db_index=True)
    status              = models.CharField(max_length=20, choices=MangaStatus.choices, default=MangaStatus.DRAFT, db_index=True)
    language            = models.CharField(max_length=20, choices=Language.choices, default=Language.ENGLISH)
    uncensored          = models.BooleanField(default=False)

    tags                = models.ManyToManyField(Tag, blank=True)
    tank                = models.ForeignKey(Tag, null=True, blank=True, related_name='+')
    collection          = models.ForeignKey(Tag, null=True, blank=True, related_name='+')
    tank_chapter        = models.CharField(max_length=20, null=True, blank=True)
    collection_part     = models.CharField(max_length=20, null=True, blank=True)

    created_by          = models.ForeignKey(User)
    created_on          = models.DateTimeField()

    class Meta:
        db_table = 'manga_history'


class MangaPage(models.Model):

    manga = models.ForeignKey(Manga)
    double = models.BooleanField(default=False)
    page = models.PositiveIntegerField()
    image = models.FileField(upload_to=manga_page_upload_to)
    name = models.CharField(max_length=100, null=True)

    class Meta:
        db_table = 'manga_page'
        ordering = ('page',)


class MangaArchive(models.Model):

    manga = models.ForeignKey(Manga)
    file = models.FileField(upload_to=manga_archive_upload_to)
    downloads = models.PositiveIntegerField(default=0)
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


class MangaHistoryTag(models.Model):

    mangahistory = models.ForeignKey(MangaHistory)
    tag = models.ForeignKey(Tag)

    class Meta:
        managed = False
        db_table = 'manga_history_tags'


#-------------------------------------------------------------------------------
# model signals
#-------------------------------------------------------------------------------


@receiver(post_delete, sender=Manga)
def manga_post_delete(instance, **kwargs):
    for field in ['cover']:
        field = getattr(instance, field)
        if field: field.storage.delete(field.path)


@receiver(post_delete, sender=MangaPage)
def manga_page_post_delete(instance, **kwargs):
    for field in ['image']:
        field = getattr(instance, field)
        if field: field.storage.delete(field.path)


@receiver(post_delete, sender=MangaArchive)
def manga_archive_post_delete(instance, **kwargs):
    for field in ['file']:
        field = getattr(instance, field)
        if field: field.storage.delete(field.path)
