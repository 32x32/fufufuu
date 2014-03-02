class ImageKeyType:

    ACCOUNT_AVATAR              = 'ACCOUNT_AVATAR'
    MANGA_THUMB                 = 'MANGA_THUMB'
    MANGA_COVER                 = 'MANGA_COVER'
    MANGA_INFO_COVER            = 'MANGA_INFO_COVER'
    MANGA_PAGE                  = 'MANGA_PAGE'
    MANGA_PAGE_DOUBLE           = 'MANGA_PAGE_DOUBLE'

    choices = (
        (ACCOUNT_AVATAR,        ACCOUNT_AVATAR),
        (MANGA_THUMB,           MANGA_THUMB),
        (MANGA_COVER,           MANGA_COVER),
        (MANGA_INFO_COVER,      MANGA_INFO_COVER),
        (MANGA_PAGE,            MANGA_PAGE),
        (MANGA_PAGE_DOUBLE,     MANGA_PAGE_DOUBLE),
    )

    choices_dict = dict(choices)
