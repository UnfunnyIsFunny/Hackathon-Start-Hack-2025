from django.shortcuts import render
from .models import Article, Customer,Portfolio
import json

def article_list(request):
	articles = Article.objects.all().order_by('-date')
	return render(request, 'article_list.html', {'articles': articles})



def view_customer(request, customer_id):
    customer = Customer.objects.get(id=customer_id)
    portfolios = [Portfolio.objects.get(name=portfolio) for portfolio in json.loads(customer.portfolio)]


    return render(request, 'view_customer.html', {'customer': customer, 'portfolios': portfolios})

def view_portfolio(request, portfolio_id):
    articles = Article.objects.filter(portfolio__icontains=Portfolio.objects.get(id=portfolio_id).name).order_by('-date')

    return render(request, 'view_portfolio.html', {'articles': articles})
