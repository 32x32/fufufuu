class ImageKeyType:

    ACCOUNT_AVATAR              = 'ACCOUNT_AVATAR'
    MANGA_THUMB                 = 'MANGA_THUMB'
    MANGA_COVER                 = 'MANGA_COVER'
    MANGA_PAGE                  = 'MANGA_PAGE'
    MANGA_PAGE_DOUBLE           = 'MANGA_PAGE_DOUBLE'
    TAG_COVER                   = 'TAG_COVER'

    choices = (
        (ACCOUNT_AVATAR,        ACCOUNT_AVATAR),
        (MANGA_THUMB,           MANGA_THUMB),
        (MANGA_COVER,           MANGA_COVER),
        (MANGA_PAGE,            MANGA_PAGE),
        (MANGA_PAGE_DOUBLE,     MANGA_PAGE_DOUBLE),
        (TAG_COVER,             TAG_COVER),
    )

    choices_dict = dict(choices)
