from django.core.management.base import BaseCommand, CommandError

from notifications.models import CompaniesGroup, Stage, EmailTemplate


class Command(BaseCommand):
    """ Helpful command to be executed on an empty database.
    """

    help = 'Generates base email templates for each group.'

    def handle(self, *args, **options):

        for group in CompaniesGroup.objects.all():
            for stage in Stage.objects.filter(can_trigger=True):
                base_email_template = EmailTemplate(
                    stage=stage,
                    group=group,
                    subject='subject',
                    body_html='<p>WIP</p>'
                )
                base_email_template.save()

        self.stdout.write(
            self.style.SUCCESS(
                'Successfully generated all base email templates.'
            )
        )
