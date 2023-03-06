from django.contrib.auth import views as auth_views
from django.urls import path
from .views import SignUp

app_name = 'users'

urlpatterns = [
    path(
        'logout/',
        auth_views.LogoutView.as_view(
            template_name='users/logged_out.html',
        ),
        name='logout'
    ),
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='users/login.html',
        ),
        name='login'
    ),
    path(
        'signup/',
        SignUp.as_view(),
        name='signup'
    ),
    path(
        'password_change/',
        auth_views.PasswordChangeView.as_view(
            template_name='users/pass_change/password_change_form.html',
        ),
        name='pass_change_form'
    ),
    path(
        'password_change/done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='users/pass_change/password_change_done.html',
        ),
        name='pass_change_done'
    ),
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='users/pass_reset/password_reset_form.html',
        ),
        name='pass_reset_form'
    ),
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='users/pass_reset/password_reset_done.html',
        ),
        name='pass_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='users/pass_reset/password_reset_confirm.html',
        ),
        name='pass_reset_confirm'
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='users/pass_reset/password_reset_complete.html',
        ),
        name='pass_reset_complete'
    ),
]
