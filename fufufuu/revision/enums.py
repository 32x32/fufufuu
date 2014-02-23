from django.utils.translation import ugettext as _


class RevisionStatus:

    PENDING             = 'PENDING'
    APPROVED            = 'APPROVED'
    REJECTED            = 'REJECTED'

    choices = (
        (PENDING, _('Pending')),
        (APPROVED, _('Approved')),
        (REJECTED, _('Rejected')),
    )

    choices_dict = dict(choices)


class RevisionAction:

    APPLY               = 'APPLY'
    RE_APPLY            = 'RE_APPLY'
    REVERT              = 'REVERT'
    RE_REVERT           = 'RE_REVERT'

    choices = (
        (APPLY, _('Apply')),
        (RE_APPLY, _('Re-apply')),
        (REVERT, _('Revert')),
        (RE_REVERT, _('Re-revert')),
    )

    choices_dict = dict(choices)
