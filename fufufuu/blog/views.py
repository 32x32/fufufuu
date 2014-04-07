from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _

from fufufuu.blog.forms import BlogEntryForm
from fufufuu.blog.models import BlogEntry
from fufufuu.comment.models import Comment
from fufufuu.core.utils import paginate
from fufufuu.core.views import TemplateView
from fufufuu.staff.views import StaffTemplateView


class BlogEntryListView(TemplateView):

    page_size = 10
    template_name = 'blog/blog-entry-list.html'

    def get(self, request):
        blog_entry_list = BlogEntry.objects.select_related('created_by').order_by('-created_on')
        blog_entry_list = paginate(blog_entry_list, self.page_size, request.GET.get('p'))

        id_list = [b.id for b in blog_entry_list]
        comment_count_list = Comment.objects\
            .filter(content_type=ContentType.objects.get_for_model(BlogEntry), object_id__in=id_list)\
            .values('object_id')\
            .annotate(count=Count('object_id'))
        comment_count_dict = dict([(c['object_id'], c['count']) for c in comment_count_list])

        for blog_entry in blog_entry_list:
            blog_entry.comment_count = comment_count_dict.get(blog_entry.id, 0)

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
