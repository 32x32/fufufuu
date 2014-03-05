from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse
from fufufuu.manga.models import Manga


class MangaSitemap(Sitemap):

    changefreq = 'never'

    def items(self):
        return Manga.published.all()

    def location(self, obj):
        return reverse('manga', args=[obj.id, obj.slug])

    def lastmod(self, obj):
        return obj.updated_on
