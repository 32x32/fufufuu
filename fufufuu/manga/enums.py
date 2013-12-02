from django.utils.translation import ugettext as _


class MangaCategory:

    NON_H       = 'NON-H'
    ECCHI       = 'ECCHI'
    VANILLA     = 'VANILLA'
    ALTERNATIVE = 'ALTERNATIVE'
    YAOI        = 'YAOI'
    YURI        = 'YURI'
    OTHER       = 'OTHER'

    choices = (
        (NON_H,         _('Non-H')),
        (ECCHI,         _('Ecchi')),
        (VANILLA,       _('Vanilla')),
        (ALTERNATIVE,   _('Alternative')),
        (YAOI,          _('Yaoi')),
        (YURI,          _('Yuri')),
        (OTHER,         _('Other')),
    )

    choices_dict = dict([(k,v) for (k,v) in choices])


class MangaStatus:

    DRAFT       = 'DRAFT'
    PUBLISHED   = 'PUBLISHED'
    HOLD        = 'HOLD'
    REMOVED     = 'REMOVED'
    DELETED     = 'DELETED'

    choices = (
        (DRAFT,     _('Draft')),
        (PUBLISHED, _('Published')),
        (HOLD,      _('On Hold')),
        (REMOVED,   _('Removed')),
        (DELETED,   _('Deleted')),
    )

    choices_dict = dict([(k,v) for (k,v) in choices])
