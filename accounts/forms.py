from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q

class CustomLoginForm(forms.Form):
    username = forms.CharField(
        label="Student ID / Username",
        widget=forms.TextInput(attrs={
            'id': 'id_username',
            'required': True,
            'placeholder': 'Enter your ID or Username'
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'id': 'id_password',
            'required': True,
            'placeholder': 'Enter your password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        login_input = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if login_input and password:
            # 1. Look for a User matching either username OR profile.student_id
            user_obj = User.objects.filter(
                Q(username__iexact=login_input) | Q(profile__student_id__iexact=login_input)
            ).first()

            if not user_obj:
                raise forms.ValidationError("User does not exist.")

            # 2. Authenticate using the real username found in the database
            user = authenticate(username=user_obj.username, password=password)
            
            if user is None:
                raise forms.ValidationError("Incorrect password.")

            # Store the valid authenticated user
            self.user_cache = user

        return cleaned_data