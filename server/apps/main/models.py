from typing import final

from django.db import models
from django.utils.translation import gettext_lazy as _

from server.common.mixins import CreatedAtMixin, UpdatedAtMixin, UUIDMixin


@final
class CommunityStats(UUIDMixin, CreatedAtMixin, UpdatedAtMixin, models.Model):
    """Model for storing community statistics."""

    weekly_ftds = models.IntegerField(_('weekly FTDs'), default=0)
    top_geo = models.CharField(_('top GEO'), max_length=100, blank=True)
    week_starting = models.DateField(_('week starting'))

    class Meta:
        verbose_name = _('Community Stats')
        verbose_name_plural = _('Community Stats')
        ordering = ['-week_starting']
