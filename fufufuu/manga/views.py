import base64
import json
import os

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from django.http.response import Http404, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext as _
from fufufuu.core.response import HttpResponseXAccel

from fufufuu.core.utils import paginate
from fufufuu.core.views import TemplateView, ProtectedTemplateView
from fufufuu.download.models import DownloadLink
from fufufuu.image.enums import ImageKeyType
from fufufuu.image.filters import image_resize
from fufufuu.manga.enums import MangaStatus, MangaCategory, MangaAction, MANGA_FIELDNAME_MAP
from fufufuu.manga.forms import MangaEditForm, MangaPageForm, MangaPageFormSet, MangaListFilterForm
from fufufuu.manga.models import Manga, MangaPage, MangaFavorite, MangaArchive
from fufufuu.manga.utils import process_zipfile, process_images, generate_manga_archive, attach_revision_tags
from fufufuu.revision.enums import RevisionStatus
from fufufuu.revision.models import Revision


class MangaListMixin:

    template_name = 'manga/manga-list.html'
    page_size = 120

    def get_filters(self):
        session_filters = self.request.session.get('manga_list_filters', {})

        filters = {}

        # filter by category
        categories = list(filter(lambda c: session_filters.get(c.lower()), list(MangaCategory.choices_dict)))
        if categories: filters['category__in'] = categories

        # filter by language
        language = session_filters.get('lang')
        if language: filters['language'] = language

        return filters

    def post(self, request, *args, **kwargs):
        form = MangaListFilterForm(request, data=request.POST)
        if form.is_valid():
            form.save()
        return redirect(request.path)


class MangaListView(MangaListMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        manga_list = Manga.published.filter(**self.get_filters()).order_by('-published_on')
        manga_list = paginate(manga_list, self.page_size, request.GET.get('p'))
        return self.render_to_response({
            'manga_list': manga_list,
        })


class MangaListFavoritesView(MangaListMixin, ProtectedTemplateView):

    template_name = 'manga/manga-list.html'
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
            key_type = page.double and ImageKeyType.MANGA_PAGE_DOUBLE or ImageKeyType.MANGA_PAGE
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

        if manga.tank_id:
            context['chapter_list'] = Manga.published.filter(tank_id=manga.tank_id).order_by('tank_chapter')

        if manga.collection_id:
            context['collection_list'] = Manga.published.filter(collection_id=manga.collection_id).order_by('collection_part')

        context.update({
            'manga': manga,
            'payload': payload,
        })
        return self.render_to_response(context)


class MangaInfoView(TemplateView):

    template_name = 'manga/manga-info.html'

    def get(self, request, id, slug):
        manga = get_object_or_404(Manga.published, id=id)
        try:
            archive = MangaArchive.objects.get(manga=manga)
        except MangaArchive.DoesNotExist:
            archive = generate_manga_archive(manga)
        if not os.path.exists(archive.file.path):
            archive = generate_manga_archive(manga)
        return self.render_to_response({
            'archive': archive,
            'manga': manga,
        })


class MangaThumbnailsView(TemplateView):

    template_name = 'manga/manga-thumbnails.html'

    def get(self, request, id, slug):
        manga = get_object_or_404(Manga.published, id=id)
        manga_page_list = manga.mangapage_set.all()
        for mp in manga_page_list:
            mp.image_thumbnail_url = image_resize(mp.image, ImageKeyType.MANGA_THUMB, mp.id)
        return self.render_to_response({
            'manga': manga,
            'manga_page_list': manga_page_list,
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

    def get_manga_restricted(self, id):
        if self.request.user.is_moderator:
            manga = get_object_or_404(Manga.objects, id=id)
        else:
            manga = get_object_or_404(Manga.objects, id=id, created_by=self.request.user)
        return manga


class MangaEditView(MangaEditMixin, ProtectedTemplateView):

    template_name = 'manga/manga-edit.html'

    def get_revision(self, manga, request):
        ct = ContentType.objects.get_for_model(manga)
        try:
            revision = Revision.objects.get(
                content_type__id=ct.id,
                object_id=manga.id,
                status=RevisionStatus.PENDING,
                created_by=request.user,
            )
        except Revision.DoesNotExist:
            revision = None
        return revision

    def get(self, request, id, slug):
        manga = self.get_manga(id)

        revision = self.get_revision(manga, request)
        if revision:
            manga, m2m = revision.apply()
            messages.info(request, _('The current changes are only visible to you. When a moderator or the uploader approves your changes, they will become visible to everyone.'))
        else:
            m2m = {}

        return self.render_to_response({
            'manga': manga,
            'form': MangaEditForm(request=request, tag_id_list=m2m.get('tags'), instance=manga),
        })

    def post(self, request, id, slug):
        manga = self.get_manga(id)

        if request.POST.get('action') == MangaAction.DELETE:
            manga.delete(updated_by=request.user)
            return redirect('upload.list')

        form = MangaEditForm(request=request, instance=manga, data=request.POST, files=request.FILES)
        if form.is_valid():
            revision = self.get_revision(manga, request)
            if revision: revision.delete()

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
        manga = self.get_manga_restricted(id)
        return self.render_to_response({
            'manga': manga,
            'formset': (self.get_formset_cls()(user=request.user, queryset=MangaPage.objects.filter(manga=manga))),
        })

    def post(self, request, id, slug):
        manga = self.get_manga_restricted(id)
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


class MangaEditImagesPageView(MangaEditMixin, ProtectedTemplateView):

    def get(self, request, id, slug, page):
        manga = self.get_manga_restricted(id)
        manga_page = get_object_or_404(MangaPage, manga=manga, page=page)
        return HttpResponseXAccel(manga_page.image.url, manga_page.image.name, attachment=False)


class MangaEditUploadView(MangaEditMixin, ProtectedTemplateView):

    def get(self, request, id, slug):
        return HttpResponseNotAllowed(permitted_methods=['post'])

    def post(self, request, id, slug):
        manga = self.get_manga_restricted(id)
        if 'zipfile' in request.FILES:
            errors = process_zipfile(manga, request.FILES.get('zipfile'), request.user)
        elif 'images' in request.FILES:
            errors = process_images(manga, request.FILES.getlist('images', []), request.user)
        else:
            raise Http404

        if errors:
            messages.error(request, '\n'.join(errors))

        return redirect('manga.edit.images', id=manga.id, slug=manga.slug)


class MangaRevisionsView(MangaEditMixin, TemplateView):

    template_name = 'manga/manga-revisions.html'
    page_size = 10

    def get(self, request, id, slug):
        manga = self.get_manga(id)
        ct = ContentType.objects.get_for_model(manga)

        revision_list = Revision.objects.filter(content_type__id=ct.id, object_id=manga.id).select_related('created_by').order_by('-created_on')
        revision_list = paginate(revision_list, self.page_size, request.GET.get('p'))
        attach_revision_tags(revision_list)

        return self.render_to_response({
            'manga': manga,
            'MANGA_FIELDNAME_MAP': MANGA_FIELDNAME_MAP,
            'revision_list': revision_list,
        })
