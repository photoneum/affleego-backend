from typing import final

from django.conf import settings
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


@final
class Promotions(UUIDMixin, CreatedAtMixin, UpdatedAtMixin, models.Model):
    """Model for storing promotional content."""

    title = models.CharField(_('title'), max_length=200)
    content = models.TextField(_('content'))
    image_background = models.ImageField(
        _('image background'), upload_to='promotions/', blank=True, null=True
    )
    cta_url = models.URLField(_('CTA URL'), max_length=500)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('created by'),
        related_name='promotions',
    )

    class Meta:
        verbose_name = _('Promotion')
        verbose_name_plural = _('Promotions')
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.title
