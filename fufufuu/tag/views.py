from django.http.response import Http404
from django.utils.translation import get_language
from fufufuu.core.languages import Language
from fufufuu.core.views import TemplateView
from fufufuu.tag.enums import TagType
from fufufuu.tag.models import TagData


class TagListGridView(TemplateView):

    page_size = 120
    tag_type = None
    template_name = 'tag/tag-list-grid.html'

    def get(self, request):
        return self.render_to_response({})


class TagListView(TemplateView):

    tag_type = None
    template_name = 'tag/tag-list.html'

    def get(self, request):
        return self.render_to_response({})

    # def get(self, request, tag_type):
    #     # Notes: this view should paginate for collections and tanks listing
    #     # possibly to 120 per page?
    #
    #     tag_type = TagType.plural_reverse_map.get(tag_type)
    #     if tag_type is None:
    #         raise Http404
    #
    #     self.set_template_name(tag_type)
    #
    #     tag_list = TagData.objects.filter(tag__tag_type=tag_type, language=get_language())
    #
    #     if get_language() != Language.ENGLISH:
    #         tag_list_missing = TagData.objects.filter(tag__tag_type=TagType.TANK, language=Language.ENGLISH).exclude(tag_id__in=tag_list.values_list('tag_id', flat=True))
    #     else:
    #         tag_list_missing = []
    #
    #     return self.render_to_response({
    #         'tag_list': tag_list,
    #         'tag_list_missing': tag_list_missing,
    #         'title': TagType.plural[tag_type],
    #     })
