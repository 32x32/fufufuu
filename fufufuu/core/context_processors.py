from fufufuu.settings import RESOURCE_VERSION


def resource_version(request):
    return {
        'RESOURCE_VERSION': RESOURCE_VERSION
    }
