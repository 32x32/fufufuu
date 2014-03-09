def email_admin_limit(record):
    """
    limit to 1 email sent to admin per minute
    """

    from django.core.cache import cache

    CACHE_KEY = 'email_admin_limit'

    if cache.get(CACHE_KEY, False):
        return False

    cache.set(CACHE_KEY, True)
    return True
