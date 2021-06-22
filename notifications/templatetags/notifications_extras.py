import requests
from requests.auth import HTTPBasicAuth

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def get_group_companies(view, group_code):
    return view.get_companies_by_group(group_code)


@register.simple_tag
def get_sidebar(user):
    params = {"username": user.username}
    response = requests.get(
        settings.BDR_SIDEMENU_URL,
        params=params,
        auth=HTTPBasicAuth(settings.BDR_API_USER, settings.BDR_API_PASSWORD),
    )
    if response.status_code == 200:
        return mark_safe(response.text)
