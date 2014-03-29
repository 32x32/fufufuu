$ ->

    #---------------------------------------------------------------------------
    # tl quick filter
    #---------------------------------------------------------------------------

    if $('#template-tag-list').length
        tagList = []
        i = 1
        $('.tli').each ->
            searchableText = []
            self = $(this)
            self.find('.tl-searchable').each -> searchableText.push($(this).text())
            obj = { id: i, el: self, text: searchableText }
            tagList.push(obj)
            i++

        foundText = (q, tag) ->
            q = q.toLowerCase()
            for text in tag.text
                if text.toLowerCase().indexOf(q) > -1
                    return true
            return false


        $tlQuickFilter = $('#tl-quick-filter')
        $tlQuickFilter.on 'keyup', ->
            query = $tlQuickFilter.val()
            showTagList = []
            hideTagList = []

            for tag in tagList
                if foundText(query, tag)
                    showTagList.push(tag)
                else
                    hideTagList.push(tag)

            hideTagList.map (tag) -> tag.el.hide()
            showTagList.map (tag) -> tag.el.show()
