from django.core.urlresolvers import reverse
from fufufuu.core.tests import BaseTestCase
from fufufuu.manga.enums import MangaStatus
from fufufuu.manga.models import Manga
from fufufuu.moderator.views import ModeratorReportMangaView
from fufufuu.report.enums import ReportQuality
from fufufuu.report.models import ReportManga


class ModeratorReportMangaListViewTests(BaseTestCase):

    def test_moderator_report_manga_list_view_get(self):
        response = self.client.get(reverse('moderator.report.manga.list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'moderator/moderator-report-manga-list.html')


class ModeratorReportMangaViewTests(BaseTestCase):

    def test_moderator_report_manga_view_get(self):
        response = self.client.get(reverse('moderator.report.manga', args=[self.manga.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'moderator/moderator-report-manga.html')

    def test_moderator_report_manga_view_get_anonymous(self):
        ReportManga.open.filter(manga=self.manga.id).update(created_by=None)
        response = self.client.get(reverse('moderator.report.manga', args=[self.manga.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'moderator/moderator-report-manga.html')

    def test_moderator_report_manga_view_post_invalid(self):
        report_list = ReportManga.open.filter(manga=self.manga)
        report_count = report_list.count()
        data = {
            'form-TOTAL_FORMS': report_count,
            'form-INITIAL_FORMS': report_count,
            'form-MAX_NUM_FORMS': '100',
        }
        for i, report in enumerate(report_list):
            data['form-{}-id'.format(i)] = report.id
            data['form-{}-quality'.format(i)] = ReportQuality.GOOD

        response = self.client.post(reverse('moderator.report.manga', args=[self.manga.id]), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'moderator/moderator-report-manga.html')

    def test_moderator_report_manga_view_post_remove(self):
        report_list = ReportManga.open.filter(manga=self.manga)
        report_count = report_list.count()
        data = {
            'form-TOTAL_FORMS': report_count,
            'form-INITIAL_FORMS': report_count,
            'form-MAX_NUM_FORMS': '100',
            'action': 'remove',
        }
        for i, report in enumerate(report_list):
            data['form-{}-id'.format(i)] = report.id
            data['form-{}-quality'.format(i)] = ReportQuality.GOOD

        response = self.client.post(reverse('moderator.report.manga', args=[self.manga.id]), data)
        self.assertRedirects(response, reverse('moderator.report.manga.list'))

    def test_moderator_report_manga_view_post_keep(self):
        report_list = ReportManga.open.filter(manga=self.manga)
        report_count = report_list.count()
        data = {
            'form-TOTAL_FORMS': report_count,
            'form-INITIAL_FORMS': report_count,
            'form-MAX_NUM_FORMS': '100',
            'action': 'keep',
        }
        for i, report in enumerate(report_list):
            data['form-{}-id'.format(i)] = report.id
            data['form-{}-quality'.format(i)] = ReportQuality.BAD

        response = self.client.post(reverse('moderator.report.manga', args=[self.manga.id]), data)
        self.assertRedirects(response, reverse('moderator.report.manga.list'))


class ModeratorReportMangaFormSetTests(BaseTestCase):

    def test_moderator_report_manga_form_set_missing_action(self):
        data = {
            'form-TOTAL_FORMS': '0',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '100',
        }
        formset_cls = ModeratorReportMangaView.get_formset_cls()
        formset = formset_cls(queryset=ReportManga.open.none(), data=data)
        self.assertFalse(formset.is_valid())
        self.assertEqual(formset.non_form_errors(), ['No action has been selected for the manga.'])

    def test_moderator_report_manga_form_set_invalid(self):
        report_list = ReportManga.open.filter(manga=self.manga)
        report_count = report_list.count()
        data = {
            'form-TOTAL_FORMS': report_count,
            'form-INITIAL_FORMS': report_count,
            'form-MAX_NUM_FORMS': '100',
            'action': 'remove',
        }
        for i, report in enumerate(report_list):
            data['form-{}-id'.format(i)] = report.id

        formset_cls = ModeratorReportMangaView.get_formset_cls()
        formset = formset_cls(queryset=report_list, data=data)
        self.assertFalse(formset.is_valid())
        self.assertEqual(formset.errors, [{'quality': ['This field is required.']} for _ in range(report_count)])

    def test_moderator_report_manga_form_set_keep(self):
        self.manga.status = MangaStatus.PENDING
        self.manga.save(self.user)

        report_list = ReportManga.open.filter(manga=self.manga)
        report_id_set = set(report_list.values_list('id', flat=True))
        report_count = report_list.count()
        data = {
            'form-TOTAL_FORMS': report_count,
            'form-INITIAL_FORMS': report_count,
            'form-MAX_NUM_FORMS': '100',
            'action': 'keep',
            'comment': 'These are incorrect reports.',
        }
        for i, report in enumerate(report_list):
            data['form-{}-id'.format(i)] = report.id
            data['form-{}-quality'.format(i)] = ReportQuality.BAD

        formset_cls = ModeratorReportMangaView.get_formset_cls()
        formset = formset_cls(queryset=report_list, data=data)
        self.assertTrue(formset.is_valid())

        resolution = formset.save(user=self.user, manga=self.manga)
        self.assertFalse(resolution.removed)
        self.assertEqual(resolution.manga, self.manga)
        self.assertEqual(resolution.comment, 'These are incorrect reports.')

        manga = Manga.objects.get(id=self.manga.id)
        self.assertEqual(manga.status, MangaStatus.PUBLISHED)

        closed_report_list = ReportManga.closed.filter(resolution=resolution)
        self.assertEqual(set(closed_report_list.values_list('id', flat=True)), report_id_set)
        for report in closed_report_list:
            self.assertEqual(report.quality, ReportQuality.BAD)

    def test_moderator_report_manga_form_set_remove(self):
        report_list = ReportManga.open.filter(manga=self.manga)
        report_id_set = set(report_list.values_list('id', flat=True))
        report_count = report_list.count()
        data = {
            'form-TOTAL_FORMS': report_count,
            'form-INITIAL_FORMS': report_count,
            'form-MAX_NUM_FORMS': '100',
            'action': 'remove',
        }
        for i, report in enumerate(report_list):
            data['form-{}-id'.format(i)] = report.id
            data['form-{}-quality'.format(i)] = ReportQuality.GOOD

        formset_cls = ModeratorReportMangaView.get_formset_cls()
        formset = formset_cls(queryset=report_list, data=data)
        self.assertTrue(formset.is_valid())

        resolution = formset.save(user=self.user, manga=self.manga)
        self.assertTrue(resolution.removed)
        self.assertEqual(resolution.manga, self.manga)

        manga = Manga.objects.get(id=self.manga.id)
        self.assertEqual(manga.status, MangaStatus.REMOVED)

        closed_report_list = ReportManga.closed.filter(resolution=resolution)
        self.assertEqual(set(closed_report_list.values_list('id', flat=True)), report_id_set)
        for report in closed_report_list:
            self.assertEqual(report.quality, ReportQuality.GOOD)
