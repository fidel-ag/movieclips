from django.urls import path
from django.contrib.auth import views as auth_views

from .views import *

app_name = 'accounts'
urlpatterns = [
    path('accounts/signup', signup_page, name='signup'),
    path('accounts/resetpasswordform/<slug:uidb64>/<slug:token>/', reset_password_form, name='reset_password_form'),
    path('accounts/activate_account_page/<slug:uidb64>/<slug:token>/', activate_account_page, name='activate_account_page'),
    path('accounts/login/', login_page, name='login'),
    path('accounts/signupFreeTrial', signup_page_free_trial, name='signupfreetrial'),
    
    path('accounts/logout/', logout_view, name='logout'),
path('contact', send_contact_email, name='send_contact_email'),

    # Reset Passoword Urls
    path('accounts/reset-password',reset_password,name="reset_password"),
    path('accounts/password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_sent.html'),
         name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_form.html'),
         name='password_reset_confirm'),
    path('accounts/reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_done.html'),
         name='password_reset_complete'),
     path("",home_view,name="home"),

]


# To update password reset functionality