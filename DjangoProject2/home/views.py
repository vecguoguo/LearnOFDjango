import datetime
from django.shortcuts import render,HttpResponse

# Create your views here.
def index(request):
    return render(request,"index.html")
def baidu(request):
    return render(request,"baidu.html")
def info(request):
    #渲染一个普通的变量
    username = "django_learn"
    # 字典类型
    book ={
        "name":"django_learn",
        "stage":"1"
    }
    # 列表类型
    books = [
        {"name":"django_learn","stage":"2"},
        {"name":"django_learn","stage":"3"}
    ]
    # 渲染模型（对象）
    class Person:
        def __init__(self,name,age):
            self.name = name
            self.age = age


    context = {'username': username,
               'book': book,
               'books': books,
               'person':Person("hello django",18)
               }
    return render(request,"info.html",context=context)


def if_view(request):
    age = 17
    return render(request,"if.html",context={"age":age})
def for_view(request):
    # 1.列表
    books = [
        {"name": "django_learn", "stage": "2"},
        {"name": "django_learn", "stage": "3"}
    ]
    # 2.字典  for x in person.item/keys/values
    person = {
        'name':'hello django',
        'age':18,
        'height':180
    }
    return render(request,"for.html",context={"books":books,"person":person})
def with_view(request):
    context={
        'books':[
            {'name':'水浒传','author':'施耐庵'},
            {'name':'三国演义','author':'罗贯中'},
        ]
    }
    return render(request,'with.html',context=context )
def url_view(request):
    return render(request,'url.html')
def book_detail(request,book_id):
    return HttpResponse(f"你所访问的图书id是：{book_id}")
def filter_view(request):
    greet = "hello world ,hello Django"
    context = {"greet":greet,
               "birthday":datetime.datetime.now(),
               "profile":"",
               "html":"<h1>欢迎来到django的学习</h1>"
        }
    return render(request,'filter.html',context)

def template_form(request):
    return render(request,"xfz_index.html")
def static_view(request):
    return render(request,'static.html')