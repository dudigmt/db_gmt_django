from django import forms
from .models import Dataset

class DatasetUploadForm(forms.ModelForm):
    class Meta:
        model = Dataset
        fields = ['name', 'file']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded dark:bg-gray-700 dark:border-gray-600'}),
            'file': forms.FileInput(attrs={'class': 'w-full px-3 py-2 border rounded dark:bg-gray-700 dark:border-gray-600'}),
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            ext = file.name.split('.')[-1].lower()
            if ext not in ['xlsx', 'xls']:
                raise forms.ValidationError('Only Excel files (.xlsx, .xls) are allowed.')
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File size must be less than 10MB.')
        return file