# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone
from django.db.models import Q
from django.db import models

from ckeditor.fields import RichTextField
from django.utils.functional import cached_property
from simple_history.models import HistoricalRecords

from notifications import ACCEPTED_PARAMS
from .managers import GetOrNoneManager
from .toolz import extract_parameters


STAGE_INITIATED = 1
STAGE_CLOSED = 6


class Stage(models.Model):
    """A stage cycle."""
    title = models.CharField(max_length=64)
    cycle = models.ForeignKey('Cycle', on_delete=models.CASCADE, related_name="stages")

    class Meta:
        unique_together = ('title', 'cycle')

    def create_stage_templates(self):
        for group in CompaniesGroup.objects.all():
            cycle_template = CycleEmailTemplate(
                stage=self,
                group=group,
                subject="",
                body_html=""
            )
            cycle_template.save()

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


class Company(models.Model):
    """ Base class for a registry, ECR or BDR, company.
    """

    class Meta:
        verbose_name_plural = 'Companies'

    external_id = models.CharField(max_length=64, db_index=True, unique=True, blank=True, null=True)
    name = models.CharField(max_length=256)
    vat = models.CharField(max_length=64, blank=True, null=True)
    country = models.CharField(max_length=256)
    group = models.ForeignKey(CompaniesGroup)

    objects = GetOrNoneManager()

    def __str__(self):
        return self.name

    def __unicode__(self):
        return '%s' % self.name


class Person(models.Model):
    """ Base class for a company user/person/contact.
    """
    username = models.CharField(max_length=128, db_index=True, unique=True)
    name = models.CharField(max_length=256)
    email = models.CharField(max_length=128, db_index=True, unique=True)
    company = models.ManyToManyField(Company, related_name='users')

    def __str__(self):
        return '{} ({})'.format(self.name, self.username)

    def __unicode__(self):
        return '{} ({})'.format(self.name, self.username)

    def admin_company(self):
        return ', '.join([c.name for c in self.company.all()])

    @cached_property
    def stages(self):
        return [notification.emailtemplate.stage for notification in self.notifications.all()]
    admin_company.short_description = 'Company'


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
    body_html = RichTextField(verbose_name='Body')
    group = models.ForeignKey(CompaniesGroup)
    stage = models.ForeignKey(Stage)

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
    history = HistoricalRecords()

    def __str__(self):
        return str(self.year)

    def __unicode__(self):
        return '%s' % self.year

    @property
    def can_edit(self):
        return self.stage.can_edit

    @property
    def can_trigger(self):
        return self.stage.can_trigger

    def last_action(self):
        return self.history.first()

    @classmethod
    def can_initiate_new_cycle(cls):
        cycles = cls.objects.order_by('-year')
        if cycles.exists():
            last_cycle = cycles.first()
            if last_cycle.stage.pk != STAGE_CLOSED:
                return False
        return True


class CycleEmailTemplate(models.Model):
    """ Base class for custom email templates for each reporting cycle
        and group.
    """

    DRAFT = 0
    PROCESSING = 1
    SENT = 2

    STATUS = (
        (DRAFT, 'draft'),
        (PROCESSING, 'processing'),
        (SENT, 'sent'),
    )

    class Meta:
        verbose_name_plural = '> Cycles email templates'

    subject = models.CharField(max_length=256)
    body_html = RichTextField(verbose_name='Body')
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE,
                              related_name="templates")
    group = models.ForeignKey(CompaniesGroup, on_delete=models.CASCADE,
                              related_name="templates")
    status = models.SmallIntegerField(choices=STATUS, default=DRAFT)

    history = HistoricalRecords()

    def __str__(self):
        return '{} {} {}'.format(self.stage.cycle, self.stage, self.group)

    def __unicode__(self):
        return '{} {} {}'.format(self.stage.cycle, self.stage, self.group)

    def last_action(self):
        return self.history.first()

    def get_parameters(self):
        return ACCEPTED_PARAMS

    @property
    def is_triggered(self):
        return self.status in (self.PROCESSING, self.SENT)


class CycleNotification(models.Model):
    """ Base class for each sent email.
    """

    class Meta:
        verbose_name_plural = '> Cycles notifications'


    subject = models.CharField(max_length=256)
    email = models.CharField(max_length=128, db_index=True)
    body_html = models.TextField()
    sent_date = models.DateTimeField(db_index=True,
                                     default=timezone.now)
    emailtemplate = models.ForeignKey(CycleEmailTemplate, related_name='emails')
    counter = models.IntegerField(default=1)
    person = models.ForeignKey(Person, related_name='notifications')
    company = models.ForeignKey(Company, related_name='notifications')

    def __str__(self):
        return '{} for {}'.format(self.emailtemplate, self.email)

    def __unicode__(self):
        return '{} for {}'.format(self.emailtemplate, self.email)

    @property
    def cycle(self):
        return self.emailtemplate.stage.cycle

    @property
    def stage(self):
        return self.emailtemplate.stage

    @property
    def group(self):
        return self.emailtemplate.group
