from django.utils.translation import get_language
from fufufuu.core.languages import Language
from fufufuu.core.utils import paginate
from fufufuu.core.views import TemplateView
from fufufuu.tag.enums import TagType
from fufufuu.tag.models import TagData


class TagListGridView(TemplateView):

    page_size = 120
    tag_type = None
    template_name = 'tag/tag-list-grid.html'

    def get(self, request):
        tag_list = TagData.objects.filter(tag__tag_type=self.tag_type, language=get_language())
        tag_list = paginate(tag_list, self.page_size, request.GET.get('p'))
        return self.render_to_response({
            'tag_list': tag_list,
            'title': TagType.plural[self.tag_type],
        })


class TagListView(TemplateView):

    tag_type = None
    template_name = 'tag/tag-list.html'

    def get(self, request):
        tag_list = TagData.objects.filter(tag__tag_type=self.tag_type, language=get_language())

        if get_language() != Language.ENGLISH:
            tag_list_missing = TagData.objects.filter(tag__tag_type=self.tag_type, language=Language.ENGLISH).exclude(tag_id__in=tag_list.values_list('tag_id', flat=True))
        else:
            tag_list_missing = []

        return self.render_to_response({
            'tag_list': tag_list,
            'tag_list_missing': tag_list_missing,
            'title': TagType.plural[self.tag_type],
        })
