from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm

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