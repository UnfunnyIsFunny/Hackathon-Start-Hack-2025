from django.urls import path
from . import views

urlpatterns = [
    path('', views.portfolio_select, name='portfolio_select'),
    path('articles/<int:portfolio_id>/', views.article_list, name='article_list'),
]
