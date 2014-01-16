$ ->

    #---------------------------------------------------------------------------
    # manga page
    #---------------------------------------------------------------------------

    if $('#template-manga').length

        #-----------------------------------------------------------------------
        # setup
        #-----------------------------------------------------------------------

        payload = $('#payload').text()
        payload = atob(payload)
        data = JSON.parse(payload)

        pageList = data.page_list
        console.log pageList

        #-----------------------------------------------------------------------
        # get page number
        #-----------------------------------------------------------------------

        pageNumRegex = new RegExp("#/page/(\\d+)/")

        getPageNum = ->
            pageNum = pageNumRegex.exec(window.location.hash)
            if not pageNum
                return 1
            pageNum = parseInt(pageNum[1])
            if pageNum < 1
                return 1
            if pageNum > data.length
                return data.length
            return pageNum

        nextChapter = $('#manga-chapter-jump option:selected').next().val()
        prevChapter = $('#manga-chapter-jump option:selected').prev().val()

        #-----------------------------------------------------------------------
        # knockout
        #-----------------------------------------------------------------------

        MangaModelView = ->
            self = this

            # helper functions
            self.prevNum = -> if self.pageNum() <= 1 then 1 else self.pageNum() - 1
            self.nextNum = -> if self.pageNum() >= pageList.length then pageList.length else self.pageNum() + 1

            # properties
            self.pageNum = ko.observable(getPageNum())
            self.page = ko.computed -> pageList[self.pageNum()-1]

            self.prevUrl = ko.computed ->
                if prevChapter and self.prevNum() == self.pageNum()
                    return "#{prevChapter}#/page/100/"
                return "#/page/#{self.pageNum()}/"

            self.nextUrl = ko.computed ->
                if nextChapter and self.nextNum() == self.pageNum()
                    return "#{nextChapter}#/page/1/"
                return "#/page/#{self.nextNum()}/"

            self.jumpPage = ->
                targetPage = $("#manga-page-jump").val()
                window.location.hash = "#/page/#{targetPage}/"

            self.preload = ->
                preloadPage = (page) ->
                    if not page.loaded
                        (new Image()).src = page.url
                        page.loaded = true
                preloadPage(data[self.prevNum()-1])
                preloadPage(data[self.prevNum()+1])

            self.showDouble = ->
                return self.page().double

            return

        mangaModelView = new MangaModelView()
        ko.applyBindings(mangaModelView)

        #-----------------------------------------------------------------------
        # hash change bindings
        #-----------------------------------------------------------------------

        changePage = ->
            pageNum = getPageNum()
            mangaModelView.pageNum(pageNum)
            mangaModelView.preload()
            if pageNum == 1
                scrollTop = 0
            else
                scrollTop = $('.m-body').offset().top()
            $('html, body').animate({ scrollTop: scrollTop }, 100)
            return

        $(window).bind 'hashchange', changePage

        #-----------------------------------------------------------------------
        # keyboard bindings
        #-----------------------------------------------------------------------

        $(document).keydown (e) ->
            if $('textarea').is(':focus')
                return
            if e.which == 37 # left arrow key
                window.location = mangaModelView.prevUrl()
            if e.which == 39 # right arrow key
                window.location = mangaModelView.nextUrl()
            return

        return
