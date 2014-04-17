from django.contrib.contenttypes.models import ContentType
from django.db.models.aggregates import Count
from fufufuu.comment.models import Comment


def attach_comment_count(object_list):
    if len(object_list) == 0:
        return

    comment_count_list = Comment.objects \
        .filter(content_type=ContentType.objects.get_for_model(model=object_list[0])) \
        .filter(object_id__in=[o.id for o in object_list]) \
        .values('object_id') \
        .annotate(count=Count('object_id'))

    comment_count_dict = dict([(c['object_id'], c['count']) for c in comment_count_list])

    for obj in object_list:
        obj.comment_count = comment_count_dict.get(obj.id, 0)
