from fufufuu.core.views import TemplateView


class FlatHelpView(TemplateView):

    template_name = 'flat/flat-help.html'

    def get(self, request):
        return self.render_to_response({})


class FlatMarkdownView(TemplateView):

    template_name = 'flat/flat-markdown.html'

    def get(self, request):
        return self.render_to_response({})
