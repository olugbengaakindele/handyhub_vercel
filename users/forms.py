from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import *
import re
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .utils import get_gallery_max_upload_bytes
from django.core.exceptions import ValidationError



User = get_user_model()

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    account_type = forms.ChoiceField(
        choices=UserProfile.ACCOUNT_TYPE_CHOICES,
        initial=UserProfile.TYPE_TRADESPERSON,
        widget=forms.RadioSelect,
        required=True
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "account_type"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_password2(self):
        pw1 = self.cleaned_data.get("password1")
        pw2 = self.cleaned_data.get("password2")

        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError("Passwords do not match.")
        if pw1 and len(pw1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        if pw1 and not re.search(r"[A-Za-z]", pw1):
            raise forms.ValidationError("Password must contain at least one letter.")
        if pw1 and not re.search(r"[0-9]", pw1):
            raise forms.ValidationError("Password must contain at least one number.")

        return pw2

    def save(self, commit=True):
        user = super().save(commit=commit)

        account_type = self.cleaned_data.get("account_type", UserProfile.TYPE_TRADESPERSON)

        # ✅ profile exists because of signal, but keep get_or_create as safety
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.account_type = account_type
        profile.save()

        return user


    def save(self, commit=True):
        """
        Save user, then set account_type on the user's profile.
        """
        user = super().save(commit=commit)

        account_type = self.cleaned_data.get("account_type", UserProfile.TYPE_TRADESPERSON)

        # ✅ Ensure profile exists (in case signals didn't create it)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.account_type = account_type
        profile.save()

        return user

# login form
class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            "class": "form-control w-full p-3 border border-gray-300 rounded-xl focus:ring focus:ring-teal-300",
            "placeholder": "Enter your email"
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control w-full p-3 border border-gray-300 rounded-xl focus:ring focus:ring-teal-300",
            "placeholder": "Enter your password"
        })
    )

# This is to update user profile
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "user_firstname",
            "user_last_name",
            "user_preferred_name",
            "user_business_name",
            "user_profile_image",
            "user_address_line1",
            "user_address_line2",
            "user_city",
            "user_province",
            "user_postal_code",
            "user_website",
        ]

        # CLEAN LABELS
        labels = {
            "user_firstname": "First Name",
            "user_last_name": "Last Name",
            "user_preferred_name": "Preferred Name",
            "user_business_name": "Business Name",
            "user_profile_image": "Profile Image",
            "user_address_line1": "Address Line 1",
            "user_address_line2": "Address Line 2",
            "user_city": "City",
            "user_province": "Province",
            "user_postal_code": "Postal Code",
            "user_website": "Website",
        }

        widgets = {
            "user_firstname": forms.TextInput(attrs={"class": "form-control"}),
            "user_last_name": forms.TextInput(attrs={"class": "form-control"}),
            "user_preferred_name": forms.TextInput(attrs={"class": "form-control"}),
            "user_business_name": forms.TextInput(attrs={"class": "form-control"}),
            "user_profile_image": forms.FileInput(attrs={"class": "form-control"}),
            "user_address_line1": forms.TextInput(attrs={"class": "form-control"}),
            "user_address_line2": forms.TextInput(attrs={"class": "form-control"}),
            "user_city": forms.TextInput(attrs={"class": "form-control"}),
            "user_province": forms.Select(attrs={"class": "form-control"}),
            "user_postal_code": forms.TextInput(attrs={"class": "form-control"}),
            "user_website": forms.URLInput(attrs={"class": "form-control"}),
        }


class UserServiceForm(forms.ModelForm):

    class Meta:
        model = UserService
        fields = ["category", "subcategory"]

        widgets = {
            "category": forms.Select(
                attrs={
                    "class": (
                        "w-full p-3 border border-gray-300 rounded-lg "
                        "focus:outline-none focus:ring-2 focus:ring-blue-500 "
                        "bg-white"
                    )
                }
            ),
            "subcategory": forms.Select(
                attrs={
                    "class": (
                        "w-full p-3 border border-gray-300 rounded-lg "
                        "focus:outline-none focus:ring-2 focus:ring-blue-500 "
                        "bg-white"
                    )
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        subcategory = cleaned_data.get("subcategory")

        # ✅ Ensure subcategory belongs to category
        if category and subcategory:
            if subcategory.category_id != category.id:
                raise forms.ValidationError(
                    "Selected subcategory does not belong to the selected category."
                )

        # ✅ Enforce max 5 services per user (only on create)
        if self.user and not self.instance.pk:
            if self.user.services.count() >= 5:
                raise forms.ValidationError(
                    "You can only add up to 5 services. "
                    "This helps keep the platform fair for small tradespeople."
                )

        return cleaned_data

    


#  editi profile form
class EditProfileForm(forms.ModelForm):

    MAX_SUMMARY_LENGTH = 1000

    class Meta:
        model = UserProfile
        fields = [
            "user_firstname",
            "user_last_name",
            "user_preferred_name",
            "user_business_name",
            "profile_summary",
        ]

        widgets = {
            "profile_summary": forms.Textarea(attrs={
                "rows": 5,
            }),
        }

    def clean_profile_summary(self):
        summary = self.cleaned_data.get("profile_summary", "")

        if summary and len(summary) > self.MAX_SUMMARY_LENGTH:
            raise forms.ValidationError(
                f"Profile summary cannot exceed {self.MAX_SUMMARY_LENGTH} characters."
            )

        return summary



class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["user_profile_image"]
        widgets = {
            "user_profile_image": forms.ClearableFileInput(
                attrs={
                    "class": "hidden",
                    "accept": "image/*",
                    "id": "id_profile_image",
                }
            )
        }


class EditContactForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'user_primary_phone',
            'user_secondary_phone',
            'user_business_phone',
            'user_website',
            
        ]
        widgets = {
            'user_primary_phone': forms.TextInput(attrs={'class': 'border rounded p-2 w-full'}),
            'user_secondary_phone': forms.TextInput(attrs={'class': 'border rounded p-2 w-full'}),
            'user_business_phone': forms.TextInput(attrs={'class': 'border rounded p-2 w-full'}),
            'user_website': forms.URLInput(attrs={'class': 'border rounded p-2 w-full'}),
            
        }
    
    def clean_user_website(self):
        website = self.cleaned_data.get("user_website")

        if website:
            website = website.strip()

            # Auto-add scheme if missing
            if not website.startswith(("http://", "https://")):
                website = "https://" + website

        return website


class EditAddressForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'user_address_line1',
            'user_address_line2',
            'user_city',
            'user_province',
            'user_postal_code'
        ]
        widgets = {
            'user_address_line1': forms.TextInput(attrs={'class': 'border rounded p-2 w-full'}),
            'user_address_line2': forms.TextInput(attrs={'class': 'border rounded p-2 w-full'}),
            'user_city': forms.TextInput(attrs={'class': 'border rounded p-2 w-full'}),
            'user_province': forms.Select(attrs={'class': 'border rounded p-2 w-full'}),
            'user_postal_code': forms.TextInput(attrs={'class': 'border rounded p-2 w-full'}),
        }


class TradeWorkPhotoForm(forms.ModelForm):
    class Meta:
        model = TradeWorkPhoto
        fields = ["image", "description"]
        widgets = {
            "description": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Briefly describe the work (max 100 words)…"
            })
        }

    def clean_image(self):
        img = self.cleaned_data.get("image")
        if not img:
            return img

        max_bytes = get_gallery_max_upload_bytes()
        if img.size > max_bytes:
            raise ValidationError("Image must be 1MB or less.")

        return img
    


class LicenseForm(forms.ModelForm):
    class Meta:
        model = License
        fields = [
            "license_name",
            "issuing_authority",
            "license_number",
            "province",
            "issue_date",
            "expiry_date",
            "status",            # ✅ new
            "public_visibility", # ✅ new
            "document",
            "notes",
        ]
        widgets = {
            "license_name": forms.TextInput(attrs={"placeholder": "e.g., Red Seal Electrician"}),
            "issuing_authority": forms.TextInput(attrs={"placeholder": "e.g., Alberta Apprenticeship"}),
            "license_number": forms.TextInput(attrs={"placeholder": "Optional"}),
            "issue_date": forms.DateInput(attrs={"type": "date"}),
            "expiry_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3, "placeholder": "Optional notes (scope, restrictions, etc.)"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["province"].queryset = Province.objects.all().order_by("name")
        self.fields["province"].empty_label = "Select province (optional)"

        
    def clean(self):
        cleaned = super().clean()
        issue_date = cleaned.get("issue_date")
        expiry_date = cleaned.get("expiry_date")

        # optional sanity check
        if issue_date and expiry_date and expiry_date < issue_date:
            self.add_error("expiry_date", "Expiry date cannot be earlier than issue date.")

        return cleaned
    

class CallOutFeeSettingsForm(forms.ModelForm):
    class Meta:
        model = CallOutFeeSettings
        fields = ["enabled", "amount", "note"]

    def clean(self):
        cleaned = super().clean()
        enabled = cleaned.get("enabled")
        amount = cleaned.get("amount")

        if enabled and (amount is None):
            self.add_error("amount", "Please enter an amount if call-out fee is enabled.")

        if (not enabled) and amount is not None:
            # optional: auto-clear amount when disabled
            cleaned["amount"] = None

        return cleaned
    


class DeleteAccountForm(forms.Form):
    password = forms.CharField(
        label="Confirm your password",
        widget=forms.PasswordInput(attrs={
            "class": "w-full rounded-xl border border-slate-300 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-rose-500",
            "placeholder": "Enter your password",
            "autocomplete": "current-password",
        })
    )