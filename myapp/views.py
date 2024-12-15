from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from myapp.models import UserProfile  # Import the UserProfile model
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

            # Validation
            if not fname or not lname:
                return JsonResponse({'success': False, 'message': 'First and last name are required.'}, status=400)
            if not contactNo or len(contactNo) != 11 or not contactNo.isdigit():
                return JsonResponse({'success': False, 'message': 'Contact number must be 10 digits.'}, status=400)
            if not signuppassword or len(signuppassword) < 6:
                return JsonResponse({'success': False, 'message': 'Password must be at least 6 characters long.'}, status=400)
            if not rewardCode or not rewardCode.startswith('SR06-') or len(rewardCode.split('-')[1]) != 5:
                return JsonResponse({'success': False, 'message': 'Invalid reward code.'}, status=400)

            if UserProfile.objects.filter(contact_no=contactNo).exists():
                return JsonResponse({'success': False, 'message': 'User with this contact number already exists.'}, status=400)

            user = User.objects.create_user(
                username=f"{fname.lower()}{lname.lower()}{contactNo[-4:]}",
                first_name=fname,
                last_name=lname,
                password=signuppassword
            )
            UserProfile.objects.create(
                user=user,
                contact_no=contactNo,
                reward_code=rewardCode
            )

            return JsonResponse({'success': True, 'message': 'User created successfully.'}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {str(e)}'}, status=500)

    return render(request, "signup.html")


import json
from django.http import JsonResponse
from django.contrib.auth import authenticate, login

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
