from .base import *
from .cycle import *
from .emailtemplate import *
from notifications.context import sentry

from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import redirect
from django.template import TemplateDoesNotExist, loader


def logout_view(request):
    logout(request)
    messages.add_message(request, messages.INFO, "You have been logged out.")
    return redirect("notifications:dashboard")


class Crashme(View):
    def get(self, request):
        if request.user.is_superuser:
            raise RuntimeError("Crashing as requested")
        else:
            return HttpResponse("Must be administrator")


def handler500(request, template_name="500.html"):
    try:
        template = loader.get_template(template_name)
    except TemplateDoesNotExist:
        return HttpResponseServerError(
            "<h1>Server Error (500)</h1>", content_type="text/html"
        )

    return HttpResponseServerError(template.render(context=sentry(request)))
