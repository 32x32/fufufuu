from collections import defaultdict
from django.http.response import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import get_language
from fufufuu.core.languages import Language
from fufufuu.core.response import HttpResponseJson
from fufufuu.core.utils import paginate, get_object_or_none
from fufufuu.core.views import TemplateView, ProtectedTemplateView
from fufufuu.manga.models import Manga
from fufufuu.manga.views import MangaListView
from fufufuu.tag.enums import TagType
from fufufuu.tag.models import Tag, TagAlias, TagData


class TagAutocompleteView(ProtectedTemplateView):

    def get(self, request):
        if not request.is_ajax():
            raise Http404

        tag_dict = defaultdict(list)
        for tag in Tag.objects.only('tag_type', 'name'):
            tag_dict[tag.tag_type].append(tag.name)
        for tag_alias in TagAlias.objects.select_related('tag').filter(language=get_language()):
            tag_dict[tag_alias.tag.tag_type].append(tag_alias.name)

        return HttpResponseJson(tag_dict)


class TagAliasDictContext:

    def get_tag_alias_dict(self, request, lang=None):
        filters = {'tag__tag_type': self.tag_type}
        if lang: filters['language'] = lang

        tag_alias_list = TagAlias.objects.filter(**filters).values('tag_id', 'name')
        tag_alias_dict = defaultdict(list)
        for tag_alias in tag_alias_list:
            tag_alias_dict[tag_alias['tag_id']].append(tag_alias['name'])

        return tag_alias_dict


class TagListGridView(TagAliasDictContext, TemplateView):

    page_size = 120
    tag_type = None
    template_name = 'tag/tag-list-grid.html'

    def get(self, request):
        lang = request.GET.get('lang')
        tag_alias_dict = self.get_tag_alias_dict(request, lang)
        tag_list = Tag.objects.filter(tag_type=self.tag_type).order_by('slug')
        tag_list = paginate(tag_list, self.page_size, request.GET.get('p'))
        for tag in tag_list:
            tag.alias_list = tag_alias_dict.get(tag.id)

        return self.render_to_response({
            'lang': lang,
            'tag_list': tag_list,
            'tag_type': self.tag_type,
            'title': TagType.plural[self.tag_type],
        })


class TagListView(TagAliasDictContext, TemplateView):

    tag_type = None
    template_name = 'tag/tag-list.html'

    def get(self, request):
        lang = request.GET.get('lang')
        tag_alias_dict = self.get_tag_alias_dict(request, lang)
        tag_list = Tag.objects.filter(tag_type=self.tag_type).order_by('slug').values('id', 'slug', 'name')
        for tag in tag_list:
            tag['alias_list'] = tag_alias_dict.get(tag['id'])

        return self.render_to_response({
            'lang': lang,
            'tag_list': tag_list,
            'tag_type': self.tag_type,
            'title': TagType.plural[self.tag_type],
        })


class TagView(MangaListView):

    template_name = 'tag/tag.html'

    def get(self, request, id, slug):
        tag = get_object_or_404(Tag, id=id)
        filters = self.get_filters()

        if tag.tag_type == TagType.TANK:
            filters['tank'] = tag
            order_by = 'tank_chapter'
        elif tag.tag_type == TagType.COLLECTION:
            filters['collection'] = tag
            order_by = 'collection_part'
        else:
            filters['tags'] = tag
            order_by = '-published_on'

        manga_list = Manga.published.filter(**filters).order_by(order_by)
        manga_list = paginate(manga_list, self.page_size, request.GET.get('p'))

        lang = request.GET.get('lang' ) or Language.ENGLISH

        tag_alias_list = TagAlias.objects.filter(tag=tag).order_by('language', 'name')
        tag_data = get_object_or_none(TagData, tag=tag, language=lang)
        return self.render_to_response({
            'lang': lang,
            'manga_list': manga_list,
            'tag': tag,
            'tag_alias_list': tag_alias_list,
            'tag_data': tag_data,
        })
