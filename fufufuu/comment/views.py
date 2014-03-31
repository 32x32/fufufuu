from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect

from fufufuu.comment.forms import CommentForm
from fufufuu.core.views import ProtectedTemplateView


class CommentPostView(ProtectedTemplateView):

    def get(self, request):
        return redirect('manga.list')

    def post(self, request):
        next_url = request.POST.get('next', reverse('manga.list'))

        form = CommentForm(data=request.POST)
        if form.is_valid():
            form.save(request)
            messages.success(request, _('Your comment has been posted.'))
            return redirect(next_url)

        messages.error(request, '\n'.join(['{}: {}'.format(field.label, error) for field in form for error in field.errors]))
        return redirect(next_url)
