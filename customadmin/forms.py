from django import forms
from shop.models import *

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'discount_price', 'image', 'description']

    # Adding 'form-control' class to all form fields and making description field smaller
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'  # Add form-control to all fields
        self.fields['description'].widget.attrs['class'] = 'form-control form-control-sm'  # Make description field smaller

class GalleryImageForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = ['image']


class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'author', 'content','image']
        widgets = {
            'content': forms.Textarea(attrs={'style': 'height: 80px;', 'class': 'form-control'}),
        }