from django.utils.translation import ugettext_lazy as _


class ReportStatus:

    OPEN        = 'OPEN'
    CLOSED      = 'CLOSED'

    choices = (
        (OPEN,      _('Open')),
        (CLOSED,    _('Closed')),
    )

    choices_dict = dict(choices)


class ReportQuality:

    UNKNOWN     = 'UNKNOWN'

    GOOD        = 'GOOD'
    NEUTRAL     = 'NETRUAL'
    BAD         = 'BAD'
    SPAM        = 'SPAM'

    choices = (
        (GOOD,      _('Good')),
        (NEUTRAL,   _('Neutral')),
        (BAD,       _('Bad')),
        (SPAM,      _('Spam')),
    )

    choices_dict = dict(choices)


class ReportMangaType:

    COPYRIGHT   = 'COPYRIGHT'
    CP          = 'CP'
    REPOST      = 'REPOST'
    UNFIT       = 'UNFIT'
    OTHER       = 'OTHER'

    choices = (
        (REPOST,        _('Repost')),
        (COPYRIGHT,     _('Copyright Infringement')),
        (CP,            _('Child Pornography')),
        (UNFIT,         _('Inappropriate Content for Fufufuu')),
        (OTHER,         _('Other')),
    )

    choices_dict = dict(choices)
