from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import CustomUser


# Shared Tailwind classes applied to every text/email/password input
INPUT_CLASSES = (
    "w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm text-slate-800 "
    "placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue/40 "
    "focus:border-blue transition-colors duration-150"
)


class RegisterForm(forms.ModelForm):
    """
    Public self-registration form. Always creates a 'patient' role account —
    hospital_admin / staff / doctor accounts are provisioned separately by an admin.
    """

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": INPUT_CLASSES,
                "placeholder": "Minimum 8 characters",
            }
        ),
        min_length=8,
    )
    confirm_password = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(
            attrs={
                "class": INPUT_CLASSES,
                "placeholder": "Re-enter your password",
            }
        ),
    )

    class Meta:
        model = CustomUser
        fields = ["full_name", "email", "phone"]
        widgets = {
            "full_name": forms.TextInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": "Jane Doe",
                    "autofocus": True,
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": "you@example.com",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": "+1 555 000 0000",
                }
            ),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone and CustomUser.objects.filter(phone=phone).exists():
            raise forms.ValidationError(
                "An account with this phone number already exists."
            )
        return phone

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned_data


class EmailAuthenticationForm(AuthenticationForm):
    """
    AuthenticationForm keeps the field name 'username' internally, but since
    CustomUser.USERNAME_FIELD = 'email', that field is used to look up by email.
    We just relabel it and restyle the widgets for the template.
    """

    username = forms.CharField(
        label="Email address",
        widget=forms.EmailInput(
            attrs={
                "class": INPUT_CLASSES,
                "placeholder": "you@example.com",
                "autofocus": True,
            }
        ),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": INPUT_CLASSES,
                "placeholder": "••••••••",
            }
        ),
    )

    error_messages = {
        "invalid_login": "No account found with that email and password.",
        "inactive": "This account has been deactivated. Contact your hospital admin.",
    }
