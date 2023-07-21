from django.db import models
from django.contrib.auth.models import User



class Profile(models.Model):
    user = models.OneToOneField(User , on_delete=models.CASCADE)
    auth_token = models.CharField(max_length=100 )
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True) # user creation date
    userimage= models.ImageField(null=True, blank=True, upload_to='image/profile')
    bio= models.TextField(null=True, max_length=1000)
    insta= models.CharField(null=True, max_length=100)
    fb= models.CharField(null=True, max_length=100)
    linkedin= models.CharField(null=True, max_length=100)

    def __str__(self):
        return self.user.username

