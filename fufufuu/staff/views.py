from fufufuu.core.views import StaffTemplateView


class StaffView(StaffTemplateView):

    template_name = 'staff/staff.html'

    def get(self, request):
        return self.render_to_response({})
