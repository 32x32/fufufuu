from django.utils.translation import ugettext as _


class RevisionStatus:

    PENDING             = 'PENDING'
    APPROVED            = 'APPROVED'
    REJECTED            = 'REJECTED'

    choices = (
        (PENDING,       _('Pending')),
        (APPROVED,      _('Approved')),
        (REJECTED,      _('Rejected')),
    )

    choices_dict = dict(choices)


class RevisionAction:

    APPLY               = 'APPLY'
    REVERT              = 'REVERT'

    choices = (
        (APPLY,         _('Apply')),
        (REVERT,        _('Revert')),
    )

    choices_dict = dict(choices)
