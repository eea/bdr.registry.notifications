from django.urls import include, path
from django.contrib.auth import views as auth_views

from . import views

accounts_patterns = [
    path('login/', auth_views.LoginView.as_view(template_name='notifications/login.html'),
        name='login'),
    path('logout/',
        views.logout_view,
        name='logout'),
]

cycle_patterns = [
    path('add/',
        views.CycleAdd.as_view(),
        name='add'),

    path('<int:pk>/view/',
        views.CycleDetailView.as_view(),
        name='view'),

    path('<int:pk>/stage/add/',
        views.StageAdd.as_view(),
        name='stage_add'),
]

email_template_patterns = [
    path('<int:pk>/view/',
        views.CycleEmailTemplateView.as_view(),
        name='view'),
    path('<int:pk>/edit/',
        views.CycleEmailTemplateEdit.as_view(),
        name='edit'),
    path('<int:pk>/trigger/',
        views.CycleEmailTemplateTrigger.as_view(),
        name='trigger'),
    path('<int:pk>/json/',
        views.CycleEmailTemplateTriggerNotificationsJson.as_view(),
        name='json'),
    path('<int:pk>/test/',
        views.CycleEmailTemplateTest.as_view(),
        name='test'),
    path('<int:pk>/sent-notifications/<int:pk_company>/',
        views.ViewSentNotificationForCompany.as_view(),
        name='sent_notifications'),
]

app_name = 'notifications'

urlpatterns = [
    path('accounts/',
        include((accounts_patterns, app_name), namespace='accounts')),

    path('cycle/',
        include((cycle_patterns, app_name), namespace='cycle')),

    path('template/',
        include((email_template_patterns, app_name), namespace='template')),

    path('',
        views.DashboardView.as_view(),
        name='dashboard'),

    path('companies/',
        views.CompaniesView.as_view(),
        name='companies'),

    path('persons/',
        views.PersonsView.as_view(),
        name='persons'),

    path('crashme/',
        views.Crashme.as_view(),
        name='crashme')
]
