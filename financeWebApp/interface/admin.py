from django.contrib import admin
from .models import Customer, Portfolio, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'assets')
    list_filter = ('category',)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname')
    filter_horizontal = ('portfolio',)
