from fufufuu.tag.models import TagData, Tag


def get_or_create_tag_data(tag_type, language, name, user):
    try:
        tag_data = TagData.objects.get(language=language, name=name, tag__tag_type=tag_type)
    except TagData.DoesNotExist:
        tag = Tag.objects.create(tag_type=tag_type)
        tag_data = TagData(tag=tag, language=language, name=name)
        tag_data.save(updated_by=user)

    while tag_data.alias: tag_data = tag_data.alias
    return tag_data
