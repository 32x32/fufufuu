from fufufuu.core.views import TemplateView


class SearchView(TemplateView):

    template_name = 'search/search.html'

    def get(self, request):
        return self.render_to_response({})
