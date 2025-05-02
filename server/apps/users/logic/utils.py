from typing import cast

from django.contrib.auth import get_user_model

from server.apps.users.models import User as CustomUser


def get_custom_user_model() -> type[CustomUser]:
    """
    Returns the User model with the correct type annotation.

    This is a wrapper around Django's get_user_model() that ensures proper typing
    for our custom User model instead of returning the generic AbstractUser type.

    Returns:
        type[CustomUser]: The custom User model class with proper type annotations
    """
    UserModel = get_user_model()  # noqa: N806
    return cast(type[CustomUser], UserModel)
