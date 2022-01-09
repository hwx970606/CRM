from stark.service.stark import StarkHandler,BaseModelForm
from django.conf.urls import url




class StudyRecordHandler(StarkHandler):
    list_display = [
        'course_record',
        'student',
        StarkHandler.get_choice_text('考勤情况','record')
    ]

    has_add_btn = False
    def get_urls(self):
        """
        对于一张表，默认定义了增删改查四个视图函数
            如果需要减少url或者重写url可以对该方法重写
        :return:
        """
        patterns = [
            url(r'^list/(?P<course_record_id>\d+)/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),

        ]
        patterns.extend(self.extra_urls())
        return patterns

    def get_list_display(self):
        value = []
        if self.list_display:
            value.extend(self.list_display)
        return value

    def get_queryset(self, request, *args, **kwargs):
        course_record_id = kwargs.get('course_record_id')
        return self.model_class.objects.filter(course_record_id=course_record_id)

    action_list = []