from stark.service.stark import StarkHandler, BaseModelForm, HttpResponse,render
from django.conf.urls import url
from management import models
from django.urls import reverse
from django.utils.safestring import mark_safe

from django.forms.models import modelformset_factory

class StudyRecordModelForm(BaseModelForm):
    class Meta:
        model = models.StudyRecord
        fields = ['record']

class CourseRecordModelForm(BaseModelForm):
    class Meta:
        model = models.CourseRecord
        fields = [
            'day_num',
            'teacher'
        ]


class CourseRecordHandler(StarkHandler):
    model_form_class = CourseRecordModelForm

    def display_studyrecord(self,obj,is_head=None,*args,**kwargs):
        if is_head:
            return '查看'
        url = reverse('stark:management_studyrecord_list',kwargs={'course_record_id':obj.pk})
        return mark_safe('<a target="_blank" href="%s">查看考勤</a>'%url)

    def display_attendance(self,obj,is_head=None,*args,**kwargs):
        if is_head:
            return '管理'
        url = reverse('stark:management_courserecord_attendance',kwargs={'course_record_id':obj.pk})
        return mark_safe('<a target="_blank" href="%s">管理管理</a>'%url)


    list_display = [
        StarkHandler.display_checkbox,
        'class_object',
        'day_num',
        'teacher',
        StarkHandler.get_datetime_text('上课时间', 'course_date'),
        display_studyrecord,
        display_attendance

    ]

    def get_queryset(self, request, *args, **kwargs):
        class_id = kwargs.get('class_id')
        return self.model_class.objects.filter(class_object_id=class_id)

    def get_urls(self):
        """
        对于一张表，默认定义了增删改查四个视图函数
            如果需要减少url或者重写url可以对该方法重写
        :return:
        """
        patterns = [
            url(r'^list/(?P<class_id>\d+)/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            url(r'^add/(?P<class_id>\d+)/$', self.wrapper(self.add_view), name=self.get_add_url_name),
            url(r'^change/(?P<class_id>\d+)/(?P<pk>\d+)/$', self.wrapper(self.change_view),
                name=self.get_change_url_name),
            url(r'^delete/(?P<class_id>\d+)/(?P<pk>\d+)/$', self.wrapper(self.delete_view),
                name=self.get_delete_url_name),
            url(r'^attendance/(?P<course_record_id>\d+)/$', self.wrapper(self.attendance_view),
                name=self.get_url_name('attendance')),
        ]
        patterns.extend(self.extra_urls())
        return patterns

    def save(self, form, request, *args, **kwargs):
        class_id = kwargs.get('class_id')
        form.instance.class_object_id = class_id
        form.save()

    def multi_init(self, request, *args, **kwargs):  # 批量初始化考勤
        course_record_id_list = request.POST.getlist('pk')
        class_id = kwargs.get('class_id')
        class_obj = models.ClassList.objects.filter(id=class_id).first()
        if not class_obj:
            return HttpResponse('班级不存在')
        student_list = class_obj.student_set.all()
        for course_record_id in course_record_id_list:
            # 判断上课记录是否合法
            course_record_obj = models.CourseRecord.objects.filter(pk=course_record_id,
                                                                   class_object_id=class_id).first()
            if not course_record_obj:
                continue

            # 判断考勤记录存不存在
            studyrecord_obj = models.StudyRecord.objects.filter(course_record=course_record_obj)
            if studyrecord_obj:
                continue

            # 批量提交
            studyrecord_object_list = [
                models.StudyRecord(student_id=stu.id, course_record_id=course_record_id) for stu in student_list]
            models.StudyRecord.objects.bulk_create(studyrecord_object_list)
    multi_init.text = '批量初始化'


    def attendance_view(self,request,course_record_id,*args,**kwargs):
        """
        考勤的批量操作
        :param request:
        :param course_record_id:当前的上课记录id
        :param args:
        :param kwargs:
        :return:
        """
        study_record_object_list = models.StudyRecord.objects.filter(course_record_id=course_record_id)
        study_model_formset = modelformset_factory(models.StudyRecord,form=StudyRecordModelForm,extra=0)
        if request.method == 'POST':
            formset = study_model_formset(queryset=study_record_object_list,data=request.POST)
            if formset.is_valid():
                formset.save()
            return render(request, 'attendance.html', {'formset': formset})
        formset = study_model_formset(queryset=study_record_object_list)
        return render(request,'attendance.html',{'formset':formset})


    action_list = [multi_init]
