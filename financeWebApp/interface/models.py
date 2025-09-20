from django.db import models


class Article(models.Model):
    name = models.CharField(max_length=200)
    content = models.TextField()
    url = models.URLField(max_length=200)
    portfolio = models.TextField()  
    date = models.DateTimeField(auto_now_add=True)  