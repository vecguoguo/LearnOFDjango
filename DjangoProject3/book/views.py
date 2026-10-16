from django.shortcuts import HttpResponse
# 使用django封装好的connection对象，会自动读取settings.py中数据库的配置信息
from django.db import connection
from .models import Book
# Create your views here.
def index(request):
    # 获取游标对象
    cursor = connection.cursor()
    # 拿到游标对象后执行sql语句
    cursor.execute("select * from book")
    # 获取所有的数据
    rows = cursor.fetchall()
    # 遍历查询到的数据
    for row in rows:
        print(row)
    return HttpResponse("查找成功")

def add_book(request):
    # book = Book(name = '三国演义',author='罗贯中',price=100)
    # book.save()

    book = Book(name='水浒传', author='施耐庵', price=99)
    book.save()

    return HttpResponse('图书插入成功')
def query_book(request):
    # books = Book.objects.all()

    # books = Book.objects.filter(name="三国演义")
    # for book in books:
    #     print(book.id,book.name,book.pub_time,book.price)
    try:
        book = Book.objects.get(name="三国演义")
        print(book.id,book.name,book.author,book.price)
    except Book.DoesNotExist:
        print("图书不存在")


    return HttpResponse("查找成功")

def order_view(request):
    books = Book.objects.order_by("pub_time")
    # 可以在order_by()内的字段前填入-，表示降序
    for book in books:
        print(book.name)
    return  HttpResponse("排序成功")

def update_view(request):
    book = Book.objects.first()
    book.name = '西游记'
    book.save()
    return HttpResponse("修改成功")
def delete_view(request):
    book = Book.objects.filter(name="西游记")
    book.delete()
    return HttpResponse('删除成功')