from django.shortcuts import redirect
from fufufuu.core.utils import paginate
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
        manga = Manga()
        manga.save(updated_by=request.user)
        return redirect('manga.edit', id=manga.id, slug=manga.slug)
