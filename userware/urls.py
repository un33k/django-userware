from django.conf.urls import url
from django.contrib.auth import views as auth_views


from .forms import UserPasswordResetForm
from .forms import UserSetPasswordForm
from . import utils as util
from .views import *

urlpatterns = [

    url(
        r'^login$',
        UserLoginView.as_view(),
        name='user_login'
    ),
    url(
        r'^logout$',
        UserLogoutView.as_view(),
        name='user_logout'
    ),
    url(
        r'^password/change$',
        UserChangePassword.as_view(),
        name='user_password_change'
    ),
    url(
        r'^delete$',
        UserDeleteView.as_view(),
        name='user_delete_account'
    ),
    url(
        r'^disable$',
        UserDisableView.as_view(),
        name='user_disable_account'
    ),
    url(
        r'^switch/on$',
        UserSwitchOnView.as_view(),
        name='user_switch_on'
    ),
    # user forgot his/her password again. ask for username or email and send a reset link
    url(
        r'^password/reset/request$',
        auth_views.password_reset,
        {
            'password_reset_form': UserPasswordResetForm,
            'template_name': util.get_template_path('password_reset_request_form.html'),
            'subject_template_name': util.get_template_path('password_reset_request_email_subject.txt'),
            'email_template_name': util.get_template_path('password_reset_request_email.txt'),
            'post_reset_redirect': 'user_password_reset_request_sent',
        },
        name='user_password_reset_request',
    ),
    # an email has been sent to the provided email address with the link to reset password
    url(
        r'^password/reset/request/sent$',
        auth_views.password_reset_done,
        {
            'template_name': util.get_template_path('password_reset_request_sent.html'),
        },
        name='user_password_reset_request_sent',
    ),
    # password reset link has been clicked on, forms allows for a new password and confirmation
    url(
        r'^password/reset/set/new/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)$',
        auth_views.password_reset_confirm,
        {
            'set_password_form': UserSetPasswordForm,
            'template_name': util.get_template_path('password_reset_set_form.html'),
            'post_reset_redirect': 'user_password_reset_is_complete',
        },
        name='user_password_reset_set_new',
    ),
    # system has changed the password and redirect to this template for the final success message
    url(
        r'^password/reset/complete$',
        auth_views.password_reset_complete,
        {
            'template_name': util.get_template_path('password_reset_is_complete.html'),
        },
        name='user_password_reset_is_complete',
    ),
    url(
        r'^password/request$',
        UserRequestPasswordView.as_view(),
        name='user_password_request'
    ),
    url(
        r'^$',
        UserAccountView.as_view(),
        name='user_account_redirect'
    ),

]
