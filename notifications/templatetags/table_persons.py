from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger

from django import template

register = template.Library()


def paginate(items, page, per_page):
    paginator = Paginator(items, per_page)

    try:
        return paginator.page(page)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)


@register.inclusion_tag('notifications/table_persons.html')
def table_persons(items, page, req_page, per_page=25):
    return dict(
        items=paginate(items, page, per_page),
        req_page=req_page
    )
