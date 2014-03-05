from django.core.urlresolvers import reverse
from fufufuu.core.tests import BaseTestCase
from fufufuu.legacy.models import LegacyTank
from fufufuu.tag.enums import TagType
from fufufuu.tag.models import Tag


class LegacyTankListViewTests(BaseTestCase):

    def test_legacy_tank_list_view_get(self):
        response = self.client.get(reverse('legacy.tank.list'))
        self.assertRedirects(response, reverse('tag.list.grid.tank'))


class LegacyTankViewTests(BaseTestCase):

    def test_legacy_tank_view_get(self):
        tank = Tag.objects.filter(tag_type=TagType.TANK)[0]
        legacy_tank = LegacyTank.objects.create(tag=tank)

        response = self.client.get(reverse('legacy.tank', args=[legacy_tank.id, 'some-slug']))
        self.assertRedirects(response, reverse('tag', args=[tank.id, tank.slug]))

    def test_legacy_tank_view_get_404(self):
        response = self.client.get(reverse('legacy.tank', args=[0, 'some-slug']))
        self.assertEqual(response.status_code, 404)
