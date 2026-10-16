from datetime import datetime

from django.shortcuts import render,HttpResponse
from .models import User,Article
# Create your views here.
def article_test(request):
    # user = User(username='admin',password='1234')
    # user.save()
    # article = Article(title='GhatGpt5已经发布了',content='xxxxxxx',author=user)
    # article.save()
    article = Article.objects.first()
    print(article.author.username)
    return HttpResponse('保存成功:',charset="utf-8")

def dele_data(request):

    user = User.objects.get(id=4)
    user.delete()
    return HttpResponse("删除成功")
def one_to_many(request):
    user = User.objects.first()
    articles = user.articles.filter(title__contains='GhatGpt5').all()
    for article in articles:
        print(article.title)

    return HttpResponse("一对多查询成功")

def query1(request):
    # article = Article.objects.filter(id = 1)  # 效果与id__exact=1 一样
    # 查询结果使用article.query 就可以看到执行的sql语句

    article = Article.objects.filter(title__iexact='GhatGpt5')
    # iexact 表示忽略大小写 模糊查询
    print(article.query)
    print(article)
    return HttpResponse("query1查询")

def query2(request):
    # article = Article.objects.filter(title__contains='chat')
    article = Article.objects.filter(title__icontains='chat')
    # 字符串前后加%

    print(article.query)
    print(article)

    return HttpResponse('query2')
def query3(request):
    article = Article.objects.filter(id__in=[1,2,3])
    # 以Ghat开头

    print(article.query)
    print(article)

    return HttpResponse('query3')

#   gt 是 查询大于指定值的数据
#   gte 是 查询大于等于指定值的数据
#   lt 是 查询小于指定值的数据
#   lte 是 查询小于等于指定值的数据
#   startswith 是 是否以某个值开始的 大小写敏感
#   endswith 是 以某个值结束的 大小写敏感

def query4(request):
    start_data = datetime(year=2026,month=10,day=14)
    end_data = datetime(year=2026,month=10,day=15)
    article = Article.objects.filter(pub_time__range=(start_data,end_data))
    print(article.query)
    print(article)


    return HttpResponse('query4')
def query5(request):

    user = User.objects.filter(articles__title__icontains='chat')
    print(user.query)
    print(user)

    return HttpResponse('query5')