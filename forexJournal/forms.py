from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError


class CSVfileForm(forms.Form):
    csv_file = forms.FileField()
    
    
    
    
class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )
    mt5_login = forms.CharField(
        max_length=50, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'MT5 Login'})
    )
    mt5_password = forms.CharField(
        max_length=50, 
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'MT5 Password'})
    )
    mt5_server = forms.CharField(
        max_length=30, 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'MT5 Server'})
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
        strip=False,
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
        strip=False,
    )
    
    class Meta:
        model = User
        fields = [
            'first_name', 
            'last_name', 
            'username', 
            'email', 
            'password1', 
            'password2', 
            'mt5_login', 
            'mt5_password', 
            'mt5_server'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
        }
        
        

class CustomLoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(
        required=False,  # Make the checkbox optional
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})  # Add CSS classes if needed
    )
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Call the parent class's constructor
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Username',  # Placeholder text for the username field
            'class': 'form-control',     # Optional: add CSS class for styling
        })
        self.fields['password'].widget.attrs.update({
            'placeholder': 'Password',  # Placeholder text for the password field
            'class': 'form-control',     # Optional: add CSS class for styling
        })
        
        
        
class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=30)
    password = forms.CharField(widget=forms.PasswordInput(), label="Password")
    
    class Meta:
        fields = ("username", "Password")
        
        
        
class NewSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text="Enter your first name")
    last_name = forms.CharField(max_length=30, required=True, help_text="Enter your last name")
    email = forms.EmailField(max_length=254, required=True, help_text="Enter a valid email address")
    
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password1")
        confirm_password = cleaned_data.get("password2")

        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match")
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email