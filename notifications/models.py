# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone
from django.db.models import Q
from django.db import models

from ckeditor.fields import RichTextField
from simple_history.models import HistoricalRecords

from .toolz import extract_parameters


STAGE_INITIATED = 1
STAGE_CLOSED = 6


class Stage(models.Model):
    """ Base class for workflow's stages:
        1 - INITIATED
        2 - INVITATIONS
        3 - REMINDER (one week before)
        4 - DEADLINE
        5 - AFTER (one week after)
        6 - CLOSED
    """
    title = models.CharField(max_length=64)
    code = models.SlugField(max_length=64, unique=True)
    can_edit = models.BooleanField(default=False)
    can_trigger = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title


class CompaniesGroup(models.Model):
    """ Base class for the 3 groups of companies:
        1 - ODS/Cars/Vans
        2 - F-gases EU
        3 - F-gases NONEU
    """
    title = models.CharField(max_length=256)
    code = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.title

    def __unicode__(self):
        return '%s' % self.title

    def count_emailtemplates(self):
        return (EmailTemplate.objects
                .filter(group=self)
                .count())
    count_emailtemplates.short_description = '#Email templates'


class EmailTemplate(models.Model):
    """ Base class for the 4 types of email templates. The corresponding
        stage is:
        2 - INVITATIONS
        3 - REMINDER
        4 - DEADLINE
        5 - AFTER
    """

    class Meta:
        unique_together = ('group', 'stage')

    subject = models.CharField(max_length=256)
    body_html = RichTextField()
    body_text = models.TextField(blank=True, null=True, default='')
    group = models.ForeignKey(CompaniesGroup)
    stage = models.ForeignKey(Stage, default=STAGE_INITIATED,
                              limit_choices_to=Q(can_trigger=True))

    def __str__(self):
        return '{} for {}'.format(self.stage, self.group)

    def __unicode__(self):
        return '{} for {}'.format(self.stage, self.group)


class Cycle(models.Model):
    """ Base class for a reporting cycle - this happens once per year.
    """

    class Meta:
        verbose_name_plural = '> Cycles'

    year = models.PositiveSmallIntegerField(unique=True,
                                            default=timezone.now().year)
    closing_date = models.DateField()
    stage = models.ForeignKey(Stage, default=STAGE_INITIATED)
    history = HistoricalRecords()

    def __str__(self):
        return self.year

    def __unicode__(self):
        return '%s' % self.year

    @property
    def can_edit(self):
        return self.stage.can_edit

    @property
    def can_trigger(self):
        return self.stage.can_trigger

    def last_action(self):
        return self.history.all()[0]

    def create_cycle_templates(self):
        year = self.year
        closing_date = self.closing_date.strftime('%d %B %Y')
        for emailtemplate in EmailTemplate.objects.all():
            cycle_emailtemplate = CycleEmailTemplate(
                cycle=self,
                emailtemplate=emailtemplate,
                subject=(emailtemplate
                         .subject
                         .format(year=year, closing_date=closing_date)),
                body_html=(emailtemplate
                           .body_html
                           .format(year=year, closing_date=closing_date)),
                body_text=(emailtemplate
                           .body_text
                           .format(year=year, closing_date=closing_date))
            )
            cycle_emailtemplate.save()


class CycleEmailTemplate(models.Model):
    """ Base class for custom email templates for each reporting cycle
        and group.
    """

    class Meta:
        verbose_name_plural = '> Cycles email templates'

    subject = models.CharField(max_length=256)
    body_html = RichTextField()
    body_text = models.TextField(blank=True, null=True, default='')
    cycle = models.ForeignKey(Cycle)
    emailtemplate = models.ForeignKey(EmailTemplate)
    is_triggered = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self):
        return '{}'.format(self.emailtemplate)

    def __unicode__(self):
        return '{}'.format(self.emailtemplate)

    @property
    def stage(self):
        return self.emailtemplate.stage

    @property
    def group(self):
        return self.emailtemplate.group

    @property
    def can_edit(self):
        return self.cycle.can_edit

    @property
    def can_trigger(self):
        return self.cycle.can_trigger and self.cycle.stage == self.stage

    def last_action(self):
        return self.history.all()[0]

    def get_parameters(self):
        return extract_parameters(self.body_html)


class CycleNotification(models.Model):
    """ Base class for each sent email.
    """

    class Meta:
        verbose_name_plural = '> Cycles notifications'
        unique_together = ('email', 'emailtemplate')

    subject = models.CharField(max_length=256)
    email = models.CharField(max_length=128, db_index=True)
    body_html = models.TextField()
    body_text = models.TextField()
    sent_date = models.DateTimeField(db_index=True,
                                     default=timezone.now)
    emailtemplate = models.ForeignKey(CycleEmailTemplate)

    def __str__(self):
        return '{} for {}'.format(self.emailtemplate, self.email)

    def __unicode__(self):
        return '{} for {}'.format(self.emailtemplate, self.email)

    @property
    def cycle(self):
        return self.emailtemplate.cycle

    @property
    def stage(self):
        return self.emailtemplate.stage

    @property
    def group(self):
        return self.emailtemplate.group
