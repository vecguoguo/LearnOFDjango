from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

# 在URL中携带参数
# 1. 通过查询字符串 （query string）: https://www.baidu.com/s?wd=python&a=1&b=2
# 2. 在path中携带 http://127.0.0.1：8000/book/2

def book_detail_query_string(request):
    book_id = request.GET.get("id")
    return HttpResponse(f"你要找的书的id是:{book_id}")

def book_detail_path(request,book_id):
    return HttpResponse(f"你要找的书的id是:{book_id}")


def book_detail_slug(request,book_id):
    return HttpResponse(f"你要找的书的id是:{book_id}")
