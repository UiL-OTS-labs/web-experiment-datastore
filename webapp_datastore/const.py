from django.conf import settings

def constants(request):
    """add useful constants to every response context"""
    return dict(
        webexp_host=settings.WEBEXPERIMENT_HOST,
        webexp_webdav_host=settings.WEBEXPERIMENT_WEBDAV_HOST
    )
