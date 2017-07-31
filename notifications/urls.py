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

    url(r'^(?P<pk>\d+)/edit/$',
        views.CycleEdit.as_view(),
        name='edit'),

    url(r'^(?P<pk>\d+)/trigger/$',
        views.CycleTrigger.as_view(),
        name='trigger'),
]

email_template_patterns = [
    url(r'^(?P<pk>\d+)/view/$',
        views.CycleEmailTemplateView.as_view(),
        name='view'),
    url(r'^(?P<pk>\d+)/edit/$',
        views.CycleEmailTemplateEdit.as_view(),
        name='edit'),
    url(r'^(?P<pk>\d+)/trigger/$',
        views.CycleEmailTemplateTriggerDetail.as_view(),
        name='trigger'),
    url(r'^(?P<pk>\d+)/test/$',
        views.CycleEmailTemplateTest.as_view(),
        name='test'),
]

actions_patterns = [

    url(r'^$',
        views.ActionsView.as_view(),
        name='home'),
    url(r'^fgases$',
        views.ActionsFGasesView.as_view(),
        name='fgases'),
    url(r'^bdr$',
        views.ActionsBDRView.as_view(),
        name='bdr'),
]

app_name = 'notifications'

urlpatterns = [
    url(r'^accounts/',
        include(accounts_patterns, namespace='accounts')),

    url(r'^cycle/',
        include(cycle_patterns, namespace='cycle')),

    url(r'^template/',
        include(email_template_patterns, namespace='template')),

    url(r'^actions/',
        include(actions_patterns, namespace='actions')),

    url(r'^$',
        views.DashboardView.as_view(),
        name='dashboard'),

    url(r'^companies/$',
        views.CompaniesView.as_view(),
        name='companies'),

    url(r'^persons/$',
        views.PersonsView.as_view(),
        name='persons'),
]
