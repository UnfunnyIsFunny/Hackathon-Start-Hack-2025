from django.shortcuts import render
from .models import Article

def article_list(request):
	articles = Article.objects.all().order_by('-date')
	return render(request, 'article_list.html', {'articles': articles})
from django.shortcuts import render

# Create your views here.
