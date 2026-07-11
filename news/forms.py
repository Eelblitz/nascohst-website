from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = [
            "name",
            "email",
            "body",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full rounded-xl border border-gray-300 px-4 py-3 focus:ring-2 focus:ring-primary focus:outline-none",
                    "placeholder": "Your Name",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "w-full rounded-xl border border-gray-300 px-4 py-3 focus:ring-2 focus:ring-primary focus:outline-none",
                    "placeholder": "Your Email",
                }
            ),

            "body": forms.Textarea(
                attrs={
                    "class": "w-full rounded-xl border border-gray-300 px-4 py-3 focus:ring-2 focus:ring-primary focus:outline-none",
                    "rows": 5,
                    "placeholder": "Write your comment...",
                }
            ),
        }