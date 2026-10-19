from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


# Create your views here.

@require_http_methods(["GET","POST"])
def login(request):
    if request.method == "GET":
        return render(request,"login.html")
    else:
        print(request.POST)
        print(request.COOKIES)
        return HttpResponse("登录成功")
