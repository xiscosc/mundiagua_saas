from django.forms import forms

from intervention.models import InterventionModification


class ModificationForm(forms.ModelForm):
    class Meta:
        model = InterventionModification
        fields = ["note"]