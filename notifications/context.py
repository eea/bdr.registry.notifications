from getenv import env


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
