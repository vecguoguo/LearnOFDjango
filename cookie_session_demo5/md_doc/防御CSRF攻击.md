# 三、防御 CSRF 攻击：

CSRF 攻击的要点就是在向服务器发送请求的时候，相应的 cookie 会自动的发送给对应的服务器。造成服务器不知道这个请求是用户发起的还是伪造的。这时候，我们可以在用户每次访问有表单的页面的时候，在网页源代码中加一个随机的字符串叫做 `csrf_token`，在 cookie 中也加入 `csrf_token` 字符串。以后给服务器发送请求的时候，必须在 form 中以及 cookie 中都携带 `csrf_token`，服务器只有检测到 cookie 中的 `csrf_token` 和 form 中的 `csrf_token` 都匹配（不是相等），才认为这个请求是正常的，否则就是伪造的。那么黑客就没办法伪造请求了。

在 Django 中，如果想要防御 CSRF 攻击，应该做两步工作。第一个是在 `settings.MIDDLEWARE` 中添加 `CsrfViewMiddleware` 中间件。第二个是在模版代码中添加一个 `input` 标签，加载 `csrf_token`。示例代码如下：

* 服务器代码：

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

* 模版代码：

```html
<form action="" method="post">
    <input type="hidden" name="csrfmiddlewaretoken" value="{{ csrf_token }}">
    <!-- 表单的其他内容 -->
</form>
```

> **注意**：在模板中，更推荐使用 Django 提供的标签 `{% csrf_token %}` 来自动生成隐藏的 input 标签，这样代码更简洁：
> ```html
> <form action="" method="post">
>     {% csrf_token %}
>     <!-- 表单的其他内容 -->
> </form>
> ```

### 补充说明：

1. **如果不加会怎样？**
   如果 `CsrfViewMiddleware` 中间件开启了，但你的 POST 表单没有携带 CSRF Token，Django 会直接拒绝该请求，并返回 `403 Forbidden (CSRF token missing or incorrect)` 错误。

2. **豁免 CSRF 验证**
   如果你写的是一些对外的 API 接口（不需要 CSRF 验证，比如给移动端或第三方调用的接口），可以使用 `@csrf_exempt` 装饰器来让某个视图免除 CSRF 验证：
   ```python
   from django.views.decorators.csrf import csrf_exempt

   @csrf_exempt
   def my_api_view(request):
       # ...
   ```