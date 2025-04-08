from django.contrib.auth.models import AbstractUser
from django.db import models

# # Create your models here.
# class User(AbstractUser):
#     pass


# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     profile_picture = models.ImageField(
#         upload_to="profile-pictures/", null=True, blank=True
#     )
#     bio = models.TextField(blank=True)
#     location = models.CharField(max_length=100, blank=True)
