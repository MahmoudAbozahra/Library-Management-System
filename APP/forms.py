from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Books, Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]
        widgets = {"name": forms.TextInput(attrs={"class": "form-control"})}


class BookForm(forms.ModelForm):
    class Meta:
        model = Books
        fields = [
            "title",
            "author",
            "photo_book",
            "photo_author",
            "pages",
            "price",
            "retal_price_day",
            "retal_period",
            "total_rental",
            "status",
            "category",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "author": forms.TextInput(attrs={"class": "form-control"}),
            "photo_book": forms.FileInput(attrs={"class": "form-control"}),
            "photo_author": forms.FileInput(attrs={"class": "form-control"}),
            "pages": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "price": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "retal_price_day": forms.NumberInput(
                attrs={"class": "form-control", "id": "rental_price", "min": 0}
            ),
            "retal_period": forms.NumberInput(
                attrs={"class": "form-control", "id": "rental_period", "min": 1}
            ),
            "total_rental": forms.NumberInput(
                attrs={"class": "form-control", "id": "total_rental", "min": 0}
            ),
            "status": forms.Select(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-control"}),
        }


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "password1", "password2"]
        help_texts = {
            "username": "Required. 150 characters or fewer.",
            "password1": "Your password must contain at least 8 characters.",
            "password2": "Enter the same password again for verification.",
        }


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())
