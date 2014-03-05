from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse
from fufufuu.tag.models import Tag


class TagSitemap(Sitemap):

    changefreq = 'weekly'

    def items(self):
        return Tag.objects.all()

    def location(self, obj):
        return reverse('tag', args=[obj.id, obj.slug])

    def lastmod(self, obj):
        return obj.updated_on
