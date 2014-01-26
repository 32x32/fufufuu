import os
from django.core.cache import cache
from django.http.response import Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils.http import base36_to_int
from django.views.generic.base import View
from django.views.static import serve
from fufufuu.image.enums import ImageKeyType
from fufufuu.image.models import Image, get_cache_key
from fufufuu.settings import DEBUG, BASE_DIR


class ImageView(View):
    """
    This view should be used in conjunction with nginx's try_files.

    If nginx is unable to find the image file, this view can take care of
    regenerating the lost image file.
    """

    def get(self, request, key_type, key_id):
        key_type = key_type.upper()
        if key_type not in ImageKeyType.choices_dict.keys():
            raise Http404

        try:
            key_id = base36_to_int(key_id)
        except ValueError:
            raise Http404

        image = get_object_or_404(Image, key_type=key_type, key_id=key_id)
        if not os.path.exists(image.file.path):
            image.regenerate()
            cache_key = get_cache_key(key_type, key_id)
            cache.set(cache_key, image.file.url)

        if DEBUG:
            return serve(request, image.file.url, document_root=BASE_DIR)

        return redirect(image.file.url)
