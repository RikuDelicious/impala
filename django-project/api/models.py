from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver


# Create your models here.
class Image(models.Model):
    upload = models.ImageField(upload_to="images/", max_length=1024)
    profile_signiture = models.CharField(max_length=255, unique=True)


@receiver(pre_delete, sender=Image)
def pre_delete_item(sender, **kwargs):
    kwargs["instance"].upload.delete(save=False)
