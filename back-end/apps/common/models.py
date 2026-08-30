from django.db import models


class TimestampMixin(models.Model):
    """
    Abstract mixin providing created_at and updated_at timestamps.
    All domain models should inherit from this.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
