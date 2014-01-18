from collections import defaultdict
from django.http.response import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import get_language
from fufufuu.core.response import HttpResponseJson
from fufufuu.core.utils import paginate
from fufufuu.core.views import TemplateView, ProtectedTemplateView
from fufufuu.tag.enums import TagType
from fufufuu.tag.models import Tag, TagAlias


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


class TagListGridView(TemplateView):

    page_size = 120
    tag_type = None
    template_name = 'tag/tag-list-grid.html'

    def get(self, request):
        tag_list = Tag.objects.filter(tag_type=self.tag_type).order_by('slug')
        tag_list = paginate(tag_list, self.page_size, request.GET.get('p'))
        return self.render_to_response({
            'tag_list': tag_list,
            'title': TagType.plural[self.tag_type],
        })


class TagListView(TemplateView):

    tag_type = None
    template_name = 'tag/tag-list.html'

    def get(self, request):
        tag_list = Tag.objects.filter(tag_type=self.tag_type).order_by('slug')
        return self.render_to_response({
            'tag_list': tag_list,
            'title': TagType.plural[self.tag_type],
        })


class TagView(TemplateView):

    template_name = 'tag/tag.html'

    def get(self, request, id, slug):
        tag = get_object_or_404(Tag, id=id)
        return self.render_to_response({
            'tag': tag,
        })
