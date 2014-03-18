from django.utils.translation import ugettext as _


class ReportMangaType:

    COPYRIGHT   = 'COPYRIGHT'
    CP          = 'CP'
    UNFIT       = 'UNFIT'
    OTHER       = 'OTHER'

    choices = (
        (COPYRIGHT,     _('Copyright Infringement')),
        (CP,            _('Child Pornography')),
        (UNFIT,         _('Unfit Content for Fufufuu')),
        (OTHER,         _('Other')),
    )

    choices_dict = dict(choices)


class ReportStatus:

    OPEN        = 'OPEN'
    CLOSED      = 'CLOSED'

    choices = (
        (OPEN,      _('Open')),
        (CLOSED,    _('Closed')),
    )

    choices_dict = dict(choices)
