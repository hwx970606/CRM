from stark.service.stark import site, StarkHandler, Option
from management import model_form
from django.shortcuts import render, redirect, HttpResponse
from django.utils.safestring import mark_safe



class ClassesHandler(StarkHandler):
    def display_semester(self, obj=None, is_head=None,*args,**kwargs):
        if is_head:
            return '班级'
        return obj

    def display_courserecord(self,obj=None,is_head=None,*args,**kwargs):
        if is_head:
            return '上课记录'
        url = self.reverse_base_url('management_courserecord_list',class_id=obj.pk)
        return mark_safe('<a target="_blank" href="%s">查看上课记录</a>'%url)


    list_display = [
        'school',
        display_semester,
        'price',
        StarkHandler.get_datetime_text('开班日期', 'start_date'),
        StarkHandler.get_datetime_text('结业日期','graduate_date'),
        'class_teacher',
        StarkHandler.get_m2m_text('任课老师', 'tech_teacher'),
        display_courserecord,
        'memo',
    ]
    model_form_class = model_form.ClassModelForm
    search_group = (
        Option('school'),
        Option('course'),
    )

    def change_view(self, request, pk, *args, **kwargs):
        """
        更改页面
        :param request:
        :return:
        """
        obj = self.model_class.objects.filter(id=pk)
        if not obj.first():
            return HttpResponse('要更改的数据不存在，请重新选择')
        form_class = self.get_model_form_class(False,request,pk,*args,**kwargs)
        if request.method == 'GET':
            form = form_class(instance=obj.first())
            return render(request, 'stark/change.html', {'form': form})
        form = form_class(request.POST)
        if form.is_valid():
            teacher = form.cleaned_data.pop('tech_teacher')
            obj.first().tech_teacher.set(teacher)
            obj.update(**form.cleaned_data)
            return redirect(self.reverse_list_url())
        return render(request, 'stark/change.html', {'form': form})