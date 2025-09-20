from django.contrib import admin


from .models import Portfolio
from django.contrib import admin

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
	list_display = ("name", "assets")
