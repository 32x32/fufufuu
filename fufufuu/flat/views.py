from fufufuu.core.views import TemplateView


class FlatMarkdownView(TemplateView):

    template_name = 'flat/flat-markdown.html'

    def get(self, request):
        return self.render_to_response({})
