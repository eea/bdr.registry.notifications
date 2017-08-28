from braces import views as braces_views
from collections import namedtuple
from django.conf import settings
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.urls import reverse_lazy

Breadcrumb = namedtuple('Breadcrumb', ['url', 'title'])


class NotificationsBaseView(braces_views.StaffuserRequiredMixin,
                            SuccessMessageMixin):

    login_url = reverse_lazy('notifications:accounts:login')

    def breadcrumbs(self):
        return [
            Breadcrumb(settings.BDR_SERVER_URL, 'BDR'),
            Breadcrumb(reverse('notifications:dashboard'),
                       'Registry Notifications')
        ]
