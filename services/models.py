from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()



class Service_page(models.Model):
    titel = models.CharField(max_length=100, null=True, blank=True)
    page_description = models.TextField(null=True, blank=True)
    service_banner_image = models.ImageField(upload_to='service_images/', help_text="Upload a page banner related image", null=True, blank=True)
    
    service_left_image = models.ImageField(upload_to='service_left_images/', help_text="Upload a service_left related image" , null=True, blank=True)
    #new add filed
    left_width = models.PositiveIntegerField(default=300)
    left_height = models.PositiveIntegerField(default=300)
    
    service_right_image = models.ImageField(upload_to='service_right_images/', help_text="Upload a service_right related image" , null=True, blank=True)
    #new add filed
    right_width = models.PositiveIntegerField(default=300)
    right_height = models.PositiveIntegerField(default=300)
    
    def __str__(self):
        return self.titel


class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    skills = models.CharField(max_length=255, help_text="Comma-separated skills related to this service")
    created_at = models.DateTimeField(auto_now_add=True)
    icon = models.ImageField(upload_to='service_icons/', null=True, blank=True)


    def __str__(self):
        return self.name
    


class ServiceRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    requested_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.title} by {self.user.username}"

