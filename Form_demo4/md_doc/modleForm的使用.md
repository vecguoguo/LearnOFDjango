# ModelForm：

## 一、基本使用

大家在写表单的时候，会发现表单中的 `Field` 和模型中的 `Field` 基本上是一模一样的，而且表单中需要验证的数据，也就是我们模型中需要保存的。那么这时候我们就可以将模型中的字段和表单中的字段进行绑定。
比如现在有个 `Article` 的模型。示例代码如下：

```python
from django.db import models
from django.core import validators
class Article(models.Model):
    title = models.CharField(max_length=10, validators=[validators.MinLengthValidator(limit_value=3)])
    content = models.TextField()
    author = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    create_time = models.DateTimeField(auto_now_add=True)
```

那么在写表单的时候，就不需要把 `Article` 模型中所有的字段都一个个重复写一遍了。示例代码如下：

```python
from django import forms
class MyForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = "__all__"
```

`MyForm` 是继承自 `forms.ModelForm`，然后在表单中定义了一个 `Meta` 类，在 `Meta` 类中指定了 `model=Article`，以及 `fields="__all__"`，这样就可以将 `Article` 模型中所有的字段都复制过来，进行验证。如果只想针对其中几个字段进行验证，那么可以给 `fields` 指定一个列表，将需要的字段写进去。比如只想验证 `title` 和 `content`，那么可以使用以下代码实现：

```python
from django import forms
class MyForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content']
```

如果要验证的字段比较多，只是除了少数几个字段不需要验证，那么可以使用 `exclude` 来代替 `fields`。比如我不想验证 `category`，那么示例代码如下：

```python
from django import forms
class MyForm(forms.ModelForm):
    class Meta:
        model = Article
        exclude = ['category']
```

---

## 二、自定义错误消息

使用 `ModelForm`，因为在 `Meta` 类中指定了 `model`，验证数据的时候，所有的错误消息都是根据模型中的字段配置自动生成的。如果我们想要自定义错误消息，可以在 `Meta` 类中添加 `error_messages` 属性，覆盖默认的错误信息。

```python
from django import forms
from .models import Article

class MyForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content']
        error_messages = {
            'title': {
                'max_length': '标题太长了，最多只能输入10个字符',
                'min_length': '标题太短了，至少需要3个字符',
                'required': '请填写标题',
            },
        }
```

---

## 三、自定义表单字段

有时候模型中的字段无法满足表单的需求，我们可以在 `ModelForm` 中重新定义该字段，这会覆盖模型默认生成的字段。

```python
from django import forms
from .models import Article

class MyForm(forms.ModelForm):
    # 重新定义 title 字段，覆盖模型中默认生成的 title
    title = forms.CharField(
        max_length=10,
        min_length=3,
        error_messages={'required': '标题不能为空'}
    )

    class Meta:
        model = Article
        fields = ['title', 'content']
```

---

## 四、ModelForm 保存数据

`ModelForm` 最大的便利在于它提供了一个 `save()` 方法，可以直接将验证通过的数据保存到数据库中。

### 1. 创建新数据

```python
def create_article(request):
    if request.method == 'POST':
        form = MyForm(request.POST)
        if form.is_valid():
            form.save()  # 直接保存到数据库，相当于调用 article.save()
            return redirect('article_list')
    else:
        form = MyForm()
    return render(request, 'create_article.html', {'form': form})
```

### 2. 更新已有数据

如果想要更新已有的数据，只需在实例化表单时传入 `instance` 参数：

```python
def edit_article(request, pk):
    article = Article.objects.get(pk=pk)
    if request.method == 'POST':
        form = MyForm(request.POST, instance=article)
        if form.is_valid():
            form.save()  # 此时是更新操作，而不是新建
            return redirect('article_list')
    else:
        form = MyForm(instance=article) # 渲染表单时，自动回显已有数据
    return render(request, 'edit_article.html', {'form': form})
```

---

## 五、使用 `commit=False` 处理额外逻辑

有时候我们在保存之前需要做一些额外的处理，比如给模型的外键字段赋值。这时可以使用 `form.save(commit=False)`，它会返回一个尚未保存到数据库的模型实例，你可以在修改该实例之后再调用 `.save()`。

```python
def create_article(request):
    if request.method == 'POST':
        form = MyForm(request.POST)
        if form.is_valid():
            # 生成模型实例，但暂不保存到数据库
            article = form.save(commit=False)
            # 给外键赋值（假设 author 是外键）
            article.author = request.user
            # 保存到数据库
            article.save()
            return redirect('article_list')
    # ...
```

---

## 六、注意事项

1. **`fields` 或 `exclude` 必须设置**：在 `ModelForm` 的 `Meta` 类中，`fields` 或 `exclude` 这两个属性必须指定其中一个，否则会抛出 `ImproperlyConfigured` 异常。
2. **慎用 `fields = "__all__"`**：如果模型中有敏感字段（比如 `is_admin`、`balance`），使用 `__all__` 会将所有字段暴露在表单中，容易被恶意篡改。尽量明确指定允许用户填写的字段。
3. **`editable=False` 的字段不会出现在表单中**：模型中设置了 `editable=False` 的字段（如 `create_time = models.DateTimeField(auto_now_add=True)`），不会自动生成表单字段。