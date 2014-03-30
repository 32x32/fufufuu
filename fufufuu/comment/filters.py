from fufufuu.comment.models import Comment


def comment_list(content_object):
    return Comment.objects.filter_content_object(content_object).select_related('created_by').order_by('-created_on')
