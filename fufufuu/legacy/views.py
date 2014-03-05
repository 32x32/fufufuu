from django.core.urlresolvers import reverse
from django.http.response import HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.base import View
from fufufuu.legacy.models import LegacyTank


class LegacyTankView(View):

    def get(self, request, id, slug):
        tag = get_object_or_404(LegacyTank.objects.select_related('tag'), id=id).tag
        return HttpResponsePermanentRedirect(reverse('tag', args=[tag.id, tag.slug]))
