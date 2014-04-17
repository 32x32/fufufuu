from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from fufufuu.comment.utils import attach_comment_count
from fufufuu.core.enums import SiteSettingKey
from fufufuu.core.models import SiteSetting
from fufufuu.core.utils import paginate, yesterday
from fufufuu.core.views import ProtectedTemplateView
from fufufuu.manga.enums import MangaStatus
from fufufuu.manga.models import Manga
from fufufuu.manga.utils import attach_manga_favorite_count, attach_manga_download_count


class UploadListView(ProtectedTemplateView):

    page_size = 100
    template_name = 'upload/upload-list.html'

    def get_upload_slots_used(self):
        non_draft_uploads = Manga.objects.filter(created_by=self.request.user, created_on__gte=yesterday()).exclude(status=MangaStatus.DRAFT).count()
        draft_uploads = Manga.objects.filter(created_by=self.request.user, status=MangaStatus.DRAFT).count()
        return non_draft_uploads + draft_uploads

    def get(self, request):
        if not SiteSetting.as_dict().get(SiteSettingKey.ENABLE_UPLOADS):
            messages.warning(request, _('Uploading at Fufufuu has been disabled.'))

        manga_list = Manga.objects.filter(created_by=request.user).order_by('-created_on')
        manga_list = paginate(manga_list, self.page_size, request.GET.get('p'))

        attach_comment_count(manga_list)
        attach_manga_favorite_count(manga_list)
        attach_manga_download_count(manga_list)

        upload_slots_used = min(self.get_upload_slots_used(), request.user.upload_limit)
        return self.render_to_response({
            'manga_list': manga_list,
            'upload_slots_used': upload_slots_used,
        })

    def post(self, request):
        if not SiteSetting.as_dict().get(SiteSettingKey.ENABLE_UPLOADS):
            return redirect('upload.list')

        if self.get_upload_slots_used() >= request.user.upload_limit:
            messages.error(request, _('You have reached your limit of {} uploads within the past 24 hours.').format(request.user.upload_limit))
            return redirect('upload.list')

        manga = Manga()
        manga.save(updated_by=request.user)
        return redirect('manga.edit.images', id=manga.id, slug=manga.slug)
