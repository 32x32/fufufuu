from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import View
from fufufuu.legacy.models import LegacyTank


class LegacyTankListView(View):

    def get(self, request):
        return redirect('tag.list.grid.tank')


class LegacyTankView(View):

    def get(self, request, id, slug):
        tag = get_object_or_404(LegacyTank.objects.select_related('tag'), id=id).tag
        return redirect('tag', id=tag.id, slug=tag.slug)
