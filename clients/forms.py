from datetime import date,timedelta
from django import forms
from .models import registration

class regform(forms.Form):
    firstname=forms.CharField(max_length=50,label="firstname")
    lastname=forms.CharField(max_length=50,label="lastname")
    contactno=forms.CharField(max_length=10,label="contactno")
    email=forms.EmailField(max_length=254, label="email")
    password=forms.CharField(max_length=100,label="password",widget=forms.PasswordInput) 
    max_date=(date.today()-timedelta(days=365*16)).strftime('%Y-%m-%d')
    dateofbirth=forms.DateField(
        label="dateofbirth",
        widget=forms.DateInput(
            attrs={
                'type':'date',
                'min':'1900-01-01',
                'max':max_date
            }
        )
    )
    gender = forms.ChoiceField(
        choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Others')],
        label='Gender',
        widget=forms.Select(attrs={'class': 'gender-dropdown'})
    )

class roomform(forms.Form):
    name=forms.CharField(max_length=50,label="name")
    description=forms.CharField(widget=forms.Textarea,label="description")
    


class createroomform(forms.Form):
    name=forms.CharField(max_length=50,label="name")
    description=forms.CharField(widget=forms.Textarea,label="description")
    