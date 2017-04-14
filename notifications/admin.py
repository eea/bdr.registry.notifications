# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from simple_history import admin as admin_simple_history

from .models import (Stage, CompaniesGroup, EmailTemplate,
                     Cycle, CycleEmailTemplate, CycleNotification)


class StageAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'can_edit', 'can_trigger')
    prepopulated_fields = {'code': ('title',)}
    ordering = ('id',)


class CompaniesGroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'count_emailtemplates')
    prepopulated_fields = {'code': ('title',)}


class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('group', 'stage', 'subject')
    list_filter = ('group', 'stage')
    ordering = ('stage',)


class CycleAdmin(admin_simple_history.SimpleHistoryAdmin):
    exclude = ('year',)
    list_display = ('year', 'stage', 'closing_date')
    ordering = ('-year',)

    def save_model(self, request, obj, form, change):
        """ When a new reporting cycle is created, all the necessary
            notifications are autmatically created.
        """
        super(CycleAdmin, self).save_model(request, obj, form, change)
        if not change:
            obj.create_cycle_templates()


class CycleEmailTemplateAdmin(admin_simple_history.SimpleHistoryAdmin):
    list_display = ('cycle', 'group', 'stage', 'is_triggered')
    list_filter = ('cycle', 'emailtemplate__group', 'emailtemplate__stage')
    ordering = ('cycle', 'emailtemplate__stage',)


class CycleNotificationAdmin(admin.ModelAdmin):
    list_display = ('cycle', 'group', 'stage', 'email', 'sent_date')
    list_filter = ('emailtemplate__cycle',
                   'emailtemplate__emailtemplate__group',
                   'emailtemplate__emailtemplate__stage')

    readonly_fields = []

    def get_readonly_fields(self, request, obj=None):
        return list(self.readonly_fields) + \
               [field.name for field in obj._meta.fields] + \
               [field.name for field in obj._meta.many_to_many]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Stage, StageAdmin)
admin.site.register(CompaniesGroup, CompaniesGroupAdmin)
admin.site.register(EmailTemplate, EmailTemplateAdmin)
admin.site.register(Cycle, CycleAdmin)
admin.site.register(CycleEmailTemplate, CycleEmailTemplateAdmin)
admin.site.register(CycleNotification, CycleNotificationAdmin)
