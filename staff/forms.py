from django import forms
from django.contrib.auth.models import User
from .models import Staff


class StaffUserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary'
            }),
        }

class StaffProfileForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = (
            'name', 'designation', 'department',
            'category', 'qualifications',
            'biography', 'photo'
        )
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full border rounded-md px-3 py-2'}),
            'designation': forms.TextInput(attrs={'class': 'w-full border rounded-md px-3 py-2'}),
            'department': forms.TextInput(attrs={'class': 'w-full border rounded-md px-3 py-2'}),
            'category': forms.Select(attrs={'class': 'w-full border rounded-md px-3 py-2'}),
            'qualifications': forms.Textarea(attrs={'class': 'w-full border rounded-md px-3 py-2', 'rows': 3}),
            'biography': forms.Textarea(attrs={'class': 'w-full border rounded-md px-3 py-2', 'rows': 4}),
        }
