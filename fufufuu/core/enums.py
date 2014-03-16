from django.utils.translation import ugettext as _


class SiteSettingKey:

    ANNOUNCEMENT                = 'ANNOUNCEMENT'
    ENABLE_COMMENTS             = 'ENABLE_COMMENTS'
    ENABLE_REGISTRATION         = 'ENABLE_REGISTRATION'
    ENABLE_UPLOADS              = 'ENABLE_UPLOADS'

    choices = (
        (ANNOUNCEMENT,          _('Announcement')),
        (ENABLE_COMMENTS,       _('Enable Comments')),
        (ENABLE_REGISTRATION,   _('Enable Registration')),
        (ENABLE_UPLOADS,        _('Enable Uploads')),
    )

    choices_dict = dict(choices)

    key_type = {
        ANNOUNCEMENT:           str,
        ENABLE_COMMENTS:        bool,
        ENABLE_REGISTRATION:    bool,
        ENABLE_UPLOADS:         bool,
    }
