$ ->

    #---------------------------------------------------------------------------
    # manga edit images page
    #---------------------------------------------------------------------------

    if $('#template-manga-edit-images').length
        $('input[type="file"]').change -> $(this).parents('form').submit()

        # upload-images sorting
        $imageList = $('.upload-pl')
        if $imageList.length
            $imageList.sortable()
            $imageOrderInput = $imageList.find('input[id$="ORDER"]')
            $imageOrderInput.attr('readonly', 'readonly')
            $imageOrderInput.attr('type', 'text')
            $imageList.bind 'sortstop', (event, ui) ->
                for item, i in $('.upload-pli')
                    $(item).find('input[id$="ORDER"]').attr('value', i+1)

        # enabling/disabling of form buttons based on selected images
        $setCoverButton = $('#id_button_set_cover')
        $deleteButton = $('#id_button_delete')

        update_buttons = ->
            selected_count = $('.mp-select:checked').length
            console.log selected_count
            if selected_count == 1
                $setCoverButton.removeAttr('disabled')
            else
                $setCoverButton.attr('disabled', 'disabled')
            if selected_count > 0
                $deleteButton.removeAttr('disabled')
            else
                $deleteButton.attr('disabled', 'disabled')

        $('.mp-select').on('change', update_buttons)
        update_buttons()

    #---------------------------------------------------------------------------
    # manga edit page
    #---------------------------------------------------------------------------

    if $('#template-manga-edit').length

        # tags autocomplete
        split = (val) -> val.split(/,\s*/)
        extractLast = (term) -> split(term).pop()

        bindAutocompleteKeydown = (e) ->
            if e.keyCode == $.ui.keyCode.TAB && $(this).data('ui-autocomplete').menu.active
                e.preventDefault()

        autocompleteParams = (source) ->
            return {
                source: (request, response) ->
                    results = $.ui.autocomplete.filter(source, extractLast(request.term))
                    response(results.slice(0, 10))
                delay: 0
                focus: -> return false
                select: (e, ui) ->
                    terms = split(this.value)
                    terms.pop()
                    terms.push(ui.item.value)
                    terms.push('')
                    this.value = terms.join(', ')
                    return false
            }

        success = (data) ->
            $('#id_authors').bind('keydown', bindAutocompleteKeydown).autocomplete(autocompleteParams(data.AUTHOR))
            $('#id_circles').bind('keydown', bindAutocompleteKeydown).autocomplete(autocompleteParams(data.CIRCLE))
            $('#id_content').bind('keydown', bindAutocompleteKeydown).autocomplete(autocompleteParams(data.CONTENT))
            $('#id_events').bind('keydown', bindAutocompleteKeydown).autocomplete(autocompleteParams(data.EVENT))
            $('#id_magazines').bind('keydown', bindAutocompleteKeydown).autocomplete(autocompleteParams(data.MAGAZINE))
            $('#id_parodies').bind('keydown', bindAutocompleteKeydown).autocomplete(autocompleteParams(data.PARODY))
            $('#id_scanlators').bind('keydown', bindAutocompleteKeydown).autocomplete(autocompleteParams(data.SCANLATOR))
            $('#id_collection').bind('keydown', bindAutocompleteKeydown).autocomplete({source: data.COLLECTION, delay: 0})
            $('#id_tank').bind('keydown', bindAutocompleteKeydown).autocomplete({source: data.TANK, delay: 0})

        $.get '/tag/autocomplete.json', success
