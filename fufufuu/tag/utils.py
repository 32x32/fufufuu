from fufufuu.tag.models import Tag, TagAlias


def get_or_create_tag_by_name_or_alias(tag_type, name, user):
    try:
        return Tag.objects.get(tag_type=tag_type, name=name)
    except Tag.DoesNotExist:
        pass

    # search in TagAlias and return the first one if found
    tag_alias_list = TagAlias.objects.select_related('tag').filter(tag__tag_type=tag_type, name=name)
    if tag_alias_list:
        return tag_alias_list[0].tag

    # create a new Tag object
    tag = Tag(tag_type=tag_type, name=name)
    tag.save(updated_by=user)
    return tag
