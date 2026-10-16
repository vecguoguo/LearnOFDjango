# 三、模型中 Meta 配置：

对于一些模型级别的配置。我们可以在模型中定义一个类，叫做 `Meta`。然后在这个类中添加一些类属性来控制模型的作用。比如我们想要在数据库映射的时候使用自己指定的表名，而不是使用模型的名称。那么我们可以在 `Meta` 类中添加一个 `db_table` 的属性。示例代码如下：

```python
class Book(models.Model):
    name = models.CharField(max_length=20, null=False)
    desc = models.CharField(max_length=100, name='description', db_column="description1")

    class Meta:
        db_table = 'book_model'
```

以下将对 `Meta` 类中的一些常用配置进行解释。

## db_table：

这个模型映射到数据库中的表名。如果没有指定这个参数，那么在映射的时候将会使用模型名来作为默认的表名。

## ordering：

设置在提取数据的排序方式。后面章节会讲到如何查找数据。比如我想在查找数据的时候根据添加的时间排序，那么示例代码如下：

```python
class Book(models.Model):
    name = models.CharField(max_length=20, null=False)
    pub_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'book_model'
        ordering = ['-pub_time']   # 按发布时间倒序排列
```

`ordering` 是一个列表，可以指定多个字段。字段名前加 `-` 表示倒序，不加表示升序。比如 `ordering = ['-pub_time', 'name']` 表示先按发布时间倒序，时间相同时再按名称升序。

## verbose_name：

给模型起一个更易读的名字，在 admin 后台显示时使用。示例代码如下：

```python
class Book(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        verbose_name = '书籍'
        verbose_name_plural = '书籍'
```

- `verbose_name`：单数形式的名字。
- `verbose_name_plural`：复数形式的名字。如果不指定，Django 会在 `verbose_name` 后面加一个 `s`。

## unique_together：

联合唯一约束，即多个字段组合起来不能重复。示例代码如下：

```python
class Book(models.Model):
    name = models.CharField(max_length=20)
    author = models.CharField(max_length=20)

    class Meta:
        unique_together = [('name', 'author')]
```

以上代码表示：同一本书的 `name` 和 `author` 组合起来必须唯一，不能出现两本完全同名的书由同一个作者编写。

## index_together：

联合索引，用于加快多字段组合查询的速度。示例代码如下：

```python
class Book(models.Model):
    name = models.CharField(max_length=20)
    author = models.CharField(max_length=20)

    class Meta:
        index_together = [('name', 'author')]
```

> 注意：在 Django 4.2 及以后的版本中，`index_together` 已被废弃，推荐使用 `indexes` 配合 `models.Index` 代替：
> ```python
> class Meta:
>     indexes = [
>         models.Index(fields=['name', 'author']),
>     ]
> ```

## abstract：

如果设置为 `True`，表示这是一个抽象基类，不会在数据库中生成对应的表。通常用于多个模型共享公共字段。示例代码如下：

```python
class BaseModel(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Book(BaseModel):
    name = models.CharField(max_length=20)
```

`Book` 会继承 `BaseModel` 中的 `create_time` 和 `update_time` 字段，但 `BaseModel` 本身不会生成表。

## permissions：

自定义权限，用于 admin 后台或权限系统。示例代码如下：

```python
class Book(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        permissions = [
            ('can_publish_book', '可以发布书籍'),
        ]
```

## default_permissions：

默认权限，默认为 `('add', 'change', 'delete', 'view')`。如果不想让某个模型拥有某些默认权限，可以在这里修改。示例代码如下：

```python
class Book(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        default_permissions = ('add', 'change')
```

## managed：

默认为 `True`，表示 Django 会管理该表的创建、修改和删除。如果设置为 `False`，Django 不会对该表做任何数据库层面的操作，通常用于已经存在的、由其他系统维护的表。示例代码如下：

```python
class Book(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        managed = False
```

## 总结：

| 配置项 | 作用 |
|--------|------|
| `db_table` | 自定义数据库表名 |
| `ordering` | 默认排序方式，`-` 表示倒序 |
| `verbose_name` | 后台显示的单数名称 |
| `verbose_name_plural` | 后台显示的复数名称 |
| `unique_together` | 联合唯一约束 |
| `index_together` | 联合索引（4.2 后推荐用 `indexes`） |
| `abstract` | 是否为抽象基类 |
| `permissions` | 自定义权限 |
| `default_permissions` | 默认权限 |
| `managed` | Django 是否管理该表的数据库操作 |

掌握这些常用的 Meta 配置，可以让你的模型更灵活、更贴合实际业务需求。遇到不常见的场景时，可以查阅 Django 官方文档中 "Model Meta options" 一节。