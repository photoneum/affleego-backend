from typing import Any

import structlog
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from server.settings.components import config

logger = structlog.get_logger(__name__)


class EmailNotification:
    """
    A comprehensive class for handling email notifications with dynamic template loading
    and context-aware templating.
    """

    def __init__(
        self,
        subject: str,
        template_path: str,
        context: dict[str, Any],
        to_emails: list[str],
        cc_emails: list[str] | None = None,
        bcc_emails: list[str] | None = None,
        reply_to: list[str] | None = None,
        attachments: list[dict[str, Any]] | None = None,
        from_email: str = settings.DEFAULT_FROM_EMAIL,
    ):
        """
        Initialize the email notification.

        Args:
            subject: Subject line of the email
            from_email: Sender email address
            template_path: Path to the Django HTML template
            context: Dictionary of variables to inject into the template
            to_emails: List of recipient email addresses
            cc_emails: List of CC recipient email addresses
            bcc_emails: List of BCC recipient email addresses
            reply_to: List of reply-to email addresses
            attachments: List of attachment dictionaries with format:
                         {'filename': 'name.ext', 'content': binary_data, 'mimetype': 'mime/type'}
        """
        self.subject = subject
        self.from_email = from_email
        self.template_path = template_path
        self.context = context
        self.to_emails = to_emails
        self.cc_emails = cc_emails or []
        self.bcc_emails = bcc_emails or []
        self.reply_to = reply_to or []
        self.attachments = attachments or []
        self.html_content = None
        self.plain_content = None

        # Validate required context variables exist
        self._validate_context()

    def _validate_context(self) -> None:
        """
        Ensure all required template variables are provided in the context.
        Raises ValueError if any required variables are missing.
        """
        # Implementation depends on specific template requirements
        required_fields = ['user']  # Example, customize based on template needs

        missing = [field for field in required_fields if field not in self.context]
        if missing:
            raise ValueError(f'Missing required context variables: {", ".join(missing)}')

    def render_template(self) -> None:
        """
        Render the HTML template with the provided context.
        Sets both HTML and plain text versions of the email content.
        """
        self.html_content = render_to_string(self.template_path, context=self.context)
        self.plain_content = strip_tags(self.html_content)

    def prepare_email(self) -> EmailMultiAlternatives:
        """
        Prepare the email message object with all components.

        Returns:
            Configured EmailMultiAlternatives object ready to send
        """
        if not self.html_content:
            self.render_template()

        email = EmailMultiAlternatives(
            subject=self.subject,
            body=self.plain_content or '',
            from_email=self.from_email,
            to=self.to_emails,
            cc=self.cc_emails,
            bcc=self.bcc_emails,
            reply_to=self.reply_to,
        )

        if self.html_content:
            email.attach_alternative(self.html_content, 'text/html')

        # Add any attachments
        for attachment in self.attachments:
            email.attach(
                filename=attachment.get('filename', ''),
                content=attachment.get('content', ''),
                mimetype=attachment.get('mimetype', 'application/octet-stream'),
            )

        return email

    def send(self, fail_silently: bool = False) -> bool:  # noqa: FBT001, FBT002
        """
        Send the email notification.

        Args:
            fail_silently: If True, exceptions during sending will be suppressed

        Returns:
            Boolean indicating whether the email was sent successfully
        """
        if not self.to_emails:
            return False

        try:
            email = self.prepare_email()
            email.send(fail_silently=fail_silently)
            logger.info(
                'Email sent successfully',
                extra={
                    'to_emails': self.to_emails,
                    'subject': self.subject,
                },
            )
        except Exception:
            # Log the error (consider adding proper logging)
            logger.exception(
                'Failed to send email',
                extra={
                    'to_emails': self.to_emails,
                    'subject': self.subject,
                },
            )
            if not fail_silently:
                # raise the error to the caller
                raise
            return False
        else:
            return True


class EmailNotificationFactory:
    """Factory class to create email notifications with predefined templates and metadata."""

    @staticmethod
    def create_verify_user_email(
        user_email: str,
        context: dict[str, Any],
    ) -> EmailNotification:
        """
        Create an email notification for abstract submission acceptance.

        Args:
            user_email: Email address of the recipient
            context: Template context variables
            cc_emails: Optional list of CC recipients
            reply_to: Optional list of reply-to addresses

        Returns:
            Configured EmailNotification object
        """
        subject = 'Verify your account'
        domain_name = config('DOMAIN_NAME')
        template_path = 'users/emails/verify_account.html'
        context['domain_name'] = domain_name

        return EmailNotification(
            subject=subject,
            template_path=template_path,
            context=context,
            to_emails=[user_email],
            reply_to=['noreply@affleego.com'],
        )

    @staticmethod
    def create_custom_email(
        subject: str,
        from_email: str,
        template_path: str,
        context: dict[str, Any],
        to_emails: list[str],
        cc_emails: list[str] | None = None,
        bcc_emails: list[str] | None = None,
        reply_to: list[str] | None = None,
        attachments: list[dict[str, Any]] | None = None,
    ) -> EmailNotification:
        """
        Create a custom email notification with specified parameters.

        Args:
            subject: Subject line of the email
            from_email: Sender email address
            template_path: Path to the Django HTML template
            context: Dictionary of variables to inject into the template
            to_emails: List of recipient email addresses
            cc_emails: List of CC recipient email addresses
            bcc_emails: List of BCC recipient email addresses
            reply_to: List of reply-to email addresses
            attachments: List of attachment dictionaries

        Returns:
            Configured EmailNotification object
        """
        return EmailNotification(
            subject=subject,
            from_email=from_email,
            template_path=template_path,
            context=context,
            to_emails=to_emails,
            cc_emails=cc_emails,
            bcc_emails=bcc_emails,
            reply_to=reply_to,
            attachments=attachments,
        )
