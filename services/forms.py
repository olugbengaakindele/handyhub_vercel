from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import ServiceCategory

User = get_user_model()

# forms.py


class ServiceCategoryForm(forms.ModelForm):
    class Meta:
        model = ServiceCategory
        fields = ["name"]  # only the name should be entered by the admin

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full p-3 border border-gray-300 rounded-lg",
                "placeholder": "Enter category name"
            })
        }
    
from .models import SubCategory, ServiceCategory


class SubCategoryForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=ServiceCategory.objects.all(),
        empty_label="Select a category",
        label="Category",
        widget=forms.Select(attrs={
            "class": "w-full p-3 bg-gray-50 text-gray-800 border border-gray-300 rounded-lg "
                     "focus:ring-2 focus:ring-green-500 focus:border-green-500",
            "id": "category-select"
        })
    )

    class Meta:
        model = SubCategory
        fields = ["category", "name"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full p-3 bg-gray-50 text-gray-800 border border-gray-300 rounded-lg "
                         "focus:ring-2 focus:ring-green-500 focus:border-green-500",
                "placeholder": "e.g. Washer Repair"
            })
        }