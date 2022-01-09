from stark.service.stark import StarkHandler,BaseModelForm
from django.conf.urls import url
from management.models import ScoreRecord

class ScordModelForm(BaseModelForm):
    class Meta:
        model = ScoreRecord
        fields = [
            'content',
            'score'
        ]

class ScordHandler(StarkHandler):
    model_form_class = ScordModelForm
    list_display = [
        'content',
        'score',
        'user'
    ]

    def get_urls(self):
        """
        对于一张表，默认定义了增删改查四个视图函数
            如果需要减少url或者重写url可以对该方法重写
        :return:
        """
        patterns = [
            url(r'^list/(?P<student_id>\d+)/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            url(r'^add/(?P<student_id>\d+)/$', self.wrapper(self.add_view), name=self.get_add_url_name),
        ]
        patterns.extend(self.extra_urls())
        return patterns

    def get_queryset(self, request, *args, **kwargs):
        student_id = kwargs.get('student_id')
        return self.model_class.objects.filter(student_id=student_id)

    def save(self, form, request, *args, **kwargs):
        student_id = kwargs.get('student_id')
        user_id = request.session['user']['id']
        form.instance.student_id = student_id
        form.instance.user_id = user_id
        form.save()

        # 原积分

        score = form.instance.score
        if score > 0:
            form.instance.student.score += abs(score)
        else:
            form.instance.student.score -= abs(score)
        form.instance.student.save()

    def get_list_display(self):
        """
        扩展显示字段，可以在子类中进行重写，不重写value为空
        :return:
        """
        value = []
        if self.list_display:
            value.extend(self.list_display)
        return value