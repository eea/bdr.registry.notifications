from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic

from notifications.forms import CycleAddForm
from notifications.forms import StageAddForm
from notifications.models import Cycle, CycleEmailTemplate
from notifications.models import Stage
from notifications.views.breadcrumb import NotificationsBaseView, Breadcrumb


class CycleAdd(NotificationsBaseView, generic.CreateView):
    model = Cycle
    form_class = CycleAddForm
    template_name = "notifications/cycle/add.html"
    success_message = "Reporting cycle added successfully"

    def get_success_url(self):
        return reverse("notifications:dashboard")

    def breadcrumbs(self):
        breadcrumbs = super(CycleAdd, self).breadcrumbs()
        breadcrumbs.extend(
            [
                Breadcrumb("", "Add reporting cycle"),
            ]
        )
        return breadcrumbs


class StageAdd(NotificationsBaseView, generic.CreateView):
    model = Stage
    form_class = StageAddForm
    template_name = "notifications/stage/add.html"
    success_message = "Notification added successfully"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["cycle"] = self.cycle
        return context

    def get(self, request, *args, **kwargs):
        self.cycle = get_object_or_404(Cycle, pk=kwargs["pk"])
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.cycle = get_object_or_404(Cycle, pk=kwargs["pk"])
        return super().post(request, *args, **kwargs)

    def get_initial(self):
        return {"cycle": self.cycle}

    def get_success_url(self):
        return reverse("notifications:cycle:view", kwargs={"pk": self.cycle.pk})

    def breadcrumbs(self):
        breadcrumbs = super(StageAdd, self).breadcrumbs()
        breadcrumbs.extend(
            [
                Breadcrumb(
                    reverse("notifications:cycle:view", kwargs={"pk": self.cycle.pk}),
                    "Reporting cycle for {}".format(self.cycle),
                ),
                Breadcrumb("", "Add notification"),
            ]
        )
        return breadcrumbs


class CycleDetailView(NotificationsBaseView, generic.DetailView):
    model = Cycle
    template_name = "notifications/cycle/view.html"
    context_object_name = "cycle"

    def breadcrumbs(self):
        cycle = self.object
        breadcrumbs = super(CycleDetailView, self).breadcrumbs()
        breadcrumbs.extend(
            [
                Breadcrumb(
                    reverse("notifications:cycle:view", kwargs={"pk": cycle.pk}),
                    "Reporting cycle for {}".format(cycle),
                ),
            ]
        )
        return breadcrumbs

    def get_context_data(self, **kwargs):
        context = super(CycleDetailView, self).get_context_data(**kwargs)
        context["templates"] = (
            CycleEmailTemplate.objects.filter(stage__cycle=self.object)
            .order_by("group")
            .prefetch_related("group", "stage")
        )
        return context
