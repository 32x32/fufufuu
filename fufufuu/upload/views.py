from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from fufufuu.core.utils import paginate, yesterday
from fufufuu.core.views import ProtectedTemplateView
from fufufuu.manga.enums import MangaStatus
from fufufuu.manga.models import Manga


class UploadListView(ProtectedTemplateView):

    page_size = 100
    template_name = 'upload/upload-list.html'

    def get_upload_slots_used(self):
        non_draft_uploads = Manga.objects.filter(created_by=self.request.user, created_on__gte=yesterday()).exclude(status=MangaStatus.DRAFT).count()
        draft_uploads = Manga.objects.filter(created_by=self.request.user, status=MangaStatus.DRAFT).count()
        return non_draft_uploads + draft_uploads

    def get(self, request):
        manga_list = Manga.objects.filter(created_by=request.user).order_by('-created_on')
        manga_list = paginate(manga_list, self.page_size, request.GET.get('p'))
        upload_slots_used = min(self.get_upload_slots_used(), request.user.upload_limit)
        return self.render_to_response({
            'manga_list': manga_list,
            'upload_slots_used': upload_slots_used,
        })

    def post(self, request):
        if self.get_upload_slots_used() > request.user.upload_limit:
            messages.error(request, _('You have reached your limit of {} uploads within the past 24 hours.').format(request.user.upload_limit))
            return redirect('upload.list')

        manga = Manga()
        manga.save(updated_by=request.user)
        return redirect('manga.edit', id=manga.id, slug=manga.slug)
