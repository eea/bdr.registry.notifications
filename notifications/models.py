# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone
from django.db import models

from ckeditor.fields import RichTextField
from django.utils.functional import cached_property
from simple_history.models import HistoricalRecords

from notifications import ACCEPTED_PARAMS
from .managers import GetOrNoneManager


STAGE_INITIATED = 1
STAGE_CLOSED = 6


class Stage(models.Model):
    """A stage cycle."""

    title = models.CharField(max_length=64)
    cycle = models.ForeignKey("Cycle", on_delete=models.CASCADE, related_name="stages")

    class Meta:
        unique_together = ("title", "cycle")

    def create_stage_templates(self):
        for group in CompaniesGroup.objects.all():
            cycle_template = CycleEmailTemplate(
                stage=self, group=group, subject="", body_html=""
            )
            cycle_template.save()

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title


class CompaniesGroup(models.Model):
    """Base class for the 3 groups of companies:
    2 - F-gases EU
    3 - F-gases NONEU
    4 - ODS
    5 - Cars
    6 - Vans
    """

    title = models.CharField(max_length=256)
    code = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.title

    def __unicode__(self):
        return "%s" % self.title

    def count_emailtemplates(self):
        return CycleEmailTemplate.objects.filter(group=self).count()

    count_emailtemplates.short_description = "#Email templates"


class Company(models.Model):
    """Base class for a registry, ECR or BDR, company."""

    related_objects = [
        ("PersonCompany", "company"),
    ]

    class Meta:
        verbose_name_plural = "Companies"

    external_id = models.CharField(
        max_length=64, db_index=True, blank=True, null=True
    )
    name = models.CharField(max_length=256)
    vat = models.CharField(max_length=64, blank=True, null=True)
    country = models.CharField(max_length=256)
    group = models.ForeignKey(CompaniesGroup, on_delete=models.PROTECT)
    status = models.CharField(max_length=64, default="")
    representative_name = models.CharField(max_length=256, blank=True, null=True)
    representative_vat = models.CharField(max_length=256, blank=True, null=True)
    representative_country_name = models.CharField(
        max_length=256, blank=True, null=True
    )
    check_passed = models.BooleanField(default=None, null=True)

    objects = GetOrNoneManager()

    def __str__(self):
        return self.name

    def __unicode__(self):
        return "%s" % self.name

    @property
    def active_users(self):
        person_companies = PersonCompany.objects.filter(company=self)
        return [person_company.person for person_company in person_companies]


class Person(models.Model):
    """Base class for a company user/person/contact."""

    related_objects = [
        ("PersonCompany", "person"),
    ]
    username = models.CharField(max_length=128, db_index=True, unique=True)
    name = models.CharField(max_length=256)
    email = models.CharField(max_length=128, db_index=True)
    company = models.ManyToManyField(
        Company, related_name="users", through="PersonCompany"
    )

    def __str__(self):
        return "{} ({})".format(self.name, self.username)

    def __unicode__(self):
        return "{} ({})".format(self.name, self.username)

    def admin_company(self):
        return ", ".join([c.name for c in self.company.all()])

    @cached_property
    def stages(self):
        return [
            notification.emailtemplate.stage
            for notification in self.notifications.all()
        ]

    admin_company.short_description = "Company"


class PersonCompanyManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return super(PersonCompanyManager, self).get_queryset().filter(current=True)

    def really_all(self):
        return super(PersonCompanyManager, self).get_queryset().all()


class PersonCompany(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    current = models.BooleanField(default=False, null=True)
    objects = PersonCompanyManager()

    class Meta:
        db_table = "notifications_person_company"


class Cycle(models.Model):
    """Base class for a reporting cycle - this happens once per year."""

    class Meta:
        verbose_name_plural = "> Cycles"

    year = models.PositiveSmallIntegerField(unique=True, default=timezone.now().year)
    closing_date = models.DateField()
    history = HistoricalRecords()

    def __str__(self):
        return str(self.year)

    def __unicode__(self):
        return "%s" % self.year

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
        cycles = cls.objects.order_by("-year")
        if cycles.exists():
            last_cycle = cycles.first()
            if last_cycle.stage.pk != STAGE_CLOSED:
                return False
        return True


class CycleEmailTemplate(models.Model):
    """Base class for custom email templates for each reporting cycle
    and group.
    """

    DRAFT = 0
    PROCESSING = 1
    SENT = 2

    STATUS = (
        (DRAFT, "draft"),
        (PROCESSING, "processing"),
        (SENT, "sent"),
    )

    class Meta:
        verbose_name_plural = "> Cycles email templates"

    subject = models.CharField(max_length=256)
    body_html = RichTextField(verbose_name="Body")
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name="templates")
    group = models.ForeignKey(
        CompaniesGroup, on_delete=models.CASCADE, related_name="templates"
    )
    status = models.SmallIntegerField(choices=STATUS, default=DRAFT)

    history = HistoricalRecords()

    def __str__(self):
        return "{} {} {}".format(self.stage.cycle, self.stage, self.group)

    def __unicode__(self):
        return "{} {} {}".format(self.stage.cycle, self.stage, self.group)

    def last_action(self):
        return self.history.first()

    def get_parameters(self):
        return ACCEPTED_PARAMS

    @property
    def is_triggered(self):
        return self.status in (self.PROCESSING, self.SENT)


class CycleNotification(models.Model):
    """Base class for each sent email."""

    class Meta:
        verbose_name_plural = "> Cycles notifications"

    subject = models.CharField(max_length=256)
    email = models.CharField(max_length=128, db_index=True)
    body_html = models.TextField()
    sent_date = models.DateTimeField(db_index=True, default=timezone.now)
    emailtemplate = models.ForeignKey(
        CycleEmailTemplate, on_delete=models.PROTECT, related_name="emails"
    )
    counter = models.IntegerField(default=1)
    person = models.ForeignKey(
        Person, on_delete=models.DO_NOTHING, related_name="notifications"
    )
    company = models.ForeignKey(
        Company, on_delete=models.DO_NOTHING, related_name="notifications"
    )

    def __str__(self):
        return "{} for {}".format(self.emailtemplate, self.email)

    def __unicode__(self):
        return "{} for {}".format(self.emailtemplate, self.email)

    @property
    def cycle(self):
        return self.emailtemplate.stage.cycle

    @property
    def stage(self):
        return self.emailtemplate.stage

    @property
    def group(self):
        return self.emailtemplate.group
