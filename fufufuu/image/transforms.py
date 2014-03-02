"""
Specification:

    crop:       (boolean)   crop to fit image to size
    height:     (int)       max height of image
    quality:    (int)       0-100 jpeg quality (default is 75)
    width:      (int)       max width of image

"""

from fufufuu.image.enums import ImageKeyType

specs = dict()

#-------------------------------------------------------------------------------
# ACCOUNT_AVATAR
#-------------------------------------------------------------------------------

specs[ImageKeyType.ACCOUNT_AVATAR] = {
    'width':    200,
    'height':   200,
    'crop':     True,
}

#-------------------------------------------------------------------------------
# MANGA_THUMB
#-------------------------------------------------------------------------------

specs[ImageKeyType.MANGA_THUMB] = {
    'width':    280,
    'height':   420,
}

#-------------------------------------------------------------------------------
# MANGA_COVER
#-------------------------------------------------------------------------------

specs[ImageKeyType.MANGA_COVER] = {
    'width':    400,
    'height':   600,
    'crop':     True,
}

#-------------------------------------------------------------------------------
# MANGA_INFO_COVER
#-------------------------------------------------------------------------------

specs[ImageKeyType.MANGA_INFO_COVER] = {
    'width':    800,
    'height':   1200,
    'crop':     True,
}

#-------------------------------------------------------------------------------
# MANGA_PAGE
#-------------------------------------------------------------------------------

specs[ImageKeyType.MANGA_PAGE] = {
    'width':    800,
    'height':   1200,
}

#-------------------------------------------------------------------------------
# MANGA_PAGE_WIDE
#-------------------------------------------------------------------------------

specs[ImageKeyType.MANGA_PAGE_DOUBLE] = {
    'width':    1200,
    'height':   900,
}
