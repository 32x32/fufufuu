from django.utils.translation import ugettext as _


class SiteSettingKey:

    ANNOUNCEMENT            = 'ANNOUNCEMENT'
    ENABLE_COMMENTS         = 'ENABLE_COMMENTS'
    ENABLE_UPLOADS          = 'ENABLE_UPLOADS'

    choices = (
        (ANNOUNCEMENT,      _('Announcement')),
        (ENABLE_COMMENTS,   _('Enable Comments')),
        (ENABLE_UPLOADS,    _('Enable Uploads')),
    )

    choices_dict = dict(choices)

    key_type = {
        ANNOUNCEMENT:       str,
        ENABLE_COMMENTS:    bool,
        ENABLE_UPLOADS:     bool,
    }
