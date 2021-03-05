from django import forms
from core.models import SystemVariable

class SystemVariableRichForm(forms.ModelForm):

    class Meta:
        model = SystemVariable
        fields = ['value']


class SystemVariablePlainForm(forms.ModelForm):

    class Meta:
        model = SystemVariable
        fields = ['plain_value']
