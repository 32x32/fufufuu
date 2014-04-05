from django import forms
from django.forms.models import BaseModelFormSet
from fufufuu.report.models import ReportManga


class ReportMangaForm(forms.ModelForm):

    class Meta:
        model = ReportManga
        fields = ['quality']


class ReportMangaFormSet(BaseModelFormSet):

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
