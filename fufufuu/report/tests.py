from django.contrib.auth.models import AnonymousUser
from fufufuu.core.tests import BaseTestCase
from fufufuu.report.enums import ReportMangaType
from fufufuu.report.forms import ReportMangaForm, ANONYMOUS_USER_REPORT_WEIGHT


class RepoprtMangaFormTests(BaseTestCase):

    def test_report_manga_form_anonymous_user(self):
        from captcha.conf import settings
        from captcha.models import CaptchaStore

        challenge, response = settings.get_challenge()()
        store = CaptchaStore.objects.create(challenge=challenge, response=response)

        self.request.user = AnonymousUser()

        form = ReportMangaForm(request=self.request, data={
            'type': ReportMangaType.COPYRIGHT,
            'check': 'on',
            'captcha_0': store.hashkey,
            'captcha_1': store.response,
        })
        self.assertTrue(form.is_valid())

        report_manga = form.save(self.manga)
        self.assertEqual(report_manga.created_by, None)
        self.assertEqual(report_manga.ip_address, '127.0.0.1')
        self.assertEqual(report_manga.weight, ANONYMOUS_USER_REPORT_WEIGHT)
        self.assertEqual(report_manga.manga, self.manga)
        self.assertEqual(report_manga.type, ReportMangaType.COPYRIGHT)

    def test_report_manga_form(self):
        form = ReportMangaForm(request=self.request, data={
            'type': ReportMangaType.REPOST,
            'comment': 'This is a repost.',
            'check': 'on',
        })
        self.assertTrue(form.is_valid())

        report_manga = form.save(self.manga)
        self.assertEqual(report_manga.created_by, self.user)
        self.assertEqual(report_manga.ip_address, '127.0.0.1')
        self.assertEqual(report_manga.weight, self.user.report_weight)
        self.assertEqual(report_manga.manga, self.manga)
        self.assertEqual(report_manga.type, ReportMangaType.REPOST)
