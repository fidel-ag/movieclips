from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.urls import reverse
from .forms import RegistrationForm, LoginForm
from .models import LoginAttempt, User
from .token import account_activation_token
from .decorators import unauthenticated_user
from .utils import retrieve_Number_of_coins,send_welcome_email_html,get_token,send_password_reset,send_client_message
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import stripe
from django.http import JsonResponse
@csrf_exempt
@unauthenticated_user
def signup_page_free_trial(request):
    form = RegistrationForm()
    if request.method == 'POST':
        email=request.POST.get("email")
        username=request.POST.get("FullName")
        password=request.POST.get("password")
        Confirmpassword=request.POST.get("Confirmpassword")
        form=RegistrationForm(data={'email': email, 'password1': password, 'password2': Confirmpassword})
        if form.is_valid():
            user = form.save()
            user.set_coins(0)
            user.set_stripe_subscription_id("")
            user.set_subscription_active(False)
            user.username=username
            user.is_active = False
            user.save()
            token=get_token(user)

            send_welcome_email_html(user.email, user.username.split(" ")[0],settings.REDIRECT_DOMAIN+f"/accounts/activate_account_page/{token['uid']}/{token['token']}")
            login_attempt, created = LoginAttempt.objects.get_or_create(user=user)
            return redirect(reverse("accounts:login"))
        else:
            if form.errors:
                for field in form:
                    for error in field.errors:
                        messages.error(request, error)
            form = RegistrationForm()
            context = {
            'form': form}
            return render(request, 'accounts/signupfreetrial.html', context)

            

    if request.method == 'GET':
        context = {
            'form': form
        }
        print('aaaaaaaaaaa')
        return render(request, 'accounts/signupfreetrial.html', context)

@csrf_exempt
@unauthenticated_user
def signup_page(request):
    form = RegistrationForm()
    if request.method == 'POST':
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY_TEST
            checkout_session_id = request.GET.get('session_id', None)
            session = stripe.checkout.Session.retrieve(checkout_session_id)
            username=session.customer_details.name
            subscription_id=session.subscription
            payment_id=stripe.Subscription.retrieve(subscription_id).plan.id
        except:
            return redirect(reverse("accounts:login"))
        number_of_coin=(retrieve_Number_of_coins(payment_id,settings.PRODUCT_PRICE))
        email=request.POST.get("email")
        password=request.POST.get("password")
        Confirmpassword=request.POST.get("Confirmpassword")
        form=RegistrationForm(data={'email': email, 'password1': password, 'password2': Confirmpassword})
        if form.is_valid():
            user = form.save()
            user.set_coins(number_of_coin)
            user.set_stripe_subscription_id(subscription_id)
            user.set_subscription_active(True)
            user.username=username
           
            user.is_active = True
            user.save()
            token=get_token(user)
            send_welcome_email_html(user.email, user.username.split(" ")[0],settings.REDIRECT_DOMAIN+f"/accounts/activate_account_page/{token['uid']}/{token['token']}")
            login_attempt, created = LoginAttempt.objects.get_or_create(user=user)
            if login_attempt.login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                login_attempt.login_attempts = 0
                login_attempt.save()
                messages.success(request, 'Account restored, you can now proceed to login')
                return redirect(reverse("accounts:login"))
            else:
                messages.success(request, 'Thank you for confirming your email. You can now login.')
                return redirect(reverse("accounts:login"))
        else:
            if form.errors:
                for field in form:
                    for error in field.errors:
                        messages.error(request, error)
            form = RegistrationForm()
    if request.method == 'GET':
        try:

            stripe.api_key = settings.STRIPE_SECRET_KEY_TEST
            checkout_session_id = request.GET.get('session_id', None)
            session = stripe.checkout.Session.retrieve(checkout_session_id)
            username=session.customer_details.name
            subscription_id=session.subscription
            payment_id=stripe.Subscription.retrieve(subscription_id).plan.id
        except:
            return redirect(reverse("accounts:login"))
        context = {
            'form': form
        }
        return render(request, 'accounts/signup.html', context)

@csrf_exempt
@unauthenticated_user
def login_page(request):
    form=LoginForm()
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        form=LoginForm(data={'email': email, 'password': password})
        if form.is_valid():
            now = timezone.now()
            try:
                _user = User.objects.get(email=email)
                login_attempt, created = LoginAttempt.objects.get_or_create(user=_user)  # get the user's login attempt
                if (login_attempt.timestamp + timedelta(seconds=settings.LOGIN_ATTEMPTS_TIME_LIMIT)) < now:
                    user = authenticate(request, username=email, password=password)
                    if user is not None:
                        login(request, user)
                        login_attempt.login_attempts = 0    # reset the login attempts
                        login_attempt.save()
                        return redirect(reverse("submitSubtitle"),context={"user":user})  # change expected_url in your project

                    else:
                        # if the password is incorrect, increment the login attempts and
                        # if the login attempts == MAX_LOGIN_ATTEMPTS, set the user to be inactive and send activation email
                        login_attempt.login_attempts += 1
                        login_attempt.timestamp = now
                        login_attempt.save()
                        if login_attempt.login_attempts == settings.MAX_LOGIN_ATTEMPTS:
                            _user.is_active = False
                            _user.save()
                            # send the re-activation email
                            mail_subject = "Account suspended"
                            current_site = get_current_site(request)
                            # send_user_email(_user, mail_subject, email, current_site, 'accounts/email_account_suspended.html')
                            messages.error(request, 'Account suspended, maximum login attempts exceeded. '
                                                    'Reactivation link has been sent to your email')
                        else:
                            messages.error(request, 'Incorrect email or password')
                        return redirect(settings.LOGIN_URL)
                else:
                    messages.error(request, 'Login failed, please try again')
                    return redirect(settings.LOGIN_URL)

            except ObjectDoesNotExist:
    
                messages.error(request, 'Incorrect email or password')

                return redirect(settings.LOGIN_URL)
        else:
            if form.errors:
                for field in form:
                    for error in field.errors:
                        messages.error(request, error)
    context = {'form': form}

    return render(request, 'accounts/login.html', context)


def activate_account_page(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login_attempt, created = LoginAttempt.objects.get_or_create(user=user)
        if login_attempt.login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
            login_attempt.login_attempts = 0
            login_attempt.save()
            messages.success(request, 'Account restored, you can now proceed to login')
        else:
            messages.success(request, 'Thank you for confirming your email. You can now login.')
        return redirect(reverse("accounts:login"))
    else:
        messages.error(request, 'Activation link is invalid!')

        return redirect(reverse("accounts:login"))


def logout_view(request):
    logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)
def send_contact_email(request):
    if request.method=="POST":
        print(request.POST)
        try:
            print(send_client_message(request.POST['email'],request.POST["full_name"],request.POST["message"]))
            return JsonResponse({"result":"message sent"},status=200)
        except:
            return JsonResponse({"result":"message is invalid"},status=403)
def home_view(request):
    if request.method=="GET":
        return render(request,'accounts/index.html')
        
def reset_password(request):
    if request.method=="GET":
        return render(request,'accounts/password_reset.html')
    if request.method=="POST":
        try:
            _user = User.objects.get(email=request.POST["email"])
        except:
            _user=None
        if _user is not None:
            token=get_token(_user)
            send_password_reset(_user.email, _user.username.split(" ")[0],settings.REDIRECT_DOMAIN+f"/accounts/resetpasswordform/{token['uid']}/{token['token']}")
        return redirect(reverse('accounts:login'))


def reset_password_form(request, uidb64, token):
    print(uidb64,token)
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        if request.method=="GET":
            return render(request,"accounts/password_reset_form.html")
        elif request.method=="POST":
            print(request.POST)
            user.set_password(request.POST["password"])
            user.save()
            login_attempt, created = LoginAttempt.objects.get_or_create(user=user)
            if login_attempt.login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                login_attempt.login_attempts = 0
                login_attempt.save()
                messages.success(request, 'Account restored, you can now proceed to login')
            else:
                messages.success(request, 'Thank you for confirming your email. You can now login.')
            return redirect(settings.LOGIN_URL)
    else:
        messages.error(request, 'Activation link is invalid!')

        return redirect(settings.LOGIN_URL)





