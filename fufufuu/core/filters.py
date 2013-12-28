from django.http.request import QueryDict


def getparams(value, exclude=None):
    """
    getparams returns the url get string for value (instance of QueryDict). E.g.

        &p=1&authors=test-author

    exclude should be comma separated names of parameters to exclude from
    urlencode. E.g.

        request.GET|getparams:"p"
        request.GET|getparams:"p,q"
    """

    if not isinstance(value, QueryDict):
        raise RuntimeError("getparams should be used on QueryDict only (e.g. request.GET)")
    if exclude:
        value = value.copy()
        for key in exclude.split(','):
            if key in value: del value[key]
    return value.urlencode()


def startswith(value, s):
    """
    returns if value starts with s, used for menu highlighting
    """

    if not value: return False
    return value.find(s) == 0
