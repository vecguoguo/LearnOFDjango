from django.core import  validators
from django.db import models

# Create your models here.
class Article(models.Model):
    title = models.CharField(max_length=200,validators=[validators.MinLengthValidator(limit_value=2)])
    content = models.TextField(validators=[validators.MinLengthValidator(limit_value=3)])
    creat_time = models.DateTimeField(auto_now_add=True)
    # blank=True只是表单验证时允许为空，不代表数据库可以为空
    category = models.CharField(max_length=100, blank=True)