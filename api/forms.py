from django import forms
from django.contrib.auth import authenticate
from .models import User


# CMS user role choices
ROLE_CHOICES = [
    ("staff", "Staff User"),
    ("superuser", "Superuser"),
]


class UserSigninForm(forms.Form):
    username = forms.CharField(
        label="Username",
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    password = forms.CharField(
        label="Password",
        min_length=4,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("Incorrect username or password")
        return super().clean(*args, **kwargs)

    class Meta:
        model = User
        fields = ["username", "password"]


class AddUser(forms.ModelForm):
    username = forms.CharField(label="Username", min_length=2, required=True,
                               widget=forms.TextInput(attrs={"class": "form-group"}))
    email = forms.EmailField(label="Email", min_length=4, required=True,
                             widget=forms.TextInput(attrs={"class": "form-group"}))
    first_name = forms.CharField(label="First Name", min_length=2, required=True,
                                 widget=forms.TextInput(attrs={"class": "form-group"}))
    last_name = forms.CharField(label="Last Name", min_length=2, required=True,
                                widget=forms.TextInput(attrs={"class": "form-group"}))
    password = forms.CharField(label="Password", min_length=4, required=True,
                               widget=forms.TextInput(attrs={"class": "form-group"}))
    user_role = forms.ChoiceField(label="User Role", choices=ROLE_CHOICES,
                                  widget=forms.RadioSelect, required=True)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]


class UpdateUser(forms.ModelForm):
    username = forms.CharField(label="Username", min_length=2, required=True,
                               widget=forms.TextInput(attrs={"class": "form-group"}))
    first_name = forms.CharField(label="First Name", min_length=2, required=True,
                                 widget=forms.TextInput(attrs={"class": "form-group"}))
    last_name = forms.CharField(label="Last Name", min_length=2, required=True,
                                widget=forms.TextInput(attrs={"class": "form-group"}))
    password = forms.CharField(label="Password", required=False, min_length=4,
                               widget=forms.TextInput(attrs={"class": "form-group"}))
    confirm_password = forms.CharField(label="Confirm Password", required=False,
                                       min_length=4,
                                       widget=forms.TextInput(attrs={"class": "form-group"}))
    user_role = forms.ChoiceField(label="User Role", choices=ROLE_CHOICES,
                                  widget=forms.RadioSelect, required=True)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "username" in self.fields:
            self.fields["username"].disabled = True
            self.fields["username"].required = False
        self.fields["password"].initial = ""
        self.fields["confirm_password"].initial = ""
        if self.instance and self.instance.pk:
            if self.instance.is_superuser:
                self.fields["user_role"].initial = "superuser"
            elif self.instance.is_staff:
                self.fields["user_role"].initial = "staff"


# ---------------------------------------------------------------------------
# TODO: Add your project-specific forms here, e.g.:
# ---------------------------------------------------------------------------
#
# class AddCategoryForm(forms.ModelForm):
#     class Meta:
#         model = Category
#         fields = ["title", "thumbnail_url"]
#
# class AddItemForm(forms.ModelForm):
#     class Meta:
#         model = Item
#         fields = ["title", "description", "thumbnail_url", "category"]
