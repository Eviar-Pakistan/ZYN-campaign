from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from myapp.models import UserProfile,RewardCode,DiscountCode,Product,SurveyOption,SurveyQuestion  
import json
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import SurveyQuestion
from django.core.mail import send_mail
from ZYN_Campaign.settings import EMAIL_HOST_USER,api_key,from_number
import requests

def ageRestrict(request):

    return render(request,"ageRestrict.html" )


def send_otp(request):
    if request.method == "POST":
        data = json.loads(request.body)

        contact_no =  data.get('contactNo')

        url = f'https://api.itelservices.net/sendotp.php?type=php&api_key={api_key}&number={contact_no}&from={from_number}&template=Welcome to ZYN Your verification code is: [otp]. Please enter this code to complete your registration.'
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return JsonResponse({'success': True, 'message': 'OTP sent successfully.'}, status=200)
            else:
                return JsonResponse({'success': False, 'message': f'Failed to send OTP: {response.text}'}, status=500)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)
        
@csrf_exempt
def verify_otp(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            contact_no = data.get('contactNo')  # Ensure 'contactNo' is coming as expected
            otp = data.get('otpInput')  # Ensure 'otpInput' is coming as expected
            print(data)
            # Verify OTP with ITel API
            url = f'https://api.itelservices.net/sendotp.php?type=php&api_key=TEbVJ1uBlNCZ0gWYmVmTjtl9LOt0IvUe&number={contact_no}&from=998008&otp={otp}'
            
            response = requests.get(url)

            if response.status_code == 200 and "success" in response.text:
                # OTP verified successfully, proceed to signup
                return JsonResponse({'success': True, 'message': 'OTP verified successfully.'}, status=200)
            else:
                return JsonResponse({'success': False, 'message': 'Invalid OTP or error in verification.'}, status=400)

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)


# Function to signup user after OTP verification
@csrf_exempt
def signup(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            fname = data.get('fname')
            lname = data.get('lname')
            contactNo = data.get('contactNo')
            signuppassword = data.get('signuppassword')
            rewardCode = data.get('rewardCode')

            # Validate input fields
            if not fname or not lname:
                return JsonResponse({'success': False, 'message': 'First and last name are required.'}, status=400)
            if not contactNo or len(contactNo) != 11 or not contactNo.isdigit():
                return JsonResponse({'success': False, 'message': 'Contact number must be 11 digits.'}, status=400)
            if not signuppassword or len(signuppassword) < 6:
                return JsonResponse({'success': False, 'message': 'Password must be at least 6 characters long.'}, status=400)
            if not rewardCode or not rewardCode.startswith('SR06-') or len(rewardCode.split('-')[1]) != 5:
                return JsonResponse({'success': False, 'message': 'Invalid reward code format.'}, status=400)

            # Check if the user already exists
            if UserProfile.objects.filter(contact_no=contactNo).exists():
                return JsonResponse({'success': False, 'message': 'User with this contact number already exists.'}, status=400)

            # Verify reward code
            try:
                reward = RewardCode.objects.get(code=rewardCode, is_used=False)
            except RewardCode.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Invalid or already used reward code.'}, status=400)

            # Create the user
            user = User.objects.create_user(
                username=f"{fname.lower()}{lname.lower()}{contactNo[-4:]}",
                first_name=fname,
                last_name=lname,
                password=signuppassword
            )

            UserProfile.objects.create(
                user=user,
                contact_no=contactNo,
                reward_code=rewardCode,
                point_accumulated=10
            )

            # Mark reward code as used
            reward.is_used = True
            reward.save()

            # Return success response
            return JsonResponse({'success': True, 'message': 'User created successfully. Points accumulated: 10.'}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {str(e)}'}, status=500)

    return render(request, "signup.html")

from django.shortcuts import redirect

from django.contrib.auth import authenticate, login
from django.shortcuts import render
from django.http import JsonResponse
import json
from .models import UserProfile

def signin(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            contact_no = data.get('contactNo')
            password = data.get('password')

            if not contact_no or not password:
                return JsonResponse({'success': False, 'message': 'Contact no & password are required.'}, status=400)

            try:
                user_profile = UserProfile.objects.get(contact_no=contact_no)
                user = authenticate(request, username=user_profile.user.username, password=password)

                if user is not None:
                    login(request, user)

                    # Store the user ID in the session
                    request.session['user_id'] = user.id

                    if not user.profile.email:
                        return JsonResponse({'success': True, 'redirect': '/emailTaking'}, status=200)
                    elif not user_profile.email_verified:
                        return JsonResponse({'success': True, 'redirect': '/emailVerification'}, status=200)
                    else:
                        return JsonResponse({'success': True, 'redirect': 'pointsAccumulated'}, status=200)
                else:
                    return JsonResponse({'success': False, 'message': 'Invalid password.'}, status=400)
            except UserProfile.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'User with this contact number does not exist.'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON format.'}, status=400)

    return render(request, "signin.html")



@login_required
def email_taking(request):
    if request.method == "POST":
        profile = request.user.profile
        data = json.loads(request.body)
        email = data.get('email')
        if email:
            profile.email = email
            profile.save()
            return JsonResponse({'success': True, 'redirect': '/emailVerification'}, status=200)
        else:
            return JsonResponse({'success': True, 'redirect': '/pointsAccumulated'}, status=200)
    return render(request, "emailTaking.html") 

from allauth.socialaccount.signals import pre_social_login
from django.dispatch import receiver
from django.contrib.auth.models import User
from myapp.models import UserProfile

# Signal to update profile without changing the user session
@receiver(pre_social_login)
def update_profile_with_google_email(sender, request, sociallogin, **kwargs):
    # Get the Google email from the social login data
    google_email = sociallogin.account.extra_data.get('email')
    
    # Only update if the email is available
    if google_email:
        user = request.user  # Get the current logged-in user
        profile = user.profile  # Access the user's profile

        # Update the user's profile email if it's empty or different from the Google email
        if not profile.email or profile.email != google_email:
            profile.email = google_email
            profile.email_verified = True  # Mark as verified or add your logic here
            profile.save()

    # You can perform additional checks here if needed (like verifying if the email already exists)






@login_required
def email_verification(request):
    if request.method == "POST":
        user = request.user
        # Simulate sending an email verification (replace with real logic)
        verification_link = request.build_absolute_uri(f"/verifyEmail?user={user.id}")
        send_mail(
            'Email Verification',
            f'Click the link to verify your email: {verification_link}',
            EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        return JsonResponse({'success': True, 'message': 'Verification email sent.'}, status=200)
    return render(request, "emailVerification.html")

@login_required
def verify_email(request):
    user = request.user

    user.profile.email_verified = True
    user.profile.save()
    return redirect("pointsAccumulated")



@login_required(login_url= "signin")
def getRewardCode(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            reward_code_input = data.get('rewardCode')

            # Check if reward code exists and is not used
            reward_code = RewardCode.objects.filter(code=reward_code_input).first()
            if not reward_code:
                return JsonResponse({'success': False, 'message': 'Invalid reward code.'}, status=400)
            if reward_code.is_used:
                return JsonResponse({'success': False, 'message': 'This reward code is expired.'}, status=400)

            # Get the logged-in user's profile
            user = request.user  
            user_profile = UserProfile.objects.get(user=user)

            # Ensure the user does not exceed the maximum points (800)
            if user_profile.point_accumulated + 80 > 800:
                return JsonResponse({'success': False, 'message': 'You cannot exceed the maximum points of 800.'}, status=400)

            # Update user's points and mark reward code as used
            user_profile.point_accumulated += 80
            reward_code.is_used = True
            reward_code.save()
            user_profile.save()

            return JsonResponse({'success': True, 'pointsAccumulated': user_profile.point_accumulated}, status=200)

        except UserProfile.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User profile not found.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)



@login_required(login_url="signin")
def pointsAccumulated(request):
    # Retrieve user ID from session
    user_id = request.session.get('user_id')

    if user_id:
        try:
            # Retrieve user profile based on user_id stored in session
            user_profile = UserProfile.objects.get(user_id=user_id)
            email = user_profile.email

            # Award points only if email is verified and points haven't been awarded yet
            if user_profile.email_verified and not user_profile.points_awarded_for_email:
                user_profile.point_accumulated += 40  # Increment points
                user_profile.points_awarded_for_email = True  # Mark points as awarded
                user_profile.save()  # Save the changes to the database

            # Get the current points from the profile
            points_accumulated = user_profile.point_accumulated

            return render(request, "pointsAccumulated.html", {'points_accumulated': points_accumulated})
        except UserProfile.DoesNotExist:
            # Handle case where UserProfile does not exist
            return redirect("signin")  # Redirect to signin page if profile does not exist
    else:
        # If the user_id is not in the session, redirect to signin page
        return redirect("signin")





@login_required(login_url = "signin")
def purchaseFromZYN(request):
    user = request.user
    try:
        # Get the user profile
        user_profile = UserProfile.objects.get(user=user)
        point_accumulated = user_profile.point_accumulated

        eligible_discount_codes = DiscountCode.objects.filter(points_required=point_accumulated)

        return render(request, "purchaseFromZYN.html", {
            "point_accumulated": point_accumulated,
            "eligible_discount_codes": eligible_discount_codes,
        })

    except UserProfile.DoesNotExist:
        return render(request, "purchaseFromZYN.html", {
            "error": "User profile not found.",
        })


def claimMerchandize(request):
    user_profile = request.user.profile  
    user_points = user_profile.point_accumulated 
    products = Product.objects.all()

    context = {
        'products': products,
        'user_points': user_points,
    }

    return render(request, 'claimMerchandize.html', context)

def redeemProduct(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user_profile = request.user.profile

    if user_profile.point_accumulated >= product.required_points:
        # Deduct points from the user's profile
        user_profile.point_accumulated -= product.required_points
        user_profile.save()
        return redirect('claimMerchandize')
    return redirect('claimMerchandize')

@login_required
def survey_view(request):
    questions = SurveyQuestion.objects.all().order_by('created_at') 

    paginator = Paginator(questions, 1)
    page_number = request.GET.get('page')  
    page_obj = paginator.get_page(page_number)

    if request.method == "POST":
        # Handle the form submission
        selected_option_id = request.POST.get('option')
        if selected_option_id:
            selected_option = SurveyOption.objects.get(id=selected_option_id)

            print(f"User selected: {selected_option.option_text}")

            if page_obj.has_next():
                return redirect("survey")
            else:
                return redirect("survey") 

    return render(request, 'surveyQuestions.html', {'page_obj': page_obj})