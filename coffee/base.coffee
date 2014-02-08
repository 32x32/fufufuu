$ ->

    #---------------------------------------------------------------------------
    # nav menu toggle
    #---------------------------------------------------------------------------

    $navbar = $('nav')
    $('#header-menu-icon').click -> $navbar.toggleClass('active')

    #---------------------------------------------------------------------------
    # messages
    #---------------------------------------------------------------------------

    $('.message .icon-cancel').click ->
        self = $(this).parent()
        self.slideUp 200, ->
            self.remove()
            if not $('#message-list li').length
                $('#message-list').remove()

    #---------------------------------------------------------------------------
    # lazy image loading
    #---------------------------------------------------------------------------

    if $('.lazy-image').length

        VERTICAL_BUFFER = 500

        isElementInViewport = (el) ->
            rect = el.getBoundingClientRect()
            return rect.top >= 0-VERTICAL_BUFFER and
                rect.right <= $(window).width() and
                rect.bottom <= $(window).height()+VERTICAL_BUFFER and
                rect.left >= 0

        checkAndLoadImages = ->
            $('.lazy-image').each ->
                if isElementInViewport(this)
                    if window.devicePixelRatio > 1 and $(this).attr('data-src-retina')
                        src = $(this).attr('data-src-retina')
                    else
                        src = $(this).attr('data-src')
                    $(this).attr('src', src)
                    $(this).removeClass('lazy-image')

        $('.content').on 'load scroll resize', checkAndLoadImages
        checkAndLoadImages()
