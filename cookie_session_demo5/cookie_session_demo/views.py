from http.client import responses

from django.shortcuts import HttpResponse

def add_cookie(request):
    response = HttpResponse("设置cookie")
    max_age = 60*60*24*7  # 7天
    response.set_cookie('username','django',max_age=max_age)
    return response

def delete_cookie(request):
    response = HttpResponse("删除cookie")
    response.delete_cookie('username')
    return response
def get_cookie(request):
    username = request.COOKIES.get('username')
    print(username)
    return HttpResponse("获取cookie")

def add_session(request):
    request.session['user_id'] = 'django'
    request.session.set_expiry(0)
    return HttpResponse("session add")
def get_session(request):
    username = request.session.get('user_id')
    print(username)
    return HttpResponse('get session')