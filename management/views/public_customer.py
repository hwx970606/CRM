from stark.service.stark import StarkHandler
from management import model_form
from django.shortcuts import render, redirect, HttpResponse
from management import models
from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.db import transaction


class PublicCustomerHandler(StarkHandler):
    """
    公户：
        与私户的差别：公户没有课程顾问
    """
    def display_record(self, obj=None, is_head=None):
        if is_head:
            return '查看跟进记录'
        url = self.reverse_base_url(self.get_record_url_name, pk=obj.pk)

        return mark_safe('<a href="%s">查看跟进<a/>' % url)
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
        return render(request, 'record.html', {'data_list': record_list,})

    model_form_class = model_form.CustomerModelForm
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
    ]

    def multi_apply(self, request, *args, **kwargs):
        """
            批量操作
        :param request:
        :return:
        """
        # 用户id
        user_id = request.session['user'].get('id')
        depart = request.session['user'].get('depart')
        if depart != '销售部':return HttpResponse('只有销售部的员工才可以将客户添加到私户')
        if not user_id:
            return redirect('/login/')

        # 客户ID
        pk_list = request.POST.getlist('pk')
        if not pk_list:
            return HttpResponse('请选择需要申请添加到私户的客户')
        # 将选中的客户更新到我的私户中：更新consultant字段
        count = models.Customer.objects.filter(consultant_id=user_id, status=2).count()
        if (count + len(pk_list)) < 150: # 对于私护个人的限制
            # 在Django中给数据库加锁,保证数据安全
            flag = False
            with transaction.atomic():# 数据库
                orgin_queryset = models.Customer.objects.filter(pk__in=pk_list, status=2, consultant__isnull=True).select_for_update()
                if len(orgin_queryset) ==len(pk_list):
                    models.Customer.objects.filter(pk__in=pk_list, status=2, consultant__isnull=True).update(
                        consultant_id=user_id)
                    flag = True
            if not flag:
                return HttpResponse('手速太慢了，选中的客户已被其他人申请，请重新选择')
        else:
            return HttpResponse('你未转化的客户超过了150人，私户中已有%s未转化的客户' % count)

    multi_apply.text = '批量申请到私户'
    action_list = [
        multi_apply
    ]

    def change_view(self, request, pk, *args, **kwargs):

        obj = self.model_class.objects.filter(id=pk)
        if not obj.first():
            return HttpResponse('要更改的数据不存在，请重新选择')
        form_class = self.get_model_form_class(False,request,pk,*args,**kwargs)
        if request.method == 'GET':
            form = form_class(instance=obj.first())
            return render(request, 'stark/change.html', {'form': form})
        form = form_class(request.POST)
        if form.is_valid():
            course = form.cleaned_data.pop('course')
            obj.first().course.set(course)
            obj.update(**form.cleaned_data)
            return redirect(self.reverse_list_url(request,*args,**kwargs))
        return render(request, 'stark/change.html', {'form': form})

    def get_queryset(self, request, *args, **kwargs):
        # 页面查询时返回课程顾问为空的
        return self.model_class.objects.filter(consultant__isnull=True,status=2)