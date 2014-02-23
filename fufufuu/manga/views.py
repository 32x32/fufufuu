import base64
import json

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from django.http.response import Http404, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext as _

from fufufuu.core.languages import Language
from fufufuu.core.utils import paginate
from fufufuu.core.views import TemplateView, ProtectedTemplateView
from fufufuu.download.models import DownloadLink
from fufufuu.image.enums import ImageKeyType
from fufufuu.image.filters import image_resize
from fufufuu.manga.enums import MangaStatus, MangaCategory, MangaAction
from fufufuu.manga.forms import MangaEditForm, MangaPageForm, MangaPageFormSet
from fufufuu.manga.models import Manga, MangaPage, MangaFavorite, MangaArchive
from fufufuu.manga.utils import process_zipfile, process_images, generate_manga_archive, attach_revision_tags
from fufufuu.revision.models import Revision


class MangaListMixin:

    template_name = 'manga/manga-list.html'
    page_size = 120

    def get_filters(self):
        filters = {}

        # filter by category
        categories = list(filter(lambda c: self.request.GET.get(c.lower()), list(MangaCategory.choices_dict)))
        if categories:
            filters['category__in'] = categories

        # filter by language
        languages = list(filter(lambda l: l in Language.choices_dict, self.request.GET.getlist('lang')))
        if languages:
            filters['language__in'] = languages

        return filters


class MangaListView(MangaListMixin, TemplateView):

    def get(self, request):
        manga_list = Manga.published.filter(**self.get_filters()).order_by('-published_on')
        manga_list = paginate(manga_list, self.page_size, request.GET.get('p'))
        return self.render_to_response({
            'manga_list': manga_list,
        })


class MangaListFavoritesView(MangaListMixin, ProtectedTemplateView):

    template_name = 'manga/manga-list-favorites.html'
    page_size = 120

    def get(self, request):
        filters = self.get_filters()
        filters['favorite_users'] = request.user
        manga_list = Manga.published.filter(**filters).order_by('-published_on')
        manga_list = paginate(manga_list, self.page_size, request.GET.get('p'))
        return self.render_to_response({
            'manga_list': manga_list,
        })


class MangaView(TemplateView):

    template_name = 'manga/manga.html'

    def get_payload(self, manga):
        """
        returns a base 64 encoded json dump of the data needed for manga page
        """

        page_list = []
        for page in manga.mangapage_set.order_by('page'):
            if page.double:
                key_type = ImageKeyType.MANGA_PAGE_DOUBLE
            else:
                key_type = ImageKeyType.MANGA_PAGE
            page_list.append({
                'double': page.double,
                'page': page.page,
                'url': image_resize(page.image, key_type, page.id),
            })

        payload = json.dumps({'page_list': page_list})
        payload = payload.encode('utf-8')
        payload = base64.b64encode(payload)
        return payload.decode('utf-8')

    def get(self, request, id, slug):
        context = {}
        manga = get_object_or_404(Manga.published, id=id)
        payload = self.get_payload(manga)

        tank = manga.tank
        if tank: context['chapter_list'] = tank.manga_set.order_by('tank_chapter')

        collection = manga.collection
        if collection: context['collection_list'] = collection.manga_set.order_by('collection_part')

        context.update({
            'manga': manga,
            'payload': payload,
        })
        return self.render_to_response(context)


class MangaInfoView(TemplateView):

    template_name = 'manga/manga-info.html'

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
            'manga_page_list': manga.mangapage_set.all(),
        })


class MangaCommentsView(TemplateView):

    template_name = 'manga/manga-comments.html'

    def get(self, request, id, slug):
        manga = get_object_or_404(Manga.published, id=id)
        return self.render_to_response({
            'manga': manga,
        })


class MangaDownloadView(TemplateView):

    def get(self, request, id, slug):
        return HttpResponseNotAllowed(permitted_methods=['post'])

    def post(self, request, id, slug):
        manga = get_object_or_404(Manga.published, id=id)
        try:
            manga_archive = MangaArchive.objects.get(manga=manga)
        except MangaArchive.DoesNotExist:
            manga_archive = generate_manga_archive(manga)

        ip_address = request.META.get('REMOTE_ADDR', '')
        ip_address = ip_address[:200]

        link, created = DownloadLink.objects.get_or_create(
            url=manga_archive.file.url,
            ip_address=ip_address,
            created_by=request.user if request.user.is_authenticated() else None,
        )

        if created:
            manga_archive.downloads += 1
            manga_archive.save()

        return redirect('download', key=link.key, filename=manga_archive.name)


class MangaReportView(TemplateView):

    template_name = 'manga/manga-report.html'

    def get(self, request, id, slug):
        manga = get_object_or_404(Manga.published, id=id)
        return self.render_to_response({
            'manga': manga,
        })


class MangaFavoriteView(ProtectedTemplateView):

    def get(self, request, id, slug):
        return redirect(reverse('manga.info', args=[id, slug]))

    def post(self, request, id, slug):
        manga = get_object_or_404(Manga.published, id=id)
        try:
            mf = MangaFavorite.objects.get(user=request.user, manga=manga)
            mf.delete()
        except MangaFavorite.DoesNotExist:
            MangaFavorite.objects.create(user=request.user, manga=manga)
        next = request.POST.get('next') or reverse('manga.info', args=[id, slug])
        return redirect(next)


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
            formset.save(manga=manga)
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


class MangaHistoryView(MangaEditMixin, TemplateView):

    template_name = 'manga/manga-history.html'
    page_size = 10

    def get(self, request, id, slug):
        manga = self.get_manga(id)
        ct = ContentType.objects.get_for_model(manga)

        revision_list = Revision.objects.filter(content_type__id=ct.id, object_id=manga.id).select_related('created_by').order_by('-created_on')
        revision_list = paginate(revision_list, self.page_size, request.GET.get('p'))
        attach_revision_tags(revision_list)

        return self.render_to_response({
            'manga': manga,
            'revision_list': revision_list,
        })
