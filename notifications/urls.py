from django.conf.urls import include, url
from django.contrib.auth import views as auth_views


from . import views


app_name = 'notifications'
urlpatterns = [
    url(r'^accounts/login/?$',
        auth_views.login, {'template_name': 'notifications/login.html'},
        name='login'),
    url(r'^accounts/logout/?$',
        views.logout_view,
        name='logout'),

    url(r'^$',
        views.DashboardView.as_view(),
        name='dashboard'),

    url(r'^cycle/add/?$',
        views.CycleAdd.as_view(),
        name='cycle_add'),
    url(r'^cycle/(?P<pk>\d+)/view/$',
        views.CycleView.as_view(),
        name='cycle_view'),
    url(r'^cycle/(?P<pk>\d+)/edit/$',
        views.CycleEdit.as_view(),
        name='cycle_edit'),
    url(r'^cycle/(?P<pk>\d+)/trigger/$',
        views.CycleTrigger.as_view(),
        name='cycle_trigger'),

    url(r'^emailtemplate/(?P<pk>\d+)/view/$',
        views.CycleEmailTemplateView.as_view(),
        name='emailtemplate_view'),
    url(r'^emailtemplate/(?P<pk>\d+)/edit/$',
        views.CycleEmailTemplateEdit.as_view(),
        name='emailtemplate_edit'),
    url(r'^emailtemplate/(?P<pk>\d+)/trigger/$',
        views.CycleEmailTemplateTrigger.as_view(),
        name='emailtemplate_trigger'),
    url(r'^emailtemplate/(?P<pk>\d+)/test/$',
        views.CycleEmailTemplateTest.as_view(),
        name='emailtemplate_test'),
]
