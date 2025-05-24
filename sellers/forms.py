from django import forms
from .models import Seller

class SellerForm(forms.ModelForm):
    terms_accepted = forms.BooleanField(
        required=True,
        label='I agree to the Terms and Conditions',
        error_messages={'required': 'You must accept the terms and conditions to register as a seller'}
    )
    
    class Meta:
        model = Seller
        fields = ['company_name', 'description', 'logo', 'website']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        self.fields['terms_accepted'].widget.attrs.update({'class': 'form-check-input'})