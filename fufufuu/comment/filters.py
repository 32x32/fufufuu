from fufufuu.comment.forms import CommentForm
from fufufuu.comment.models import Comment


def get_comment_list(content_object):
    return Comment.objects.filter_content_object(content_object).select_related('created_by').order_by('-created_on')

def get_comment_form(content_object):
    return CommentForm(content_object)
