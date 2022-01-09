from stark.service.stark import StarkHandler,Option
from django.conf.urls import url

class CheckPaymentHandler(StarkHandler):
    list_display = [
        StarkHandler.display_checkbox,
        'customer',
        'consultant',
        StarkHandler.get_choice_text('缴费类型', 'pay_type'),
        'paid_fee',
        'class_list',
        StarkHandler.get_choice_text('状态', 'confirm_status'),
        StarkHandler.get_datetime_text('申请时间', 'apply_date'),
        'confirm_user'
    ]
    has_add_btn = None

    def get_list_display(self):
        value = []
        if self.list_display:
            value.extend(self.list_display)
        return value
    def get_urls(self):
        patterns = [
            url(r'^list/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            ]
        patterns.extend(self.extra_urls())
        return patterns

    order = ['confirm_status']

    def multi_check(self,request,*args,**kwargs):
        pk_list = request.POST.getlist('pk')
        user_id = request.session['user']['id']
        for pk in pk_list:
            # 更新缴费表中的缴费状态
            payment_object = self.model_class.objects.filter(pk=pk,confirm_status=1).first()
            if not payment_object:
                continue
            payment_object.confirm_status = 2
            payment_object.confirm_user_id = user_id
            payment_object.save()

            # 更新客户表中的客户状态
            payment_object.customer.status = 1
            payment_object.customer.save()

            # 更新学生表中的学员状态
            payment_object.customer.student.student_status = 2
            payment_object.customer.student.save()



    multi_check.text = '批量确认'

    def multi_reject(self,request,*args,**kwargs):
        pk_list = request.POST.getlist('pk')
        user_id = request.session['user']['id']
        self.model_class.objects.filter(pk__in=pk_list,confirm_status=1).update(confirm_status=3,confirm_user_id=user_id)

    multi_reject.text = '批量驳回'
    action_list = [multi_check,multi_reject]

    search_list = [
        'customer__name__contains'
    ]
    search_group = [
        Option('confirm_status')
    ]
