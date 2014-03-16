from django.db import models
from django.utils import timezone
from django.core.cache import cache

from fufufuu.account.models import User
from fufufuu.core.enums import SiteSettingKey


SITE_SETTING_CACHE_KEY = 'site_settings'
SITE_SETTING_CACHE_TIMEOUT = 30 * 24 * 60 * 60


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

    key = models.CharField(max_length=255, choices=SiteSettingKey.choices, unique=True)
    val = models.TextField(blank=True, null=True)
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)

    revision_field_list = ['key', 'val']

    class Meta:
        db_table = 'site_setting'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    @classmethod
    def as_dict(cls):
        _site_settings = cache.get(SITE_SETTING_CACHE_KEY)
        if _site_settings: return _site_settings

        _site_settings = dict([(s.key, s.val) for s in SiteSetting.objects.all()])
        for k, v in _site_settings.items():
            if SiteSettingKey.key_type[k] == bool:
                _site_settings[k] = v == 'True'

        cache.set(SITE_SETTING_CACHE_KEY, _site_settings, SITE_SETTING_CACHE_TIMEOUT)
        return _site_settings
