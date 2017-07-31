from django.urls import reverse
from django.views import generic

from notifications.models import STAGE_CLOSED, Cycle, CompaniesGroup
from notifications.views.breadcrumb import NotificationsBaseView, Breadcrumb


class DashboardView(NotificationsBaseView, generic.ListView):
    model = Cycle
    template_name = 'notifications/dashboard.html'
    context_object_name = 'items'

    def get_queryset(self):
        return Cycle.objects.order_by('-year')

    def can_initiate_new_cycle(self):
        r = True
        cycles = Cycle.objects.order_by('-year')
        if len(cycles) > 0:
            last_cycle = cycles[0]
            if last_cycle.stage.pk != STAGE_CLOSED:
                r = False
        return r


class CompaniesView(NotificationsBaseView, generic.TemplateView):
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
        return CompaniesGroup.objects.all()


class PersonsView(NotificationsBaseView, generic.TemplateView):
    template_name = 'notifications/persons.html'
    page_bdr = 1
    page_fgas = 1

    def dispatch(self, request, *args, **kwargs):
        # get current page from request
        self.page_bdr = request.GET.get('page_bdr', 1)
        self.page_fgas = request.GET.get('page_fgas', 1)

        return super(PersonsView, self).dispatch(request, *args, **kwargs)

    def get_bdr(self):
        return Person.objects.filter(
            company__group__code=BDR_GROUP_CODE)

    def get_fgas(self):
        return Person.objects.filter(
            company__group__code__in=FGASES_GROUP_CODE)

    def breadcrumbs(self):
        breadcrumbs = super(PersonsView, self).breadcrumbs()
        breadcrumbs.extend([
            Breadcrumb(
                reverse('notifications:persons'),
                'Persons'),
        ])
        return breadcrumbs
