from django.http.request import QueryDict
from fufufuu.core.languages import Language


def exclude_keys(value, *exclude):
    """
    getquerydict returns a mutable copy of the querydict with exclude values
    removed.
    """

    if not isinstance(value, QueryDict):
        raise RuntimeError("getquerydict should be used with QueryDict instances only (e.g. request.GET)")

    value = value.copy()
    for key in exclude:
        if key in value: del value[key]
    return value


def startswith(value, s):
    """
    returns if value starts with s, used for menu highlighting
    """

    if not value: return False
    return value.find(s) == 0


def language_display(lang):
    return Language.choices_dict[lang]
