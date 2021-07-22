from django import forms
from django.forms.widgets import CheckboxSelectMultiple

from .models import Intervention, Zone


class ImageForm(forms.Form):
    image = forms.ImageField(
        label='Selecciona una foto'
    )


class NewInterventionForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NewInterventionForm, self).__init__(*args, **kwargs)
        self.fields['zone'].queryset = Zone.objects.all().exclude(pk=9).order_by('pk')

    class Meta:
        model = Intervention
        fields = ['address', 'short_description', 'description', 'zone', 'tags']
        widgets = {
            'tags': CheckboxSelectMultiple(),
        }


class EarlyInterventionModificationForm(forms.ModelForm):
    class Meta:
        model = Intervention
        fields = ['description', 'short_description', 'tags']
        widgets = {
            'tags': CheckboxSelectMultiple(),
        }


class InterventionModificationForm(forms.ModelForm):
    class Meta:
        model = Intervention
        fields = ['short_description', 'tags']
        widgets = {
            'tags': CheckboxSelectMultiple(),
        }
