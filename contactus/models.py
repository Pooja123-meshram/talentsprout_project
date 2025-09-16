from django.db import models

class ConsultingMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=15)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"

class SupportInfo(models.Model):
    title = models.CharField(max_length=255, help_text="Title for the support section (e.g., TalentSprout Support)")
    description = models.TextField(help_text="A brief description (e.g., Feel free to connect with us)")
    phone = models.CharField(max_length=15, help_text="Contact phone number")
    email = models.EmailField(help_text="Support email address")
    address = models.TextField(help_text="Physical address of the support center")
    support_image = models.ImageField(upload_to='support_images/', help_text="Upload a support-related image" , null=True, blank=True)
    contatus_image = models.ImageField(upload_to='contatus_images/', help_text="Upload a contatus related image" , null=True, blank=True)

    # 🔽 Add these 3 new fields:
    map_title = models.CharField(max_length=255, blank=True, null=True, help_text="Title above the map (e.g., Find Us on Google Maps)")
    map_description = models.TextField(blank=True, null=True, help_text="Short description under the map title")
    map_embed_url = models.TextField(blank=True, null=True, help_text="Paste your Google Maps iframe embed URL")

    def __str__(self):
        return self.title