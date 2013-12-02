from django.db import models
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from fufufuu.account.models import User
from fufufuu.core.languages import Language
from fufufuu.core.uploads import manga_cover_upload_to, manga_archive_upload_to, manga_page_upload_to
from fufufuu.core.utils import slugify
from fufufuu.manga.enums import MangaCategory, MangaStatus
from fufufuu.tag.models import Tag


class MangaManager(models.Manager):

    def get_query_set(self):
        return super().get_query_set().exclude(status=MangaStatus.DELETED)


class Manga(models.Model):

    uploader            = models.ForeignKey(User, related_name='manga_uploads', on_delete=models.SET_NULL, null=True)

    title               = models.CharField(max_length=100, default='Untitled')
    slug                = models.SlugField(max_length=100)
    markdown            = models.TextField(blank=True)
    html                = models.TextField(blank=True)
    cover               = models.FileField(upload_to=manga_cover_upload_to, null=True)
    category            = models.CharField(max_length=20, choices=MangaCategory.choices, default=MangaCategory.VANILLA, db_index=True)
    status              = models.CharField(max_length=20, choices=MangaStatus.choices, default=MangaStatus.DRAFT, db_index=True)
    language            = models.CharField(max_length=10, choices=Language.choices, default=Language.ENGLISH)

    collections         = models.ManyToManyField(Tag, blank=True, through='MangaCollection', related_name='collection+')
    tanks               = models.ManyToManyField(Tag, blank=True, through='MangaTank', related_name='tank+')
    tags                = models.ManyToManyField(Tag, blank=True)
    favorite_users      = models.ManyToManyField(User, related_name='manga_favorites', blank=True)

    created_on          = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_on          = models.DateTimeField(auto_now=True)
    published_on        = models.DateTimeField(null=True, db_index=True)

    objects             = MangaManager()
    all                 = models.Manager()

    def __unicode__(self):
        return '{}: {}'.format(self.id, self.title)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)[:100] or '-'
        super(Manga, self).save(*args, **kwargs)

    def delete(self, delete_from_db=False, *args, **kwargs):
        if self.status == MangaStatus.DRAFT or delete_from_db:
            super(Manga, self).delete(*args, **kwargs)
        else:
            self.status = MangaStatus.DELETED
            self.save()


class MangaTank(models.Model):

    manga           = models.ForeignKey(Manga)
    tag             = models.ForeignKey(Tag)
    chapter         = models.CharField(max_length=10)


class MangaCollection(models.Model):

    manga           = models.ForeignKey(Manga)
    tag             = models.ForeignKey(Tag)
    chapter         = models.CharField(max_length=10)


class MangaPage(models.Model):

    manga           = models.ForeignKey(Manga)
    double          = models.BooleanField(default=False)
    page            = models.PositiveIntegerField()
    image           = models.FileField(upload_to=manga_page_upload_to)
    name            = models.CharField(max_length=200, null=True)

    class Meta:
        ordering = ('page',)

    def __unicode__(self):
        return '{}: {} - Page {}'.format(self.id, self.manga.title, self.page)


class MangaArchive(models.Model):

    manga           = models.ForeignKey(Manga)
    file            = models.FileField(upload_to=manga_archive_upload_to)
    downloads       = models.PositiveIntegerField(default=0)
    created_on      = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '{}: {}'.format(self.id, self.manga.title)


#-------------------------------------------------------------------------------
# unmanaged join tables
#-------------------------------------------------------------------------------


class MangaTag(models.Model):

    manga = models.ForeignKey(Manga)
    tag = models.ForeignKey(Tag)

    class Meta:
        managed = False
        db_table = 'manga_manga_tags'


class MangaFavorite(models.Model):

    manga = models.ForeignKey(Manga)
    user = models.ForeignKey(User)

    class Meta:
        managed = False
        db_table = 'manga_manga_favorite_users'


#-------------------------------------------------------------------------------
# model signals
#-------------------------------------------------------------------------------


@receiver(post_delete, sender=Manga)
def manga_post_delete(instance, **kwargs):
    for field in ['cover']:
        field = getattr(instance, field)
        if field: field.storage.delete(field.path)


@receiver(post_delete, sender=MangaPage)
def manga_image_post_delete(instance, **kwargs):
    for field in ['image']:
        field = getattr(instance, field)
        if field: field.storage.delete(field.path)


@receiver(post_delete, sender=MangaArchive)
def manga_archive_post_delete(instance, **kwargs):
    for field in ['file']:
        field = getattr(instance, field)
        if field: field.storage.delete(field.path)
