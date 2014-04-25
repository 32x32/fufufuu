from django import forms
from django.utils.translation import ugettext_lazy as _


class SiteSettingKey:

    ANNOUNCEMENT                = 'ANNOUNCEMENT'
    DOWNLOAD_LIMIT              = 'DOWNLOAD_LIMIT'
    DOWNLOAD_TIMEOUT            = 'DOWNLOAD_TIMEOUT'
    ENABLE_COMMENTS             = 'ENABLE_COMMENTS'
    ENABLE_DOWNLOADS            = 'ENABLE_DOWNLOADS'
    ENABLE_REGISTRATION         = 'ENABLE_REGISTRATION'
    ENABLE_UPLOADS              = 'ENABLE_UPLOADS'
    REPORT_THRESHOLD            = 'REPORT_THRESHOLD'

    choices = (
        (ANNOUNCEMENT,          _('Announcement')),
        (DOWNLOAD_LIMIT,        _('Download Limit')),
        (DOWNLOAD_TIMEOUT,      _('Download Timeout (in seconds)')),
        (ENABLE_COMMENTS,       _('Enable Comments')),
        (ENABLE_DOWNLOADS,      _('Enable Downloads')),
        (ENABLE_REGISTRATION,   _('Enable Registration')),
        (ENABLE_UPLOADS,        _('Enable Uploads')),
        (REPORT_THRESHOLD,      _('Report Threshold')),
    )

    choices_dict = dict(choices)

    key_type = {
        ANNOUNCEMENT:           str,
        DOWNLOAD_LIMIT:         int,
        DOWNLOAD_TIMEOUT:       int,
        ENABLE_COMMENTS:        bool,
        ENABLE_DOWNLOADS:       bool,
        ENABLE_REGISTRATION:    bool,
        ENABLE_UPLOADS:         bool,
        REPORT_THRESHOLD:       int,
    }

    form_field_type = {
        ANNOUNCEMENT:           forms.CharField,
        DOWNLOAD_LIMIT:         forms.IntegerField,
        DOWNLOAD_TIMEOUT:       forms.IntegerField,
        ENABLE_COMMENTS:        forms.BooleanField,
        ENABLE_DOWNLOADS:       forms.BooleanField,
        ENABLE_REGISTRATION:    forms.BooleanField,
        ENABLE_UPLOADS:         forms.BooleanField,
        REPORT_THRESHOLD:       forms.IntegerField,
    }

    default = {
        ANNOUNCEMENT:           '',
        DOWNLOAD_LIMIT:         10,
        DOWNLOAD_TIMEOUT:       10 * 60, # 10 minutes
        ENABLE_COMMENTS:        False,
        ENABLE_DOWNLOADS:       False,
        ENABLE_REGISTRATION:    False,
        ENABLE_UPLOADS:         False,
        REPORT_THRESHOLD:       50,
    }
