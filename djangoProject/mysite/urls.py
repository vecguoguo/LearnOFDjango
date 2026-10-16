"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path,include
from book import views
from django.urls import reverse
#URL与视图的映射
#/s(URL) -> 视图函数 进行映射
# http://127.0.0.1:8000 -> 返回 “欢迎 来到 Django”
def index(request):
    # 结果： /book
    # print(reverse("book_detail_query_string"))

    #  结果 /book/str/1
    # print(reverse("book_str",kwargs={"book_id":1}))

    #/book?id=1  如果只查询字符串拼接 就只能拼接
    # print(reverse("book_detail_query_string")+"?id=1")

    # 命名空间下的movie
    print(reverse("movie:movie_list"))
    return HttpResponse("欢迎 来到 Django")


urlpatterns = [
    path('admin/', admin.site.urls),
    # 首页
    # path('s', index), #访问地址为 http://127.0.0.1:8000/s,

    # http://127.0.0.1:8000/book?id=1
    path('book', views.book_detail_query_string,name="book_detail_query_string"),
    path('book/slug/<slug:book_id>', views.book_detail_slug,name='book_slug'),
    # http://127.0.0.1:8000/book/1
    # book id 指定为int,否则默认str
    # 还有str,slug,uuid,path类型    # slug: 由字母、数字、下划线、中划线组成的字符串 abc_123-def
    # path: 由字母、数字、下划线、中划线、斜线组成的字符串
    # uuid: 通用唯一识别码
    path('book/str/<str:book_id>', views.book_detail_path,name="book_str"),
    path('book/<int:book_id>', views.book_detail_path,name="book_int"),
    path('movie/',include("movie.urls")),
    path('',index,name='index')
]
