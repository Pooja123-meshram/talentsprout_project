from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from django.http import Http404, HttpResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import Payment, Profile, Subscription
from signUp.models import CustomUser
import logging
from decimal import Decimal
import razorpay
from notifications.signals import notify
from profiles.models import UserProfile

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

logger = logging.getLogger(__name__)

@login_required
def payment_page(request, candidate_id,subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id)

    candidate = get_object_or_404(CustomUser, id=candidate_id, role='candidate')

    subscription_price = Decimal(subscription.price)
    

   
    service_fee = round(subscription_price * Decimal('0.02'), 2)
    gst = round(subscription_price * Decimal('0.18'), 2)
    total_amount = round(subscription_price + service_fee + gst, 2)
    


    profile_image_url = None
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            profile_image_url = user_profile.profile_image.url if user_profile.profile_image else None
        except UserProfile.DoesNotExist:
            profile_image_url = None

    razorpay_order = razorpay_client.order.create({
        'amount': int(total_amount * 100),  # Convert to paise
        'currency': 'INR',
        'payment_capture': '1'
    })
    razorpay_order_id = razorpay_order['id']

    # Set the callback URL with HTTPS
    callback_url = request.build_absolute_uri(reverse('payment_callback'))

    return render(request, 'payment/payment_page.html', {
        'subscription': subscription,
        'service_fee': service_fee,
        'gst': gst,
        'total_amount': total_amount,
        'razorpay_order_id': razorpay_order_id,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'callback_url': callback_url,
        'profile_image_url':profile_image_url,
        'candidate':candidate,
        'user_profile':user_profile,
    })


@login_required
def payment_callback(request):
    if request.method == 'POST':
        try:
            razorpay_payment_id = request.POST.get('razorpay_payment_id')
            razorpay_order_id = request.POST.get('razorpay_order_id')
            razorpay_signature = request.POST.get('razorpay_signature')

            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            razorpay_client.utility.verify_payment_signature(params_dict)

            payment_details = razorpay_client.payment.fetch(razorpay_payment_id)
            amount = Decimal(payment_details['amount']) / 100  # Convert paise to INR
            
            # Get the profile of the logged-in user
            user_profile = get_object_or_404(Profile, user=request.user)
            preferred_candidate_username = user_profile.preferred_candidate_username
            
            if not preferred_candidate_username:
                raise Http404("Preferred candidate not specified.")
            


            payment, created = Payment.objects.update_or_create(
                razorpay_payment_id=razorpay_payment_id,
                defaults={
                    'recruiter': request.user,
                     'candidate_username': preferred_candidate_username,
                    'amount': amount,
                    'razorpay_order_id': razorpay_order_id,
                    'razorpay_signature': razorpay_signature,
                    'status': 'successful'
                }
            )

            context = {
                'recruiter': request.user,
                'candidate_name': request.user.profile.preferred_candidate_name,
                'candidate_username': request.user.profile.preferred_candidate_username,
                'amount': amount,
                'payment_method': 'Razorpay',
                'date': payment.payment_date
            }
            
            subject = 'Payment Confirmation and Invoice'
            html_message = render_to_string('payment/invoice.html', context)
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = request.user.email

            msg = EmailMultiAlternatives(subject, html_message, from_email, [to_email])
            msg.attach_alternative(html_message, "text/html")
            msg.send()

            logger.info("Email sent successfully")
            messages.success(request, 'Payment processed successfully! An invoice has been sent to your email.')
            # Redirect to success page with payment_id
            return redirect(reverse('payment_successful') + f'?payment_id={razorpay_payment_id}')

        except razorpay.errors.SignatureVerificationError as e:
            logger.error(f'Razorpay Signature Verification Error: {e}')
            messages.error(request, 'Payment verification failed. Please try again.')

            Payment.objects.update_or_create(
                razorpay_payment_id=razorpay_payment_id,
                defaults={
                    'recruiter': request.user,
                     'candidate_username': preferred_candidate_username,
                    'amount': Decimal(request.POST.get('amount', '0')) / 100,
                    'razorpay_order_id': razorpay_order_id,
                    'razorpay_signature': razorpay_signature,
                    'status': 'failed'
                }
            )
            return redirect('payment_failed', error_code='INVALID_SIGNATURE', error_description=str(e))

        except Exception as e:
            logger.error(f'Error processing payment callback: {e}')
            messages.error(request, 'An error occurred while processing the payment. Please try again later.')

            Payment.objects.update_or_create(
                razorpay_payment_id=razorpay_payment_id,
                defaults={
                    'recruiter': request.user,
                    'candidate_username': preferred_candidate_username,
                    'amount': Decimal(request.POST.get('amount', '0')) / 100,
                    'razorpay_order_id': razorpay_order_id,
                    'razorpay_signature': razorpay_signature,
                    'status': 'failed'
                }
            )
            return redirect('payment_failed', error_code='UNKNOWN_ERROR', error_description=str(e))

    return HttpResponse("Payment callback received.")



# @login_required
# def custom_payment(request):
#     """
#     A custom payment view for handling special payment scenarios.
#     """
#     # Manually define custom price and description for the custom payment
#     custom_amount = Decimal(request.POST.get('custom_amount', '0'))
#     description = request.POST.get('description', 'Custom Payment')
    
#     if custom_amount <= 0:
#         messages.error(request, 'Invalid amount provided.')
#         return redirect('custom_payment')

#     # ✅ Calculate service fee (2%) and GST (18%)
#     service_fee = round(custom_amount * Decimal('0.02'), 2)
#     gst = round(custom_amount * Decimal('0.18'), 2)
#     total_amount = round(custom_amount + service_fee + gst, 2)

#     # Create Razorpay order
#     razorpay_order = razorpay_client.order.create({
#         'amount': int(total_amount * 100),  # Convert to paise
#         'currency': 'INR',
#         'payment_capture': '1'
#     })
#     razorpay_order_id = razorpay_order['id']

#     # Set the callback URL
#     callback_url = request.build_absolute_uri(reverse('payment_callback'))

#     # Fetch profile image URL
#     profile_image_url = None
#     try:
#         user_profile = UserProfile.objects.get(user=request.user)
#         profile_image_url = user_profile.profile_image.url if user_profile.profile_image else None
#     except UserProfile.DoesNotExist:
#         profile_image_url = None

#     return render(request, 'payment/custom_payment.html', {
#         'custom_amount': custom_amount,
#         'description': description,
#         'service_fee': service_fee,
#         'gst': gst,
#         'total_amount': total_amount,
#         'razorpay_order_id': razorpay_order_id,
#         'razorpay_key_id': settings.RAZORPAY_KEY_ID,
#         'callback_url': callback_url,
#         'profile_image_url': profile_image_url,
#         'user_profile':user_profile,
#     })


@login_required
def custom_payment(request, candidate_id):
    candidate = get_object_or_404(CustomUser, id=candidate_id, role='candidate')

    profile_image_url = None
    user_profile = None
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        profile_image_url = user_profile.profile_image.url if user_profile.profile_image else None
    except UserProfile.DoesNotExist:
        pass

    if request.method == 'POST':
        custom_amount = Decimal(request.POST.get('custom_amount', '0'))
        description = request.POST.get('description', 'Custom Payment')

        if custom_amount <= 0:
            messages.error(request, 'Invalid amount provided.')
            return redirect('subscription_list', candidate_id=candidate_id)

        service_fee = round(custom_amount * Decimal('0.02'), 2)
        gst = round(custom_amount * Decimal('0.18'), 2)
        total_amount = round(custom_amount + service_fee + gst, 2)

        razorpay_order = razorpay_client.order.create({
            'amount': int(total_amount * 100),
            'currency': 'INR',
            'payment_capture': '1'
        })

        callback_url = request.build_absolute_uri(reverse('payment_callback'))

        return render(request, 'payment/custom_payment.html', {
            'custom_amount': custom_amount,
            'description': description,
            'service_fee': service_fee,
            'gst': gst,
            'total_amount': total_amount,
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'callback_url': callback_url,
            'profile_image_url': profile_image_url,
            'user_profile': user_profile,
            'candidate': candidate,
        })

    # If GET request: Show empty form
    return render(request, 'payment/custom_payment.html', {
        'custom_amount': None,
        'description': None,
        'profile_image_url': profile_image_url,
        'user_profile': user_profile,
        'candidate': candidate,
    })



@login_required
def edit_billing_info(request, candidate_id, subscription_id):
    candidate = get_object_or_404(CustomUser, id=candidate_id, role='candidate')

    # Fix: use Profile instead of UserProfile
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        profile.full_name = request.POST.get('full_name', '')  # use full_name if that’s the field name
        profile.company_name = request.POST.get('company_name', '')
        profile.country = request.POST.get('country', '')
        profile.state = request.POST.get('state', '')
        profile.address = request.POST.get('address', '')
        profile.city = request.POST.get('city', '')
        profile.postal_code = request.POST.get('postal_code', '')
        profile.is_indian_citizen = request.POST.get('is_indian_citizen') == 'yes'
        profile.receive_invoices_via_email = 'receive_invoices_via_email' in request.POST
        profile.preferred_candidate_name = request.POST.get('preferred_candidate_name', '')
        profile.preferred_candidate_username = request.POST.get('preferred_candidate_username', '')
        profile.save()

        # Redirect after saving
        if subscription_id == 'custom':
            request.session['custom_amount'] = request.POST.get('custom_amount', '0')
            request.session['description'] = request.POST.get('description', 'Custom Payment')
            return redirect('custom_payment', candidate_id=candidate_id)
        else:
            return redirect('payment_page', candidate_id=candidate_id, subscription_id=subscription_id)

    return render(request, 'payment/edit_billing_info.html', {
        'profile': profile,
        'subscription_id': subscription_id,
        'candidate_id': candidate_id,
        'candidate': candidate,
    })



def subscription_list(request, candidate_id):
     # Get the candidate object (only if role is 'candidate')
    candidate = get_object_or_404(CustomUser, id=candidate_id, role='candidate')

    profile_image_url = None
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            profile_image_url = user_profile.profile_image.url if user_profile.profile_image else None
        except UserProfile.DoesNotExist:
            profile_image_url = None

    subscriptions = Subscription.objects.all()
    for subscription in subscriptions:
        subscription.features_list = subscription.features.split(",")

    return render(request, 'payment/subscription_list.html', {
        'subscriptions': subscriptions,
        'profile_image_url': profile_image_url,
        'candidate': candidate,
    })


def payment_failed(request):
    error_code = request.GET.get('error_code')
    error_description = request.GET.get('error_description')

    profile_image_url = None
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            profile_image_url = user_profile.profile_image.url if user_profile.profile_image else None
        except UserProfile.DoesNotExist:
            profile_image_url = None

    return render(request, 'payment/payment_failed.html', {
        'error_code': error_code,
        'error_description': error_description,
        'profile_image_url': profile_image_url,
    })


@login_required
def payment_successful(request):
    payment_id = request.GET.get('payment_id')
    
    if not payment_id:
        return render(request, 'payment/payment_failed.html', {
            'error_code': 'MISSING_PAYMENT_ID',
            'error_description': 'Payment ID is missing in the request.'
        })

    try:
        payment = get_object_or_404(Payment, razorpay_payment_id=payment_id)

        # Ensure candidate is the preferred candidate
        preferred_candidate_username = request.user.profile.preferred_candidate_username
        
        if not preferred_candidate_username:
            raise Http404("Preferred candidate not specified.")
        
        # Set candidate_username field to the preferred candidate username
        if payment.candidate_username != preferred_candidate_username:
            payment.candidate_username = preferred_candidate_username
            payment.save()

    except Profile.DoesNotExist:
        return render(request, 'payment/payment_failed.html', {
            'error_code': 'CANDIDATE_NOT_FOUND',
            'error_description': f'Preferred candidate with username {preferred_candidate_username} does not exist.'
        })

    except Http404:
        return render(request, 'payment/payment_failed.html', {
            'error_code': 'PAYMENT_NOT_FOUND',
            'error_description': f'No payment found with ID: {payment_id}'
        })

    profile_image_url = None
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            profile_image_url = user_profile.profile_image.url if user_profile.profile_image else None
        except UserProfile.DoesNotExist:
            profile_image_url = None
    
    # Prepare notification context
    context = {
        'recruiter': request.user,
        'candidate_name': preferred_candidate_username,
        'amount': payment.amount,
        'payment_method': 'Razorpay',
        'date': payment.payment_date,
        'payment_id': payment_id,
        'profile_image_url': profile_image_url,
    }
    
    # Send notifications
    notify.send(
        request.user,
        recipient=request.user,
        verb='Payment successful',
        description=f'Your payment of INR {payment.amount} was successful.'
    )

    # Notify candidate if available
    if preferred_candidate_username:
        candidate_user = get_object_or_404(CustomUser, username=preferred_candidate_username)
        notify.send(
            request.user,
            recipient=candidate_user,
            verb='Payment has been made for you',
            description=f'A payment of INR {payment.amount} has been made for you.'
        )

    # Notify admins
    admins = CustomUser.objects.filter(is_superuser=True)
    for admin in admins:
        notify.send(
            request.user,
            recipient=admin,
            verb='Payment notification',
            description=f'A payment of INR {payment.amount} was made by {request.user.username}.'
        )

    return render(request, 'payment/payment_successful.html', context )





