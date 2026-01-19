from django.db import models
from django.contrib.auth.models import AbstractUser

class CustumUser(AbstractUser):
    ROLE_CHOISE = (
        ('admin', 'admin'),
        ('mentor', 'mentor'),
        ('student', 'student'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOISE, default='student')

    def __str__(self):
        return self.username

class Profile(models.Model):
    user = models.OneToOneField(CustumUser, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    country = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username
    
    

