import io, csv

from django import forms

from .models import Contact

class ContactForm(forms.ModelForm):

    class Meta:
        model = Contact
        fields = ('first_name', 'last_name', 'contact_number', 'address')

class DataForm(forms.Form):
    file_contacts = forms.FileField()