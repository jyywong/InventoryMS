from django import forms 
from core import settings
from django.contrib.auth import get_user_model

class InviteForm(forms.Form):
    user_email = forms.EmailField(required= True)
    
    def clean_user_email(self):
        data = self.cleaned_data.get('user_email')
        if not get_user_model().objects.filter(email = data).exists():
            
            # Why is validation error not being raised?
            raise forms.ValidationError('This is not a valid email.')
        return data
            

