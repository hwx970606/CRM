from stark.service.stark import StarkHandler
from django.conf.urls import url
from management import models
from management.model_form import RecoreModelForm
from django.shortcuts import render, redirect, HttpResponse


class ConsultRecordHandler(StarkHandler):
    change_list_template = 'consult_record.html'
    list_display = [
        'customer',
        'consultant',
        'date',
        'note'
    ]
    model_form_class = RecoreModelForm

    def get_urls(self):
        """
        对于一张表，默认定义了增删改查四个视图函数
            如果需要减少url或者重写url可以对该方法重写
        :return:
        """
        patterns = [
            url(r'^list/(?P<customer_id>\d+)/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            url(r'^add/(?P<customer_id>\d+)/$', self.wrapper(self.add_view), name=self.get_add_url_name),
            url(r'^change/(?P<customer_id>\d+)/(?P<pk>\d+)/$', self.wrapper(self.change_view),
                name=self.get_change_url_name),
            url(r'^delete/(?P<customer_id>\d+)/(?P<pk>\d+)/$', self.wrapper(self.delete_view),
                name=self.get_delete_url_name),
        ]
        patterns.extend(self.extra_urls())
        return patterns

    def get_queryset(self, request, *args, **kwargs):
        customer_id = kwargs['customer_id']
        current_user_id = request.session['user'].get('id')
        return self.model_class.objects.filter(customer_id=customer_id, customer__consultant_id=current_user_id)

    def save(self, form, request, *args, **kwargs):
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

    def get_change_object(self,request, pk, *args, **kwargs):
        """
        kwargs:{'customer_id': '5'}
        """
        current_user_id = request.session['user'].get('id')
        return models.ConsultRecord.objects.filter(pk=pk,**kwargs,consultant__id=current_user_id)

    def delete_object(self, request, pk, *args, **kwargs):
        current_user_id = request.session['user'].get('id')
        record_object = models.ConsultRecord.objects.filter(pk=pk, **kwargs, consultant__id=current_user_id)

        if not record_object.exists():
            response = HttpResponse('要删除的数据不存在，请重新选择')
            response.status_code = 404
            return response
        record_object.delete()