from getenv import env


def use_sidemenu(request):
    return {
        'USE_SIDEMENU': env('USE_SIDEMENU')
    }

def sentry(request):
    sentry_id = ''
    if hasattr(request, 'sentry'):
        sentry_id = request.sentry['id']
    return {
        'sentry_id': sentry_id,
        'sentry_public_id': env('SENTRY_PUBLIC_DSN', ''),
    }


def debug(request):
    return {
        'debug': env('DEBUG')
    }

def utils(request):
    return {
        'bcc_email_address': env('BCC', ''),
        'USE_ZOPE_LOGIN': env('USE_ZOPE_LOGIN', ''),
        'BDR_SERVER_URL': env('BDR_SERVER_URL', ''),
    }
