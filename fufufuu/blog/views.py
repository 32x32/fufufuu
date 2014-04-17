from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _

from fufufuu.blog.forms import BlogEntryForm
from fufufuu.blog.models import BlogEntry
from fufufuu.comment.utils import attach_comment_count
from fufufuu.core.utils import paginate
from fufufuu.core.views import TemplateView
from fufufuu.staff.views import StaffTemplateView


class BlogEntryListView(TemplateView):

    page_size = 10
    template_name = 'blog/blog-entry-list.html'

    def get(self, request):
        blog_entry_list = BlogEntry.objects.select_related('created_by').order_by('-created_on')
        blog_entry_list = paginate(blog_entry_list, self.page_size, request.GET.get('p'))
        attach_comment_count(blog_entry_list)
        return self.render_to_response({
            'blog_entry_list': blog_entry_list,
        })


class BlogEntryView(TemplateView):

    template_name = 'blog/blog-entry.html'

    def get(self, request, id, slug):
        blog_entry = get_object_or_404(BlogEntry, id=id)
        return self.render_to_response({
            'blog_entry': blog_entry,
        })


#-------------------------------------------------------------------------------

class BlogEntryEditView(StaffTemplateView):

    template_name = 'blog/blog-entry-edit.html'

    @staticmethod
    def get_blog_entry(id):
        if id:
            blog_entry = get_object_or_404(BlogEntry, id=id)
        else:
            blog_entry = None
        return blog_entry

    def get(self, request, id=None, slug=None):
        blog_entry = self.get_blog_entry(id)
        return self.render_to_response({
            'blog_entry': blog_entry,
            'form': BlogEntryForm(instance=blog_entry),
        })

    def post(self, request, id=None, slug=None):
        blog_entry = self.get_blog_entry(id)
        form = BlogEntryForm(instance=blog_entry, data=request.POST)
        if form.is_valid():
            blog_entry = form.save(request.user)
            messages.success(request, _('The post has been updated.'))
            return redirect('blog.entry.edit', id=blog_entry.id, slug=blog_entry.slug)

        return self.render_to_response({
            'blog_entry': blog_entry,
            'form': form,
        })
