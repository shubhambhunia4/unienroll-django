from django import forms
from .models import Course, Department

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['code', 'title', 'department', 'credits', 'fee_per_credit', 'description']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CS501'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Advanced Quantum Computing'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'credits': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12, 'placeholder': 'e.g. 4'}),
            'fee_per_credit': forms.NumberInput(attrs={'class': 'form-control', 'step': '100.00', 'placeholder': 'e.g. 2500.00'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Course overview and learning objectives...'}),
        }

    def clean_code(self):
        code = self.cleaned_data.get('code', '').strip().upper()
        if not code:
            raise forms.ValidationError("Course code is required.")
        return code
