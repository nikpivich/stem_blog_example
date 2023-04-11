from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from faker import Faker
from ckeditor.fields import RichTextField

class News(models.Model):
    title = models.CharField(max_length=15)
    content = RichTextField()
    date = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='news_img/%Y/%m/%d/', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, null=True)
    country = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=100, null=True)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        f = Faker('ru_RU')
        Profile.objects.create(
            user=instance,
            phone=f.phone_number(),
            country=f.country(),
        )

# @receiver()