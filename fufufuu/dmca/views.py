from django.http.response import Http404
from fufufuu.core.utils import paginate
from fufufuu.core.views import ProtectedTemplateView
from fufufuu.dmca.models import DmcaRequest


class DmcaListView(ProtectedTemplateView):

    page_size = 100
    template_name = 'dmca/dmca-list.html'

    def get(self, request):
        dmca_account = request.user.dmca_account
        if not dmca_account: raise Http404

        dmca_list = DmcaRequest.objects.filter(dmca_account=dmca_account).select_related('manga', 'manga__created_by').order_by('-created_on')
        dmca_list = paginate(dmca_list, self.page_size, request.GET.get('p'))
        return self.render_to_response({
            'dmca_list': dmca_list,
        })
