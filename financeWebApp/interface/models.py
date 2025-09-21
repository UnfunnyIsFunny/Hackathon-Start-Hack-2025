from django.db import models


class Article(models.Model):
    name = models.CharField(max_length=200)
    content = models.TextField()
    url = models.URLField(max_length=200)
    portfolio = models.TextField()  
    date = models.DateTimeField(auto_now_add=True)  
    verdict = models.CharField(max_length=100, blank=True, null=True)

class Portfolio(models.Model):
    name = models.CharField(max_length=100, unique=True)
    assets = models.TextField(help_text="Comma-separated list of assets, e.g. Bitcoin, USD, Gold")

    def __str__(self):
        return self.name
    
class Customer(models.Model):
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    portfolio = models.JSONField()
    
class Filing(models.Model):
    company = models.CharField(max_length=200)
    content = models.TextField()
    url = models.URLField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)
    portfolio = models.TextField()
    verdict = models.CharField(max_length=100, blank=True, null=True)