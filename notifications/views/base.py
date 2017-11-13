from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse
from django.views import generic

from notifications import BDR_GROUP_CODE, ECR_GROUP_CODES
from notifications.models import Cycle, CompaniesGroup, Person, Company
from notifications.views.breadcrumb import NotificationsBaseView, Breadcrumb


class PaginatedDataViewBase:
    PER_PAGE = 5

    def get_current_page(self, data, page):
        paginator = Paginator(data, self.PER_PAGE)
        try:
            return paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            return paginator.page(1)
        except EmptyPage:
            # If page is out of range deliver last page of results.
            return paginator.page(paginator.num_pages)


class DashboardView(NotificationsBaseView, generic.ListView):
    model = Cycle
    template_name = 'notifications/dashboard.html'
    context_object_name = 'items'

    def get_queryset(self):
        return Cycle.objects.order_by('-year').prefetch_related('stage')

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['model'] = self.model
        return context


class CompaniesView(NotificationsBaseView, PaginatedDataViewBase,
                    generic.TemplateView):
    template_name = 'notifications/companies.html'

    def breadcrumbs(self):
        breadcrumbs = super(CompaniesView, self).breadcrumbs()
        breadcrumbs.extend([
            Breadcrumb(
                reverse('notifications:companies'),
                'Companies'),
        ])
        return breadcrumbs

    def get_groups(self):
        return CompaniesGroup.objects.values('pk', 'code', 'title')

    def get_companies_by_group(self, group):
        return Company.objects.filter(
            group__code=group).distinct().order_by("name")


class PersonsView(NotificationsBaseView, PaginatedDataViewBase,
                  generic.TemplateView):
    template_name = 'notifications/persons.html'

    def get_bdr(self):
        page_bdr = self.request.GET.get('page_bdr', 1)
        return self.get_current_page(
            data=Person.objects
                 .filter(company__group__code=BDR_GROUP_CODE)
                 .prefetch_related('company')
                 .order_by('name')
                 .distinct(),
            page=page_bdr
        )

    def get_ecr(self):
        page_ecr = self.request.GET.get('page_ecr', 1)
        return self.get_current_page(
            data=Person.objects
                .filter(company__group__code__in=ECR_GROUP_CODES)
                .prefetch_related('company')
                .order_by('name')
                .distinct(),
            page=page_ecr
        )

    def breadcrumbs(self):
        breadcrumbs = super(PersonsView, self).breadcrumbs()
        breadcrumbs.extend([
            Breadcrumb(
                reverse('notifications:persons'),
                'Persons'),
        ])
        return breadcrumbs
