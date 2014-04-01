from fufufuu.core.views import ModeratorTemplateView


class ModeratorDashboardView(ModeratorTemplateView):

    template_name = 'moderator/moderator-dashboard.html'

    def get(self, request):
        return self.render_to_response({})
