# F 表达式和 Q 表达式

## 1. F 表达式

F 表达式是用来优化 ORM 操作数据库的。比如我们要将公司所有员工的薪水都增加 1000 元，如果按照正常的流程，应该是先从数据库中提取所有的员工工资到 Python 内存中，然后使用 Python 代码在员工工资的基础之上增加 1000 元，最后再保存到数据库中。这里面涉及的流程就是，首先从数据库中提取数据到 Python 内存中，然后在 Python 内存中做完运算，之后再保存到数据库中。示例代码如下：

```
employees = Employee.objects.all()
for employee in employees:
    employee.salary += 1000
    employee.save()
```

而我们的 F 表达式就可以优化这个流程，他可以不需要先把数据从数据库中提取出来，计算完成后再保存回去，他可以直接执行 SQL 语句，就将员工的工资增加 1000 元。示例代码如下：

```
from django.db.models import F
Employee.objects.update(salary=F("salary")+1000)
```

F 表达式并不会马上从数据库中获取数据，而是在生成 SQL 语句的时候，动态获取传给 F 表达式的值。

比如如果想要获取作者中，`name`和`email`相同的作者数据。如果不使用 F 表达式，那么需要使用以下代码来完成：

```
authors = Author.objects.all()
for author in authors:
    if author.name == author.email:
        print(author)
```

> 
> 缺点：需要把所有作者数据查询加载到内存，再在 Python 层面做判断，数据量大时性能很差。

使用 F 表达式，直接在数据库层面进行字段对比：

```
from django.db.models import F
authors = Author.objects.filter(name=F("email"))
```

> 
> 原理：生成 SQL，在数据库中直接比较`name`字段和`email`字段，不需要把数据读到 Python 内存。

### F 表达式小结

1. **作用**：引用模型字段的值，**在数据库层面做运算 / 字段对比**，而不是读取到 Python 内存运算。
2. **优点**：减少查询次数、减少内存占用、并发安全（不会出现读取旧值再修改带来的竞争问题）。
3. **适用场景**：
   - 批量更新：字段自增、自减（`F("price")+10`）
   - 同一条记录内，两个字段互相比较（`filter(字段1=F("字段2"))`）

---

## 2. Q 表达式

Q 表达式用来包装查询条件，可以实现**复杂的逻辑查询**：`and`、`or`、`not`。
ORM 中直接使用`filter()`多个参数，默认是`AND`（并且）关系；如果需要`OR`（或者）、取反`NOT`，就要使用`Q`。

### 基础使用

导入：`from django.db.models import Q`

- `Q(条件)`：包装查询条件
- `|` 代表 `OR` 或
- `&` 代表 `AND` 且
- `~` 代表 `NOT` 非（取反）

#### 示例 1：OR 查询，查询名字是三国演义 或者 价格大于 98 的图书

```
from django.db.models import Q
# name="三国演义" OR price>98
books = Book.objects.filter(Q(name="三国演义") | Q(price__gt=98))
```

#### 示例 2：AND 多条件（可以和普通 filter 参数混用）

```
# (price>90 AND rating>4.8) 并且 pages>900
books = Book.objects.filter(Q(price__gt=90) & Q(rating__gt=4.8), pages__gt=900)
```

#### 示例 3：NOT ~ 取反，查询不是 “三国演义” 的图书

```
books = Book.objects.filter(~Q(name="三国演义"))
```

#### 示例 4：复杂组合条件

查询：(价格> 97 或者 评分 > 4.85)，并且作者 id=1

```
books = Book.objects.filter(
    Q(price__gt=97) | Q(rating__gt=4.85),
    author_id=1
)
```

### Q 表达式小结

1. 普通`filter(条件1,条件2)`是`AND`，**不能直接做 OR**；
2. Q 对象用`|`或`&`组合条件，`~`实现非；
3. Q 对象可以和普通 filter 关键字参数混用，Q 和普通参数之间是 AND 关系；

---

## 3. 结合你上面图书模型的实战练习代码

```
from django.db.models import F, Q
from front.models import Author,Book,Publisher,BookOrder

# ========= F表达式练习 =========
# 所有图书价格 + 2
Book.objects.update(price=F("price")+2)

# 查询图书名字等于出版社名字的数据（字段对比）
books = Book.objects.filter(name=F("publisher__name"))

# ========= Q表达式练习 =========
# 查询价格>98 或者 页数>1000 的图书
res = Book.objects.filter(Q(price__gt=98)|Q(pages__gt=1000))

# 查询 价格大于95，并且 评分不是4.8 的图书
res = Book.objects.filter(Q(price__gt=95) & ~Q(rating=4.8))
```

## 4. 底层 SQL 对照理解

```
# F表达式：Book.objects.update(price=F("price")+2)
# 生成SQL: UPDATE front_book SET price = price + 2;

# Q查询：Book.objects.filter(Q(price__gt=98)|Q(pages__gt=1000))
# 生成SQL: SELECT * FROM front_book WHERE price >98 OR pages>1000;
```