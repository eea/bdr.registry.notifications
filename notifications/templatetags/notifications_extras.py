from django import template


register = template.Library()


@register.simple_tag
def get_group_companies(view, group_code):
    return view.get_companies_by_group(group_code)
