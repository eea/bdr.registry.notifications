from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet

class GetOrNoneManager(models.Manager):
    """ Adds get_or_none method to objects.
    """
    def get_queryset(self):
        return QuerySet(self.model).filter(Q(group_id=1) | Q(status='VALID'))

    def really_all(self):
        return QuerySet(self.model).all()

    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None
