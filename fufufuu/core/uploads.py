import os


def user_avatar_upload_to(instance, filename):
    return os.sep.join(['avatar', filename])


def manga_cover_upload_to(instance, filename):
    return os.sep.join(['cover', filename])


def manga_archive_upload_to(instance, filename):
    return os.sep.join(['download', filename])


def manga_page_upload_to(instance, filename):
    return os.sep.join(['manga', filename])


def tag_image_upload_to(instance, filename):
    return os.sep.join(['tag', filename])

