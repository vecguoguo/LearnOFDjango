from django.urls import path

from . import views

#应用命名空间
app_name = 'book'
urlpatterns =[
    path('', views.index, name='index'),
    path('book/add', views.add_book, name='add_book'),
    path('book/query', views.query_book, name='query_book'),
    path('book/order', views.order_view, name='order_view'),
    path('book/update', views.update_view, name='update_view'),
    path('book/delete', views.delete_view, name='delete_view')
]