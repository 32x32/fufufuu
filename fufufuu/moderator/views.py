from django.db.models.aggregates import Count, Sum
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
