from django.contrib import messages

from fufufuu.core.enums import SiteSettingKey
from fufufuu.core.models import SiteSetting
from fufufuu.settings import RESOURCE_VERSION


def resource_version(request):
    return {
        'RESOURCE_VERSION': RESOURCE_VERSION
    }


def site_settings(request):
    SITE_SETTINGS = SiteSetting.as_dict()

    announcement = SITE_SETTINGS.get(SiteSettingKey.ANNOUNCEMENT)
    if announcement: messages.info(request, announcement)

    return {
        'SITE_SETTINGS': SITE_SETTINGS,
    }
