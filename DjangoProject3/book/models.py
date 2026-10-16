from django.db import models

# Create your models here.
class Book(models.Model):
    name = models.CharField(max_length=20, null=False)
    author = models.CharField(max_length=20, null=False)
    pub_time = models.DateTimeField(auto_now_add=True)
    price = models.FloatField(default=0)