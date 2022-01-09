from stark.service.stark import BaseModelForm, StarkForm
from django import forms
from django.forms.utils import ValidationError
from management import models
from management.utils.md5 import gen_md5


class AddUserModelForm(BaseModelForm):
    """
        添加用户的ModelForm
    """
    r_password = forms.CharField(max_length=32, label='确认密码', widget=forms.PasswordInput())
    password = forms.CharField(max_length=32, label='密码', widget=forms.PasswordInput())

    class Meta:
        model = models.UserInfo
        fields = ['username', 'password', 'r_password', 'name', 'email', 'phone', 'gender', 'depart']

    def clean_r_password(self):
        password = self.cleaned_data['password']
        r_password = self.cleaned_data['r_password']
        if not password == r_password:
            raise ValidationError('两次密码输入不一致')
        return r_password

    def clean(self):
        password = self.cleaned_data['password']
        self.cleaned_data['password'] = gen_md5(password)
        return self.cleaned_data


class UpdateUserModelForm(BaseModelForm):
    class Meta:
        model = models.UserInfo
        fields = ['name', 'email', 'phone', 'gender', 'depart']


class ResetPasswordModelForm(StarkForm):
    password = forms.CharField(max_length=255, widget=forms.PasswordInput(), label='请输入密码')
    r_password = forms.CharField(max_length=255, widget=forms.PasswordInput(), label='请重新输入密码')

    def clean_r_password(self):
        password = self.cleaned_data['password']
        r_password = self.cleaned_data['r_password']
        if password != r_password:
            raise ValidationError('两次密码输入不一致，请重新输入')
        return r_password

    def clean(self):
        password = self.cleaned_data['password']
        self.cleaned_data['password'] = gen_md5(password)
        return self.cleaned_data


from stark.utils.datetime_picker import DateTimeInput

class ClassModelForm(BaseModelForm):
    # start_date = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}),label='开班时间')
    # graduate_date = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}),label='结业时间')
    class Meta:
        model = models.ClassList
        fields = '__all__'
        widgets = {
            'start_date':DateTimeInput(),
            'graduate_date':DateTimeInput()
        }


class CustomerModelForm(BaseModelForm):
    class Meta:
        model = models.Customer
        exclude = ['consultant']


class RecoreModelForm(BaseModelForm):
    class Meta:
        model = models.ConsultRecord
        fields = ['note']

class PaymentModelForm(BaseModelForm):
    class Meta:
        model = models.PaymentRecord
        fields = ['pay_type','paid_fee','class_list','note']

class StudentPaymentModelForm(BaseModelForm):
    qq = forms.CharField(label='学员QQ号',max_length=32)
    mobile = forms.CharField(label='学员手机号',max_length=32)
    emergency_contract = forms.CharField(label='紧急联系人',max_length=32)
    class Meta:
        model = models.PaymentRecord
        fields = ['pay_type', 'paid_fee', 'class_list','qq','mobile','emergency_contract','note']


class StudentModelForm(BaseModelForm):
    class Meta:
        model = models.Student
        exclude = [
            'customer',
            'student_status',
            'class_list'
        ]