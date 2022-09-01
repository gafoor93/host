from django  import forms
from django_countries import widgets

from.models import *
from django_countries.fields import CountryField
from django_countries .widgets import CountrySelectWidget

class productform(forms.ModelForm):

    class Meta:
        model = product
        fields = '__all__'
        widgets = {
            'name':forms.TextInput(attrs={'class':'login'}),
            'category':forms.Select(attrs={'class':'login'}),
            'description':forms.Textarea(attrs={'class':'login'}),
            'price':forms.NumberInput(attrs={'class':'login'}),
            'product_available':forms.NumberInput(attrs={'class':'login form'}),
            'image':forms.FileInput(attrs={'class':'login form'}),
     }



class CheckoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'class' : 'form-control',
        'placeholder' : 'street name'
    }))

    apartment_address = forms.CharField(required=False,  widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Apartment or House Name'
    }))

    country = CountryField(blank_label='select country').formfield(widgets=CountrySelectWidget(attrs={
        'class' : 'custom-select d-block w-100'
    }))

    zip_code = forms.CharField(widget=forms.TextInput(attrs={
        'class' : 'form-control'
    }))

