from django import forms

class StudentCSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="Select CSV file",
        help_text="Upload a CSV with matriculation_number, full_name, programme, graduation_year"
    )
