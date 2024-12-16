from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from myapp.models import UserProfile,RewardCode,DiscountCode  
import json
from django.shortcuts import render

def ageRestrict(request):

    return render(request,"ageRestrict.html" )




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

            if not fname or not lname:
                return JsonResponse({'success': False, 'message': 'First and last name are required.'}, status=400)
            if not contactNo or len(contactNo) != 11 or not contactNo.isdigit():
                return JsonResponse({'success': False, 'message': 'Contact number must be 11 digits.'}, status=400)
            if not signuppassword or len(signuppassword) < 6:
                return JsonResponse({'success': False, 'message': 'Password must be at least 6 characters long.'}, status=400)
            if not rewardCode or not rewardCode.startswith('SR06-') or len(rewardCode.split('-')[1]) != 5:
                return JsonResponse({'success': False, 'message': 'Invalid reward code format.'}, status=400)

            if UserProfile.objects.filter(contact_no=contactNo).exists():
                return JsonResponse({'success': False, 'message': 'User with this contact number already exists.'}, status=400)

            try:
                reward = RewardCode.objects.get(code=rewardCode, is_used=False)
            except RewardCode.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Invalid or already used reward code.'}, status=400)

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
            reward.is_used = True 
            reward.save()

            return JsonResponse({'success': True, 'message': 'User created successfully. Points accumulated: 10.'}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {str(e)}'}, status=500)

    return render(request, "signup.html")

def signin(request):
    if request.method == "POST":
        try:
            # Parse the incoming JSON request body
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
                    return JsonResponse({'success': True, 'message': 'Login successful.'}, status=200)
                else:
                    return JsonResponse({'success': False, 'message': 'Invalid password.'}, status=400)
            except UserProfile.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'User with this contact number does not exist.'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON format.'}, status=400)
        
    return render(request, "signin.html")

@login_required
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
            if user_profile.point_accumulated + 10 > 800:
                return JsonResponse({'success': False, 'message': 'You cannot exceed the maximum points of 800.'}, status=400)

            # Update user's points and mark reward code as used
            user_profile.point_accumulated += 10
            reward_code.is_used = True
            reward_code.save()
            user_profile.save()

            return JsonResponse({'success': True, 'pointsAccumulated': user_profile.point_accumulated}, status=200)

        except UserProfile.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User profile not found.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)


@login_required
def pointsAccumulated(request):
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    point_accumulated = user_profile.point_accumulated

    return render(request,"pointsAccumulated.html" ,{'points_accumulated':point_accumulated})

from django.shortcuts import render
from .models import UserProfile, DiscountCode

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
