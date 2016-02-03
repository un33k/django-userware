from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.contrib.auth.forms import UserChangeForm as DjangoUserChangeForm
from django.contrib.auth.forms import AuthenticationForm as DjangoAuthenticationForm
from django.contrib.auth.forms import PasswordResetForm as DjangoPasswordResetForm
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm
from django.contrib.auth.forms import SetPasswordForm as DjangoSetPasswordForm
from django.contrib.auth import get_user_model
from django.utils.html import simple_email_re

from toolware.utils.mixin import CleanSpacesMixin
from auditware.utils import force_logout

from . import utils as util
from . import defaults as defs

User = get_user_model()


class UserCreationForm(DjangoUserCreationForm):
    """
    A form to create a user based on a unique email and a verified password.
    """
    required_css_class = 'required_field'
    pass_len = defs.USERWARE_PASSWORD_MIN_LENGTH

    username = forms.RegexField(
        label=_("Username"),
        min_length=3,
        max_length=32,
        regex=r"^[a-zA-Z0-9]+(-[a-zA-Z0-9]+)*$",
        help_text=_("Username may only contain alphanumeric or dashes "
                    "and cannot begin or end with a dash. "),
        error_messages={
            'invalid': _("Username may only contain alphanumeric characters "
                    " or dashes and cannot begin or end with a dash.")},
    )

    email = forms.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.error_messages['duplicate_email'] = _("A user with that email already exists.")
        self.fields['email'].help_text = _("A valid email address")
        self.fields['password1'].help_text = _("Password must be minimum of %s characters." % self.pass_len)
        self.fields.keyOrder = ['username', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data["username"]
        if username not in defs.USERWARE_RESERVED_USERNAMES and len(username) >= defs.USERWARE_USERNAME_MIN_LENGTH:
            try:
                User.objects.get(username__iexact=username)
            except User.DoesNotExist:
                return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(self.error_messages['duplicate_email'])

    def clean_password2(self):
        password2 = super(UserCreationForm, self).clean_password2()
        if len(password2) < self.pass_len:
            raise forms.ValidationError(_("Password too short! minimum length is ") + " [%d]." % self.pass_len)
        return password2


class UserChangeForm(DjangoUserChangeForm):
    """
    Customized username change form.
    """
    required_css_class = 'required_field'

    username = forms.RegexField(
        label=_("Username"), min_length=3, max_length=30, regex=r"^[a-zA-Z0-9]+(-[a-zA-Z0-9]+)*$",
        help_text=_("Username may only contain alphanumeric or dashes "
                    "and cannot begin or end with a dash."),
        error_messages={
            'invalid': _("Username may only contain alphanumeric characters "
                    " or dashes and cannot begin or end with a dash.")},
    )

    def clean_username(self):
        username = self.cleaned_data["username"]
        if username not in defs.USERWARE_RESERVED_USERNAMES and len(username) >= defs.USERWARE_USERNAME_MIN_LENGTH:
            users = User.objects.filter(username__iexact=username).exclude(id=self.instance.id)
            if not users:
                return username
        raise forms.ValidationError(_("A user with that username already exists."))

    def clean_email(self):
        email = self.cleaned_data["email"]
        users = User.objects.filter(email__iexact=email).exclude(id=self.instance.id)
        if users:
            raise forms.ValidationError(_("A user with that email already exists."))
        return email.lower()


class UserAuthenticationForm(DjangoAuthenticationForm):
    """
    Customized authentication form.
    """
    required_css_class = 'required_field'

    def __init__(self, *args, **kwargs):
        super(UserAuthenticationForm, self).__init__(*args, **kwargs)
        self.error_messages['invalid_login'] = _("Login Failed.  Note that both fields may be case-sensitive.")
        self.fields['username'].label = "Username or Email"
        self.fields['username'].help_text = "Enter your account's username or email address."
        self.fields['username'].widget.attrs['autofocus'] = ''


class UserPasswordResetForm(DjangoPasswordResetForm):
    """
    Customized password reset form.
    """
    required_css_class = 'required_field'
    error_messages = {}

    def __init__(self, *args, **kwargs):
        super(UserPasswordResetForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget = forms.HiddenInput()
        self.fields['email'].required = False
        self.fields['email'].widget.attrs['autofocus'] = ''

        self.error_messages = {
            'invalid_login': _("Please enter a username or a valid email address."),
            'unknown_email': _("That email address doesn't have an associated "
                         "user account or is not a email address."),
            'unusable_email': _("The user account associated with this email "
                          "address cannot reset the password."),
            'unknown_username': _("That username doesn't have an associated "
                         "user account. Are you sure you've registered? "),
            'unusable_username': _("The user account associated with this username "
                          "address cannot reset the password."),
        }

    username_or_email = forms.CharField(
        label=_("Username or Email"),
        max_length=254,
        help_text=_("Enter your username or email address to receive "
            "instructions on how to reset your password."),
    )

    def clean_username_or_email(self):
        username_or_email = self.cleaned_data.get("username_or_email")
        if not username_or_email:
            raise forms.ValidationError(self.error_messages['invalid_login'])
        return username_or_email

    def clean(self):
        """
        Validates that an active user exists with the given username / email address.
        """
        username_or_email = self.clean_username_or_email()
        user = util.get_user_by_username_or_email(username_or_email)
        if not user:
            if simple_email_re.match(username_or_email):
                raise forms.ValidationError(self.error_messages['unknown_email'])
            else:
                raise forms.ValidationError(self.error_messages['unknown_username'])
        elif not user.is_active:
            if simple_email_re.match(username_or_email):
                raise forms.ValidationError(self.error_messages['unusable_email'])
            else:
                raise forms.ValidationError(self.error_messages['unusable_username'])
        self.cleaned_data["email"] = user.email
        return self.cleaned_data


class UserPasswordChangeForm(DjangoPasswordChangeForm):
    """
    Customized password change form.
    """
    required_css_class = 'required_field'
    pass_len = defs.USERWARE_PASSWORD_MIN_LENGTH

    def __init__(self, *args, **kwargs):
        super(UserPasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['old_password', 'new_password1', 'new_password2']
        self.fields['old_password'].label = _("Current Password")
        self.fields['old_password'].help_text = _("Changing your password will log you out of all of your other sessions.")
        self.fields['new_password1'].help_text = _("Password must be minimum of %s characters." % self.pass_len)
        self.fields['old_password'].widget.attrs['autofocus'] = ''

    def clean_new_password2(self):
        new_password2 = super(UserPasswordChangeForm, self).clean_new_password2()
        if len(new_password2) < self.pass_len:
            raise forms.ValidationError(_("Password too short! minimum length is ") + " [%d]." % self.pass_len)
        if self.user.check_password(new_password2):
            raise forms.ValidationError(_("New password is too similar to the old password. Please choose a different password."))
        return new_password2


class UserSetPasswordForm(DjangoSetPasswordForm):
    """
    Customized password reset form.
    """
    required_css_class = 'required_field'
    pass_len = defs.USERWARE_PASSWORD_MIN_LENGTH

    def __init__(self, user, *args, **kwargs):
        super(UserSetPasswordForm, self).__init__(user, *args, **kwargs)
        self.fields['new_password1'].help_text = _("Password must be minimum of %s characters." % self.pass_len)
        self.fields['new_password2'].help_text = _("Resetting your password will log you out of all of your other sessions.")
        self.fields['new_password1'].widget.attrs['autofocus'] = ''

    def clean_new_password2(self):
        new_password2 = super(UserSetPasswordForm, self).clean_new_password2()
        if len(new_password2) < self.pass_len:
            raise forms.ValidationError(_("Password too short! minimum length is ") + " [%d]." % self.pass_len)
        if self.user.check_password(new_password2):
            raise forms.ValidationError(_("New password is too similar to the old password. Please choose a different password."))
        force_logout(self.user)
        return new_password2


class UserDeletionForm(CleanSpacesMixin, forms.Form):
    """
    Delete a user (account) form.
    """
    required_css_class = 'required_field'

    username_or_email = forms.CharField(
        label=_("Username or Email Confirmation"),
        help_text=_("Please confirm your username or email address."),
    )

    password = forms.CharField(
        label=_("Password Confirmation"),
        widget=forms.PasswordInput,
        help_text=_("Please confirm permanent account deletion by entering your password."),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(UserDeletionForm, self).__init__(*args, **kwargs)

    def clean_username_or_email(self):
        username_or_email = self.cleaned_data['username_or_email']
        user = util.get_user_by_username_or_email(username_or_email)
        if self.user != user:
            raise forms.ValidationError(_("Confirmation failed."))
        return username_or_email

    def clean_password(self):
        password = self.cleaned_data["password"]
        if not self.user.has_usable_password(password):
            raise forms.ValidationError(_("Invalid password, please try again."))
        return password


class UserSwitchForm(CleanSpacesMixin, forms.Form):
    """
    Switch user form. `su`.
    """
    required_css_class = 'required_field'

    switched_username = forms.CharField(max_length=30, label=_('Username / Email'),
        help_text=_("Email or username of the user to switch to."),
    )

    def __init__(self, *args, **kwargs):
        super(UserSwitchForm, self).__init__(*args, **kwargs)
        self.fields['switched_username'].widget.attrs['autofocus'] = ''

    def clean_switched_username(self):
        username = self.cleaned_data['switched_username']
        to_user = util.get_user_by_username_or_email(username)
        if not to_user:
            raise forms.ValidationError(_("Invalid username"))
        elif to_user.is_superuser:
            raise forms.ValidationError(_("Operation is not permitted."))
        return username
