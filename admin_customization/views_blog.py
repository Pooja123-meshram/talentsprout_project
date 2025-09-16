from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect,HttpResponse
from django.contrib import messages
from studentPost.forms import BlogPostForm , BlogImageForm, CandidatePreferenceForm ,BlogScheduleForm # Assuming you already have this form
from studentPost.models import BlogPost, CandidatePreference, BlogImage # Your blog model
from django.core.paginator import Paginator
from profiles.models import UserProfile
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404

from django.utils import timezone
from datetime import timedelta
from studentPost.utils import publish_scheduled_posts



def is_admin_user(user):
    return user.is_superuser or user.groups.filter(name='admin').exists()

@login_required
@user_passes_test(is_admin_user)
def admin_create_blog_post(request):
    if request.method == 'POST':
        blog_post_form = BlogPostForm(request.POST)
        candidate_preference_form = CandidatePreferenceForm(request.POST)
        blog_image_form = BlogImageForm(request.POST, request.FILES)

        if blog_post_form.is_valid() and candidate_preference_form.is_valid():
            blog_post = blog_post_form.save(commit=False)
            blog_post.user = request.user
            blog_post.save()

            preference = candidate_preference_form.save(commit=False)
            preference.blog_post = blog_post
            preference.save()

            for image_file in request.FILES.getlist('image'):
                BlogImage.objects.create(blog_post=blog_post, image=image_file)

            messages.success(request, 'Blog post created successfully!')
            return redirect('admin_blog_list')  # Change to your target view
        else:
            messages.error(request, 'There were errors in the form. Please fix them.')
    else:
        blog_post_form = BlogPostForm()
        candidate_preference_form = CandidatePreferenceForm()
        blog_image_form = BlogImageForm()

    return render(request, 'admin_customization/blog/blog_create.html', {
        'blog_post_form': blog_post_form,
        'candidate_preference_form': candidate_preference_form,
        'blog_image_form': blog_image_form
    })




@login_required
@user_passes_test(is_admin_user)
def admin_blog_post_list(request):
    publish_scheduled_posts()

    posts_list = BlogPost.objects.all().order_by('-publication_date')
    paginator = Paginator(posts_list, 12)  # 12 per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    profile_image_url = None
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            profile_image_url = user_profile.profile_image.url if user_profile.profile_image else None
        except UserProfile.DoesNotExist:
            profile_image_url = None

    context = {
        'posts': page_obj,
        'profile_image_url': profile_image_url,
    }
    return render(request, 'admin_customization/blog/admin_blog_post_list.html', context)



@login_required
@user_passes_test(is_admin_user)
def edit_blog_post(request, pk):
    blog_post = get_object_or_404(BlogPost, pk=pk)
    preference = CandidatePreference.objects.filter(blog_post=blog_post).first()

    if request.method == 'POST':
        blog_post_form = BlogPostForm(request.POST, instance=blog_post)
        preference_form = CandidatePreferenceForm(request.POST, instance=preference)
        image_form = BlogImageForm(request.POST, request.FILES)

        if blog_post_form.is_valid() and preference_form.is_valid():
            blog_post = blog_post_form.save()
            preference = preference_form.save(commit=False)
            preference.blog_post = blog_post
            preference.save()

            # Replace images if new ones uploaded
            if request.FILES.getlist('image'):
                BlogImage.objects.filter(blog_post=blog_post).delete()
                for image_file in request.FILES.getlist('image'):
                    BlogImage.objects.create(blog_post=blog_post, image=image_file)

            messages.success(request, 'Blog post updated successfully.')
            return redirect('admin_blog_list')
        else:
            messages.error(request, 'Error updating blog post.')
    else:
        blog_post_form = BlogPostForm(instance=blog_post)
        preference_form = CandidatePreferenceForm(instance=preference)
        image_form = BlogImageForm()

    return render(request, 'admin_customization/blog/blog_edit.html', {
        'blog_post_form': blog_post_form,
        'preference_form': preference_form,
        'image_form': image_form,
        'blog_post': blog_post,
    })

@login_required
@user_passes_test(is_admin_user)
def delete_blog_post(request, pk):
    post = BlogPost.objects.get(pk=pk)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Blog post deleted successfully.')
        return redirect('admin_blog_list')

    return render(request, 'admin_customization/blog/blog_delete.html', {'post': post})

@login_required
@user_passes_test(is_admin_user)
def hold_post(request, id):
    post = get_object_or_404(BlogPost, id=id)
    post.status = 'pending'
    post.save()
    messages.success(request, "Post put on hold.")
    return redirect('admin_blog_list')



@login_required
@user_passes_test(is_admin_user)
def publish_post(request, id):
    post = get_object_or_404(BlogPost, id=id)
    post.status = 'published'
    post.publication_date = timezone.now()
    post.save()
    messages.success(request, "Post published successfully.")
    return redirect('admin_blog_list')

@login_required
@user_passes_test(is_admin_user)
def schedule_post(request, id):
    post = get_object_or_404(BlogPost, id=id)

    if request.method == 'POST':
        form = BlogScheduleForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.status = 'scheduled'
            post.save()
            messages.success(request, 'Post scheduled successfully.')
            return redirect('admin_blog_list')
    else:
        form = BlogScheduleForm(instance=post)

    return render(request, 'admin_customization/blog/schedule_post.html', {'form': form, 'post': post})
