from django import forms
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm, PasswordChangeForm


class MundiaguaLoginForm(AuthenticationForm):
    password = forms.CharField(label="Password", strip=False,
                               widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))

    def __init__(self, request=None, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        if request.user_agent.is_mobile:
            self.fields['password'].widget.attrs.pop("autocomplete", 'false')



class MundiaguaChangePasswordForm(PasswordChangeForm, SetPasswordForm):
    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.update_change_password()
            self.user.save()
        return self.user
