# ORM模型介绍

## 一、ORM模型介绍

随着项目越来越大，采用写原生SQL的方式在代码中会出现大量的SQL语句，那么问题就出现了：

1. SQL语句重复利用率不高，越复杂的SQL语句条件越多，代码越长。会出现很多相近的SQL语句。

2. 很多SQL语句是在业务逻辑中拼出来的，如果有数据库需要更改，就要去修改这些逻辑，这会很容易漏掉对某些SQL语句的修改。

3. 写SQL时容易忽略web安全问题，给未来造成隐患。SQL注入。

ORM，全称Object Relational Mapping，中文叫做对象关系映射，通过ORM我们可以通过类的方式去操作数据库，而不用再写原生的SQL语句。通过把表映射成类，把行作实例，把字段作为属性，ORM在执行对象操作的时候最终还是会把对应的操作转换为数据库原生语句。使用ORM有许多优点：

1. 易用性：使用ORM做数据库的开发可以有效的减少重复SQL语句的概率，写出来的模型也更加直观、清晰。

2. 性能损耗小：ORM转换成底层数据库操作指令确实会有一些开销。但从实际的情况来看，这种性能损耗很少（不足5%），只要不是对性能有严苛的要求，综合考虑开发效率、代码的阅读性，带来的好处要远远大于性能损耗，而且项目越大作用越明显。

3. 设计灵活：可以轻松的写出复杂的查询。

4. 可移植性：Django的ORM封装了底层数据库的差异，开发者只需要面向ORM编写代码，切换数据库时只需要修改配置文件即可，不用修改大量的业务代码。

## 二、创建ORM模型

ORM模型一般都是放在app的`models.py`文件中。每个app都可以拥有自己的模型。并且如果这个模型想要映射到数据库中，那么这个app必须要放在`settings.py`的`INSTALLED_APPS`中。示例代码如下：

```python
from django.db import models

class Book(models.Model):
    name = models.CharField(max_length=100, null=False)
    author = models.CharField(max_length=50, null=False)
    price = models.FloatField(default=0, null=False)

    def __str__(self):
        return f"{self.name} - {self.author}"
```

以上便定义了一个模型。这个模型继承自`django.db.models.Model`，如果这个模型想要映射到数据库中，就必须继承自这个类。这个模型以后映射到数据库中，表名是`book`（小写app名字 + 下划线 + 模型名小写）。如果想让表名自定义，可以在模型内部定义一个`class Meta`，然后添加`db_table`属性，示例代码如下：

```python
class Book(models.Model):
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=50)

    class Meta:
        db_table = 'book_model'
```

## 三、映射模型到数据库中

将ORM模型映射到数据库中，总结起来就是以下几步：

1. 在`settings.py`中，配置好`DATABASES`，做好数据库相关的配置。

2. 在app中的`models.py`中定义好模型，这个模型必须继承自`django.db.models`。

3. 将这个app添加到`settings.py`的`INSTALLED_APPS`中。

4. 在命令行终端，进入到项目所在的路径，执行命令`python manage.py makemigrations`来生成迁移脚本文件。

5. 同样在命令行中，执行命令`python manage.py migrate`来将迁移脚本文件映射到数据库中。