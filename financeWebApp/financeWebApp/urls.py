"""
URL configuration for financeWebApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from interface import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('articles/', views.article_list, name='article_list'),
    path('portfolio/<int:portfolio_id>/', views.view_portfolio, name='view_portfolio'),
    path('add-customer/', views.add_customer, name='add_customer'),
    path('delete-customers/', views.bulk_delete_customers, name='bulk_delete_customers'),
    path('customer/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('filings/', views.filing_list, name='filing_list'),
]
