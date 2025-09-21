from django import forms
from .models import Customer, Portfolio

class CustomerForm(forms.ModelForm):
    portfolio = forms.ModelMultipleChoiceField(
        queryset=Portfolio.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Portfolios"
    )

    class Meta:
        model = Customer
        fields = ['firstname', 'lastname', 'portfolio']
from .models import Portfolio

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['name', 'assets']
