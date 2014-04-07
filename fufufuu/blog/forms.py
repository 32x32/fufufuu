from django import forms
from django.utils.translation import ugettext_lazy as _
from fufufuu.blog.models import BlogEntry


class BlogEntryForm(forms.ModelForm):

    title = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'maxlength': '200',
            'placeholder': _('Title of this post.'),
        }),
        max_length=200,
    )

    markdown = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'rows': '10',
            'placeholder': _('Enter the contents of your post here.'),
        }),
    )

    class Meta:
        model = BlogEntry
        fields = ['title', 'markdown', 'html']

    def save(self, user, commit=True):
        blog_entry = super().save(commit=False)

        if commit:
            blog_entry.save(user)

        return blog_entry
