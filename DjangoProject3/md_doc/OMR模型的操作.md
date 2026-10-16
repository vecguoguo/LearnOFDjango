# 一、模型常用的字段类型

| 字段类型 | 说明 |
|----------|------|
| `AutoField` | 自增字段，通常用作主键。Django 默认会为每个模型添加一个名为 `id` 的自增主键，所以一般不需要手动定义 |
| `BigAutoField` | 大整数自增字段，Django 3.2+ 默认使用 |
| `CharField` | 字符串字段，必须指定 `max_length` |
| `TextField` | 大文本字段，不限制长度 |
| `IntegerField` | 整数字段 |
| `FloatField` | 浮点数字段 |
| `DecimalField` | 高精度小数，需指定 `max_digits` 和 `decimal_places` |
| `BooleanField` | 布尔字段 |
| `DateField` | 日期字段，`auto_now_add` 表示创建时自动设置，`auto_now` 表示每次保存自动更新 |
| `DateTimeField` | 日期时间字段 |
| `EmailField` | 邮箱字段，会做格式校验 |
| `URLField` | URL 字段 |
| `ImageField` | 图片字段，需配合 `Pillow` 使用 |
| `FileField` | 文件字段 |

# 二、模型常用的字段参数

| 参数 | 说明 |
|------|------|
| `null` | 数据库中该字段是否可以为空，默认为 `False` |
| `blank` | 表单验证时是否允许为空，默认为 `False` |
| `default` | 默认值 |
| `primary_key` | 是否为主键，默认为 `False` |
| `unique` | 是否唯一，默认为 `False` |
| `db_index` | 是否创建索引 |
| `verbose_name` | 字段在后台显示的名称 |
| `choices` | 提供选项，通常配合 `get_字段名_display()` 使用 |
| `auto_now_add` | 创建时自动设置当前时间 |
| `auto_now` | 每次保存时自动设置当前时间 |

# 三、模型常用的 Meta 选项

```python
class Book(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'book_model'         # 自定义表名
        ordering = ['-id']              # 默认排序规则
        verbose_name = '书籍'           # 后台显示的单数名称
        verbose_name_plural = '书籍'    # 后台显示的复数名称
```

| 选项 | 说明 |
|------|------|
| `db_table` | 自定义数据库表名 |
| `ordering` | 默认排序字段，`-` 表示倒序 |
| `verbose_name` | 后台显示的单数名称 |
| `verbose_name_plural` | 后台显示的复数名称 |
| `unique_together` | 联合唯一约束 |
| `index_together` | 联合索引 |

# 四、ORM 常用查询接口

### 1. 查询所有数据

```python
books = Book.objects.all()
```

### 2. 条件查询

```python
# 精确查询
book = Book.objects.get(id=1)       # 不存在或存在多条都会报错

# 过滤查询（返回 QuerySet）
books = Book.objects.filter(author='张三')

# 排除查询
books = Book.objects.exclude(author='张三')

# 第一条数据
book = Book.objects.first()
```

### 3. 常用的过滤条件

```python
Book.objects.filter(price__gt=10)         # 大于
Book.objects.filter(price__gte=10)        # 大于等于
Book.objects.filter(price__lt=10)         # 小于
Book.objects.filter(price__lte=10)        # 小于等于
Book.objects.filter(name__contains='Django')     # 包含（区分大小写）
Book.objects.filter(name__icontains='django')    # 包含（不区分大小写）
Book.objects.filter(name__startswith='D')        # 以...开头
Book.objects.filter(name__endswith='o')          # 以...结尾
Book.objects.filter(id__in=[1, 2, 3])            # 在列表中
Book.objects.filter(price__range=(10, 100))      # 在范围内
```

### 4. 排序

```python
Book.objects.order_by('price')        # 升序
Book.objects.order_by('-price')       # 降序
```

### 5. 新增数据

```python
# 方式一
book = Book(name='Django入门', author='张三', price=59.9)
book.save()

# 方式二
Book.objects.create(name='Django入门', author='张三', price=59.9)
```

### 6. 修改数据

```python
book = Book.objects.get(id=1)
book.price = 69.9
book.save()

# 或者批量修改
Book.objects.filter(author='张三').update(price=69.9)
```

### 7. 删除数据

```python
book = Book.objects.get(id=1)
book.delete()

# 或者批量删除
Book.objects.filter(author='张三').delete()
```

# 五、外键关系

### 1. 一对多

```python
class Author(models.Model):
    name = models.CharField(max_length=50)

class Book(models.Model):
    name = models.CharField(max_length=100)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
```

- `on_delete=models.CASCADE`：级联删除，作者删除时书籍也删除
- `on_delete=models.SET_NULL`：作者删除时书籍的 author 字段设为 NULL（需要 `null=True`）
- `on_delete=models.PROTECT`：有书籍关联时禁止删除作者

### 2. 多对多

```python
class Book(models.Model):
    name = models.CharField(max_length=100)

class Tag(models.Model):
    name = models.CharField(max_length=50)

class BookTag(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
```

或者直接用 `ManyToManyField`：

```python
class Book(models.Model):
    name = models.CharField(max_length=100)
    tags = models.ManyToManyField('Tag')

class Tag(models.Model):
    name = models.CharField(max_length=50)
```

# 六、QuerySet 特性

1. **惰性执行**：`filter()` 不会立刻查数据库，只有在遍历、切片、打印等操作时才会真正执行 SQL。

2. **缓存**：第一次遍历 QuerySet 时会把结果缓存下来，再次遍历同一个 QuerySet 不会重新查数据库。

3. **链式调用**：`Book.objects.filter(...).exclude(...).order_by(...)` 可以链式组合多个查询。

4. **切片**：`Book.objects.all()[:10]` 限制返回条数，等价于 SQL 的 `LIMIT`。

# 七 、总结

- ORM 让开发者通过**类与对象**操作数据库，不用手写 SQL。
- 核心流程：**定义模型 → 注册 app → makemigrations → migrate**。
- 常用接口：`all`、`filter`、`get`、`exclude`、`order_by`、`create`、`update`、`delete`。
- 字段、参数、Meta 选项掌握常用的即可，遇到特殊需求查官方文档。
- 项目越大，ORM 的优势越明显，建议优先使用 ORM 而不是原生 SQL。