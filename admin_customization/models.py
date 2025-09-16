from django.db import models
from django.conf import settings

class Traffic(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)  # Optional user field
    timestamp = models.DateTimeField(auto_now_add=True)  # Automatically set to now when created
    page_visited = models.CharField(max_length=255)  # URL or name of the page visited
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # Optional field for storing IP address

    def __str__(self):
        return f"Traffic from {self.user if self.user else 'Guest'} on {self.timestamp} - {self.page_visited}"


class HeroSection(models.Model):
    heading = models.CharField(max_length=255)
    sub_heading = models.CharField(max_length=255)
    description = models.TextField()
    button_text = models.CharField(max_length=50, default="Connect With Us")
    button_url = models.URLField()
    image1 = models.ImageField(upload_to='hero_images/', blank=True, null=True)
    image2 = models.ImageField(upload_to='hero_images/', blank=True, null=True)
    image3 = models.ImageField(upload_to='hero_images/', blank=True, null=True)

    # New Feature Section Fields
    feature1_icon = models.CharField(max_length=10, blank=True, null=True)
    feature1_title = models.CharField(max_length=100, blank=True, null=True)
    feature1_desc = models.CharField(max_length=255, blank=True, null=True)

    feature2_icon = models.CharField(max_length=10, blank=True, null=True)
    feature2_title = models.CharField(max_length=100, blank=True, null=True)
    feature2_desc = models.CharField(max_length=255, blank=True, null=True)

    feature3_icon = models.CharField(max_length=10, blank=True, null=True)
    feature3_title = models.CharField(max_length=100, blank=True, null=True)
    feature3_desc = models.CharField(max_length=255, blank=True, null=True)


    def __str__(self):
        return self.heading
    

    
class WhyChooseUs(models.Model):
    heading = models.CharField(max_length=255, blank=True, null=True)
    sub_heading = models.TextField(blank=True, null=True)

    # Feature points with icons
    point1_icon = models.CharField(max_length=50, blank=True, null=True)
    point1_title = models.CharField(max_length=100, blank=True, null=True)
    point1_desc = models.TextField(blank=True, null=True)

    point2_icon = models.CharField(max_length=50, blank=True, null=True)
    point2_title = models.CharField(max_length=100, blank=True, null=True)
    point2_desc = models.TextField(blank=True, null=True)

    point3_icon = models.CharField(max_length=50, blank=True, null=True)
    point3_title = models.CharField(max_length=100, blank=True, null=True)
    point3_desc = models.TextField(blank=True, null=True)

    point4_icon = models.CharField(max_length=50, blank=True, null=True)
    point4_title = models.CharField(max_length=100, blank=True, null=True)
    point4_desc = models.TextField(blank=True, null=True)

    point5_icon = models.CharField(max_length=50, blank=True, null=True)
    point5_title = models.CharField(max_length=100, blank=True, null=True)
    point5_desc = models.TextField(blank=True, null=True)

    point6_icon = models.CharField(max_length=50, blank=True, null=True)
    point6_title = models.CharField(max_length=100, blank=True, null=True)
    point6_desc = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.heading or "Why Choose Us"


class WorkStep(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    icon = models.CharField(max_length=50)  # Store icon class name for flexibility (e.g., 'fa-solid fa-sign-in-alt')

    def __str__(self):
        return self.title    
    
class ContactInfo(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    description = models.TextField()
    address = models.CharField(max_length=255, blank=True) 
    button_text = models.CharField(max_length=50, default="Contact Us")
    contact_image = models.ImageField(upload_to='contact_images/', blank=True, null=True) 

    def __str__(self):
        return self.name    
    
    
class Footer(models.Model):
    company_name = models.CharField(max_length=100, blank=True, null=True)
    copyright_text = models.CharField(max_length=255, default="© 2024 Your Company. All rights reserved.")
    quick_links = models.JSONField(default=dict, blank=True)  # Store quick links as key-value pairs (e.g., {"About Us": "/about"})
    social_links = models.JSONField(default=dict, blank=True)  # Store social links as key-value pairs (e.g., {"Facebook": "https://facebook.com"})
    address = models.TextField(blank=True, null=True)  # Company address in the footer
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.company_name or "Footer"    
    
class FooterPortfolioImage(models.Model):
    footer = models.ForeignKey(Footer, related_name="portfolio_images", on_delete=models.CASCADE)  # Relation to Footer
    image = models.ImageField(upload_to='footer_portfolio_images/')
    caption = models.CharField(max_length=255, blank=True, null=True)  # Optional caption for the image

    def __str__(self):
        return f"Portfolio Image for {self.footer.company_name or 'Footer'}"    