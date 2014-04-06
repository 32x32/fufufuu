from fufufuu.core.views import TemplateView
from fufufuu.staff.views import StaffTemplateView


class BlogEntryListView(TemplateView):

    template_name = 'blog/blog-entry-list.html'

    def get(self, request):
        return self.render_to_response({})


class BlogEntryView(TemplateView):

    template_name = 'blog/blog-entry.html'

    def get(self, request, id, slug):
        return self.render_to_response({})


#-------------------------------------------------------------------------------


class BlogEntryCreateView(StaffTemplateView):

    template_name = 'blog/blog-entry-create.html'

    def get(self, request):
        return self.render_to_response({})

    def post(self, request):
        return self.render_to_response({})


class BlogEntryEditView(StaffTemplateView):

    template_name = 'blog/blog-entry-edit.html'

    def get(self, request, id, slug):
        return self.render_to_response({})

    def post(self, rqeuest):
        return self.render_to_response({})
