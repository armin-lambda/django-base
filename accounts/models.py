from django.db import models
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from phonenumber_field.modelfields import PhoneNumberField

from utils.paths import get_user_profile_image_upload_path
from utils.validators import UsernameValidator, NameValidator


User = settings.AUTH_USER_MODEL


class CustomUser(AbstractUser):
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[UsernameValidator()],
        error_messages={
            'unique': 'This username already exists.',
        },
    )
    email = models.EmailField(
        unique=True,
        verbose_name='email address',
        error_messages={
            'unique': 'This email address already exists.',
        },
    )
    first_name = models.CharField(
        max_length=15,
        validators=[NameValidator('FirstName')],
    )
    last_name = models.CharField(
        max_length=15,
        validators=[NameValidator('LastName')],
    )
    phone_number = PhoneNumberField(
        unique=True,
        error_messages={
            'unique': 'This phone number already exists.',
        },
    )
    image = models.ImageField(
        upload_to=get_user_profile_image_upload_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'gif'])],
    )

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'phone_number']

    class Meta:
        ordering = ['username']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.username
    
    # ----- URLS -----

    def get_absolute_url(self):
        return reverse('accounts:user-detail', args=[self.username])
    
    def get_update_url(self):
        return reverse('accounts:user-update')
    
    def get_delete_url(self):
        return reverse('accounts:user-delete')
    
    def get_profile_image_delete_url(self):
        return reverse('accounts:user-profile-image-delete')
    
    def get_follow_url(self):
        return reverse('accounts:user-follow', args=[self.username])
    
    def get_unfollow_url(self):
        return reverse('accounts:user-unfollow', args=[self.username])
    
    def get_follower_list_url(self):
        return reverse('accounts:user-follower-list', args=[self.username])
    
    def get_following_list_url(self):
        return reverse('accounts:user-following-list', args=[self.username])

    # ----- COUNTS -----

    def get_followers_count(self):
        return self.followers.count()
    
    def get_following_count(self):
        return self.following.count()

    # ----- LISTS -----

    def get_follower_list(self):
        return CustomUser.objects.filter(following__to_user=self)

    def get_following_list(self):
        return CustomUser.objects.filter(followers__from_user=self)


class Relation(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['from_user', 'to_user']
    
    def __str__(self):
        return f"{self.from_user} followed {self.to_user}"
