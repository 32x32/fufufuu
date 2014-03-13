from PIL import Image
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, Page
from django.shortcuts import _get_queryset
from django.utils import timezone
from django.utils.text import slugify as django_slugify
import markdown
from unidecode import unidecode


IMAGE_FORMAT_EXTENSION = {
    'PNG': 'png',
    'JPEG': 'jpg',
}


def slugify(s):
    """
    Slugify based on django's slugify except uses unidecode to work with
    non-ascii characters.
    """

    return django_slugify(unidecode(s))


def paginate(object_list, page_size, page_num):
    """
    Takes an object_list, page_size, page_num and paginates the object list.
    """

    page_num = page_num or 1
    paginator = Paginator(object_list, page_size)

    try:
        page = paginator.page(page_num)
    except PageNotAnInteger:
        return Page([], 1, paginator)
    except EmptyPage:
        return Page([], 1, paginator)

    return page


def yesterday():
    """
    Returns a datetime object representing yesterday.
    """

    return timezone.now() - timezone.timedelta(days=1)


def get_image_extension(f):
    """
    Returns the file's image format if it is in IMAGE_FORMAT_EXTENSION,
    otherwise return 'unknown'.
    """

    f.seek(0)
    im = Image.open(f)
    return IMAGE_FORMAT_EXTENSION.get(im.format, 'unknown')



def get_object_or_none(klass, *args, **kwargs):
    """
    This function is equivalent to django's get_object_or_404. None is returned
    instead of a 404 exception being raised in the case where the object is
    not found.
    """

    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None


def get_ip_address(request):
    """
    Returns the user's ip address from the request
    """

    ip_address = request.META.get('REMOTE_ADDR', '')
    ip_address = ip_address[:200]
    return ip_address


def convert_markdown(markdown_text):
    """
    returns the markdown converted into HTML
    """

    markdown_text = markdown_text.strip()
    if not markdown_text:
        return ''

    html = markdown.markdown(markdown_text, safe_mode='escape')
    return html
