from django.db import models

# Create your models here.

class Category(models.Model):
	category_title = models.CharField(max_length=50)
	category_alias = models.CharField(max_length=5)
	category_image = models.CharField(max_length=100,null=True)
	def __str__(self):
		return self.category_title