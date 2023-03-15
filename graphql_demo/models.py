from django.db import models


class Product(models.Model):
	name = models.CharField(max_length=50, unique=True, null=False, blank=False)
	price = models.DecimalField(max_digits=5, decimal_places=2, null=False, blank=False)
	category = models.ManyToManyField("Category", blank=True, null=True)
	in_stock = models.BooleanField(default=True, null=False, blank=False)
	date_created = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)

	def __str__(self):
		return self.name


class Category(models.Model):
	name = models.CharField(max_length=50, unique=True, null=False, blank=False)

	def __str__(self):
		return self.name
