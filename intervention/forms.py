from django import forms


class ImageForm(forms.Form):
    image = forms.ImageField(
        label='Selecciona una foto'
    )


class DocumentForm(forms.Form):
    document = forms.FileField(
        label='Selecciona un documento'
    )
