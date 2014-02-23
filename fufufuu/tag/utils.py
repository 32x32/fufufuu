from django.utils.translation import get_language
from fufufuu.tag.models import Tag, TagAlias


def get_or_create_tag_by_name_or_alias(tag_type, name, user):
    try:
        return Tag.objects.get(tag_type=tag_type, name=name)
    except Tag.DoesNotExist:
        pass

    try:
        return TagAlias.objects.select_related('tag').get(tag__tag_type=tag_type, language=get_language(), name=name).tag
    except TagAlias.DoesNotExist:
        pass

    tag = Tag(tag_type=tag_type, name=name)
    tag.save(updated_by=user)
    return tag
