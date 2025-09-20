
from django.db import models

class Portfolio(models.Model):
	name = models.CharField(max_length=100, unique=True)
	assets = models.TextField(help_text="Comma-separated list of assets, e.g. Bitcoin, USD, Gold")

	def __str__(self):
		return self.name
