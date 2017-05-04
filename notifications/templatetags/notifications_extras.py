from django import template

from notifications.models import Company


register = template.Library()


@register.simple_tag
def get_group_companies(group):
    """ Returns all companies for the given group
    """
    return Company.objects.filter(group=group)
