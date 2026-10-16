from django.urls import path
from . import views

urlpatterns = [
    path('avg',views.avg_view,name='avg'),
    path('count',views.count_view,name='count'),
    path('max_min',views.max_min_view,name='max_min'),
    path('sum',views.sum_view,name='sum'),
    path('f',views.f_view,name='f'),
    path('q',views.q_view,name='q'),
]