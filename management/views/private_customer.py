from stark.service.stark import site, StarkHandler, Option
from management import model_form
from django.shortcuts import render
from management import models
from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.urls import reverse


class PrivateCustomerHandler(StarkHandler):
    """
    私户
    """
    model_form_class = model_form.CustomerModelForm

    def display_record(self, obj=None, is_head=None):
        if is_head:
            return '查看跟进记录'
        url = reverse('stark:management_consultrecord_list', kwargs={'customer_id': obj.pk})
        return mark_safe('<a target="_blank" href="%s">查看跟进<a/>' % (url))

    def display_payment_record(self, obj=None, is_head=None):
        if is_head:
            return '缴费记录'
        url = reverse('stark:management_paymentrecord_list', kwargs={'customer_id': obj.pk})
        return mark_safe('<a target="_blank" href="%s">缴费<a/>'%url )

    @property
    def get_record_url_name(self):
        """
        跟进记录url
        :return:
        """
        return self.get_url_name('record')

    def extra_urls(self):
        """
         增加自定义的url
        :return:
        """
        patterns = [
            url(r'^record/(?P<pk>\d+)', self.wrapper(self.record_view), name=self.get_record_url_name)
        ]
        return patterns

    def record_view(self, request, pk):
        record_list = models.ConsultRecord.objects.filter(consultant_id=pk)
        return render(request, 'record.html', {'data_list': record_list, })

    list_display = [
        StarkHandler.display_checkbox,
        'name',
        'qq',
        StarkHandler.get_choice_text('状态', 'status'),
        StarkHandler.get_choice_text('性别', 'gender'),
        StarkHandler.get_choice_text('客户来源', 'source'),
        'referral_from',
        'consultant',
        StarkHandler.get_m2m_text('咨询课程', 'course'),
        StarkHandler.get_choice_text('学历', 'education'),
        'graduation_shcool',
        'major',
        StarkHandler.get_choice_text('工作经验', 'experence'),
        StarkHandler.get_datetime_text('咨询时间', 'date'),
        display_record,
        display_payment_record
    ]

    def multi_pop(self, request, *args, **kwargs):
        current_user_id = request.session['user']['id']

        pk_list = request.POST.getlist('pk')
        self.model_class.objects.filter(consultant_id=current_user_id, pk__in=pk_list).update(consultant_id=None)

    multi_pop.text = '批量移动到公户'

    action_list = [multi_pop]

    def save(self, form,request,*args,**kwargs):
        form.instance.consultant_id = self.request.session['user']['id']
        form.save()


    def get_queryset(self, request, *args, **kwargs):
        current_user_id = request.session['user'].get('id')

        return self.model_class.objects.filter(consultant_id=current_user_id)
