from fufufuu.image.enums import ImageKeyType

specs = dict()

#-------------------------------------------------------------------------------
# MANGA_THUMB
#-------------------------------------------------------------------------------

specs[ImageKeyType.MANGA_THUMB] = {
    'width':    140,
    'height':   210,
}

#-------------------------------------------------------------------------------
# MANGA_THUMB_RETINA
#-------------------------------------------------------------------------------

specs[ImageKeyType.MANGA_THUMB_RETINA] = {
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
# MANGA_PAGE
#-------------------------------------------------------------------------------

specs[ImageKeyType.MANGA_PAGE] = {
    'width':    800,
    'height':   1200,
}

#-------------------------------------------------------------------------------
# MANGA_PAGE_WIDE
#-------------------------------------------------------------------------------

specs[ImageKeyType.MANGA_PAGE] = {
    'width':    1200,
    'height':   900,
}