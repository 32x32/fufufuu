$ ->

    #---------------------------------------------------------------------------
    # manga edit images page
    #---------------------------------------------------------------------------

    if $('#template-manga-edit-images').length
        $('input[type="file"]').change -> $(this).parents('form').submit()

        # upload-images sorting
        $imageList = $('.mtl')
        if $imageList.length
            $imageList.sortable()
            $imageOrderInput = $imageList.find('input[id$="ORDER"]')
            $imageOrderInput.attr('readonly', 'readonly')
            $imageOrderInput.attr('type', 'text')
            $imageList.bind 'sortstop', (event, ui) ->
                for item, i in $('.mtli')
                    $(item).find('input[id$="ORDER"]').attr('value', i+1)

        # enabling/disabling of form buttons based on selected images
        $setCoverButton = $('#id_button_set_cover')
        $deleteButton = $('#id_button_delete')

        update_buttons = ->
            selected_count = $('.mp-select:checked').length
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
