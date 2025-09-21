import json as pyjson

def portfolios_to_json(portfolios):
    if isinstance(portfolios, str):
        items = [p.strip() for p in portfolios.split(',') if p.strip()]
    else:
        items = list(portfolios)
    return pyjson.dumps(items)
from django.shortcuts import render
from .models import Article, Customer, Portfolio, Filing
from .forms import PortfolioForm
def filing_list(request):
    sort = request.GET.get('sort', 'date')
    order = request.GET.get('order', 'desc')
    if sort == 'verdict':
        ordering = ['highly relevant', 'relevant', 'somewhat relevant', 'not relevant']
        filings = list(Filing.objects.all())
        filings.sort(key=lambda f: ordering.index(f.verdict) if f.verdict in ordering else 99)
        if order == 'desc':
            filings = filings[::-1]
    else:
        filings = Filing.objects.all().order_by('-date' if order == 'desc' else 'date')
    paginator = Paginator(filings, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'filing_list.html', {'page_obj': page_obj, 'sort': sort, 'order': order})
import json
from django.core.paginator import Paginator
from .forms import CustomerForm
from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse

def article_list(request):
    sort = request.GET.get('sort', 'date')
    order = request.GET.get('order', 'desc')
    if sort == 'relevancy':
        ordering = ['highly relevant', 'relevant', 'somewhat relevant', 'not relevant']
        articles = list(Article.objects.all())
        articles.sort(key=lambda a: ordering.index(a.verdict) if a.verdict in ordering else 99)
        if order == 'desc':
            articles = articles[::-1]
    else:
        articles = Article.objects.all().order_by('-date' if order == 'desc' else 'date')
    paginator = Paginator(articles, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'article_list.html', {'page_obj': page_obj, 'sort': sort, 'order': order})

def view_customer(request, customer_id):
    customer = Customer.objects.get(id=customer_id)
    portfolios = [Portfolio.objects.get(name=portfolio) for portfolio in json.loads(customer.portfolio)]
    return render(request, 'view_customer.html', {'customer': customer, 'portfolios': portfolios})

def view_portfolio(request, portfolio_id):
    sort = request.GET.get('sort', 'date')
    order = request.GET.get('order', 'desc')
    articles = Article.objects.filter(portfolio__icontains=Portfolio.objects.get(id=portfolio_id).name)
    if sort == 'relevancy':
        ordering = ['highly relevant', 'relevant', 'somewhat relevant', 'not relevant']
        articles = list(articles)
        articles.sort(key=lambda a: ordering.index(a.verdict) if a.verdict in ordering else 99)
        if order == 'desc':
            articles = articles[::-1]
    else:
        articles = articles.order_by('-date' if order == 'desc' else 'date')
    paginator = Paginator(articles, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'view_portfolio.html', {'page_obj': page_obj, 'sort': sort, 'order': order})


def home(request):
    customers = Customer.objects.all()
    return render(request, "home.html", {"customers": customers})

    
def add_customer(request):
    if request.method == "POST":
        selected_portfolios = request.POST.getlist('portfolio')
        form = CustomerForm(request.POST)
        portfolio_form = PortfolioForm(request.POST, prefix="portfolio")
        if 'add_portfolio' in request.POST and portfolio_form.is_valid():
            portfolio_form.save()
            form = CustomerForm()
            portfolio_form = PortfolioForm(prefix="portfolio")
        elif form.is_valid():
            customer = form.save(commit=False)
            portfolios = Portfolio.objects.filter(id__in=selected_portfolios)
            customer.portfolio = portfolios_to_json([p.name for p in portfolios])
            customer.save()
            return redirect('home')
    else:
        form = CustomerForm()
        portfolio_form = PortfolioForm(prefix="portfolio")
    return render(request, "add_customer.html", {"form": form, "portfolio_form": portfolio_form})

def bulk_delete_customers(request):
    if request.method == "POST":
        ids_to_delete = request.POST.getlist('customers')
        Customer.objects.filter(id__in=ids_to_delete).delete()
        return redirect('home')

    customers = Customer.objects.all()
    return render(request, "bulk_delete.html", {"customers": customers})

def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    portfolios = [Portfolio.objects.get(name=portfolio) for portfolio in json.loads(customer.portfolio)]
    return render(request, "customer_detail.html", {"customer": customer, "portfolios": portfolios})