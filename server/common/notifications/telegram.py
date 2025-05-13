# server/common/notifications/telegram.py
import asyncio
from typing import cast

import structlog
from telegram import Bot

from server.settings.components import config

logger = structlog.get_logger(__name__)


class TelegramNotification:
    """A class for handling Telegram notifications."""

    def __init__(
        self,
        token: str,
        chat_id: str,
        message: str,
    ):
        """
        Initialize the Telegram notification.

        Args:
            token: Telegram Bot API token
            chat_id: Recipient's chat ID
            message: Message to send
        """
        self.token = token
        self.chat_id = chat_id
        self.message = message

    async def _send_message_async(self) -> bool:
        """
        Send the message asynchronously.

        Returns:
            Boolean indicating success
        """
        try:
            bot = Bot(self.token)
            async with bot:
                await bot.send_message(chat_id=self.chat_id, text=self.message)
            logger.info(
                'Telegram message sent successfully',
                extra={
                    'chat_id': self.chat_id,
                },
            )
        except Exception:
            logger.exception(
                'Failed to send Telegram message',
                extra={
                    'chat_id': self.chat_id,
                },
            )
            return False
        else:
            return True

    def send(self) -> bool:
        """
        Send the Telegram notification.

        Returns:
            Boolean indicating whether the message was sent successfully
        """
        return asyncio.run(self._send_message_async())


class TelegramNotificationFactory:
    """Factory class to create Telegram notifications with predefined templates."""

    @staticmethod
    def create_notification(
        message: str,
    ) -> TelegramNotification:
        """
        Create a basic Telegram notification.

        Args:
            chat_id: Recipient's chat ID
            message: Message text to send

        Returns:
            Configured TelegramNotification object
        """
        telegram_token = cast(str, config('TELEGRAM_BOT_TOKEN', default=''))
        telegram_chat_id = cast(str, config('TELEGRAM_CHAT_ID', default=''))

        return TelegramNotification(
            token=telegram_token,
            chat_id=telegram_chat_id,
            message=message,
        )
