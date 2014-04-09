from django.utils.translation import ugettext as _


class MangaCategory:

    NON_H               = 'NON_H'
    ECCHI               = 'ECCHI'
    VANILLA             = 'VANILLA'
    ALTERNATIVE         = 'ALTERNATIVE'
    YAOI                = 'YAOI'
    YURI                = 'YURI'
    OTHER               = 'OTHER'

    choices = (
        (NON_H,         _('Non-H')),
        (ECCHI,         _('Ecchi')),
        (VANILLA,       _('Vanilla')),
        (ALTERNATIVE,   _('Alternative')),
        (YAOI,          _('Yaoi')),
        (YURI,          _('Yuri')),
        (OTHER,         _('Other')),
    )

    choices_dict = dict(choices)


class MangaStatus:

    DRAFT               = 'DRAFT'
    PUBLISHED           = 'PUBLISHED'
    PENDING             = 'PENDING'
    REMOVED             = 'REMOVED'
    DELETED             = 'DELETED'

    choices = (
        (DRAFT,         _('Draft')),
        (PUBLISHED,     _('Published')),
        (PENDING,       _('Pending')),
        (REMOVED,       _('Removed')),
        (DELETED,       _('Deleted')),
    )

    choices_dict = dict(choices)


class MangaAction:

    SAVE                = 'save'
    PUBLISH             = 'publish'
    REMOVE              = 'remove'
    DELETE              = 'delete'

    choices = (
        (SAVE, SAVE),
        (PUBLISH, PUBLISH),
        (REMOVE, REMOVE),
        (DELETE, DELETE),
    )


MANGA_FIELDNAME_MAP = {
    'title':            _('Title'),
    'markdown':         _('Description'),
    'html':             _('Description'),
    'cover':            _('Cover'),
    'status':           _('Status'),
    'category':         _('Category'),
    'language':         _('Language'),
    'uncensored':       _('Uncensored'),
    'tags':             _('Tags'),
    'tank':             _('Tank'),
    'collection':       _('Collection'),
    'tank_chapter':     _('Chapter'),
    'collection_part':  _('Part'),
}

