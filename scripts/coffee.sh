if [ "$1" != "--no-watch" ]; then
    WATCH="--watch"
fi

coffee --join static/js/app.js $WATCH --compile \
    coffee/base.coffee \
    coffee/ad.coffee \
    coffee/manga/manga.coffee \
    coffee/manga/manga-edit.coffee \
    coffee/manga/manga-edit-images.coffee \
    coffee/manga/manga-thumbnails.coffee \
    coffee/tag.coffee
