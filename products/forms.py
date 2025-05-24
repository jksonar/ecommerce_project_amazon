from django import forms
from .models import Product, ProductImage, ProductSpecification, Category

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'discount_price', 'stock', 'is_available']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        self.fields['is_available'].widget.attrs.update({'class': 'form-check-input'})

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control', 'multiple': True}),
        }

class ProductSpecificationForm(forms.ModelForm):
    class Meta:
        model = ProductSpecification
        fields = ['name', 'value']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Weight, Color'}),
            'value': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2kg, Red'}),
        }

ProductSpecificationFormSet = forms.inlineformset_factory(
    Product, ProductSpecification, form=ProductSpecificationForm,
    extra=3, can_delete=True
)