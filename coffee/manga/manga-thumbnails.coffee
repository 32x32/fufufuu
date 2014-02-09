$ ->

    #---------------------------------------------------------------------------
    # set height of thumbnail images for small screens
    #---------------------------------------------------------------------------

    $('.mtli-image-wrapper').each ->
        self = $(this)
        self.height(self.width() * 1.5)
