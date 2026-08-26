from django import forms
from .models import DoctorReview


class DoctorReviewForm(forms.ModelForm):
    class Meta:
        model = DoctorReview
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "max": 5,
                    "placeholder": "Rating (1-5)",
                }
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Write your feedback here...",
                }
            ),
        }
