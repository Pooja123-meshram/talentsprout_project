from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Skill, Test, Answer ,ExamRule
from datetime import timedelta
from profiles.models import UserProfile



def test(request):
    profile_image_url = None
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            profile_image_url = user_profile.profile_image.url if user_profile.profile_image else None
        except UserProfile.DoesNotExist:
            profile_image_url = None
    return render(request, 'examination/test.html', {'profile_image_url':profile_image_url})

def choose_skill(request):
    profile_image_url = None
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            profile_image_url = user_profile.profile_image.url if user_profile.profile_image else None
        except UserProfile.DoesNotExist:
            profile_image_url = None
    skills = Skill.objects.all()

    return render(request, 'examination/choose_skill.html', {'skills': skills, 'profile_image_url':profile_image_url})

def rules_and_regulations(request):
    profile_image_url = None
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            profile_image_url = user_profile.profile_image.url if user_profile.profile_image else None
        except UserProfile.DoesNotExist:
            profile_image_url = None

    rules = ExamRule.objects.all()

    if request.method == "POST":
        # Mark the user as having accepted the rules
        request.session['accepted_rules'] = True  # Store in session
        return redirect('choose_skill')  # Redirect to choose_skill after acceptance

    context = {
        'rules': rules,
        'profile_image_url': profile_image_url,
        'site_header': "Examination Rules and Regulations"
    }
    return render(request, 'examination/rules_and_regulations.html', context)






@login_required
def start_test(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id)
    user = request.user

    profile_image_url = None
    try:
        user_profile = UserProfile.objects.get(user=user)
        profile_image_url = user_profile.profile_image.url if user_profile.profile_image else None
    except UserProfile.DoesNotExist:
        pass  # profile_image_url remains None

    # Determine whether it's the second attempt
    second_attempt = request.GET.get('second_attempt', 'false').lower() == 'true'

    # Fetch completed tests
    completed_tests = Test.objects.filter(user=user, skill=skill, completed=True).order_by('completed_date')

    if completed_tests.exists():
        latest_test = completed_tests.last()
        attempt_count = completed_tests.count()

        if latest_test.score is None:
            return render(request, 'examination/cannot_retake_test.html', {
                'message': "Your test result is being processed. Please wait until your score is available.",
                'profile_image_url': profile_image_url
            })

        if latest_test.is_passed():
            wait_days = 5
            if (timezone.now() - latest_test.completed_date).days < wait_days:
                next_attempt_date = latest_test.completed_date + timedelta(days=wait_days)
                return render(request, 'examination/cannot_retake_test.html', {
                    'next_attempt_date': next_attempt_date,
                    'message': f"You passed the exam. You can retake it after {next_attempt_date.strftime('%B %d, %Y, %I:%M %p')}.",
                    'profile_image_url': profile_image_url
                })

        else:
            wait_days = 5
            if attempt_count >= 2:
                return render(request, 'examination/cannot_retake_test.html', {
                    'next_attempt_date': None,
                    'message': "You have used all attempts for this skill. Please contact support for further help.",
                    'profile_image_url': profile_image_url
                })

            if (timezone.now() - latest_test.completed_date).days < wait_days:
                next_attempt_date = latest_test.completed_date + timedelta(days=wait_days)
                return render(request, 'examination/cannot_retake_test.html', {
                    'next_attempt_date': next_attempt_date,
                    'message': f"You did not pass the exam. You can reattempt after 5 days ({next_attempt_date.strftime('%B %d, %Y, %I:%M %p')}). Please use this time to review your materials.",
                    'profile_image_url': profile_image_url
                })

    # Create new test if not already started
    test, created = Test.objects.get_or_create(user=user, skill=skill, completed=False)

    if created or second_attempt:
        # Assign questions based on attempt type using is_second_attempt field
        if second_attempt:
            questions = skill.questions.filter(is_second_attempt=True).order_by('id')
        else:
            questions = skill.questions.filter(is_second_attempt=False).order_by('id')

        test.questions.set(questions)

    return redirect('take_test', test_id=test.id)

@login_required
def take_test(request, test_id):
    profile_image_url = None
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            profile_image_url = user_profile.profile_image.url if user_profile.profile_image else None
        except UserProfile.DoesNotExist:
            profile_image_url = None 
            
    test = get_object_or_404(Test, id=test_id, user=request.user)
    # questions = test.skill.questions.all()
    second_attempt = request.session.get('second_attempt', False)

    if second_attempt:
    # Only fetch questions marked for second attempt
        questions = test.skill.questions.filter(is_second_attempt=True).order_by('id')
    else:
    # Only fetch questions marked for first attempt
        questions = test.skill.questions.filter(is_second_attempt=False).order_by('id')


    
    for question in questions:
        if question.type == 'MCQ' and isinstance(question.options, list):
            question.options_list = question.options

    user_answers = {answer.question_id: answer.answer for answer in test.answers.all()}

    # Initialize error variable
    error = None    
    
    if request.method == 'POST':
        print("Processing POST request")
        for question in questions:
            answer_text = request.POST.get(f'question_{question.id}')
            print(f"Question {question.id}: Answer - {answer_text}")
            if not answer_text:
                error = 'All questions must be answered.'
                break
            is_correct = answer_text.strip().lower() == question.correct_answer.strip().lower()
            Answer.objects.update_or_create(
                test=test,
                question=question,
                defaults={'answer': answer_text, 'is_correct': is_correct}
            )

        if not error:
            test.completed = True
            test.completed_date = timezone.now()
            
            # test.calculate_total_score()

            test.save()
            print(f"Redirecting to test_completed with test_id: {test.id}")
            return redirect('test_completed', test_id=test.id)

    return render(request, 'examination/take_test.html', {
        'test': test,
        'questions': questions,
        'profile_image_url': profile_image_url,
        'user_answers': user_answers,
        'error': error
    })

@login_required
def test_completed(request, test_id):
    # user_profile = UserProfile.objects.get(user=request.user)
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    profile_image_url = user_profile.profile_image.url if user_profile.profile_image else None    
    test = get_object_or_404(Test, id=test_id, user=request.user)
    return render(request, 'examination/test_completed.html', {'test': test, 'home_url': '/' ,'profile_image_url':profile_image_url})