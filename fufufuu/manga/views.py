from fufufuu.core.views import TemplateView


class MangaListView(TemplateView):

    template_name = 'manga/manga-list.html'

    def get(self, request):
        return self.render_to_response({})
