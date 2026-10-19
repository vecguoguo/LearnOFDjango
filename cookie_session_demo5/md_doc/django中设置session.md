# 三、在 Django 中操作 session:

django 中的 `session` 默认情况下是存储在服务器的数据库中的，在表中会根据 `sessionid` 来提取指定的 `session` 数据，然后再把这个 `sessionid` 放到 `cookie` 中发送给浏览器存储，浏览器下次在向服务器发送请求的时候会自动的把所有 `cookie` 信息都发送给服务器，服务器再从 `cookie` 中获取 `sessionid`，然后再从数据库中获取 `session` 数据。但是我们在操作 `session` 的时候，这些细节压根就不用管。我们只需要通过 `request.session` 即可操作。示例代码如下：

```python
def index(request):
    request.session.get('username')
    return HttpResponse('index')
```

session 常用的方法如下：

1. `get`：用来从 session 中获取指定值。
2. `pop`：从 session 中删除一个值。
3. `keys`：从 session 中获取所有的键。
4. `items`：从 session 中获取所有的值。
5. `clear`：清除当前这个用户的 session 数据。
6. `flush`：删除 session 并且删除在浏览器中存储的 `session_id`，一般在注销的时候用得比较多。
7. `set_expiry(value)`：设置过期时间。
    * 整形：代表秒数，表示多少秒后过期。
    * `0`：代表只要浏览器关闭，session 就会过期。
    * `None`：会使用全局的 session 配置。在 `settings.py` 中可以设置 `SESSION_COOKIE_AGE` 来配置全局的过期时间。默认是 1209600 秒，也就是 2 周的时间。
8. `clear_expired`：清除过期的 session。Django 并不会清除过期的 session，需要定期手动的清理，或者是在终端，使用命令行 `python manage.py clearsessions` 来清除过期的 session。
---

### 💡 补充：Session 的基本操作示例

**1. 设置 Session**

与 Cookie 不同，Session 直接通过 `request.session` 操作即可，不需要依赖 `response` 对象。

```python
def set_session(request):
    # 设置 session
    request.session['username'] = '张三'
    # 设置 session 的过期时间，单位为秒（比如 7 天）
    request.session.set_expiry(7 * 24 * 60 * 60)
    return HttpResponse("Session 已设置")
```

**2. 获取 Session**

```python
def get_session(request):
    # 获取 session，如果不存在则返回默认值 '游客'
    username = request.session.get('username', '游客')
    return HttpResponse(f"读取到的用户名: {username}")
```

**3. 删除 Session 数据**

```python
def delete_session(request):
    # 删除指定的 key
    request.session.pop('username', None)
    
    # 清空所有数据（保留 sessionid 记录）
    # request.session.clear()
    
    return HttpResponse("Session 已删除")
```

**4. 注销登录（清除 Session）**

```python
def logout(request):
    # flush 会清除所有 session 数据并删除 cookie 中的 sessionid
    request.session.flush()
    return redirect('login')
```

---

### 💡 补充：Session 的存储方式

虽然 Django 默认把 session 存在数据库里（`django.contrib.sessions.models.Session`），但你可以在 `settings.py` 中通过 `SESSION_ENGINE` 更改存储位置：

*   **数据库（默认）**：`'django.contrib.sessions.backends.db'`
*   **缓存**：`'django.contrib.sessions.backends.cache'`（速度快，但重启缓存可能丢失）
*   **缓存+数据库**：`'django.contrib.sessions.backends.cached_db'`
*   **文件**：`'django.contrib.sessions.backends.file'`
*   **签名 Cookie**：`'django.contrib.sessions.backends.signed_cookies'`（数据存在客户端，安全性依赖 SECRET_KEY）

# 四、修改 session 的存储机制：

默认情况下，session 数据是存储到数据库中的。当然也可以将 session 数据存储到其他地方。可以通过设置 `SESSION_ENGINE` 来更改 session 的存储位置，这个可以配置为以下几种方案：

1. `django.contrib.sessions.backends.db`：使用数据库。默认就是这种方案。

2. `django.contrib.sessions.backends.file`：使用文件来存储 session。

3. `django.contrib.sessions.backends.cache`：使用缓存来存储 session。想要将数据存储到缓存中，前提是你必须要在 `settings.py` 中配置好 `CACHES`，并且是需要使用 `Memcached`，而不能使用纯内存作为缓存。

4. `django.contrib.sessions.backends.cached_db`：在存储数据的时候，会将数据先存到缓存中，再存到数据库中。这样就可以保证万一缓存系统出现问题，session 数据也不会丢失。在获取数据的时候，会先从缓存中获取，如果缓存中没有，那么就会从数据库中获取。

5. `django.contrib.sessions.backends.signed_cookies`：将 session 信息加密后存储到浏览器的 cookie 中。这种方式要注意安全，建议设置 `SESSION_COOKIE_HTTPONLY=True`，那么在浏览器中不能通过 js 来操作 session 数据，并且还需要对 `settings.py` 中的 `SECRET_KEY` 进行保密，因为一旦别人知道这个 `SECRET_KEY`，那么就可以进行解密。另外还有就是在 cookie 中，存储的数据不能超过 4k。