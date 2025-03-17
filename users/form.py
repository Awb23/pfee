from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm , SetPasswordForm , PasswordResetForm
from django.contrib.auth.models import User
from .models import CustomUser , Parent

class LoginForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password']
        
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from datetime import date, timedelta

class NEW(UserCreationForm):
    role = forms.ChoiceField(
        choices=[('parent', 'Parent'), ('child', 'Child')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=True
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'birth_date', 'role', 'password1', 'password2')

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            
            role = self.cleaned_data.get('role')
            if role == 'child' and age >= 18:
                raise forms.ValidationError("A child account must be under 18 years old.")
            elif role == 'parent' and age < 18:
                raise forms.ValidationError("A parent account must be at least 18 years old.")
        
        return birth_date


class RESETFORM(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Current Password'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'}))

    class Meta:
        model = CustomUser
        fields = ('old_password', 'new_password1', 'new_password2')
class PRFM(forms.ModelForm):
     class Meta:
        model = CustomUser
        fields = ['username',"birth_date"]    

