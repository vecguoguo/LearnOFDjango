# 二、在 django 中操作 cookie

## 1. 设置 cookie：

设置 cookie 是设置值给浏览器的。因此我们需要通过 `response` 的对象来设置，设置 cookie 可以通过 `response.set_cookie` 来设置，这个方法的相关参数如下：

1. `key`：这个 cookie 的 key。
2. `value`：这个 cookie 的 value。
3. `max_age`：最长的生命周期。单位是秒。
4. `expires`：过期时间。跟 `max_age` 是类似的，只不过这个参数需要传递一个具体的日期，比如 `datetime` 或者符合日期格式的字符串。如果同时设置了 `expires` 和 `max_age`，那么将会使用 `expires` 的值作为过期时间。
5. `path`：对域名下哪个路径有效。默认是对域名下所有路径都有效。
6. `domain`：针对哪个域名有效。默认是针对主域名下都有效，如果只要针对某个子域名才有效，那么可以设置这个属性。
7. `secure`：是否是安全的，如果设置为 `True`，那么只能在 https 协议下才可用。
8. `httponly`：默认是 `False`。如果为 `True`，那么在客户端不能通过 JavaScript 进行操作。

---

## 2. 删除 cookie：

通过 `response.delete_cookie` 来删除指定的 cookie。示例代码如下：

```python
response = HttpResponse("删除cookie")
response.delete_cookie("username")
return response
```

> **注意**：删除 cookie 实际上是将该 cookie 的值设为空，并将其 `expires`（或 `max_age`）设置为 0，从而让浏览器立刻丢弃它。

---

## 3. 获取 cookie：

获取 cookie 是通过 `request.COOKIES` 来获取，它返回的是一个字典（类似字典的对象）。示例代码如下：

```python
def my_view(request):
    # 获取名为 'username' 的 cookie
    username = request.COOKIES.get('username')
    
    # 如果 cookie 不存在，可以设置默认值
    theme = request.COOKIES.get('theme', 'light')
    
    return HttpResponse(f"用户名: {username}, 主题: {theme}")
```

---

## 4. 完整示例

**设置 Cookie 的视图：**

```python
from django.http import HttpResponse
import datetime

def set_cookie_view(request):
    response = HttpResponse("Cookie 已设置")
    
    # 设置一个有效期为 7 天的 cookie (7 * 24 * 60 * 60 秒)
    response.set_cookie('username', '张三', max_age=7 * 24 * 60 * 60)
    
    # 使用 expires 设置过期时间
    # expire_date = datetime.datetime.now() + datetime.timedelta(days=7)
    # response.set_cookie('username', '张三', expires=expire_date)
    
    # 设置一个只在 https 下可用的、且禁止 JS 读取的安全 cookie
    response.set_cookie('session_id', 'abc123xyz', secure=True, httponly=True)
    
    return response
```

**读取 Cookie 的视图：**

```python
def get_cookie_view(request):
    username = request.COOKIES.get('username', '未登录')
    return HttpResponse(f"读取到的用户名: {username}")
```

**删除 Cookie 的视图：**

```python
def delete_cookie_view(request):
    response = HttpResponse("Cookie 已删除")
    response.delete_cookie('username')
    return response
```

---

## 5. Cookie 的安全性（补充）

- **不要存储敏感信息**：Cookie 是保存在客户端的，用户可以随意查看甚至修改。因此千万不要在 cookie 中直接存储密码、余额等敏感信息。
- **加密签名**：如果需要存储一些不容易被篡改的数据，可以使用 Django 提供的 `request.get_signed_cookie()` 和 `response.set_signed_cookie()`，它会对 cookie 的值进行签名，防止用户恶意修改。
- **httponly 和 secure**：对于登录凭证（如 Session ID），一定要设置 `httponly=True`（防止 XSS 攻击窃取 cookie）和 `secure=True`（只在 HTTPS 下传输）。