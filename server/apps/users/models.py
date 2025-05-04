import textwrap
from typing import ClassVar, final, override

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from server.apps.users.managers import UserManager
from server.common.mixins import UUIDMixin
from server.common.utils.file_url_helpers import get_full_url


# # Create your models here.
@final
class User(AbstractUser, UUIDMixin):
    """User model."""

    class Type(models.TextChoices):
        """User type choices."""

        ADMIN = 'admin', 'Admin'
        USER = 'user', 'User'

    id: int
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(_('phone number'), blank=True, max_length=20)
    image = models.ImageField(_('image'), upload_to='users/', null=True, blank=True)
    is_verified = models.BooleanField(
        _('verified'),
        default=False,
        help_text=_('Designates whether this user has verified their accounts.'),
    )
    type = models.CharField(
        _('type'),
        max_length=10,
        choices=Type.choices,
        default=Type.USER,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS: ClassVar[list[str]] = ['first_name', 'last_name']
    objects = UserManager()  # type: ignore

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        constraints = [
            models.CheckConstraint(
                name='users_user_type_valid',
                condition=models.Q(type__in=['admin', 'user']),  # type: ignore
            ),
        ]

    @override
    def __str__(self):
        return textwrap.wrap(self.username, 40)[0]

    @property
    def full_name(self):
        return self.get_full_name()

    @property
    def get_image_url(self):
        if self.image:
            return get_full_url(self.image.url)
        return None
