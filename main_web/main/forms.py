from django import forms
from .models import Portfolio

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['name', 'assets']
        widgets = {
            'assets': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Comma-separated assets, e.g. Bitcoin, USD, Gold'})
        }
