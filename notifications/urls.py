from django.conf.urls import include, url
from django.contrib.auth import views as auth_views

from . import views

accounts_patterns = [
    url(r'^login/?$',
        auth_views.login, {'template_name': 'notifications/login.html'},
        name='login'),

    url(r'^logout/?$',
        views.logout_view,
        name='logout'),
]

cycle_patterns = [
    url(r'^add/?$',
        views.CycleAdd.as_view(),
        name='add'),

    url(r'^(?P<pk>\d+)/view/$',
        views.CycleDetailView.as_view(),
        name='view'),
]

email_template_patterns = [
    url(r'^(?P<pk>\d+)/view/$',
        views.CycleEmailTemplateView.as_view(),
        name='view'),
    url(r'^(?P<pk>\d+)/edit/$',
        views.CycleEmailTemplateEdit.as_view(),
        name='edit'),
    url(r'^(?P<pk>\d+)/trigger/$',
        views.CycleEmailTemplateTrigger.as_view(),
        name='trigger'),
    url(r'^(?P<pk>\d+)/test/$',
        views.CycleEmailTemplateTest.as_view(),
        name='test'),
    url(r'^(?P<pk>\d+)/company/(?P<pk_company>\d+)/person/(?P<pk_person>\d+)/$',
        views.ResendEmail.as_view(),
        name='resend'),
    url(r'^(?P<pk>\d+)/sent-notifications/(?P<pk_company>\d+)/$',
        views.ViewSentNotificationForCompany.as_view(),
        name='sent_notifications'),
]

app_name = 'notifications'

urlpatterns = [
    url(r'^accounts/',
        include(accounts_patterns, namespace='accounts')),

    url(r'^cycle/',
        include(cycle_patterns, namespace='cycle')),

    url(r'^template/',
        include(email_template_patterns, namespace='template')),

    url(r'^$',
        views.DashboardView.as_view(),
        name='dashboard'),

    url(r'^companies/$',
        views.CompaniesView.as_view(),
        name='companies'),

    url(r'^persons/$',
        views.PersonsView.as_view(),
        name='persons'),

    url(r'^crashme/$',
        views.Crashme.as_view(),
        name='crashme')
]
