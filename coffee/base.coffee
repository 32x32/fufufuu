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
            messageList = self.parent().parent()
            if not messageList.length
                messageList.remove()

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

        $(document).on 'load scroll resize', checkAndLoadImages
        checkAndLoadImages()

    #---------------------------------------------------------------------------
    # toggle switches
    #---------------------------------------------------------------------------

    $('.toggle-switch').each ->
        self = $(this)
        $id = $('#' + self.attr('data-toggle-id'))
        $class = $('.' + self.attr('data-toggle-class'))

        self.click ->
            text1 = self.attr('data-toggle-text')
            text2 = self.text()
            self.text(text1)
            self.attr('data-toggle-text', text2)
            $id.toggle()
            $class.toggle()

    #---------------------------------------------------------------------------
    # auto submit
    #---------------------------------------------------------------------------

    $('.auto-submit').each ->
        form = $(this)
        form.find('input, select, textarea').change -> form.submit()

    #---------------------------------------------------------------------------
    # back to top
    #---------------------------------------------------------------------------

    $('.back-to-top').click ->
        $('html, body').animate { 'scrollTop': 0 }, 'slow'
        return false

    #---------------------------------------------------------------------------
    # markdown preview
    #---------------------------------------------------------------------------

    if $('.markdown-preview').length
        $('.markdown-preview').each ->
            preview = $(this)
            input = $('#' + preview.attr('data-for'))
            input.on 'keyup', -> preview.html(markdown.toHTML(input.val()))
            preview.html(markdown.toHTML(input.val()))



