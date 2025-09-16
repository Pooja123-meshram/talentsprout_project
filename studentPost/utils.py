from django.utils import timezone
from .models import BlogPost

def publish_scheduled_posts():
    now = timezone.now()
    scheduled = BlogPost.objects.filter(status='scheduled', scheduled_at__lte=now)
    for post in scheduled:
        post.status = 'published'
        post.publication_date = now
        post.save()
