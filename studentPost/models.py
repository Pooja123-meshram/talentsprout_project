from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class BlogPost(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    publication_date = models.DateTimeField()
    content = models.TextField()
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('published', 'Published'),
        ('scheduled', 'Scheduled'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_at = models.DateTimeField(null=True, blank=True)



    def __str__(self):
        return self.title

class BlogImage(models.Model):
    blog_post = models.ForeignKey(BlogPost, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='blog_images/')


class CandidatePreference(models.Model):
    blog_post = models.OneToOneField(BlogPost, on_delete=models.CASCADE)
    service_title = models.CharField(max_length=200)
    description = models.TextField()
    delivery_time = models.CharField(max_length=100,blank=True, null=True)
    revisions = models.CharField(max_length=100 ,blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2 ,blank=True, null=True)

    def __str__(self):
        return self.service_title