from django.db import models
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator

from utils.paths import get_user_profile_image_path
from utils.validators import UsernameValidator, NameValidator


User = settings.AUTH_USER_MODEL


class CustomUser(AbstractUser):
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[UsernameValidator()],
        help_text='Required. Unique. 30 characters or fewer. Lowercase letters, numbers, _ and . only.',
        error_messages={
            'unique': 'This username already exists.',
        },
    )
    email = models.EmailField(
        unique=True,
        verbose_name='email address',
        help_text='Required. Unique. Must be a valid and unique email address.',
        error_messages={
            'unique': 'This email address already exists.',
        },
    )
    first_name = models.CharField(
        max_length=15,
        validators=[NameValidator('FirstName')],
        help_text='Required. 15 characters or fewer. Letters only.',
    )
    last_name = models.CharField(
        max_length=15,
        validators=[NameValidator('LastName')],
        help_text='Required. 15 characters or fewer. Letters only.',
    )
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        help_text='Required. Unique. 15 characters or fewer.',
        error_messages={
            'unique': 'This phone number already exists.',
        },
    )
    image = models.ImageField(
        upload_to=get_user_profile_image_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'gif'])],
        help_text='Allowed formats: png, jpg, jpeg, gif.',
    )

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'phone_number']

    class Meta:
        ordering = ['username']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.username
    
    def get_edit_url(self):
        return reverse('accounts:edit')
    
    def get_delete_url(self):
        return reverse('accounts:delete')
    
    def get_delete_profile_image_url(self):
        return reverse('accounts:profile_image_delete')
    
    def get_profile_url(self):
        return reverse('accounts:profile', args=[self.username])
    
    def get_follow_url(self):
        return reverse('accounts:follow', args=[self.username])
    
    def get_unfollow_url(self):
        return reverse('accounts:unfollow', args=[self.username])
    
    def get_followers_url(self):
        return reverse('accounts:followers', args=[self.username])
    
    def get_following_url(self):
        return reverse('accounts:following', args=[self.username])

    def get_followers_count(self):
        return self.followers.count()
    
    def get_following_count(self):
        return self.following.count()

    def get_followers(self):
        return CustomUser.objects.filter(following__to_user=self)

    def get_following(self):
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
