from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from apps.users.models import User
from apps.properties.models import Property


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    def clean(self, data, initial=None):
        if not data:
            return []

        files = data if isinstance(data, (list, tuple)) else [data]
        if len(files) > 3:
            raise ValidationError("Maksimal 3 ta rasm yuklash mumkin.")

        cleaned_files = []
        for file_obj in files:
            cleaned = super().clean(file_obj, initial)
            if cleaned.size > 8 * 1024 * 1024:
                raise ValidationError("Har bir rasm hajmi 8MB dan oshmasligi kerak.")
            cleaned_files.append(cleaned)
        return cleaned_files


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'password1', 'password2')


class PropertyForm(forms.ModelForm):
    images = MultipleImageField(
        required=False,
        widget=MultipleFileInput(attrs={'accept': 'image/*'}),
        help_text="3 tagacha rasm yuklash mumkin (har biri 8MB gacha).",
    )

    class Meta:
        model = Property
        fields = [
            'title', 'description', 'property_type', 'city', 'district', 'address',
            'price', 'bedrooms', 'bathrooms', 'area_m2', 'is_premium'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone')
