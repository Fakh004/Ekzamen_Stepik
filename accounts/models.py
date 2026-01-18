from django.db import models
from django.contrib.auth.models import AbstractUser

class CustumUser(AbstractUser):
    pass

class Profile(models.Model):
    user = models.OneToOneField(CustumUser, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    country = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username
    
    

