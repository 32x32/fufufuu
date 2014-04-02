from django.db.models.aggregates import Count
from fufufuu.core.views import ModeratorTemplateView
from fufufuu.manga.models import Manga
from fufufuu.report.models import ReportManga


class ModeratorReportMangaListView(ModeratorTemplateView):

    template_name = 'moderator/moderator-report-manga-list.html'

    def get(self, request):
        report_list = ReportManga.open.values('manga').annotate(count=Count('manga'))
        report_dict = dict([(r['manga'], r['count']) for r in report_list])

        manga_list = Manga.objects.filter(id__in=report_dict.keys()).select_related('created_by')
        for manga in manga_list:
            manga.report_count = report_dict[manga.id]

        return self.render_to_response({
            'manga_list': manga_list,
        })
