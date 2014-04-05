from django.contrib.auth.decorators import login_required
from django.db.models.aggregates import Count, Sum
from django.forms.models import modelformset_factory
from django.http import Http404
from django.shortcuts import get_object_or_404, get_list_or_404
from django.utils.decorators import method_decorator
from fufufuu.core.views import TemplateView
from fufufuu.manga.models import Manga
from fufufuu.moderator.forms import ModeratorReportMangaFormSet, ModeratorReportMangaForm
from fufufuu.report.models import ReportManga


class ModeratorTemplateView(TemplateView):
    """
    Return HTTP404 if user is not a moderator or staff.
    """

    def render_to_response(self, context):
        context.update({
            'report_manga_count': ReportManga.open.values('manga').distinct().count(),
            'report_comment_count': 0,
        })
        return super().render_to_response(context)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_moderator and not request.user.is_staff:
            raise Http404
        return super().dispatch(request, *args, **kwargs)


class ModeratorReportMangaListView(ModeratorTemplateView):

    page_size = 50
    template_name = 'moderator/moderator-report-manga-list.html'

    def get(self, request):
        report_list = ReportManga.open.values('manga')\
            .annotate(count=Count('manga'), weight=Sum('weight'))\
            .order_by('-weight')[:self.page_size]
        report_dict = dict([(r['manga'], (r['count'], r['weight'])) for r in report_list])

        manga_list = Manga.objects.filter(id__in=report_dict.keys()).select_related('created_by')
        for manga in manga_list:
            manga.report_count = report_dict[manga.id][0]
            manga.report_weight = int(report_dict[manga.id][1])

        manga_list = sorted(manga_list, key=lambda m: m.report_weight, reverse=True)
        return self.render_to_response({
            'manga_list': manga_list,
        })


class ModeratorReportMangaView(ModeratorTemplateView):

    template_name = 'moderator/moderator-report-manga.html'

    @classmethod
    def get_formset_cls(cls):
        return modelformset_factory(
            model=ReportManga,
            form=ModeratorReportMangaForm,
            formset=ModeratorReportMangaFormSet,
            extra=0,
        )

    def get(self, request, id):
        manga = get_object_or_404(Manga.objects, id=id)
        report_list = get_list_or_404(
            klass=ReportManga.open.select_related('created_by').order_by('-weight'),
            manga=manga
        )
        formset = self.get_formset_cls()(user=request.user, queryset=report_list),
        return self.render_to_response({
            'manga': manga,
            'formset': formset,
        })
