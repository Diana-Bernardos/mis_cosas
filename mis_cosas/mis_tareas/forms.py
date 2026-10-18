from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Tarea


class RegistroForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username',)


class TareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ('nombre', 'descripcion', 'fecha_vencimiento', 'completada')
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre de la tarea'}),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
        }
