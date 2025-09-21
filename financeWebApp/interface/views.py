import json
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .models import Article, Customer, Portfolio, Filing
from .forms import CustomerForm, PortfolioForm


# Utility to convert portfolios to JSON (for legacy or string-based storage if needed)
def portfolios_to_json(portfolios):
    if isinstance(portfolios, str):
        items = [p.strip() for p in portfolios.split(',') if p.strip()]
    else:
        items = list(portfolios)
    return json.dumps(items)


# Home view
def home(request):
    customers = Customer.objects.all()
    return render(request, "home.html", {"customers": customers})


# Add customer view with portfolio selection and inline portfolio creation
def add_customer(request):
    if request.method == "POST":
        # Main customer form
        form = CustomerForm(request.POST)
        portfolio_form = PortfolioForm(request.POST, prefix="portfolio")

        # If user submitted inline add portfolio
        if 'add_portfolio' in request.POST and portfolio_form.is_valid():
            portfolio_form.save()
            form = CustomerForm()  # Reset main form
            portfolio_form = PortfolioForm(prefix="portfolio")
        elif form.is_valid():
            customer = form.save(commit=False)
            # Get selected portfolios
            selected_portfolios = request.POST.getlist('portfolio')
            portfolios = Portfolio.objects.filter(id__in=selected_portfolios)
            customer.save()  # Must save first for M2M
            customer.portfolio.set(portfolios)  # Assign ManyToMany
            return redirect('home')
    else:
        form = CustomerForm()
        portfolio_form = PortfolioForm(prefix="portfolio")

    # Get all portfolios ordered by category
    portfolios = Portfolio.objects.select_related('category').order_by('category__name', 'name')
    return render(
        request,
        "add_customer.html",
        {
            "form": form,
            "portfolio_form": portfolio_form,
            "portfolios": portfolios
        }
    )


# Customer detail page with portfolios
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    portfolios = customer.portfolio.all().select_related("category").order_by("category__name", "name")
    return render(request, "customer_detail.html", {
        "customer": customer,
        "portfolios": portfolios,
    })


# Bulk delete customers
def bulk_delete_customers(request):
    if request.method == "POST":
        ids_to_delete = request.POST.getlist('customers')
        Customer.objects.filter(id__in=ids_to_delete).delete()
        return redirect('home')
    customers = Customer.objects.all()
    return render(request, "bulk_delete.html", {"customers": customers})


# Article list view
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


# View filings
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


# View portfolio-specific articles
def view_portfolio(request, portfolio_id):
    sort = request.GET.get('sort', 'date')
    order = request.GET.get('order', 'desc')
    portfolio = get_object_or_404(Portfolio, pk=portfolio_id)
    articles = Article.objects.filter(portfolio__icontains=portfolio.name)

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
    return render(request, 'view_portfolio.html', {'page_obj': page_obj, 'portfolio': portfolio, 'sort': sort, 'order': order})

def add_investment(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == "POST":
        selected_portfolios = request.POST.getlist("portfolio")
        portfolios = Portfolio.objects.filter(id__in=selected_portfolios)
        customer.portfolio.set(portfolios)
        return redirect("customer_detail", pk=customer.pk)

    # Order portfolios by category to make regroup work
    portfolios = Portfolio.objects.all().select_related("category").order_by("category__name", "name")

    return render(request, "add_investment.html", {
        "customer": customer,
        "portfolios": portfolios,
    })
