"""
URL configuration for ZYN_Campaign project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp.views import ageRestrict,send_otp,verify_otp,signup,signin,email_taking,email_verification,verify_email,pointsAccumulated,purchaseFromZYN,getRewardCode,claimMerchandize,redeemProduct,survey_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('rewardCodes', getRewardCode, name="rewardCodes"),
    path('',ageRestrict,name="ageRestrict"),
    path("send-otp",send_otp,name="send-otp"),
    path("verify-otp",verify_otp,name="verify-otp"),
    path('signup',signup,name="signup"),
    path("signin",signin,name="signin"),
    path('emailTaking',email_taking,name="emailTaking"),
    path('emailVerification',email_verification,name="emailVerification"),
    path('verifyEmail/', verify_email, name='verifyEmail'),
    path("pointsAccumulated",pointsAccumulated , name="pointsAccumulated"),
    path("purchaseFromZYN",purchaseFromZYN,name="purchaseFromZYN"),
    path('claimMerchandize',claimMerchandize,name="claimMerchandize"),
    path('redeem/<int:product_id>/', redeemProduct, name='redeem_product'),
    path('survey', survey_view, name='survey'),


]
