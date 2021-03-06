from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect, get_object_or_404

from fufufuu.comment.forms import CommentForm
from fufufuu.comment.models import Comment
from fufufuu.core.views import ProtectedTemplateView


class CommentPostView(ProtectedTemplateView):

    def get(self, request):
        return redirect('manga.list')

    def post(self, request):
        next_url = request.POST.get('next', reverse('manga.list'))

        form = CommentForm(request=request, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Your comment has been posted.'))
            return redirect(next_url)

        messages.error(request, '\n'.join(['{}: {}'.format(field.label, error) for field in form for error in field.errors]))
        return redirect(next_url)


class CommentDeleteView(ProtectedTemplateView):

    def get(self, request, id):
        return redirect('manga.list')

    def post(self, request, id):
        filters = {
            'klass': Comment,
            'id': id,
        }
        if not request.user.is_moderator:
            filters['created_by'] = request.user

        comment = get_object_or_404(**filters)
        comment.delete()

        messages.error(request, _('The comment has been successfully deleted.'))
        next_url = request.POST.get('next', reverse('manga.list'))
        return redirect(next_url)
