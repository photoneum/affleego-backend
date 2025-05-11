import secrets
import textwrap
from datetime import timedelta
from typing import TYPE_CHECKING, ClassVar, final, override

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from server.apps.users.managers import UserManager
from server.common.mixins import CreatedAtMixin, UpdatedAtMixin, UUIDMixin
from server.common.utils.file_url_helpers import get_full_url

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager


# # Create your models here.
@final
class User(AbstractUser, UUIDMixin):
    """User model."""

    class Type(models.TextChoices):
        """User type choices."""

        ADMIN = 'admin', 'Admin'
        USER = 'user', 'User'

    if TYPE_CHECKING:
        verification_codes = RelatedManager['VerificationCode']()

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
                check=models.Q(type__in=['admin', 'user']),
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


# Add this new model for verification codes
@final
class VerificationCode(models.Model):
    """Model for storing verification codes."""

    # if TYPE_CHECKING:
    #     user = ForeignKey[User]

    class Type(models.TextChoices):
        """Verification code type choices."""

        VERIFY_ACCOUNT = 'verify_account', 'Verify Account'
        RESET_PASSWORD = 'reset_password', 'Reset Password'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='verification_codes',
        verbose_name=_('user'),
    )
    code = models.CharField(
        _('verification code'),
        max_length=12,
        unique=True,
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
    )
    expires_at = models.DateTimeField(
        _('expires at'),
    )
    is_used = models.BooleanField(
        _('is used'),
        default=False,
    )
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=Type.choices,
        default=Type.VERIFY_ACCOUNT,
    )

    class Meta:
        verbose_name = _('Verification Code')
        verbose_name_plural = _('Verification Codes')
        constraints = [
            models.CheckConstraint(
                check=models.Q(type__in=['verify_account', 'reset_password']),
                name='users_verificationcode_type_valid',
            ),
        ]

    def __str__(self):
        return f'Code for {self.user.email}'

    def is_valid(self) -> bool:
        """Check if the verification code is valid."""
        return not self.is_used and self.expires_at > timezone.now()

    @classmethod
    def generate_code(
        cls,
        user: User,
        code_type: Type = Type.VERIFY_ACCOUNT,
        expiry_minutes: int = 10,
    ) -> 'VerificationCode':
        """Generate a new verification code for the user."""
        # Generate a random 12-character code with letters and numbers
        import string  # noqa: PLC0415

        chars = string.ascii_letters + string.digits
        code = ''.join(secrets.choice(chars) for _ in range(12))

        # Set expiry time
        expires_at = timezone.now() + timedelta(minutes=expiry_minutes)

        # Create and return the verification code
        return cls.objects.create(
            user=user,
            code=code,
            expires_at=expires_at,
            type=code_type,
        )


@final
class UserOnboarding(UUIDMixin, CreatedAtMixin, UpdatedAtMixin, models.Model):
    """Model for storing user onboarding data."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='onboarding',
        verbose_name=_('user'),
    )
    brand_name = models.CharField(
        _('brand name'),
        max_length=255,
    )
    website = models.URLField(
        _('website'),
        blank=True,
    )
    marketing_methods = models.CharField(
        _('marketing methods'),
        blank=True,
        help_text=_('List of marketing methods used by the user'),
    )
    heard_from = models.CharField(
        _('heard from'),
        max_length=255,
    )
    feedback_message = models.TextField(
        _('feedback message'),
        blank=True,
    )

    class Meta:
        verbose_name = _('User Onboarding')
        verbose_name_plural = _('User Onboardings')

    def __str__(self):
        return f'Onboarding for {self.user.email}'
