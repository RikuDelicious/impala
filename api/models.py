from django.db import models


# Create your models here.
class Image(models.Model):
    upload = models.ImageField(upload_to="images/", max_length=1024)
    profile_signiture = models.CharField(max_length=255, unique=True)
