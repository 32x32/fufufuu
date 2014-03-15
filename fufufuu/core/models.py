from django.db import models
from django.utils import timezone
from django.core.cache import cache
from django.utils.functional import SimpleLazyObject
from django.utils.translation import ugettext as _
from fufufuu.account.models import User


class BaseAuditableModel(models.Model):

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True, db_index=True)

    created_by = models.ForeignKey(User, null=True, blank=True, related_name='+', on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(User, null=True, blank=True, related_name='+', on_delete=models.SET_NULL)

    class Meta:
        abstract = True

    def save(self, updated_by, *args, **kwargs):
        self.updated_by = updated_by
        if not self.created_by:
            self.created_by = updated_by
        super().save(*args, **kwargs)


def default_delete_time():
    return timezone.now() + timezone.timedelta(hours=24)


class DeletedFile(models.Model):
    """
    This model is used to store file paths that should be not be deleted
    immediately. The management command "clear_deleted_files" should be
    used to remove the actual underlying files and database entries.

    Files are marked safe to delete after 24 hours by default.

    Note: delete signals are not used so we can properly catch and handle
    any file deletion errors.
    """

    path = models.CharField(max_length=1024)
    delete_after = models.DateTimeField(default=default_delete_time)

    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'deleted_file'



class SiteSetting(models.Model):

    choices = (
        ('ANNOUNCEMENT',        _('Announcement')),
        ('ENABLE_COMMENTS',     _('Enable Comments')),
        ('ENABLE_UPLOADS',      _('Enable Uploads')),
    )

    choices_dict = dict(choices)

    key = models.CharField(max_length=255, choices=choices)
    val = models.CharField(max_length=255, blank=True, null=True)
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'site_setting'

    revision_field_list = ['key', 'val']


def _get_site_settings():
    """
    Try to get site_settings object from cache before going to the database.
    """

    _site_settings = cache.get('site_settings')
    if _site_settings: return _site_settings

    _site_settings = dict([(s.key, s.val) for s in SiteSetting.objects.all()])
    cache.set('site_settings', _site_settings)
    return _site_settings


site_settings = SimpleLazyObject(_get_site_settings)
