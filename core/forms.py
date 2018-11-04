from django import forms
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm, PasswordChangeForm
from core.models import SystemVariable


class MundiaguaLoginForm(AuthenticationForm):
    password = forms.CharField(label="Password", strip=False,
                               widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))

    def __init__(self, request=None, *args, **kwargs):
        super(MundiaguaLoginForm, self).__init__(*args, **kwargs)
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


class SystemVariableRichForm(forms.ModelForm):

    class Meta:
        model = SystemVariable
        fields = ['value']


class SystemVariablePlainForm(forms.ModelForm):

    class Meta:
        model = SystemVariable
        fields = ['plain_value']
