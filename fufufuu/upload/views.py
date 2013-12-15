from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from fufufuu.core.utils import paginate, yesterday
from fufufuu.core.views import ProtectedTemplateView
from fufufuu.manga.models import Manga


class UploadListView(ProtectedTemplateView):

    page_size = 100
    template_name = 'upload/upload-list.html'

    def get(self, request):
        manga_list = Manga.objects.filter(created_by=request.user).order_by('-created_on')
        manga_list = paginate(manga_list, self.page_size, request.GET.get('p'))
        return self.render_to_response({
            'manga_list': manga_list,
        })

    def post(self, request):
        if Manga.objects.filter(created_on__gte=yesterday()).count() > request.user.upload_limit:
            messages.error(request, _('You have reached your limit of {} uploads within the past 24 hours.').format(request.user.upload_limit))
            return redirect('upload.list')

        manga = Manga()
        manga.save(updated_by=request.user)
        return redirect('manga.edit', id=manga.id, slug=manga.slug)
