import base64
import json
import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from django.http.response import Http404, HttpResponseNotAllowed, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _

from fufufuu.core.response import HttpResponseXAccel
from fufufuu.core.utils import paginate, get_ip_address, natural_sort, send_email_alert
from fufufuu.core.views import TemplateView, ProtectedTemplateView
from fufufuu.dmca.forms import DmcaRequestForm
from fufufuu.dmca.models import DmcaRequest
from fufufuu.download.models import DownloadLink
from fufufuu.image.enums import ImageKeyType
from fufufuu.image.filters import image_resize
from fufufuu.manga.enums import MangaCategory, MangaAction, MangaStatus
from fufufuu.manga.exceptions import MangaDmcaException
from fufufuu.manga.forms import MangaEditForm, MangaPageForm, MangaPageFormSet, MangaListFilterForm, MangaReportForm, MangaDownloadForm
from fufufuu.manga.models import Manga, MangaPage, MangaFavorite, MangaArchive
from fufufuu.manga.utils import process_zipfile, process_images, MangaArchiveGenerator
from fufufuu.report.models import ReportManga


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

        redirect_path = request.path
        query = request.POST.get('q')
        if query: redirect_path = '{}?q={}'.format(redirect_path, query)

        return redirect(redirect_path)


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


#-------------------------------------------------------------------------------


class BaseMangaView(TemplateView):

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except MangaDmcaException as e:
            self.template_name = 'manga/manga-dmca.html'
            manga = e.manga
            messages.error(request, _('This gallery has been removed due to a DMCA takedown request.'))
            dmca_list = DmcaRequest.objects.filter(manga=manga)
            return self.render_to_response({
                'dmca_list': dmca_list,
                'manga': manga,
            })

    def get_manga_for_view(self, id):
        user = self.request.user
        if not user.is_authenticated():
            manga = get_object_or_404(Manga.public, id=id)
        elif user.is_staff:
            manga = get_object_or_404(Manga.all, id=id)
        elif user.is_moderator:
            manga = get_object_or_404(Manga.objects, id=id)
        else:
            manga = get_object_or_404(Manga.public, id=id)

        if manga.status == MangaStatus.DMCA and not user.is_staff:
            raise MangaDmcaException(manga)

        return manga

    def get_manga_for_edit(self, id):
        user = self.request.user
        if not user.is_authenticated():
            raise Http404
        if user.is_staff:
            manga = get_object_or_404(Manga.all, id=id)
        elif user.is_moderator:
            manga = get_object_or_404(Manga.objects, id=id)
        else:
            manga = get_object_or_404(Manga.objects, id=id, created_by=user)

        if manga.status == MangaStatus.DMCA and not user.is_staff:
            raise MangaDmcaException(manga)

        return manga


class BaseMangaProtectedView(BaseMangaView):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class MangaView(BaseMangaView):

    template_name = 'manga/manga.html'

    def get_payload(self, manga_page_list):
        """
        returns a base 64 encoded json dump of the data needed for manga page
        """

        page_list = []
        for page in manga_page_list:
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

    def get(self, request, id, slug=None):
        context = {}
        manga = self.get_manga_for_view(id)

        if slug is None:
            return HttpResponsePermanentRedirect(reverse('manga', args=[manga.id, manga.slug]))

        manga_page_list = list(manga.mangapage_set.order_by('page'))
        payload = self.get_payload(manga_page_list)

        if manga.tank_id:
            manga_list = Manga.published.filter(tank_id=manga.tank_id, language=manga.language)
            context['chapter_list'] = natural_sort(manga_list, 'tank_chapter')

        if manga.collection_id:
            manga_list = Manga.published.filter(collection_id=manga.collection_id, language=manga.language)
            context['collection_list'] = natural_sort(manga_list, 'collection_part')

        try:
            archive = MangaArchive.objects.get(manga=manga)
        except MangaArchive.DoesNotExist:
            archive = MangaArchiveGenerator.generate(manga)

        download_available = (archive != None) and os.path.exists(archive.file.path)
        if not download_available:
            MangaArchiveGenerator.generate(manga)

        context.update({
            'archive': archive,
            'download_available': download_available,
            'download_form': MangaDownloadForm(request=request),
            'manga': manga,
            'page_count': len(manga_page_list),
            'payload': payload,
        })
        return self.render_to_response(context)


class MangaThumbnailsView(BaseMangaView):

    template_name = 'manga/manga-thumbnails.html'

    def get(self, request, id, slug):
        manga = self.get_manga_for_view(id)
        manga_page_list = manga.mangapage_set.all()
        for mp in manga_page_list:
            mp.image_thumbnail_url = image_resize(mp.image, ImageKeyType.MANGA_THUMB, mp.id)
        return self.render_to_response({
            'manga': manga,
            'manga_page_list': manga_page_list,
        })


class MangaDownloadView(BaseMangaView):

    def get(self, request, id, slug):
        return HttpResponseNotAllowed(permitted_methods=['post'])

    def post(self, request, id, slug):
        manga = self.get_manga_for_view(id)

        form = MangaDownloadForm(request=request, data=request.POST)
        if not form.is_valid():
            messages.error(request, _('You have failed the CAPTCHA, please try again.'))
            return redirect('manga', id=id, slug=slug)
        else:
            form.update_limit()

        try:
            manga_archive = MangaArchive.objects.get(manga=manga)
        except MangaArchive.DoesNotExist:
            manga_archive = MangaArchiveGenerator.generate(manga)
        if not manga_archive or not os.path.exists(manga_archive.file.path):
            MangaArchiveGenerator.generate(manga)
            messages.error(request, _('Sorry, the download is currently unavailable.'))
            return redirect('manga', id=id, slug=slug)

        link, created = DownloadLink.objects.get_or_create(
            url=manga_archive.file.url,
            ip_address=get_ip_address(request),
            created_by=request.user if request.user.is_authenticated() else None,
        )

        if created:
            manga_archive.downloads += 1
            manga_archive.save()

        return redirect('download', key=link.key, filename=manga_archive.name)


class MangaReportView(BaseMangaView):

    template_name = 'manga/manga-report.html'

    def get(self, request, id, slug):
        manga = self.get_manga_for_view(id)
        if request.user.is_authenticated() and ReportManga.open.filter(manga=manga, created_by=request.user).exists():
            messages.error(request, _('You have already reported this manga.'))

        return self.render_to_response({
            'form': MangaReportForm(request, manga=manga),
            'manga': manga,
        })

    def post(self, request, id, slug):
        manga = self.get_manga_for_view(id)
        form = MangaReportForm(request, manga=manga, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Thank you for reporting. Your report will be reviewed by a moderator shortly.'))
            return redirect('manga.list')

        return self.render_to_response({
            'form': form,
            'manga': manga,
        })


class MangaDmcaRequestView(BaseMangaProtectedView):

    template_name = 'manga/manga-dmca-request.html'

    def get(self, request, id, slug):
        if not request.user.dmca_account_id:
            raise Http404

        manga = self.get_manga_for_view(id)
        if manga.status == MangaStatus.DMCA:
            return redirect('manga', id=id, slug=slug)

        return self.render_to_response({
            'form': DmcaRequestForm(manga=manga, request=request),
            'manga': manga,
        })

    def post(self, request, id, slug):
        if not request.user.dmca_account_id:
            raise Http404

        manga = self.get_manga_for_view(id)
        if manga.status == MangaStatus.DMCA:
            return redirect('manga', id=id, slug=slug)

        form = DmcaRequestForm(manga=manga, request=request, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Your DMCA request has been successfully issued.'))
            return redirect('manga', id=id, slug=slug)

        return self.render_to_response({
            'form': form,
            'manga': manga,
        })


class MangaFavoriteView(BaseMangaProtectedView):

    def get(self, request, id, slug):
        return redirect(reverse('manga', args=[id, slug]))

    def post(self, request, id, slug):
        manga = self.get_manga_for_view(id)
        try:
            mf = MangaFavorite.objects.get(user=request.user, manga=manga)
            mf.delete()
        except MangaFavorite.DoesNotExist:
            MangaFavorite.objects.create(user=request.user, manga=manga)
        next = request.POST.get('next') or reverse('manga', args=[id, slug])
        return redirect(next)


#-------------------------------------------------------------------------------


class MangaEditView(BaseMangaProtectedView):

    template_name = 'manga/manga-edit.html'

    def get(self, request, id, slug):
        manga = self.get_manga_for_edit(id)

        return self.render_to_response({
            'manga': manga,
            'form': MangaEditForm(request=request, instance=manga),
        })

    def post(self, request, id, slug):
        manga = self.get_manga_for_edit(id)

        if request.POST.get('action') == MangaAction.DELETE:
            manga.delete(updated_by=request.user)
            messages.error(request, _('{} has been deleted.').format(manga.title))
            return redirect('upload.list')
        elif request.POST.get('action') == MangaAction.REMOVE and request.user.is_moderator:
            manga.status = MangaStatus.REMOVED
            manga.save(request.user)
            messages.error(request, _('{} has been removed.').format(manga.title))
            return redirect('manga.list')

        form = MangaEditForm(request=request, instance=manga, data=request.POST, files=request.FILES)
        if form.is_valid():
            manga = form.save()
            messages.success(request, _('{} has been updated').format(manga.title))
            for message in form.messages:
                messages.info(request, message)
            if request.POST.get('action') == MangaAction.PUBLISH:
                manga.update_tag_dictionary()
                send_email_alert(subject='[Fufufuu] Published: {}'.format(manga.title), message=manga.info_text)
            return redirect('manga.edit', id=id, slug=manga.slug)

        messages.error(request, _('{} has not been updated. Please fix the errors on the page and try again.').format(manga.title))
        return self.render_to_response({
            'manga': manga,
            'form': form,
        })


class MangaEditImagesView(BaseMangaProtectedView):

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
        manga = self.get_manga_for_edit(id)
        return self.render_to_response({
            'manga': manga,
            'formset': self.get_formset_cls()(user=request.user, queryset=MangaPage.objects.filter(manga=manga)),
        })

    def post(self, request, id, slug):
        manga = self.get_manga_for_edit(id)
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


class MangaEditImagesPageView(BaseMangaProtectedView):

    def get(self, request, id, slug, page):
        manga = self.get_manga_for_edit(id)
        manga_page = get_object_or_404(MangaPage, manga=manga, page=page)
        return HttpResponseXAccel(manga_page.image.url, manga_page.image.name, attachment=False)


class MangaEditUploadView(BaseMangaProtectedView):

    def get(self, request, id, slug):
        return HttpResponseNotAllowed(permitted_methods=['post'])

    def post(self, request, id, slug):
        manga = self.get_manga_for_edit(id)
        if 'zipfile' in request.FILES:
            errors = process_zipfile(manga, request.FILES.get('zipfile'), request.user)
        elif 'images' in request.FILES:
            errors = process_images(manga, request.FILES.getlist('images', []), request.user)
        else:
            raise Http404

        if errors:
            messages.error(request, '\n'.join(errors))

        return redirect('manga.edit.images', id=manga.id, slug=manga.slug)
