from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from fufufuu.comment.models import Comment
from fufufuu.core.utils import get_ip_address, convert_markdown


class CommentForm(forms.ModelForm):

    content_type = forms.ModelChoiceField(
        widget=forms.HiddenInput,
        queryset=ContentType.objects.all(),
    )

    object_id = forms.IntegerField(widget=forms.HiddenInput)

    markdown = forms.CharField(
        label=_('Comment'),
        max_length=300,
        widget=forms.Textarea(attrs={
            'class': 'comment-textarea',
            'maxlength': '300',
            'placeholder': _('Leave a comment'),
            'required': 'required',
            'rows': '3'
        }),
        help_text=_('<a href="/f/markdown/" class="text-xsmall" target="_blank">This field uses markdown for formatting.</a>'),
        error_messages={
            'required': _('Your comment cannot be blank.'),
        },
    )

    class Meta:
        model = Comment
        fields = ('content_type', 'object_id', 'markdown')

    def __init__(self, content_object=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if content_object:
            self.fields['content_type'].initial = ContentType.objects.get_for_model(content_object).id
            self.fields['object_id'].initial = content_object.id
        self.html = None

    def clean_markdown(self):
        markdown = self.cleaned_data.get('markdown')
        self.html = convert_markdown(markdown)

        if not self.html:
            raise forms.ValidationError(_('Your comment cannot be blank.'))

        return markdown

    def save(self, request, commit=True):
        comment = super().save(commit=False)
        comment.ip_address = get_ip_address(request)
        comment.created_by = request.user
        comment.html = self.html

        if commit:
            comment.save()

        return comment
