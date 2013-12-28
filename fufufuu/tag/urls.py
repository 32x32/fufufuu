from django.conf.urls import patterns, url
from fufufuu.tag.enums import TagType
from fufufuu.tag.views import TagListView, TagListGridView, TagAutocompleteView


urlpatterns = patterns('',

    url(r'^autocomplete.json',      TagAutocompleteView.as_view(), name='tag.autocomplete'),

    url(r'^collections/$',          TagListGridView.as_view(tag_type=TagType.COLLECTION), name='tag.list.collection'),
    url(r'^tanks/$',                TagListGridView.as_view(tag_type=TagType.TANK), name='tag.list.tank'),

    url(r'^authors/$',              TagListView.as_view(tag_type=TagType.AUTHOR), name='tag.list.author'),
    url(r'^circles/$',              TagListView.as_view(tag_type=TagType.CIRCLE), name='tag.list.circle'),
    url(r'^content/$',              TagListView.as_view(tag_type=TagType.CONTENT), name='tag.list.content'),
    url(r'^events/$',               TagListView.as_view(tag_type=TagType.EVENT), name='tag.list.event'),
    url(r'^magazines/$',            TagListView.as_view(tag_type=TagType.MAGAZINE), name='tag.list.magazine'),
    url(r'^parodies/$',             TagListView.as_view(tag_type=TagType.PARODY), name='tag.list.parody'),
    url(r'^scanlators/$',           TagListView.as_view(tag_type=TagType.SCANLATOR), name='tag.list.scanlator'),

)
