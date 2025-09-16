from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import send_mail
from django.contrib import messages
from signUp.models import CustomUser
from progress_tracker.models import ProjectDetails
from django.utils.timezone import now
from django.db.models import Count, Sum
from django.db.models.functions import ExtractMonth
import calendar
from payment.models import Payment
from django.contrib.auth.decorators import login_required
from .views import admin_required

def is_admin(user):
    return user.is_superuser or user.is_staff

@login_required    
@admin_required

def admin_clients(request):
    # Total recruiters (clients)
    total_clients = CustomUser.objects.filter(role=CustomUser.RECRUITER).count()

    # Recruiters with at least one assigned project
    clients_with_projects = CustomUser.objects.filter(
        role=CustomUser.RECRUITER,
        assigned_projects__isnull=False
    ).distinct().count()

    # Total amount paid by all recruiters
    total_payments = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0

    # Monthly signup analytics
    current_year = now().year
    clients_by_month = CustomUser.objects.filter(role=CustomUser.RECRUITER, date_joined__year=current_year) \
        .annotate(month=ExtractMonth('date_joined')) \
        .values('month') \
        .annotate(count=Count('id')) \
        .order_by('month')

    months = [calendar.month_name[i] for i in range(1, 13)]
    client_counts = [0] * 12
    for entry in clients_by_month:
        client_counts[entry['month'] - 1] = entry['count']

    # Recruiter-level analytics (name, total payments, total projects)
    recruiter_data = CustomUser.objects.filter(role=CustomUser.RECRUITER).annotate(
        total_paid=Sum('payments_made__amount'),
        project_count=Count('assigned_projects')
    )

    context = {
        'total_clients': total_clients,
        'clients_with_projects': clients_with_projects,
        'client_total_payments': total_payments,
        'months': months,
        'client_counts': client_counts,
        'month_data': zip(months, client_counts),
        'recruiter_data': recruiter_data,
    }
    return render(request, 'admin_customization/clients/admin_clients.html', context)



@login_required    
@admin_required
def admin_candidates(request):
    candidates = CustomUser.objects.filter(role=CustomUser.CANDIDATE)
    total_candidates = candidates.count()
    appeared_candidates = candidates.filter(tests__completed=True).distinct().count()
    took_project_candidates = candidates.filter(received_projects__isnull=False).distinct().count()
    # Get candidates with a test score below 60
    failed_candidates = candidates.filter(tests__completed=True, tests__score__lt=60).distinct().count()
    pending_exam_candidates = candidates.exclude(tests__completed=True).distinct()


    context = {
        'total_candidates': total_candidates,
        'appeared_candidates': appeared_candidates,
        'took_project_candidates': took_project_candidates,
        'failed_candidates': failed_candidates,
        'pending_exam_candidates': pending_exam_candidates,
    }
    return render(request, 'admin_customization/clients/admin_candidates.html', context)



@login_required    
@admin_required
def send_reminder_email(request, user_id):
    candidate = get_object_or_404(CustomUser, id=user_id, role=CustomUser.CANDIDATE)

    subject = "Reminder: Complete Your Exam to Move Forward"
    message = f"""Hi {candidate.username},

We noticed you haven’t submitted your exam yet on TalentSprout. Completing your exam is the first step towards unlocking exciting projects and real opportunities.

If you’re facing any issues or need help, feel free to reach out to our team. We’re here to support you.

Don’t miss out—submit your exam today and take the next step in your journey!

Best regards,  
TalentSprout"""

    send_mail(subject, message, 'noreply@talentsprout.com', [candidate.email])
    messages.success(request, f"Reminder sent to {candidate.email}")
    return redirect('admin_candidates')
