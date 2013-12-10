from fufufuu.core.views import ProtectedTemplateView


class UploadListView(ProtectedTemplateView):

    template_name = 'upload/upload-list.html'

    def get(self, request):
        return self.render_to_response({})
