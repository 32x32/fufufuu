from django.utils.translation import get_language
from fufufuu.tag.models import Tag, TagAlias


def get_or_create_tag_by_name_or_alias(tag_type, name, user):
    tag_list = Tag.objects.filter(tag_type=tag_type, name=name)[:1]
    if tag_list:
        return tag_list[0]

    tag_alias_list = TagAlias.objects.select_related('tag').filter(tag__tag_type=tag_type, language=get_language(), name=name)[:1]
    if tag_alias_list:
        return tag_alias_list[0].tag

    tag = Tag(tag_type=tag_type, name=name)
    tag.save(updated_by=user)
    return tag
