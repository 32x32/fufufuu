from django.core.urlresolvers import reverse
from fufufuu.core.enums import SiteSettingKey
from fufufuu.core.models import SiteSetting
from fufufuu.core.tests import BaseTestCase
from fufufuu.staff.forms import SiteSettingForm


class StaffSiteMetricsViewTests(BaseTestCase):

    def test_staff_site_metrics_view_get(self):
        response = self.client.get(reverse('staff.site.metrics'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/staff-site-metrics.html')


class StaffSiteSettingsViewTests(BaseTestCase):

    def test_staff_view_get_non_staff(self):
        self.user.is_staff = False
        self.user.save()

        response = self.client.get(reverse('staff.site.settings'))
        self.assertEqual(response.status_code, 404)

    def test_staff_view_get(self):
        response = self.client.get(reverse('staff.site.settings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/staff-site-settings.html')

    def test_staff_view_post(self):
        announcement = 'This is an important announcement update!'
        response = self.client.post(reverse('staff.site.settings'), {
            'announcement': announcement,
        })
        self.assertRedirects(response, reverse('staff.site.settings'))
        self.assertEqual(SiteSetting.get_val(SiteSettingKey.ANNOUNCEMENT), announcement)


class SiteSettingFormTests(BaseTestCase):

    def test_site_setting_form_no_settings(self):
        form = SiteSettingForm()
        self.assertEqual(form.fields['announcement'].initial, None)
        self.assertEqual(form.fields['enable_comments'].initial, True)
        self.assertEqual(form.fields['enable_uploads'].initial, True)

    def test_site_setting_form(self):
        SiteSetting.set_val(SiteSettingKey.ANNOUNCEMENT, 'This is a sample announcement', self.user)
        SiteSetting.set_val(SiteSettingKey.ENABLE_COMMENTS, 'True', self.user)
        SiteSetting.set_val(SiteSettingKey.ENABLE_UPLOADS, 'False', self.user)

        form = SiteSettingForm()
        self.assertEqual(form.fields['announcement'].initial, 'This is a sample announcement')
        self.assertEqual(form.fields['enable_comments'].initial, True)
        self.assertEqual(form.fields['enable_uploads'].initial, False)

    def test_site_setting_form_save(self):
        form = SiteSettingForm(data={
            'announcement': 'This is a sample announcement',
            'enable_comments': 'on',
        })
        self.assertTrue(form.is_valid())
        form.save(self.user)

        settings_dict = SiteSetting.as_dict()
        self.assertEqual(settings_dict.get(SiteSettingKey.ANNOUNCEMENT), 'This is a sample announcement')
        self.assertEqual(settings_dict.get(SiteSettingKey.ENABLE_COMMENTS), True)
        self.assertEqual(settings_dict.get(SiteSettingKey.ENABLE_UPLOADS), False)


class StaffDmcaAccountListViewTests(BaseTestCase):

    def test_staff_dmca_account_list_view_get(self):
        response = self.client.get(reverse('staff.dmca.account.list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/staff-dmca-account-list.html')


class StaffDmcaAccountViewTests(BaseTestCase):

    def test_staff_dmca_account_view_get(self):
        response = self.client.get(reverse('staff.dmca.account', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/staff-dmca-account.html')
