
from stark.service.stark import StarkHandler,Option
from django.conf.urls import url
from management.model_form import StudentModelForm
from django.utils.safestring import mark_safe

class StudentHandler(StarkHandler):
    def score_display(self,obj, is_head=None, *args, **kwargs):
        if is_head:
            return '积分管理'
        url = self.reverse_base_url('management_scorerecord_list',student_id=obj.pk)
        return mark_safe('<a href="%s">%s</a>'%(url,obj.score))

    model_form_class = StudentModelForm
    list_display = [
        'customer',
        'qq',
        'mobile',
        StarkHandler.get_m2m_text('已报名的班级','class_list'),
        StarkHandler.get_choice_text('学员状态','student_status'),
        score_display,
        'memo'
    ]
    has_add_btn = False



    def get_list_display(self):
        """
        扩展显示字段，可以在子类中进行重写，不重写value为空
        :return:
        """
        value = []
        if self.list_display:
            value.extend(self.list_display)
            value.append(StarkHandler.display_edit)
        return value

    def get_urls(self):
        """
        对于一张表，默认定义了增删改查四个视图函数
            如果需要减少url或者重写url可以对该方法重写
        :return:
        """
        patterns = [
            url(r'^list/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            url(r'^add/$', self.wrapper(self.add_view), name=self.get_add_url_name),
            url(r'^change/(?P<pk>\d+)/$', self.wrapper(self.change_view), name=self.get_change_url_name),
        ]
        patterns.extend(self.extra_urls())
        return patterns

    search_group = [
        Option('class_list'),
        Option('student_status'),

    ]
    search_list = [
        'customer__name'
    ]