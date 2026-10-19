# 阶段4—Form表单

> Form_demo4 项目代码分析与复习。本文档基于 `1.start/form_demo4` 的实际代码整理，用于后续复习。
> 覆盖知识点：**forms.Form 表单定义、字段类型与参数、内置验证器、自定义验证（clean_字段 / clean）、ModelForm 与模型绑定、表单验证流程、错误信息提取、@require_http_methods 装饰器、模板中渲染表单**。
>
> Django 版本：**5.2** ｜ 项目名：`Form_demo4` ｜ 应用：`front` ｜ 数据库：**SQLite（默认）**
> 配套笔记：`md_doc/`（4 篇：表单、表单验证、表单提取错误信息、ModelForm 的使用）

---

## 目录

1. [与前三阶段的对比（本阶段学了什么）](#一与前三阶段的对比本阶段学了什么)
2. [项目结构总览](#二项目结构总览)
3. [一个请求的完整生命周期（结合本项目）](#三一个请求的完整生命周期结合本项目)
4. [核心知识点对照代码](#四核心知识点对照代码)
   - [forms.Form 表单定义](#41-formsform-表单定义)
   - [字段类型与常用参数](#42-字段类型与常用参数)
   - [内置验证器](#43-内置验证器)
   - [自定义字段验证：clean_字段名](#44-自定义字段验证clean_字段名)
   - [自定义全局验证：clean()](#45-自定义全局验证clean)
   - [表单验证流程：is_valid → cleaned_data](#46-表单验证流程is_valid--cleaned_data)
   - [错误信息提取](#47-错误信息提取)
   - [ModelForm：模型与表单绑定](#48-modelform模型与表单绑定)
   - [ModelForm 的 save() 与 commit=False](#49-modelform-的-save-与-commitfalse)
   - [@require_http_methods 装饰器](#410-require_http_methods-装饰器)
   - [模板中渲染表单](#411-模板中渲染表单)
   - [CSRF 中间件](#412-csrf-中间件)
5. [三个视图的分工](#五三个视图的分工)
6. [与 md_doc 笔记的对应关系](#六与-md_doc-笔记的对应关系)
7. [易错点与注意事项](#七易错点与注意事项)
8. [复习自测清单](#八复习自测清单)
9. [待完善（下一阶段预留）](#九待完善下一阶段预留)

---

## 一、与前三阶段的对比（本阶段学了什么）

| 维度 | 阶段 1（djangoProject 路由） | 阶段 2（DjangoProject2 模板） | 阶段 3（DjangoProject3 ORM） | **阶段 4（Form_demo4 表单）** |
|------|------|------|------|------|
| 核心主题 | URL 路由 | 模板系统 | 数据库与 ORM | **表单验证与数据处理** |
| 数据来源 | 视图里写死 | context 里写死 | 数据库查询 | **用户提交（request.POST）** |
| 数据库 | SQLite（未用） | SQLite（未用） | MySQL（真正使用） | SQLite（默认） |
| 视图返回 | `HttpResponse` | `render` | `HttpResponse` | **`render` + `HttpResponse`** |
| 应用数 | 2 个 | 1 个 | 3 个 | **1 个（front）** |
| 新增知识 | 路径转换器、reverse、命名空间 | 模板标签/过滤器/继承 | 模型、迁移、ORM 查询 | **forms.Form / ModelForm / 验证器 / clean** |

> 一句话总结：阶段 1 解决「URL 怎么找到视图」，阶段 2 解决「视图怎么返回网页」，
> 阶段 3 解决「数据怎么存怎么查」，**阶段 4 解决「用户提交的数据怎么验证、怎么处理」**。

---

## 二、项目结构总览

```
form_demo4/
├── manage.py
├── db.sqlite3
├── Form_demo4/                    # 项目配置包
│   ├── settings.py                # ★ CSRF 中间件已注释；DIRS 配置 templates
│   ├── urls.py                    # 根路由：只分发到 front
│   └── wsgi.py / asgi.py
├── front/                         # 唯一应用
│   ├── models.py                  # ★ Article 模型（带 validators）
│   ├── forms.py                   # ★ 三个表单：MessageBoardForm / RegisterForm / ArticleForm
│   ├── views.py                   # ★ 三个视图，均用 @require_http_methods
│   ├── urls.py                    # ★ 3 条路由：'' / register / article
│   ├── admin.py / tests.py        # 空（预留）
│   └── migrations/
├── templates/                     # ★ 项目级模板目录（DIRS 查找）
│   ├── index.html                 # 留言板（{{ form }} 整体渲染）
│   ├── register.html              # 注册（手写 HTML 字段）
│   └── article.html               # 文章表单（手写 HTML 字段）
└── md_doc/                        # 4 篇课程笔记
    ├── 表单.md / 表单验证.md
    ├── 表单提取错误信息.md
    └── modleForm的使用.md
```

---

## 三、一个请求的完整生命周期（结合本项目）

```
浏览器访问 http://127.0.0.1:8000/front/
        │
        ▼
Form_demo4/urls.py  ──include──▶  front/urls.py  ──''──▶  views.index
        │                                                        │
        │                                                        ▼
        │                                              @require_http_methods(["GET","POST"])
        │                                                        │
        │                                    ┌─── GET ──────────┤
        │                                    │                    └─── POST ───┐
        │                                    ▼                                ▼
        │                           MessageBoardForm()              MessageBoardForm(request.POST)
        │                           render(index.html, form)        form.is_valid()
        │                                    │                        │
        │                                    ▼                    ┌── True ──┤
        │                           展示空白表单                   │          └── False ──┐
        │                                                             ▼                  ▼
        │                                                     cleaned_data 提取数据    form.errors
        │                                                             │                  │
        ▼                                                             ▼                  ▼
浏览器收到 HTML 页面                                          HttpResponse 返回结果   返回 "表单验证失败!"
```

> **核心流程**：GET 请求返回空表单 → 用户填写提交 → POST 请求到同一视图 → `is_valid()` 验证 →
> 通过则从 `cleaned_data` 取数据处理，失败则从 `form.errors` 取错误信息。

---

## 四、核心知识点对照代码

### 4.1 forms.Form 表单定义

表单的本质是一个继承自 `forms.Form` 的类，每个类属性对应一个表单字段。

```python
# front/forms.py
from django import forms

class MessageBoardForm(forms.Form):
    title = forms.CharField(min_length=2, max_length=20, label='标题')
    content = forms.CharField(widget=forms.Textarea, label='内容')
    email = forms.EmailField(label='邮箱')
```

**要点**：
- 继承 `forms.Form` → 普通表单（不依赖模型）
- 继承 `forms.ModelForm` → 模型表单（与模型绑定，见 4.8）
- 每个字段 = 一个 `Field` 实例，既负责**接收数据**，也负责**验证数据**

---

### 4.2 字段类型与常用参数

| Field 类型 | 用途 | 关键参数 |
|------------|------|----------|
| `CharField` | 文本输入 | `max_length`, `min_length`, `required`, `error_messages` |
| `EmailField` | 邮箱输入 | 自动验证邮箱格式 |
| `FloatField` | 浮点数 | `max_value`, `min_value` |
| `IntegerField` | 整数 | `max_value`, `min_value` |
| `URLField` | URL 输入 | 自动验证 URL 格式 |
| `BooleanField` | 布尔值 | `required` |
| `ChoiceField` | 下拉选择 | `choices=[(value, display), ...]` |
| `FileField` / `ImageField` | 文件上传 | ImageField 验证图片真实性 |

**CharField 参数详解**（本项目中的实际用法）：

```python
title = forms.CharField(
    min_length=2,            # 最小长度
    max_length=20,           # 最大长度
    label='标题',             # 模板中显示的标签
    error_messages={          # 自定义错误信息
        "min_length": "标题最小的长度不能少于2",
        "max_length": "标题最大的长度不能超过20",
    }
)
```

**widget 参数**：控制字段渲染成什么 HTML 控件。

```python
content = forms.CharField(widget=forms.Textarea, label='内容')
# 默认 CharField 渲染为 <input type="text">
# 指定 widget=forms.Textarea 后渲染为 <textarea></textarea>
```

---

### 4.3 内置验证器

验证器（validators）是附加在字段上的进一步校验逻辑，通过 `validators=[...]` 参数传入。

| 验证器 | 作用 | 示例 |
|--------|------|------|
| `RegexValidator` | 正则表达式验证 | `RegexValidator(r'1[345678]\d{9}', message='手机号码格式不符合')` |
| `MaxValueValidator` | 最大值验证 | `MaxValueValidator(100)` |
| `MinValueValidator` | 最小值验证 | `MinValueValidator(18)` |
| `MaxLengthValidator` | 最大长度验证 | `MaxLengthValidator(10)` |
| `MinLengthValidator` | 最小长度验证 | `MinLengthValidator(3)` |
| `EmailValidator` | 邮箱格式验证 | `EmailValidator()` |

**本项目中的实际用法**（RegisterForm 的手机号验证）：

```python
telephone = forms.CharField(
    validators=[
        validators.RegexValidator(
            r'1[345678]\d{9}',          # 正则：1开头，第二位3-8，后面9位数字
            message=('手机号码格式不符合')
        )
    ]
)
```

---

### 4.4 自定义字段验证：clean_字段名

Django 会自动寻找名为 `clean_<字段名>()` 的方法，在字段验证通过后执行额外的自定义校验。

```python
# front/forms.py — RegisterForm
class RegisterForm(forms.Form):
    telephone = forms.CharField(validators=[...])
    pwd1 = forms.CharField(min_length=6, max_length=100)
    pwd2 = forms.CharField(min_length=6, max_length=100)

    def clean_telephone(self):
        """ telephone 字段验证通过后自动调用 """
        telephone = self.cleaned_data.get('telephone')
        # 从数据库中查找 telephone 是否存在
        if telephone == '128888888':
            raise forms.ValidationError('该手机号码已存在')
        else:
            return telephone    # ★ 必须 return 值
```

**要点**：
- 方法名必须是 `clean_` + 字段名
- 从 `self.cleaned_data` 获取已验证的数据
- 验证失败：`raise forms.ValidationError('错误信息')`
- 验证成功：`return 值`（返回值会替换 `cleaned_data` 中该字段的值）

---

### 4.5 自定义全局验证：clean()

当验证逻辑涉及**多个字段**时，重写 `clean()` 方法。它在所有 `clean_<field>()` 之后执行。

```python
# front/forms.py — RegisterForm
def clean(self):
    """ 所有字段验证通过后自动调用 """
    clean_data = super().clean()          # ★ 必须先调用父类方法
    pwd1 = clean_data.get('pwd1')
    pwd2 = clean_data.get('pwd2')
    if pwd1 != pwd2:
        raise forms.ValidationError("两次密码不一样")
    else:
        return clean_data                  # ★ 必须 return clean_data
```

**验证执行顺序**：
```
字段定义（min_length 等） → clean_<field>() → clean() → 验证完成
```

---

### 4.6 表单验证流程：is_valid → cleaned_data

视图中的标准验证流程：

```python
# front/views.py
def index(request):
    if request.method == "GET":
        form = MessageBoardForm()             # 空表单
        return render(request, 'index.html', context={'form': form})
    else:
        form = MessageBoardForm(request.POST)  # 用 POST 数据填充表单
        if form.is_valid():                    # ★ 触发验证
            title = form.cleaned_data.get('title')
            content = form.cleaned_data.get('content')
            email = form.cleaned_data.get('email')
            return HttpResponse(f"{title},{content},{email}")
        else:
            print(form.errors)
            return HttpResponse('表单验证失败!')
```

**流程图**：
```
request.POST ──▶ form = Form(request.POST)
                      │
                      ▼
               form.is_valid()
                      │
            ┌── True ─┤──── False ──┐
            ▼                        ▼
    cleaned_data                form.errors
    （字典，已清洗数据）          （ErrorDict，错误信息）
```

---

### 4.7 错误信息提取

验证失败后，有多种方式获取错误信息：

| 方法 | 返回类型 | 用途 |
|------|----------|------|
| `form.errors` | `ErrorDict`（含 HTML 标签） | 模板中直接显示 |
| `form.errors.get_json_data()` | `dict`（结构化数据） | 程序中处理错误 |
| `form.as_json()` | `str`（JSON 字符串） | 返回给前端/接口 |

**`get_json_data()` 示例**：

```python
form = RegisterForm(data={'telephone': '123', 'pwd1': 'abc', 'pwd2': 'def'})
form.is_valid()  # False
print(form.errors.get_json_data())
# {
#     'telephone': [{'message': '手机号码格式不符合', 'code': 'invalid'}],
#     'pwd1': [{'message': 'Ensure this value has at least 6 characters...', 'code': 'min_length'}],
#     'pwd2': [{'message': 'Ensure this value has at least 6 characters...', 'code': 'min_length'}],
#     '__all__': [{'message': '两次密码不一样', 'code': ''}]   # clean() 中的错误
# }
```

**自定义格式化错误信息**（方便前端处理）：

```python
class MyForm(forms.Form):
    username = forms.URLField(max_length=4)

    def get_errors(self):
        errors = self.errors.get_json_data()
        new_errors = {}
        for key, message_dicts in errors.items():
            messages = []
            for message in message_dicts:
                messages.append(message['message'])
            new_errors[key] = messages
        return new_errors
# 返回: {'username': ['Enter a valid URL.', 'Ensure this value has at most 4 characters...']}
```

---

### 4.8 ModelForm：模型与表单绑定

`ModelForm` 可以自动根据模型字段生成表单字段，避免重复定义。

```python
# front/models.py
class Article(models.Model):
    title = models.CharField(max_length=200, validators=[validators.MinLengthValidator(limit_value=2)])
    content = models.TextField(validators=[validators.MinLengthValidator(limit_value=3)])
    creat_time = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=100, blank=True)

# front/forms.py
class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = "__all__"    # 包含模型所有字段
        # fields = ['title', 'content']   # 只包含指定字段
        # exclude = ['category']           # 排除指定字段
```

**`fields` vs `exclude`**：

| 用法 | 说明 |
|------|------|
| `fields = "__all__"` | 包含所有字段 |
| `fields = ['title', 'content']` | 白名单：只包含指定字段 |
| `exclude = ['category']` | 黑名单：排除指定字段 |

> **注意**：`fields` 和 `exclude` 必须指定其中一个，否则会抛出 `ImproperlyConfigured` 异常。

**`blank=True` 的区别**：
- 模型中 `blank=True`：表单验证时允许为空
- 数据库层面：`blank` 不影响，数据库是否允许为空取决于 `null=True`

---

### 4.9 ModelForm 的 save() 与 commit=False

**基本保存**：

```python
def article_view(request):
    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            # form.save()  # 直接保存到数据库
            title = form.cleaned_data.get('title')
            content = form.cleaned_data.get('content')
            return HttpResponse(f"{title},{content}")
```

**更新已有数据**（传入 `instance`）：

```python
article = Article.objects.get(pk=pk)
form = ArticleForm(request.POST, instance=article)
if form.is_valid():
    form.save()  # 此时是更新，不是新建
```

**`commit=False` 延迟保存**：

```python
article = form.save(commit=False)  # 返回模型实例，但不写入数据库
article.author = request.user       # 额外赋值
article.save()                      # 手动保存
```

---

### 4.10 @require_http_methods 装饰器

限制视图只接受指定的 HTTP 方法，其他方法返回 `405 Method Not Allowed`。

```python
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET", "POST"])
def index(request):
    ...
```

| 装饰器 | 效果 |
|--------|------|
| `@require_http_methods(["GET", "POST"])` | 只允许 GET 和 POST |
| `@require_GET` | 只允许 GET |
| `@require_POST` | 只允许 POST |

> **与不用装饰器的区别**：不用装饰器时，所有方法都会进入视图，需要手动 `if request.method == "GET"` 判断。

---

### 4.11 模板中渲染表单

**方式一：整体渲染（`{{ form }}`）**

```html
<!-- templates/index.html -->
<form action='' method="POST">
    {{ form }}                              <!-- 自动渲染所有字段为 <table> -->
    <input type="submit" value="提交">
</form>
```

**方式二：手写 HTML 字段**

```html
<!-- templates/register.html -->
<form action="" method="POST">
    <div><input type="text" name="telephone" placeholder="请输入手机号码"></div>
    <div><input type="password" name="pwd1" placeholder="请输入密码"></div>
    <div><input type="password" name="pwd2" placeholder="请确认密码"></div>
    <input type="submit" value="提交">
</form>
```

**方式三：逐字段渲染（常用，灵活控制布局）**

```html
<form method="POST">
    {% csrf_token %}
    <div>{{ form.title.label_tag }} {{ form.title }}</div>
    <div>{{ form.content.label_tag }} {{ form.content }}</div>
    <div>{{ form.email.label_tag }} {{ form.email }}</div>
    <input type="submit" value="提交">
</form>
```

| 渲染方式 | 输出 | 适用场景 |
|----------|------|----------|
| `{{ form }}` | `<table>` 包裹所有字段 | 快速原型 |
| `{{ form.as_p }}` | `<p>` 包裹每个字段 | 简单表单 |
| `{{ form.as_ul }}` | `<li>` 包裹每个字段 | 列表式表单 |
| 手动 `{{ form.field }}` | 单独控件 | 完全自定义布局 |

---

### 4.12 CSRF 中间件

本项目 `settings.py` 中 **CSRF 中间件被注释掉了**：

```python
MIDDLEWARE = [
    # 'django.middleware.csrf.CsrfViewMiddleware',  # ← 注释掉了，表单提交不需要 CSRF token
    ...
]
```

> **原因**：学习阶段为了方便，避免 `{% csrf_token %}` 遗漏导致 403 错误。
> **生产环境必须开启**，并在模板表单中添加 `{% csrf_token %}`。

---

## 五、三个视图的分工

| 视图 | 路由 | 表单 | 特点 |
|------|------|------|------|
| `index` | `/front/` | `MessageBoardForm` | GET 显示表单，POST 验证并提取数据 |
| `register_view` | `/front/register` | `RegisterForm` | 含正则验证 + 跨字段验证（两次密码一致） |
| `article_view` | `/front/article` | `ArticleForm` | ModelForm 与模型绑定 |

**三个视图的共性模式**：
```
GET  → 创建空表单 → render 模板（显示表单）
POST → 创建绑定表单 → is_valid() → 提取 cleaned_data 或打印 errors
```

---

## 六、与 md_doc 笔记的对应关系

| 笔记文件 | 覆盖内容 | 对应代码位置 |
|----------|----------|-------------|
| `表单.md` | 表单验证：Field 类型、验证器、自定义验证器、验证流程 | `front/forms.py` 全部 |
| `表单验证.md` | 表单验证：更完整的 Field 列表（含 BooleanField、ChoiceField、FileField） | 知识扩展 |
| `表单提取错误信息.md` | `form.errors` / `get_json_data()` / `as_json()` / 自定义 `get_errors()` | `views.py` 中 `print(form.errors...)` |
| `modleForm的使用.md` | ModelForm 基本使用、自定义错误消息、自定义字段、save()、commit=False、注意事项 | `ArticleForm` |

---

## 七、易错点与注意事项

1. **`clean_<field>()` 必须 return 值**：不 return 会导致该字段在 `cleaned_data` 中变成 `None`。
2. **`clean()` 必须调用 `super().clean()` 并 return `clean_data`**：否则后续验证会出错。
3. **`is_valid()` 只能调用一次**：重复调用会重新验证，且 `errors` 会被覆盖。
4. **`fields` 和 `exclude` 必须设置一个**：都不设置会抛 `ImproperlyConfigured`。
5. **慎用 `fields = "__all__"`**：敏感字段（如 `is_admin`）不应暴露在表单中。
6. **`editable=False` 的字段不会出现在 ModelForm 中**：如 `auto_now_add=True` 的时间字段。
7. **`blank=True` ≠ `null=True`**：`blank` 是表单层面的验证，`null` 是数据库层面的。
8. **CSRF 中间件**：学习时可注释，生产环境必须开启。
9. **POST 数据必须是 `request.POST`**：不能直接传 `request.GET` 给表单。
10. **`error_messages` 的 key 要与验证类型匹配**：如 `min_length`、`max_length`、`required`、`invalid`。

---

## 八、复习自测清单

能独立完成以下内容，说明本阶段过关：

- [ ] 说出 `forms.Form` 和 `forms.ModelForm` 的区别
- [ ] 熟练定义 `CharField` / `EmailField` 并设置 `min_length` / `max_length` / `label` / `error_messages`
- [ ] 使用 `validators=[...]` 添加 `RegexValidator` 等内置验证器
- [ ] 写出 `clean_<field>()` 方法实现单字段自定义验证
- [ ] 写出 `clean()` 方法实现跨字段验证（如两次密码一致）
- [ ] 在视图中正确使用 `is_valid()` → `cleaned_data` / `form.errors` 流程
- [ ] 使用 `form.errors.get_json_data()` 提取结构化错误信息
- [ ] 用 `ModelForm` 绑定模型，理解 `fields` / `exclude` 的区别
- [ ] 说出 `ModelForm.save()` 和 `save(commit=False)` 的区别
- [ ] 在模板中用 `{{ form }}` 或 `{{ form.field }}` 渲染表单
- [ ] 说出 `@require_http_methods` 的作用
- [ ] 理解 CSRF 中间件的作用及何时开启

---

## 九、待完善（下一阶段预留）

- [ ] 表单数据真正保存到数据库（当前只是提取后返回 HttpResponse）
- [ ] 模板中展示表单错误信息（`{{ form.title.errors }}`）
- [ ] 使用 `as_p` / `as_ul` 等方式渲染表单
- [ ] 文件上传表单（`FileField` / `ImageField`）
- [ ] 表单集（formset）处理多个表单
- [ ] 结合 `ModelForm.save()` 实现真正的数据持久化

---

> **一句话总结**：本阶段抓住「**用户提交数据 → 表单接收 → 验证器逐层校验 → cleaned_data 提取 → 错误处理**」这条主线，
> 掌握 `Form` 与 `ModelForm` 两种表单模式，能应对绝大多数 Web 表单场景。
