from django import forms

class CSVfileForm(forms.Form):
    csv_file = forms.FileField()