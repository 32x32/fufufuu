import subprocess
from django import forms
from django.utils.translation import ugettext as _
from fufufuu.settings import MD2HTML


class BlankLabelSuffixMixin(object):

    def __init__(self, *args, **kwargs):
        if 'label_suffix' not in kwargs:
            kwargs['label_suffix'] = ''
        super().__init__(*args, **kwargs)


def convert_markdown(markdown):
    """
    returns the markdown converted into HTML
    """

    markdown = markdown.strip()
    try:
        p = subprocess.Popen([MD2HTML], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = p.communicate(markdown.encode('utf-8'), timeout=1)
        if err is not None:
            raise forms.ValidationError(_('An error occurred while processing the description.'))
        html = out.decode('utf-8').strip()
    except subprocess.TimeoutExpired:
        raise forms.ValidationError(_('Timeout while processing the description.'))
    except Exception:
        raise forms.ValidationError(_('An unknown error occurred while processing the description.'))
    return html
