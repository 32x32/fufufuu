import re

from PIL import Image
from django import forms
from django.core.mail import send_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, Page
from django.shortcuts import _get_queryset
from django.utils import timezone
from django.utils.text import slugify as django_slugify
from django.utils.translation import ugettext_lazy as _
import markdown
from unidecode import unidecode

from fufufuu.settings import DEBUG, ADMINS, DEFAULT_FROM_EMAIL, MAX_IMAGE_FILE_SIZE, SUPPORTED_IMAGE_FORMATS, MAX_IMAGE_DIMENSION


IMAGE_FORMAT_EXTENSION = {
    'PNG': 'png',
    'JPEG': 'jpg',
}

class MarkdownExtension(markdown.Extension):
    """
    Taken from http://blog.magicalhobo.com/2011/05/05/disabling-images-in-python-markdown/
    """

    def extendMarkdown(self, md, md_globals):
        del md.inlinePatterns['image_link']
        del md.inlinePatterns['image_reference']


markdown_extension = MarkdownExtension()


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
    Returns the user's ip address from the request.
    """

    ip_address = request.META.get('REMOTE_ADDR', '')
    ip_address = ip_address[:200]
    return ip_address


def convert_markdown(markdown_text):
    """
    returns the markdown converted into HTML.
    """

    markdown_text = markdown_text.strip()
    if not markdown_text:
        return ''

    html = markdown.markdown(markdown_text, [markdown_extension], safe_mode='escape').strip()
    return html


def send_email_alert(subject, message, fail_silently=False):
    """
    Send an email to ADMINS.
    """

    if DEBUG: return

    send_mail(
        subject=subject,
        message=message,
        from_email=DEFAULT_FROM_EMAIL,
        recipient_list=[email for _, email in ADMINS],
        fail_silently=fail_silently,
    )


def natural_sort(l, key_attr):
    """
    Sort a list in the way humans expect.
    http://stackoverflow.com/questions/4836710/does-python-have-a-built-in-function-for-string-natural-sort
    """

    convert = lambda text: int(text) if text.isdigit() else text.lower()
    key = lambda item: [convert(c) for c in re.split('([0-9]+)', getattr(item, key_attr))]
    return sorted(l, key=key)


def validate_image(f):
    """
    This method validates an image file that a user uploads.
    """

    if f.size > MAX_IMAGE_FILE_SIZE:
        raise forms.ValidationError(_('{} is over 10MB in size.').format(f.name))

    try:
        Image.open(f).verify()
        f.seek(0)
    except Exception as e:
        raise forms.ValidationError(_('{} failed to verify as an image file.').format(f.name))

    im = Image.open(f)

    if im.format not in SUPPORTED_IMAGE_FORMATS:
        raise forms.ValidationError(_('{} is not a supported image type.').format(f.name))

    if im.size[0] > MAX_IMAGE_DIMENSION[0] or im.size[1] > MAX_IMAGE_DIMENSION[1]:
        raise forms.ValidationError(_('{} is larger than 8000x8000 pixels.').format(f.name))

    return f
