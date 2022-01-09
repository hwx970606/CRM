from stark.service.stark import StarkHandler, Option
from management import model_form
from django.shortcuts import render, redirect, HttpResponse
from management import models
from django.utils.safestring import mark_safe
from django.conf.urls import url


class UserInfoHandler(StarkHandler):
    @property
    def get_reset_url_name(self):
        return self.get_url_name('reset')

    def reset_password(self, request, pk, *args, **kwargs):
        """
        重置密码
        :param request:
        :param pk:
        :param args:
        :param kwargs:
        :return:
        """
        userinfo_obj = models.UserInfo.objects.filter(pk=pk).first()
        if not userinfo_obj:
            return HttpResponse('该用户不存在')
        if request.method == 'GET':
            form = model_form.ResetPasswordModelForm()
            return render(request, 'stark/change.html', {'form': form})
        form = model_form.ResetPasswordModelForm(request.POST)
        if form.is_valid():
            userinfo_obj.password = form.cleaned_data['password']
            userinfo_obj.save()
            return redirect(self.reverse_list_url(*args, **kwargs))
        return render(request, 'stark/change.html', {'form': form})

    def extra_urls(self):
        """
         增加自定义的url
        :return:
        """
        patterns = [
            url(r'^reset/pwd/(?P<pk>\d+)', self.wrapper(self.reset_password), name=self.get_reset_url_name)
        ]
        return patterns

    def display_reset_password(self, obj, is_head=None,*args,**kwargs):
        if is_head:
            return '重置密码'
        url = self.reverse_base_url(name=self.get_reset_url_name, pk=obj.pk)
        return mark_safe('<a href="%s">重置密码</a>' % url)

    list_display = [
        'username',
        'name',
        'email',
        'phone',
        StarkHandler.get_choice_text('性别', 'gender'),
        'depart',
        display_reset_password

    ]
    search_list = ['username__contains', 'name__contains', 'email__contains']
    search_group = [
        Option('gender'),
        Option('depart', is_multi=True)
    ]

    def get_model_form_class(self,is_add,request,pk,*args,**kwargs):
        if is_add:
            return model_form.AddUserModelForm
        else:
            return model_form.UpdateUserModelForm