from django.contrib import messages
from django.http.response import Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext as _
from fufufuu.core.utils import paginate
from fufufuu.core.views import TemplateView, ProtectedTemplateView
from fufufuu.manga.enums import MangaStatus, MangaCategory
from fufufuu.manga.forms import MangaEditForm
from fufufuu.manga.models import Manga


class MangaListView(TemplateView):

    template_name = 'manga/manga-list.html'
    page_size = 120

    def get_filters(self):
        filters = {}

        # filter by category
        categories = list(filter(lambda c: self.request.GET.get(c.lower()), list(MangaCategory.choices_dict)))
        if categories:
            filters['category__in'] = categories

        # filter by language

        return filters

    def get(self, request):
        manga_list = Manga.published.filter(**self.get_filters())
        manga_list = paginate(manga_list, self.page_size, request.GET.get('p'))
        return self.render_to_response({
            'manga_list': manga_list,
        })


class MangaView(TemplateView):

    template_name = 'manga/manga.html'

    def get(self, request, id, slug):
        manga = get_object_or_404(Manga.published, id=id)
        return self.render_to_response({
            'manga': manga,
        })


class MangaThumbnailsView(TemplateView):

    template_name = 'manga/manga-thumbnails.html'

    def get(self, request, id, slug):
        manga = get_object_or_404(Manga.published, id=id)
        return self.render_to_response({
            'manga': manga,
        })


class MangaCommentsView(TemplateView):

    template_name = 'manga/manga-comments.html'

    def get(self, request, id, slug):
        manga = get_object_or_404(Manga.published, id=id)
        return self.render_to_response({
            'manga': manga,
        })


class MangaDownloadView(TemplateView):

    template_name = 'manga/manga-download.html'

    def get(self, request, id, slug):
        manga = get_object_or_404(Manga.published, id=id)
        return self.render_to_response({
            'manga': manga,
        })


class MangaReportView(TemplateView):

    template_name = 'manga/manga-report.html'

    def get(self, request, id, slug):
        manga = get_object_or_404(Manga.published, id=id)
        return self.render_to_response({
            'manga': manga,
        })


class MangaHistoryView(TemplateView):

    template_name = 'manga/manga-history.html'

    def get(self, request, id, slug):
        manga = get_object_or_404(Manga.published, id=id)
        return self.render_to_response({
            'manga': manga,
        })


#-------------------------------------------------------------------------------


class MangaEditMixin:

    def get_manga(self, id):
        """
        draft mode      --> editable only by created user
        published mode  --> editable everyone
        pending mode    --> editable only by moderators
        deleted mode    --> raise 404
        """

        manga = get_object_or_404(Manga.objects, id=id)
        if manga.status == MangaStatus.DRAFT:
            if manga.created_by != self.request.user: raise Http404
        elif manga.status == MangaStatus.PUBLISHED:
            pass
        elif manga.status == MangaStatus.PENDING:
            pass
        return manga


class MangaEditView(MangaEditMixin, ProtectedTemplateView):

    template_name = 'manga/manga-edit.html'

    def get(self, request, id, slug):
        manga = self.get_manga(id)
        return self.render_to_response({
            'manga': manga,
            'form': MangaEditForm(request=request, instance=manga),
        })

    def post(self, request, id, slug):
        manga = self.get_manga(id)
        form = MangaEditForm(request=request, instance=manga, data=request.POST)
        if form.is_valid():
            manga = form.save()
            messages.success(request, _('{} has been updated').format(manga.title))
            return redirect('manga.edit', id=id, slug=manga.slug)

        messages.error(request, _('{} has not been updated. Please fix the errors on the page and try again.').format(manga.title))
        return self.render_to_response({
            'manga': manga,
            'form': form,
        })


class MangaEditImagesView(MangaEditMixin, ProtectedTemplateView):

    template_name = 'manga/manga-edit-images.html'

    def get(self, request, id, slug):
        manga = self.get_manga(id)
        return self.render_to_response({
            'manga': manga,
        })
