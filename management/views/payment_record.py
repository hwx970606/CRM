from management import models
from stark.service.stark import StarkHandler
from django.conf.urls import url
from management.model_form import PaymentModelForm,StudentPaymentModelForm
from django.shortcuts import HttpResponse


class PaymentHandler(StarkHandler):


    def save(self, form, request, *args, **kwargs):
        """
        保存缴费记录，保存缴费记录的时候要判断学生表中该客户是否存在，不存在要重新创建
        :param form:
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        customer_id = kwargs['customer_id']
        current_user_id = request.session['user'].get('id')
        exists_object = models.Customer.objects.filter(id=customer_id,consultant__id=current_user_id).exists()
        if not exists_object:
            response = HttpResponse('保存数据失败，请重试')
            response.status_code = 404
            return response
        form.instance.customer_id = customer_id
        form.instance.consultant_id = current_user_id
        form.save()

        # 创建学员信息
        student_obj = models.Student.objects.filter(customer_id=customer_id).first()
        class_list = form.cleaned_data.get('class_list')
        if not student_obj:
            # 如果不存在学员信息，则添加新学员
            qq = form.cleaned_data.get('qq')
            mobile = form.cleaned_data.get('mobile')
            emergency_contract = form.cleaned_data.get('emergency_contract')
            student = models.Student.objects.create(customer_id=customer_id,qq=qq,mobile=mobile,emergency_contract=emergency_contract)
            student.class_list.add(class_list)
        else:
            # 更新班级
            student_obj.class_list.add(class_list)

    def get_urls(self):
        """
        对于一张表，默认定义了增删改查四个视图函数
            如果需要减少url或者重写url可以对该方法重写
        :return:
        """
        patterns = [
            url(r'^list/(?P<customer_id>\d+)/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            url(r'^add/(?P<customer_id>\d+)/$', self.wrapper(self.add_view), name=self.get_add_url_name),
        ]
        patterns.extend(self.extra_urls())
        return patterns

    list_display = [
        'customer',
        'consultant',
        StarkHandler.get_choice_text('缴费类型', 'pay_type'),
        'paid_fee',
        'class_list',
        StarkHandler.get_datetime_text('申请时间','apply_date'),
        StarkHandler.get_choice_text('状态','confirm_status'),
        'note'
    ]
    def get_queryset(self, request, *args, **kwargs):
        customer_id = kwargs['customer_id']
        current_user_id = request.session['user'].get('id')
        return self.model_class.objects.filter(customer_id=customer_id, customer__consultant_id=current_user_id)

    def get_list_display(self):
        """
        扩展显示字段，可以在子类中进行重写，不重写value为空
        :return:
        """
        value = []
        if self.list_display:
            value.extend(self.list_display)
        return value

    def get_model_form_class(self,is_add,request, pk, *args, **kwargs):
        """
        如果有过缴费记录，就让返回正常的model，如果没有则添加一些联系方式
        :param is_add:
        :param request:
        :param pk:
        :param args:
        :param kwargs:
        :return:
        """
        customer_id = kwargs.get('customer_id')
        customer_obj = models.Student.objects.filter(customer_id=customer_id)
        if customer_obj.exists():
            return PaymentModelForm
        else:
            return StudentPaymentModelForm


