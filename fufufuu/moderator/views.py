from django.db.models.aggregates import Count, Sum
from django.shortcuts import get_object_or_404, get_list_or_404
from fufufuu.core.utils import paginate
from fufufuu.core.views import ModeratorTemplateView
from fufufuu.manga.models import Manga
from fufufuu.report.models import ReportManga


class ModeratorReportMangaListView(ModeratorTemplateView):

    max_show = 50
    template_name = 'moderator/moderator-report-manga-list.html'

    def get(self, request):
        report_list = ReportManga.open.values('manga').annotate(count=Count('manga'), weight=Sum('weight'))
        report_dict = dict([(r['manga'], (r['count'], r['weight'])) for r in report_list])

        manga_list = Manga.objects.filter(id__in=report_dict.keys()).select_related('created_by')
        for manga in manga_list:
            manga.report_count = report_dict[manga.id][0]
            manga.report_weight = int(report_dict[manga.id][1])

        manga_list = sorted(manga_list, key=lambda m: m.report_weight, reverse=True)
        return self.render_to_response({
            'manga_list': manga_list[:self.max_show],
        })


class ModeratorReportMangaView(ModeratorTemplateView):

    template_name = 'moderator/moderator-report-manga.html'

    def get(self, request, id):
        manga = get_object_or_404(Manga.objects, id=id)
        report_list = get_list_or_404(
            klass=ReportManga.open.select_related('created_by').order_by('-weight'),
            manga=manga
        )
        return self.render_to_response({
            'manga': manga,
            'report_list': report_list,
        })

