$ ->

    if $('#no-ads').length
        return

    #---------------------------------------------------------------------------
    # ad list
    #---------------------------------------------------------------------------

    # leaderboard top (728 x 90)
    ad295296 = '<iframe border=0 frameborder=0 marginheight=0 marginwidth=0 width=736 height=110 scrolling=no allowtransparency=true src=http://adserver.juicyads.com/adshow.php?adzone=295296></iframe>'

    # bottom ads (125 x 125 x 6)
    ad295298 = '<iframe border=0 frameborder=0 marginheight=0 marginwidth=0 width=780 height=152 scrolling=no allowtransparency=true src=http://adserver.juicyads.com/adshow.php?adzone=295298></iframe>'

    # manga ad (300 x 250)
    ad295299 = '<iframe border=0 frameborder=0 marginheight=0 marginwidth=0 width=300 height=270 scrolling=no allowtransparency=true src=http://adserver.juicyads.com/adshow.php?adzone=295299></iframe>'

    #---------------------------------------------------------------------------
    # ad loader
    #---------------------------------------------------------------------------

    if $('.ad295296').is(':visible')
        $('.ad295296').html(ad295296)

    if $('.ad295298').is(':visible')
        $('.ad295298').html(ad295298)

    if $('.ad295299').is(':visible')
        $('.ad295299').html(ad295299)
