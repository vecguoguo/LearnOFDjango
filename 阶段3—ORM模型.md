# 阶段3—ORM模型

> DjangoProject3 项目代码分析与复习。本文档基于 `1.start/DjangoProject3` 的实际代码整理，用于后续复习。
> 覆盖知识点：**MySQL 连接配置、模型定义与字段、迁移、三种表关系、ORM 增删改查、字段查找、反向查询、聚合函数、F/Q 表达式、原生 cursor**。
>
> Django 版本：**5.2** ｜ 项目名：`DjangoProject3` ｜ 应用：`book`、`article`、`front` ｜ 数据库：**MySQL**
> 配套笔记：`md_doc/`（9 篇）+ 测试数据 `sql_doc/data_insert.sql`

---

## 目录

1. [与前两阶段的对比（本阶段学了什么）](#一与前两阶段的对比本阶段学了什么)
2. [项目结构总览](#二项目结构总览)
3. [一个请求的完整生命周期（结合本项目）](#三一个请求的完整生命周期结合本项目)
4. [核心知识点对照代码](#四核心知识点对照代码)
   - [连接 MySQL：settings + pymysql](#41-连接-mysqlsettings--pymysql)
   - [迁移：模型 → 数据库表](#42-迁移模型--数据库表)
   - [模型定义：字段类型与参数](#43-模型定义字段类型与参数)
   - [三种表关系](#44-三种表关系)
   - [Meta 配置：db_table](#45-meta-配置db_table)
   - [ORM 增删改查（book 应用）](#46-orm-增删改查book-应用)
   - [查询：字段查找与跨关系查询（article 应用）](#47-查询字段查找与跨关系查询article-应用)
   - [反向查询 related_name](#48-反向查询-related_name)
   - [聚合函数（front 应用）](#49-聚合函数front-应用)
   - [F 表达式与 Q 表达式](#410-f-表达式与-q-表达式)
   - [原生 SQL：connection + cursor](#411-原生-sqlconnection--cursor)
   - [测试数据 data_insert.sql](#412-测试数据-data_insertsql)
5. [三个应用的分工](#五三个应用的分工)
6. [与 md_doc 笔记的对应关系](#六与-md_doc-笔记的对应关系)
7. [易错点与注意事项](#七易错点与注意事项)
8. [复习自测清单](#八复习自测清单)
9. [待完善（下一阶段预留）](#九待完善下一阶段预留)

---

## 一、与前两阶段的对比（本阶段学了什么）

| 维度 | 阶段 1（my.site 路由） | 阶段 2（DjangoProject2 模板） | 阶段 3（DjangoProject3 ORM） |
|------|------------------------|------------------------------|------------------------------|
| 核心主题 | URL 路由 | 模板系统 | **数据库与 ORM** |
| 数据来源 | 视图里写死 | context 里写死 | **数据库查询** |
| 数据库 | SQLite（默认，未用） | SQLite（未用） | **MySQL（真正连接使用）** |
| 视图返回 | `HttpResponse` | `render` | `HttpResponse`（打印结果到控制台） |
| 新增配置 | — | DIRS、STATIC、MEDIA | **DATABASES 切 MySQL + pymysql 驱动** |
| 模型 | 空 | 空 | **3 个应用 10 个模型 + 迁移文件** |

> 一句话总结：阶段 1 解决「请求怎么到视图」，阶段 2 解决「视图怎么返回网页」，
> 阶段 3 解决「**数据从哪来、怎么存、怎么查**」——本阶段全部围绕 `models.py` 和 QuerySet。

---

## 二、项目结构总览

```
DjangoProject3/
├── manage.py
├── DjangoProject3/                 # 项目配置包
│   ├── settings.py                 # ★ DATABASES 切换为 MySQL；注册 3 个应用
│   ├── __init__.py                 # ★ pymysql.install_as_MySQLdb()
│   ├── urls.py                     # 根路由：分发到 book / article / front
│   └── wsgi.py / asgi.py
├── book/                           # 应用 1：原生 SQL + ORM 基础增删改查
│   ├── models.py                   # ★ Book（name/author/pub_time/price）
│   ├── views.py                    # ★ cursor 查询、save/get/order_by/update/delete
│   ├── urls.py                     # ★ app_name = 'book'（命名空间）
│   └── migrations/0001_initial.py
├── article/                        # 应用 2：模型关系 + 查询（本阶段重头戏）
│   ├── models.py                   # ★ User / UserExtension / Article / Comment / Tag
│   ├── views.py                    # ★ 保存、删除、关联查询、字段查找 query1~query5
│   ├── urls.py                     # 7 条路由
│   └── migrations/0001~0005        # ★ 5 个迁移文件，记录模型演化过程
├── front/                          # 应用 3：Meta 配置 + 聚合 + F/Q
│   ├── models.py                   # ★ Author/Publisher/Book/BookOrder + Meta.db_table
│   ├── views.py                    # ★ aggregate/annotate/Avg/Count/Max/Min/Sum/F/Q
│   └── migrations/0001_initial.py  # options 里带 db_table
├── sql_doc/
│   └── data_insert.sql             # ★ 手动插入 front_* 测试数据
└── md_doc/                         # 9 篇课程笔记（本文档独立放在项目根目录）
    ├── 链接数据库.md / ORM模型.md / OMR模型的操作.md
    ├── 数据库操作.md / cursor 对象常用接口.md
    ├── 外键的配置.md / 模型中 Meta 配置.md
    ├── 聚合函数.md / F 表达式和 Q 表达式.md
```

**模型一览表（本阶段的资产）**

| 应用 | 模型 | 关键字段 | 关系 |
|------|------|---------|------|
| book | `Book` | name / author / pub_time(auto_now_add) / price(default=0) | 无 |
| article | `User` | username / password | 被引用方 |
| article | `UserExtension` | birthday / university | `OneToOneField → User`（扩展表） |
| article | `Article` | title / content / pub_time | `ForeignKey → User`（related_name="articles"）、`M2M → Tag` |
| article | `Comment` | content | `ForeignKey("self")` 自引用（楼中楼） |
| article | `Tag` | name | 被 Article 多对多引用 |
| front | `Author` | name / age / email | 被 Book 引用 |
| front | `Publisher` | name | 被 Book 引用 |
| front | `Book` | name / pages / price / rating | `FK → Author`、`FK → Publisher` |
| front | `BookOrder` | price | `FK → Book` |

> 注意：`book.Book` 和 `front.Book` 是**两个不同应用里的同名模型**，Django 靠「应用标签」区分：
> 表名分别是 `book_book` 和 `front_book`，互不冲突。

---

## 三、一个请求的完整生命周期（结合本项目）

以访问 `http://127.0.0.1:8000/book/book/query` 为例：

```
浏览器请求 /book/book/query
   │
   ▼
根路由 DjangoProject3/urls.py
   │  匹配 path('book/', include("book.urls")) → 剥掉 'book/' 前缀
   ▼
book/urls.py（app_name='book'）
   │  匹配 path('book/query', views.query_book, name='query_book')
   ▼
book/views.py → query_book(request)
   │  Book.objects.get(name="三国演义")      ← ORM：模型类 → SELECT SQL
   │  Django 自动把 SQL 发给 MySQL（配置读自 settings.DATABASES）
   │  结果行 → 转成 Book 模型实例（对象）
   │  try/except Book.DoesNotExist 处理没查到的情况
   ▼
HttpResponse("查找成功")（查询结果 print 到开发服务器控制台）
   │
   ▼
浏览器收到响应
```

**与前两阶段的差别**：视图里多了「ORM 查询」这一步，而 ORM 的 SQL 是 Django 根据
`models.py` 自动生成的——这就是 ORM（Object-Relational Mapping，对象-关系映射）的含义：
**用 Python 类操作数据库表，用对象操作表中一行数据**。

---

## 四、核心知识点对照代码

### 4.1 连接 MySQL：settings + pymysql

Django **不需要手动创建连接对象**，只要配置好，ORM 用到时自动连接：

```python
# DjangoProject3/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',   # 数据库引擎
        'NAME':   'Django_project3',            # 数据库名（需先在 MySQL 中创建）
        'USER':   'root',
        'PASSWORD': '1234',
        'HOST':   '127.0.0.1',
        'PORT':   '3306',
    }
}
```

```python
# DjangoProject3/__init__.py —— 用 pymysql 模块冒充 MySQLdb
import pymysql
pymysql.install_as_MySQLdb()
```

**要点**

1. Django 官方支持的引擎：`mysql` / `postgresql` / `sqlite3` / `oracle`。
2. 驱动二选一：
   - `mysqlclient`（官方推荐，C 扩展，`pip install mysqlclient`）——用它就**不需要** `__init__.py` 里那两行；
   - `pymysql`（纯 Python）——必须 `install_as_MySQLdb()` 冒充，因为 Django 找的模块名是 `MySQLdb`。
3. 配置改完后的同步命令：`python manage.py migrate`（把迁移应用到 MySQL）。
4. SQLite 与 MySQL 的差异体会点：MySQL 要**先建库**（`CREATE DATABASE Django_project3`），
   SQLite 会自动建文件；错误信息风格、数据类型细节也不同。

### 4.2 迁移：模型 → 数据库表

迁移是「模型代码」与「数据库表结构」之间的版本管理：

```bash
python manage.py makemigrations   # models.py 变化 → 生成/更新迁移文件（只改代码，不动数据库）
python manage.py migrate          # 迁移文件 → 真正执行 SQL，改数据库结构
```

**article 应用的 5 个迁移文件 = 模型的完整演化史**（复习时按顺序看，就是在回顾怎么一步步加字段）：

| 迁移文件 | 操作 | 对应的代码变化 |
|---------|------|---------------|
| `0001_initial.py` | CreateModel ×2 | 最初只有 `User` 和 `Article`（此时 Article 还没 pub_time、没 tags） |
| `0002_comment.py` | CreateModel | 新增 `Comment` 模型 |
| `0003_alter_article_author_userextension.py` | AlterField + CreateModel | 修改 Article.author 字段 + 新增 `UserExtension` |
| `0004_tag_article_tags.py` | CreateModel + AddField | 新增 `Tag` + 给 Article 加 `tags` 多对多字段 |
| `0005_article_pub_time.py` | AddField | 给 Article 加 `pub_time` |

**规律**：每执行一次 `makemigrations`，Django 对比模型与上个迁移的差异，生成一个带序号的新文件；
迁移文件里记录的就是**纯数据结构操作**（CreateModel/AddField/AlterField...），与业务逻辑无关。

迁移文件还能反向：`migrate app名 0002` 可**回滚**到某个版本（撤销后续迁移）。

### 4.3 模型定义：字段类型与参数

```python
# book/models.py —— 最简单的模型
class Book(models.Model):
    name = models.CharField(max_length=20, null=False)
    author = models.CharField(max_length=20, null=False)
    pub_time = models.DateTimeField(auto_now_add=True)   # 创建时间自动写入
    price = models.FloatField(default=0)

# article/models.py
class User(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=100)

# front/models.py
class Author(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    email = models.EmailField()          # 自带格式校验的 CharField
```

**本项目用到的字段类型**

| 字段 | 用途 | 出现处 |
|------|------|--------|
| `CharField(max_length=n)` | 短字符串，**必须写 max_length** | name/username/password |
| `TextField` | 长文本（文章内容、评论） | Article.content |
| `IntegerField` | 整数 | age/pages |
| `FloatField` | 浮点数 | price/rating |
| `DateTimeField` | 日期时间 | pub_time |
| `EmailField` | 邮箱（= CharField + 校验） | Author.email |
| `BigAutoField` | 自增主键（默认自动有 id 字段） | 所有模型 |

**常用字段参数**

| 参数 | 含义 | 本项目示例 |
|------|------|-----------|
| `default` | 默认值 | `price = FloatField(default=0)` |
| `null=True` | 数据库层允许为空 | `origin_comment`、`pub_time` |
| `auto_now_add=True` | **首次创建**时自动写入当前时间（之后不变） | `pub_time` |
| `auto_now=True` | **每次保存**都更新为当前时间（本项目未用） | — |
| `on_delete` | 外键被引用方删除时怎么办 | 见 4.4 |

> 记忆口诀：记录「创建时间」用 `auto_now_add`，记录「最后修改时间」用 `auto_now`。

### 4.4 三种表关系

```python
# article/models.py
class UserExtension(models.Model):                      # ① 一对一：用户扩展资料
    birthday = models.CharField(max_length=100)
    university = models.CharField(max_length=100)
    content = models.OneToOneField('User', on_delete=models.CASCADE)

class Article(models.Model):                            # ② 一对多：一个作者写多篇文章
    author = models.ForeignKey("User", on_delete=models.CASCADE, related_name="articles")
    tags = models.ManyToManyField("Tag", related_name="articles")   # ③ 多对多：一篇文章多个标签

class Comment(models.Model):                            # ④ 自引用：楼中楼评论
    origin_comment = models.ForeignKey("self", on_delete=models.CASCADE, null=True)
```

| 关系 | 字段 | 数据库实现 | 本项目示例 | 理解 |
|------|------|-----------|-----------|------|
| 一对多 | `ForeignKey` | 存对方主键（`author_id` 列） | User → Article | 一个用户多篇文章 |
| 一对一 | `OneToOneField` | 本质是 FK + unique | User → UserExtension | 1:1，扩展表不冗余 |
| 多对多 | `ManyToManyField` | **额外生成一张中间表** | Article ↔ Tag | 两表都存不下，必须第三张表 |
| 自引用 | `ForeignKey("self")` | 还是 FK | 评论 → 回复的评论 | 表自己关联自己 |

**`on_delete` 参数**（引用方数据的生死跟随策略）：

| 取值 | 行为 | 代码里出现 |
|------|------|-----------|
| `CASCADE` | 级联删除：作者删了，文章全删 | 全部外键都用它 |
| `SET_NULL` | 置空（需 `null=True`） | 笔记里练过，代码未用 |
| `SET_DEFAULT` | 设为默认值 | 笔记里练过 |
| `PROTECT` | 阻止删除 | 笔记里练过 |

**代码中的实战验证**（`article/views.py`）：

```python
def dele_data(request):
    user = User.objects.get(id=4)
    user.delete()          # ← CASCADE 生效：该用户的所有文章也被删除
    return HttpResponse("删除成功")
```

### 4.5 Meta 配置：db_table

```python
# front/models.py —— 每个模型都配了
class Author(models.Model):
    name = models.CharField(max_length=100)
    ...
    class Meta:
        db_table = 'front_author'      # 数据库表名
```

- 不配时 Django 的默认表名规则：**`应用名_模型名小写`** → `front_author`、`book_book`。
- 迁移文件里能看到它被固化：`options={'db_table': 'front_author'}`。
- `sql_doc/data_insert.sql` 里 `INSERT INTO front_author...` 能对上，就是因为表名确定。
- ⚠️ 细心会发现：这里的 `db_table` 值**恰好等于默认值**（`front_author`），
  所以「配了但看不出效果」。真正体会它的方法是改成一个不一样的名字（如 `author_info`）再 migrate。
- 其他 Meta 选项（`ordering` / `verbose_name` / `unique_together` / `abstract` ...）见笔记《模型中 Meta 配置》。

### 4.6 ORM 增删改查（book 应用）

`book/views.py` 是标准 CRUD 五连：

```python
# ① 增 —— 两种写法
book = Book(name='水浒传', author='施耐庵', price=99)
book.save()                              # 写法一：实例.save()
# Book.objects.create(name=..., author=..., price=...)   # 写法二（笔记里的批量/单行创建）

# ② 查 —— get（取单个，可能抛异常，必须处理）
try:
    book = Book.objects.get(name="三国演义")   # 返回一个模型对象
    print(book.id, book.name, book.author, book.price)
except Book.DoesNotExist:                # ★ 查不到时不返回 None，而是抛这个异常
    print("图书不存在")

# ③ 查 —— all/filter（返回 QuerySet 集合）
books = Book.objects.all()
books = Book.objects.filter(name="三国演义")

# ④ 排序
books = Book.objects.order_by("pub_time")   # 升序；字段前加 - 为降序：order_by("-pub_time")

# ⑤ 改 —— 先查后改（对象属性赋值后 save）
book = Book.objects.first()
book.name = '西游记'
book.save()                              # save() 会 UPDATE 该行所有字段

# ⑥ 删 —— filter 出集合后批量删
book = Book.objects.filter(name="西游记")
book.delete()                            # 也可以单个对象 .delete()
```

**关键区分**：

| 方法 | 返回 | 查不到时 |
|------|------|---------|
| `get(**kwargs)` | 单个对象 | 抛 `DoesNotExist` 异常 |
| `filter(**kwargs)` | QuerySet（列表状） | 空 QuerySet（不报错） |
| `first()` | 第一个或 `None` | 返回 `None` |

**QuerySet 惰性**：`filter/order_by/annotate` 一堆调用**不会立即发 SQL**，
真正遍历（for）、`len()`、`print(queryset)` 时才执行——一条链可反复追加条件，最终合成一条 SQL。

### 4.7 查询：字段查找与跨关系查询（article 应用）

`article/views.py` 的 query1~query5 是**字段查找（field lookup）**练习，
核心语法：`字段__查找类型=值`（双下划线分隔）：

```python
# query1：精确 / 忽略大小写的精确
Article.objects.filter(id=1)                  # 等价 id__exact=1
Article.objects.filter(title__iexact='GhatGpt5')   # i 忽略大小写

# query2：包含（LIKE '%chat%'）
Article.objects.filter(title__icontains='chat')    # contains 大小写敏感 / icontains 不敏感

# query3：枚举
Article.objects.filter(id__in=[1,2,3])             # WHERE id IN (1,2,3)

# query4：时间范围
Article.objects.filter(pub_time__range=(start_data, end_data))   # BETWEEN

# query5：跨关系查询（从 User 查它的文章标题）
User.objects.filter(articles__title__icontains='chat')
#                  ↑ related_name='articles'，两个下划线一路穿到 Article.title
```

**视图注释里记录的其余查找类型**（复习时背下来）：

| 查找 | 含义 |
|------|------|
| `gt` / `gte` | 大于 / 大于等于（date、数值通用） |
| `lt` / `lte` | 小于 / 小于等于 |
| `startswith` / `endswith` | 以…开头 / 结尾（大小写敏感；`istartswith` 不敏感） |
| `range` | 区间（闭区间） |
| `isnull` | 是否为空（`__isnull=True`） |

**查看 ORM 生成的 SQL（调试神器）**：

```python
qs = Article.objects.filter(title__iexact='GhatGpt5')
print(qs.query)     # 输出对应 SELECT 语句 —— 代码注释里强调的技巧
print(qs)           # 打印 QuerySet 本身；真正执行 SQL 发生在遍历时
```

### 4.8 反向查询 related_name

```python
# 模型里定义
author = models.ForeignKey("User", on_delete=models.CASCADE, related_name="articles")

# 视图里使用 —— 正向：Article → User（author 属性）；反向：User → Article（articles 属性）
user = User.objects.first()
articles = user.articles.filter(title__contains='GhatGpt5').all()   # 一对多反向
for article in articles:
    print(article.title)
```

- **正向**：顺着外键字段名查（`article.author`）。
- **反向**：被引用方通过 `related_name` 给的名字查（`user.articles`）；
  不设 `related_name` 时默认是 `小写模型名_set`（如 `user.article_set`）。
- `related_name` 同时决定**跨关系查询的写法**：`articles__title__icontains`（见 4.7 的 query5）。
- 多对多同理：`article.tags.all()` / `tag.articles.all()`（tags 的 related_name 也是 "articles"）。

### 4.9 聚合函数（front 应用）

```python
from django.db.models import Avg, Count, Max, Min, Sum, F, Q

# ① aggregate —— 整表聚合，返回字典
Book.objects.aggregate(Avg('price'))                       # {'price__avg': 97.25}
Book.objects.aggregate(book_count=Count('id'))             # {'book_count': 4}（起别名）
Author.objects.aggregate(max_age=Max('age'), min_age=Min('age'))   # 可同时多个

# ② annotate —— 分组聚合：每本书带出它的订单总价
Book.objects.annotate(total=Sum("bookorder__price")).values('name', 'total')
#                     ↑ 跨到 BookOrder（反向，模型名小写 bookorder），按书分组求和
#                    .values('name','total') 只取需要的列 → [{name:..., total:...}, ...]
```

**aggregate vs annotate（笔记里的核心考点）**：

| | `aggregate` | `annotate` |
|---|------------|-----------|
| 结果 | 一个汇总**字典** | QuerySet 每行**多一个字段** |
| 语义 | 全表/筛选集 → 一个数 | **按某字段分组** → 每组一个数 |
| SQL | `SELECT AVG(price) FROM ...` | `SELECT name, SUM(price) ... GROUP BY` |

### 4.10 F 表达式与 Q 表达式

```python
# F：引用「同一行的字段」参与运算 —— 不是取出来在 Python 里算
Book.objects.update(price=F('price') - 10)
# 生成：UPDATE front_book SET price = price - 10;   （SQL 层完成，一条语句搞定）

# Q：组装复杂条件（& 且 | 或 ~ 非），可加括号改变优先级
Book.objects.filter(Q(price__gte=80) | Q(rating__gte=9)).all()
# 生成：WHERE price >= 80 OR rating >= 9
```

- **F 解决的问题**：「给所有书加价 10 元」若用普通写法要先查出来逐个改（N+1 次 UPDATE）；
  F 让数据库一条 UPDATE 搞定，还能避免并发下的读写覆盖。
- **Q 解决的问题**：`filter(a>1, b<2)` 只能 AND；要 OR、要 `(A or B) and C` 就必须 Q。
- 笔记《F 表达式和 Q 表达式》末尾有 4 道实战练习题（价格+2、字段对比、组合条件），值得重做。

### 4.11 原生 SQL：connection + cursor

Django 封装了 `connection` 对象，**自动读取 settings 的数据库配置**，无需自己建连接：

```python
# book/views.py
from django.db import connection

def index(request):
    cursor = connection.cursor()          # 1. 获取游标
    cursor.execute("select * from book")  # 2. 执行 SQL
    rows = cursor.fetchall()              # 3. 取全部结果（元组的列表）
    for row in rows:
        print(row)
    return HttpResponse("查找成功")
```

**cursor 常用接口**（对应笔记《cursor 对象常用接口》）：

| 接口 | 作用 |
|------|------|
| `execute(sql, params=None)` | 执行一条 SQL（建议用参数占位防注入：`"WHERE name=%s", [name]`） |
| `executemany(sql, seq)` | 批量执行同一结构的 SQL |
| `fetchone()` | 取一行 |
| `fetchmany(n)` | 取 n 行 |
| `fetchall()` | 取全部行 |
| `close()` | 关闭游标 |

**什么时候用原生 SQL 而不是 ORM**：超复杂聚合/窗口函数、ORM 不支持的语法、
已有 DBA 优化好的语句——日常业务优先 ORM。

### 4.12 测试数据 data_insert.sql

```sql
INSERT INTO front_author(name,age,email) VALUES ('曹雪芹',35,'cxq@qq.com'), ...;
INSERT INTO front_publisher(name) VALUES ('中国邮电出版社'), ...;
INSERT INTO front_book(name,pages,price,rating,author_id,publisher_id) VALUES ('三国演义',987,98,4.8,3,1), ...;
INSERT INTO front_book_order(book_id,price) VALUES (1,95), (1,85), ...;
```

- 表名 `front_*` 与模型的 `Meta.db_table` 对应；**外键列名 = 字段名 + `_id`**
  （`author = ForeignKey(Author)` → 列 `author_id`），这是 Django 的列命名规则。
- 这份数据正是给 front 的聚合视图（avg/count/max_min/sum/q）准备的——
  `data_insert.sql` 里的 4 本书、2 个出版社、5 张订单，跑 `front/avg` 就能出结果。
- 复习方式：**手敲一遍这个 SQL**，同时对照 front 模型默写表结构。

---

## 五、三个应用的分工

| 应用 | 主题 | 视图清单 | 对应笔记 |
|------|------|---------|---------|
| **book** | 原生 SQL + ORM 基础 CRUD | `index`(cursor) / `add_book` / `query_book` / `order_view` / `update_view` / `delete_view` | 数据库操作、cursor 接口、OMR模型的操作 |
| **article** | 模型关系 + 字段查找 | `article_test`(保存) / `dele_data` / `one_to_many` / `query1~query5` | ORM模型、外键的配置 |
| **front** | Meta + 聚合 + F/Q | `avg` / `count` / `max_min` / `sum` / `f` / `q` | 模型中 Meta 配置、聚合函数、F/Q 表达式 |

路由结构（根 `urls.py` 统一用 `include` 分发，沿袭阶段1 规范）：

```
/book/       → book.urls    （app_name='book'，反向解析用 'book:xxx'）
/article/    → article.urls
/front/      → front.urls
/admin/      → Django 后台
```

---

## 六、与 md_doc 笔记的对应关系

| md_doc 笔记 | 对应代码 | 复习重点 |
|------------|---------|---------|
| `链接数据库.md` | `settings.py` + `__init__.py` | DATABASES 六项配置、驱动选择、migrate 同步 |
| `ORM模型.md` | 三个 `models.py` | ORM 概念、模型创建、映射到数据库 |
| `OMR模型的操作.md`（文件名笔误，应为 ORM） | `book/views.py` + `article/views.py` | 字段类型/参数、增删改查、过滤条件、排序、QuerySet 特性 |
| `数据库操作.md` | `book/views.py → index` | connection + cursor 三步走 |
| `cursor 对象常用接口.md` | 同上 | execute/fetchone/fetchmany/fetchall |
| `外键的配置.md` | `article/models.py` | on_delete 五种策略、related_name、正向/反向查询、M2M、O2O |
| `模型中 Meta 配置.md` | `front/models.py` | db_table、ordering、verbose_name、unique_together、abstract |
| `聚合函数.md` | `front/views.py → avg/count/max_min/sum` | 五聚合函数、aggregate vs annotate |
| `F 表达式和 Q 表达式.md` | `front/views.py → f_view/q_view` | 字段间运算、OR/AND 组合、底层 SQL 对照 + 4 道练习 |

---

## 七、易错点与注意事项

1. **`select * from book` 的表名问题（最值得验证的一处）**
   `book` 应用的模型默认表名是 **`book_book`**（`应用名_模型名`），而 cursor 里写的是 `select * from book`。
   如果 MySQL 里没有手动建过名为 `book` 的表，这条语句会报 `Table 'Django_project3.book' doesn't exist`。
   复习时到 MySQL 里 `SHOW TABLES;` 核对：你查的到底是手动建的 `book` 表，还是 Django 生成的 `book_book`？

2. **`query5` 视图写了但没注册路由**
   `article/views.py` 定义了 `query5`，但 `article/urls.py` 只到 `query4`——访问 `/article/query5` 会 404。
   （同阶段1 的教训：视图和路由要成对出现。）

3. **三个 `admin.py` 全是空的**
   10 个模型都没注册到后台，`/admin/` 里什么也看不到。注册一行即可：
   `admin.site.register(Book)`（对应你路线图的「Admin 后台」，也是阶段2 遗留待办）。

4. **`from django.db.models.expressions import result` 是多余导入**
   `front/views.py` 第 1 行（多半是 IDE 自动补全带进来的），紧接着函数内 `result = ...` 又把它覆盖了。
   删掉不影响任何功能——清理无用 import 是好习惯。

5. **`settings.py` 里的明文密码**
   MySQL `root/1234` 和 `SECRET_KEY` 都明文写在代码里，`DEBUG=True`。学习环境无妨，**上线必须**改
   环境变量 + 关 DEBUG + 非 root 账号 + `ALLOWED_HOSTS`。

6. **`TEMPLATES DIRS` 指向不存在的 `templates/` 目录**
   本项目所有视图都直接返回 `HttpResponse`，没用模板——DIRS 配了但目录不存在（目前不报错，
   等你第一次 `render` 时就会找不到模板）。沿袭阶段2，目录建好即可用。

7. **`save()` 是全字段更新**
   `book.save()` 会 UPDATE 该行**所有列**。批量改一个字段应使用
   `Book.objects.update(price=...)` 或 F 表达式（见 `f_view`），效率更高。

8. **`auto_now_add` 不会随 save 更新**
   `pub_time` 只在插入时写一次；想记录修改时间要另加 `updated_at = DateTimeField(auto_now=True)`。

9. **`DoesNotExist` 必须 try/except**
   `get()` 查不到抛异常而非返回 None；用 `filter().first()` 则返回 None——两种风格别混。

10. **外键列名是 `xxx_id`**
    模型字段叫 `author`，数据库列叫 `author_id`（SQL 手写 INSERT 时最容易忘，见 data_insert.sql）。

11. **`password` 明文存进 CharField**
    `User.password = CharField` 直接存 `'1234'`。真实项目必须用 Django 自带 auth 的
    `make_password/check_password`（阶段「用户认证」再学）。

12. **路由依然没有尾斜杠**（三个阶段一贯如此）
    `/book/book/query` 能开、`/book/book/query/` 404。建议从下个项目起统一加 `/`。

13. **FloatField 存金额有精度隐患**
    price/rating 用 FloatField 练手没问题，正式项目金额应使用 `DecimalField(max_digits, decimal_places)`。

---

## 八、复习自测清单

合上文档，回答以下问题：

<details>
<summary>点击展开答案</summary>

1. **Django 连接数据库需要手动创建 connection 对象吗？需要配什么？**
   → 不需要，ORM 自动连接；配 `settings.DATABASES`（ENGINE/NAME/USER/PASSWORD/HOST/PORT）。

2. **`makemigrations` 和 `migrate` 各做什么？区别？**
   → 前者对比 models.py 生成迁移文件（不动数据库）；后者执行迁移文件里的 SQL 改数据库结构。

3. **article 应用为什么有 5 个迁移文件？**
   → 模型分 5 次演化：初始(User+Article) → 加 Comment → 改 author/加 UserExtension → 加 Tag 和 M2M → 加 pub_time。

4. **ForeignKey / OneToOneField / ManyToManyField 各自的数据库实现？**
   → FK 存对方主键列；O2O = FK + 唯一约束；M2M 额外生成一张中间表。

5. **`on_delete=CASCADE` 什么意思？代码哪里体现了？**
   → 引用方随被引用方一起删；`dele_data` 里删 User 会连带删掉他的所有 Article。

6. **`get()` 与 `filter()` 的区别？查不到时各是什么表现？**
   → get 返回单个对象、查不到抛 DoesNotExist；filter 返回 QuerySet、查不到是空集不报错。

7. **`user.articles.filter(...)` 这个反向能力是谁给的？不写会怎样？**
   → 模型里的 `related_name="articles"`；不写默认是 `user.article_set`。

8. **写一条忽略大小写的「包含 chat」查询。**
   → `Article.objects.filter(title__icontains='chat')`

9. **想看 ORM 生成的 SQL 怎么办？**
   → `print(qs.query)`（SQL 在首次遍历 QuerySet 时才真正执行）。

10. **`aggregate` 和 `annotate` 的区别？各自的 SQL 长什么样？**
    → aggregate 全表汇总返回字典（`SELECT AVG(...)` 无 GROUP BY）；annotate 分组、每行多一列（带 GROUP BY）。

11. **`Book.objects.update(price=F('price')-10)` 生成什么 SQL？为什么比先查后改好？**
    → `UPDATE front_book SET price=price-10`；一条 SQL 数据库内完成，无 N+1、无并发覆盖。

12. **`Q(price__gte=80) | Q(rating__gte=9)` 中 | 是什么？**
    → Q 对象的按位或 = SQL 的 OR（`&` 是 AND，`~` 是 NOT）。

13. **原生 SQL 三步走？connection 的好处？**
    → `connection.cursor()` → `execute()` → `fetchall()`；connection 自动读 settings 的数据库配置。

14. **模型字段 `author = ForeignKey(...)` 对应数据库列名？**
    → `author_id`（列名 = 字段名 + `_id`）。

15. **`book` 和 `front` 里都有 Book 模型，会冲突吗？**
    → 不会，应用标签不同，表名分别为 `book_book` / `front_book`。

</details>

---

## 九、待完善（下一阶段预留）

按你《Django学习指南》路线图，「数据与后台」还差**后台**这一半，此外可补：

- [ ] **注册 Admin 后台**：三个 `admin.py` 都为空 → `admin.site.register(...)` + `list_display/search_fields`
- [ ] 补上 `query5` 的路由（或删除视图）
- [ ] 验证并修正 cursor 视图的表名（`book` vs `book_book`）
- [ ] `User.password` 换成 Django auth 的哈希存储
- [ ] 模型加 `__str__` 方法（Admin 和调试打印更友好）
- [ ] 给 front 的 FloatField 金额换成 `DecimalField`
- [ ] 金额/评分等加 `Meta.ordering`（体会 ordering 与 order_by 的关系）
- [ ] 练习笔记里的 Q/F 实战题（4 道）
- [ ] 写入数据时改用 `bulk_create` / `update_fields`（效率专题）
- [ ] `python manage.py shell` 交互式练查询（比写视图-访问-看控制台更快）

**建议的下一步动手练习**：把 article 的数据展示做成真实页面——
在 admin 后台录入文章 → 视图 `Article.objects.select_related('author').all()` 查数据
→ 用阶段2 的模板 `{% for %}` 渲染列表。既补上 Admin 待办，又把三个阶段串成一条线
（顺带解决这里 `select_related` 预取外键这个新知识点：避免 N+1 查询）。
