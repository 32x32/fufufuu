from django.utils.translation import ugettext as _


class TagType:

    AUTHOR      = 'AUTHOR'
    CIRCLE      = 'CIRCLE'
    COLLECTION  = 'COLLECTION'
    CONTENT     = 'CONTENT'
    EVENT       = 'EVENT'
    MAGAZINE    = 'MAGAZINE'
    PARODY      = 'PARODY'
    SCANLATOR   = 'SCANLATOR'
    TANK        = 'TANK'

    manga_m2m = [AUTHOR, CIRCLE, CONTENT, EVENT, MAGAZINE, PARODY, SCANLATOR]
    manga_fk = [COLLECTION, TANK]

    choices = (
        (AUTHOR,        _('Author')),
        (CIRCLE,        _('Circle')),
        (COLLECTION,    _('Collection')),
        (CONTENT,       _('Content')),
        (EVENT,         _('Event')),
        (MAGAZINE,      _('Magazine')),
        (PARODY,        _('Parody')),
        (SCANLATOR,     _('Scanlator')),
        (TANK,          _('Tank')),
    )

    choices_dict = dict(choices)

    plural = {
        AUTHOR:         _('Authors'),
        CIRCLE:         _('Circles'),
        COLLECTION:     _('Collections'),
        CONTENT:        _('Content'),
        EVENT:          _('Events'),
        MAGAZINE:       _('Magazines'),
        PARODY:         _('Parodies'),
        SCANLATOR:      _('Scanlators'),
        TANK:           _('Tanks'),
    }

    plural_reverse_map = {
        'authors':      AUTHOR,
        'circles':      CIRCLE,
        'collections':  COLLECTION,
        'content':      CONTENT,
        'events':       EVENT,
        'magazines':    MAGAZINE,
        'parodies':     PARODY,
        'scanlators':   SCANLATOR,
        'tanks':        TANK,
    }
