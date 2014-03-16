from django.core.urlresolvers import reverse
from fufufuu.core.enums import SiteSettingKey
from fufufuu.core.models import SiteSetting
from fufufuu.core.tests import BaseTestCase
from fufufuu.staff.forms import SiteSettingForm


class StaffViewTests(BaseTestCase):

    def test_staff_view_get_non_staff(self):
        self.user.is_staff = False
        self.user.save()

        response = self.client.get(reverse('staff'))
        self.assertEqual(response.status_code, 404)

    def test_staff_view_get(self):
        response = self.client.get(reverse('staff'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/staff.html')

    def test_staff_view_post(self):
        announcement = 'This is an important announcement update!'
        response = self.client.post(reverse('staff'), {
            'announcement': announcement,
        })
        self.assertRedirects(response, reverse('staff'))
        self.assertEqual(SiteSetting.objects.get(key=SiteSettingKey.ANNOUNCEMENT).val, announcement)


class SiteSettingFormTests(BaseTestCase):

    def test_site_setting_form_no_settings(self):
        form = SiteSettingForm()
        self.assertEqual(form.fields['announcement'].initial, None)
        self.assertEqual(form.fields['enable_comments'].initial, None)
        self.assertEqual(form.fields['enable_uploads'].initial, None)

    def test_site_setting_form(self):
        SiteSetting.objects.create(key=SiteSettingKey.ANNOUNCEMENT, val='This is a sample announcement', updated_by=self.user)
        SiteSetting.objects.create(key=SiteSettingKey.ENABLE_COMMENTS, val='True', updated_by=self.user)
        SiteSetting.objects.create(key=SiteSettingKey.ENABLE_UPLOADS, val='False', updated_by=self.user)

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
