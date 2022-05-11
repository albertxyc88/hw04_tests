from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.views import PasswordChangeDoneView as PCDV
from django.contrib.auth.views import PasswordChangeView as PCV
from django.contrib.auth.views import PasswordResetCompleteView as PRCmV
from django.contrib.auth.views import PasswordResetConfirmView as PRCnV
from django.contrib.auth.views import PasswordResetDoneView as PRDV
from django.contrib.auth.views import PasswordResetView as PRV
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path(
        'password_change/',
        PCV.as_view(template_name='users/password_change_form.html'),
        name='password_change_form'
    ),
    path(
        'password_change/done/',
        PCDV.as_view(template_name='users/password_change_done.html'),
        name='password_change_done'
    ),
    path(
        'password_reset/',
        PRV.as_view(template_name='users/password_reset_form.html'),
        name='password_reset_form'
    ),
    path(
        'password_reset/done/',
        PRDV.as_view(template_name='users/password_reset_done.html'),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        PRCnV.as_view(template_name='users/password_reset_confirm.html'),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        PRCmV.as_view(template_name='users/password_reset_complete.html'),
        name='password_reset_complete'
    ),
    path('signup/', views.SignUp.as_view(), name='signup')
]
