from django.utils.translation import ugettext_lazy as _


class ReportStatus:

    OPEN        = 'OPEN'
    CLOSED      = 'CLOSED'

    choices = (
        (OPEN,      _('Open')),
        (CLOSED,    _('Closed')),
    )

    choices_dict = dict(choices)


class ReportMangaType:

    COPYRIGHT   = 'COPYRIGHT'
    CP          = 'CP'
    REPOST      = 'REPOST'
    UNFIT       = 'UNFIT'
    OTHER       = 'OTHER'

    choices = (
        (COPYRIGHT,     _('Copyright Infringement')),
        (CP,            _('Child Pornography')),
        (REPOST,        _('Repost')),
        (UNFIT,         _('Unfit Content for Fufufuu')),
        (OTHER,         _('Other')),
    )

    choices_dict = dict(choices)
