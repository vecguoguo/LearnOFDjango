from django import forms
from django.core import validators
# 留言表的表单
class MessageBoardForm(forms.Form):
    title = forms.CharField(min_length=2,max_length=20,label='标题',
                            error_messages={
                                "min_length":"标题最小的长度不能少于2",
                                "max_length":"标题最大的长度不能超过20",
                            })
    content = forms.CharField(widget=forms.Textarea,label = '内容')
    email = forms.EmailField(label='邮箱')

    # 注册的表单
class RegisterForm(forms.Form):
    telephone = forms.CharField(validators=[validators.RegexValidator(r'1[345678]\d{9}',message=('手机号码格式不符合'))])
    pwd1 = forms.CharField(min_length=6,max_length=100)
    pwd2 = forms.CharField(min_length=6,max_length=100)

# clean_[field]
    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')

    #     从数据库中查找telephone是否存在
        if telephone == '128888888':
            raise forms.ValidationError('该手机号码已存在')
        else:
            return telephone
    def clean(self):
        clean_data = super().clean()