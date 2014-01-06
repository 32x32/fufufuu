from django.contrib import messages
from django.forms.models import modelformset_factory
from django.http.response import Http404, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext as _
from fufufuu.core.utils import paginate
from fufufuu.core.views import TemplateView, ProtectedTemplateView
from fufufuu.manga.enums import MangaStatus, MangaCategory, MangaAction
from fufufuu.manga.forms import MangaEditForm, MangaPageForm, MangaPageFormSet
from fufufuu.manga.models import Manga, MangaPage
from fufufuu.manga.utils import process_zipfile, process_images


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
        manga_list = Manga.published.filter(**self.get_filters()).order_by('-published_on')
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

        if request.POST.get('action') == MangaAction.DELETE:
            manga.delete(updated_by=request.user)
            return redirect('upload.list')

        form = MangaEditForm(request=request, instance=manga, data=request.POST, files=request.FILES)
        if form.is_valid():
            manga = form.save()
            messages.success(request, _('{} has been updated').format(manga.title))
            for message in form.messages:
                messages.info(request, message)
            return redirect('manga.edit', id=id, slug=manga.slug)

        messages.error(request, _('{} has not been updated. Please fix the errors on the page and try again.').format(manga.title))
        return self.render_to_response({
            'manga': manga,
            'form': form,
        })


class MangaEditImagesView(MangaEditMixin, ProtectedTemplateView):

    template_name = 'manga/manga-edit-images.html'

    @classmethod
    def get_formset_cls(cls):
        return modelformset_factory(
            model=MangaPage,
            form=MangaPageForm,
            formset=MangaPageFormSet,
            extra=0,
            can_order=True,
            max_num=100,
        )

    def get(self, request, id, slug):
        manga = self.get_manga(id)
        return self.render_to_response({
            'manga': manga,
            'formset': self.get_formset_cls()(user=request.user, queryset=MangaPage.objects.filter(manga=manga))
        })

    def post(self, request, id, slug):
        manga = self.get_manga(id)
        formset = self.get_formset_cls()(
            user=request.user,
            queryset=MangaPage.objects.filter(manga=manga),
            data=request.POST
        )

        if formset.is_valid():
            formset.save()
            for level, message in formset.messages:
                getattr(messages, level)(request, message)
            return redirect('manga.edit.images', id=id, slug=manga.slug)

        for error in formset.non_form_errors():
            messages.error(request, error)

        return self.render_to_response({
            'manga': manga,
            'formset': formset,
        })


class MangaEditUploadView(MangaEditMixin, ProtectedTemplateView):

    def get(self, request, id, slug):
        return HttpResponseNotAllowed(permitted_methods=['post'])

    def post(self, request, id, slug):
        manga = self.get_manga(id)
        if 'zipfile' in request.FILES:
            errors = process_zipfile(manga, request.FILES.get('zipfile'), request.user)
        elif 'images' in request.FILES:
            errors = process_images(manga, request.FILES.getlist('images', []), request.user)
        else:
            raise Http404

        if errors:
            messages.error(request, '\n'.join(errors))

        return redirect('manga.edit.images', id=manga.id, slug=manga.slug)
