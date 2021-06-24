# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib import admin
from simple_history import admin as admin_simple_history

from .models import (
    Stage,
    CompaniesGroup,
    Company,
    Person,
    Cycle,
    CycleEmailTemplate,
    CycleNotification,
)


class StageAdmin(admin.ModelAdmin):
    list_display = ("cycle", "title")
    ordering = ("cycle",)


class CompaniesGroupAdmin(admin.ModelAdmin):
    list_display = ("title", "code", "count_emailtemplates")
    prepopulated_fields = {"code": ("title",)}


class CompanyAdmin(admin.ModelAdmin):
    list_display = ("external_id", "name", "vat", "country", "group")
    list_filter = ("group",)
    search_fields = ("id", "external_id", "name", "vat", "country")

    def has_add_permission(self, request):
        return settings.ALLOW_EDITING_COMPANIES

    def has_delete_permission(self, request, obj=None):
        return settings.ALLOW_EDITING_COMPANIES


class PersonAdmin(admin.ModelAdmin):
    list_display = ("username", "name", "email", "admin_company")
    list_filter = ("company__group",)
    search_fields = ("username", "name", "email", "company__name")

    def has_add_permission(self, request):
        return settings.ALLOW_EDITING_COMPANIES

    def has_delete_permission(self, request, obj=None):
        return settings.ALLOW_EDITING_COMPANIES


class CycleAdmin(admin_simple_history.SimpleHistoryAdmin):
    exclude = ("year",)
    list_display = ("year", "closing_date")
    ordering = ("-year",)

    def save_model(self, request, obj, form, change):
        """When a new reporting cycle is created, all the necessary
        notifications are autmatically created.
        """
        super(CycleAdmin, self).save_model(request, obj, form, change)
        if not change:
            obj.create_cycle_templates()


class CycleEmailTemplateAdmin(admin_simple_history.SimpleHistoryAdmin):
    list_display = ("stage", "is_triggered")
    list_filter = ()
    ordering = ()


class CycleNotificationAdmin(admin.ModelAdmin):
    list_display = ("cycle", "group", "stage", "email", "sent_date")
    list_filter = ()

    readonly_fields = []

    def get_readonly_fields(self, request, obj=None):
        return (
            list(self.readonly_fields)
            + [field.name for field in obj._meta.fields]
            + [field.name for field in obj._meta.many_to_many]
        )

    def has_add_permission(self, request):
        return False


admin.site.register(Stage, StageAdmin)
admin.site.register(CompaniesGroup, CompaniesGroupAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Cycle, CycleAdmin)
admin.site.register(CycleEmailTemplate, CycleEmailTemplateAdmin)
admin.site.register(CycleNotification, CycleNotificationAdmin)
