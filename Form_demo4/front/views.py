from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .forms import MessageBoardForm, RegisterForm


# Create your views here.
# 请求的method
# 1.GET: 用来从服务器上获取数据的
# 2.POST: 用来向服务器提交数据的
# 3.PUT/DELETE/HEAD
@require_http_methods(["GET", "POST"])
def index(request):
    if request.method == "GET":
        form = MessageBoardForm()
        return render(request,'index.html',context={'form':form})
    else:
         # 验证请求
        form = MessageBoardForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            content = form.cleaned_data.get('content')
            email = form.cleaned_data.get('email')
            return  HttpResponse(f"{title},{content},{email}")
        else:
            print(form.errors)
            return HttpResponse('表单验证失败!')
@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.method == "GET":
        return render(request,'register.html')
    else:
        form = RegisterForm(request.POST)
        if form.is_valid():
            telephone = form.cleaned_data.get('telephone')
            return HttpResponse(f"{telephone}")
        else:
            print(form.errors)
            return HttpResponse('表单验证失败!')

