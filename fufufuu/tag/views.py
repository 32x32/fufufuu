from fufufuu.core.utils import paginate
from fufufuu.core.views import TemplateView
from fufufuu.tag.enums import TagType
from fufufuu.tag.models import Tag


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
