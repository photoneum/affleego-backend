from typing import final

from django.db import models
from tinymce import models as tinymce_models

from server.apps.users.models import User
from server.common.mixins import CreatedAtMixin, UpdatedAtMixin, UUIDMixin


@final
class Deal(UUIDMixin, CreatedAtMixin, UpdatedAtMixin, models.Model):
    """Model for storing deals."""

    class Status(models.TextChoices):
        """Status choices for deals."""

        OPEN = 'open'
        CLOSED = 'closed'

    name = models.CharField(max_length=255, blank=False)
    requirements = models.CharField(
        max_length=255,
        blank=True,
        help_text='The requirements for the deal',
    )
    commission_type = models.CharField(
        max_length=255,
        blank=True,
        help_text='The commission type for the deal',
    )
    projected_payout = models.CharField(
        max_length=255,
        blank=True,
        help_text='The projected payout for the deal',
    )
    revenue_share = models.CharField(
        max_length=255,
        blank=True,
        help_text='The revenue share for the deal',
    )
    payout_schedule = models.CharField(
        max_length=255,
        blank=True,
        help_text='The payout schedule for the deal',
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    is_featured = models.BooleanField(default=False)
    referral_link = models.URLField(max_length=255)
    description = tinymce_models.HTMLField(blank=True)
    keywords = models.CharField(
        max_length=255,
        blank=True,
        help_text='The keywords for the deal, comma separated',
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name='deals',
    )

    class Meta:
        verbose_name = 'Deal'
        verbose_name_plural = 'Deals'
        constraints = [
            models.CheckConstraint(
                name='deals_status_valid', check=models.Q(status__in=['open', 'closed'])
            )
        ]

    def __str__(self):
        return self.name
