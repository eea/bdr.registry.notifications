from django.conf import settings
from django.core.management import call_command
from django.http import HttpResponseForbidden, JsonResponse
from django.views import View
from notifications.views.breadcrumb import NotificationsBaseView


class FetchView(View):
    def get(self, request, *args, **kwargs):
        # Check for authorization token in request headers
        auth_token = request.headers.get("Authorization")
        if auth_token != "Bearer {}".format(settings.NOTIFICATIONS_TOKEN):
            return HttpResponseForbidden("Authorization token is missing")

        bdr_result = call_command("fetch_bdr")
        ecr_result = call_command("fetch_ecr")
        return JsonResponse(
            {
                "bdr": bdr_result,
                "ecr": ecr_result,
            }
        )
