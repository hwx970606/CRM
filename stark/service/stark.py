from django.conf.urls import url
from django.shortcuts import HttpResponse, render, redirect
from types import FunctionType
from django.urls import reverse
from django.utils.safestring import mark_safe
from stark.utils.pagination import Pagination
from django.http import QueryDict
from django import forms
from django.db.models import Q
from django.db.models import ForeignKey, ManyToManyField
import functools


class BaseModelForm(forms.ModelForm):
    """
    给modelform加上样式的鸡肋
    """

    def __init__(self, *args, **kwargs):
        super(BaseModelForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class StarkForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(StarkForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class SearchGroupRow(object):
    def __init__(self, data_List, title, query_dict, option):
        """

        :param data_List: 组合搜索关联获取到的数据
        :param title: 组合搜索的列名称
        :param quert_dict:request.GET
        :param field: 组合搜索的字段名
        """
        # 传入的值的类型有可能是queryset和tuple
        self.data_list = data_List
        self.title = title  # 表模型
        self.query_dict = query_dict
        self.option = option

    def __iter__(self):
        # 如果一个类中定义类iter方法且返回了一个迭代器，那么称这个类为可迭代对象

        yield self.title
        total_queryset_dict = self.query_dict.copy()
        orgin_value_list = self.query_dict.getlist(self.option.field)
        if not orgin_value_list:
            span = '<a href="%s" class="btn btn-primary">{}</a>' % total_queryset_dict.urlencode()

        else:
            total_queryset_dict.pop(self.option.field)
            span = '<a href="?%s" class="btn btn-default">{}</a>' % total_queryset_dict.urlencode()
        yield span.format('全部')

        for item in self.data_list:
            text = self.get_text(item)
            value = str(self.get_value(item))
            query_dict = self.query_dict.copy()
            query_dict._mutable = True

            # 判断是否支持多选功能
            if not self.option.is_multi:
                query_dict[self.option.field] = value
                if value in orgin_value_list:
                    query_dict.pop(self.option.field)
                    yield '<a href="?%s" class="btn btn-primary">%s</a>' % (query_dict.urlencode(), text)
                else:
                    yield '<a href="?%s" class="btn btn-default">%s</a>' % (query_dict.urlencode(), text)
            else:
                multi_value_list = query_dict.getlist(self.option.field)
                if value in multi_value_list:
                    multi_value_list.remove(value)
                    query_dict.setlist(self.option.field, multi_value_list)
                    yield '<a href="?%s" class="btn btn-primary">%s</a>' % (query_dict.urlencode(), text)

                else:
                    multi_value_list.append(value)
                    query_dict.setlist(self.option.field, multi_value_list)
                    yield '<a href="?%s" class="btn btn-default">%s</a>' % (query_dict.urlencode(), text)

    def get_text(self, item_obj):
        if isinstance(item_obj, tuple):
            return item_obj[1]
        return str(item_obj)

    def get_value(self, item_obj):
        if isinstance(item_obj, tuple):
            return item_obj[0]
        return item_obj.pk


class Option(object):
    def __init__(self, field, is_multi=False, db_condition=None):
        """

        :param field: 字段
        :param is_multi: 是否支持多选
        :param db_condition: 条件
        """
        self.field = field
        self.is_multi = is_multi
        if not db_condition:
            db_condition = {}
        self.db_condition = db_condition

    def get_db_condition(self, request, *args, **kwargs):
        return self.db_condition

    def get_queryset_or_tuple(self, model_class, request, *args, **kwargs):
        # 根据gender 或 depart字符串，去自己对应的Model类中找到字段对象，再根据字段对象获取关联数据
        field_obj = model_class._meta.get_field(self.field)
        title = field_obj.verbose_name

        # 获取关联数据
        if isinstance(field_obj, ForeignKey) or isinstance(field_obj, ManyToManyField):
            # FK ,M2M
            db_condition = self.get_db_condition(request, *args, **kwargs)
            # 返回类型是queryset
            return SearchGroupRow(field_obj.related_model.objects.filter(**db_condition), title, request.GET,
                                  self)
        else:
            # 获取choice,返回值是元祖
            return SearchGroupRow(field_obj.choices, title, request.GET, self)


class StarkHandler(object):
    """
    list_display ：开发者自定义需要在页面上显示的字段
    per_page ：每页显示多少条数据，用于分页
    has_add_btn ：是否有添加按钮
    model_form_class ：添加、编辑的modelform，可选，如果不传的话使用该组件默认的modelform
    order ：接收一个列表参数，列表内写根据什么什么字段进行排序
    search_list ： 查询框根据什么字段进行模糊查询
    action_list ：该列表接收一个对数据进行批量操作的函数
    search_group ：分组搜索的字段，接收一个Option类的实例
    """
    change_list_template = None
    list_display = []
    per_page = 20
    has_add_btn = True
    model_form_class = None
    order = []
    search_list = []
    action_list = []
    search_group = []

    def get_search_group(self):
        return self.search_group

    def get_search_list(self):
        return self.search_list

    def get_order(self):
        if self.order:
            return self.order
        return ['id', ]

    def __init__(self, site, model_class, prev):
        self.site = site
        self.model_class = model_class
        self.prev = prev
        self.request = None

    def get_add_btn(self, request, *args, **kwargs):
        if self.has_add_btn:
            # print(self.reverse_base_url(self.get_add_url_name, args, kwargs))
            return '<a href="%s" class="btn btn-primary"><i class="fa fa-database" aria-hidden="true"></i>添加</a>' % self.reverse_base_url(
                self.get_add_url_name, *args, **kwargs)
        return None

    def search_group_condition(self, request):
        condition = {}
        for option in self.get_search_group():
            if option.is_multi:
                values_list = request.GET.getlist(option.field)
                if not values_list:
                    continue
                condition['%s__in' % option.field] = values_list
            else:
                value = request.GET.get(option.field)
                if not value:
                    continue
                condition[option.field] = value

        return condition

    def get_queryset(self, request, *args, **kwargs):

        return self.model_class.objects

    def changelist_view(self, request, *args, **kwargs):
        """
        列表页面
        :param request:
        :return:
        """
        self.request = request
        order_list = self.get_order()  # 排序
        search_list = self.get_search_list()

        # 处理action批量处理列表
        action_list = self.get_action_list()
        action_dict = {func.__name__: func.text for func in action_list}

        if request.method == 'POST':
            action_func_name = request.POST.get('active')
            if action_func_name and action_func_name in action_dict:
                action_response = getattr(self, action_func_name)(request, *args, **kwargs)
                if action_response:
                    return action_response

        # 处理组合搜索
        search_group_row_list = []
        search_group = self.get_search_group()
        for option_object in search_group:
            row = option_object.get_queryset_or_tuple(self.model_class, request, *args, **kwargs)
            search_group_row_list.append(row)

        # 获取组合搜索的条件
        condition = self.search_group_condition(request)

        # 根据查询条件筛选出需要的数据
        search_val = request.GET.get('query', '')
        conn = Q()
        conn.connector = 'OR'
        if search_val:
            for item in search_list:
                conn.children.append((item, search_val))
            queryset = self.get_queryset(request, *args, **kwargs).filter(conn).filter(**condition).order_by(
                *order_list)
        else:
            queryset = self.get_queryset(request, *args, **kwargs).filter(**condition).order_by(*order_list)

        # 处理表头
        # 假设页面要显示列：['username','password','email']
        list_dispyay = self.get_list_display()
        header_list = []
        if list_dispyay:
            for key in list_dispyay:
                if isinstance(key, FunctionType):
                    verbose_name = key(self, obj=None, is_head=True, *args, **kwargs)
                else:
                    # 从模型表中取出verbose_name
                    verbose_name = self.model_class._meta.get_field(key).verbose_name
                header_list.append(verbose_name)
        else:
            header_list.append(self.model_class._meta.model_name)
        # 分页
        # def __init__(self, current_page, all_count, base_url, query_params, per_page=20, pager_page_count=11):
        query_params = request.GET.copy()
        query_params._mutbale = True
        pager = Pagination(
            current_page=request.GET.get('page'),
            all_count=queryset.count(),
            base_url=request.path_info,
            query_params=query_params,
            per_page=self.per_page,

        )

        # 处理表的内容
        data_list = queryset[pager.start:pager.end]
        body_list = []
        for item in data_list:
            row_List = []
            if list_dispyay:
                for key in list_dispyay:
                    if isinstance(key, FunctionType):
                        row_List.append(key(self, item, is_head=False, *args, **kwargs))
                    else:
                        row_List.append(getattr(item, key))
            else:
                row_List.append(item)
            body_list.append(row_List)

        add_btn = self.get_add_btn(request, *args, **kwargs)
        return render(
            request,
            self.change_list_template or 'stark/list.html',
            {
                'header_list': header_list,
                'body_list': body_list,
                'pager': pager,
                'add_btn': add_btn,
                'search_list': search_list,
                'search_val': search_val,
                'action_dict': action_dict,
                'search_group_row_list': search_group_row_list
            })

    def add_view(self, request, *args, **kwargs):
        """
        添加页面
        :param request:
        :return:
        """
        model_form = self.get_model_form_class(True,request,None,*args,**kwargs)
        if request.method == 'GET':
            form = model_form()
            return render(request, 'stark/change.html', {'form': form})
        form = model_form(request.POST)
        if form.is_valid():
            response = self.save(form, request, *args, **kwargs)
            url = self.reverse_list_url(request, *args, **kwargs)
            return response or redirect(url)
        return render(request, 'stark/change.html', {'form': form})

    def get_change_object(self, request, pk, *args, **kwargs):
        """
        自定义的钩子方法，获取需要更改的数据，pk是数据的主键，返回值是一个queryset对象
            默认更改的数据是主键与pk对应，如果需要再加查询条件可以使用**kwargs，
        :param pk:
        :param args:
        :param kwargs:
        :return:
        """
        return self.model_class.objects.filter(id=pk)

    def change_view(self, request, pk, *args, **kwargs):
        """
        更改页面
        :param request:
        :return:
        """
        obj = self.get_change_object(request, pk, *args, **kwargs)
        if not obj.first():
            response = HttpResponse('要更改的数据不存在，请重新选择')
            response.status_code = 404
            return response
        form_class = self.get_model_form_class(False, request, pk, *args, **kwargs)
        if request.method == 'GET':
            form = form_class(instance=obj.first())
            return render(request, 'stark/change.html', {'form': form})
        form = form_class(request.POST)
        if form.is_valid():
            # teacher = form.cleaned_data.pop('tech_teacher')
            obj.update(**form.cleaned_data)
            url = self.reverse_list_url(request, *args, **kwargs)
            return redirect(url)
        return render(request, 'stark/change.html', {'form': form})

    def delete_object(self, request, pk, *args, **kwargs):
        """
        与编辑页面类似，默认是删除主键pk，如果删除时需要加其他的条件，避免影响数据安全，可以重写这个方法
        :param request:
        :param pk:
        :param args:
           :param kwargs:
        :return:
        """
        self.model_class.objects.filter(pk=pk).delete()

    def delete_view(self, request, pk, *args, **kwargs):
        """
        删除页面
        :param request:
        :param pk:
        :return:
        """
        url = self.reverse_list_url(request, *args, **kwargs)
        if request.method == 'GET':
            return render(request, 'stark/delete.html', {'cancel': url})
        response = self.delete_object(request, pk, *args, **kwargs)
        return response or redirect(url)

    def save(self, form, request, *args, **kwargs):
        """
        用户可以进行重写，保存的默认值
        :param form:
        :return: save函数可以返回一个响应对象，响应对象一般是错误信息，如果返回值为空则表示添加成功跳转到对应表的列表页面
        """
        form.save()

    def reverse_base_url(self, name, *args, **kwargs):
        """
        根据传入的值生成代理源搜索条件的URL；
        :param name: self.get_list_url_name,self.get_change_url_name,self.get_delete_url_name
        :param args:
        :param kwargs:
        :return:
        """
        base_url = reverse(self.site.namespace + ':' + name, args=args, kwargs=kwargs)
        if not self.request.GET:
            add_url = base_url
        else:
            value = self.request.GET.urlencode()
            new_quert_dict = QueryDict(mutable=True)
            new_quert_dict['_filter'] = value
            add_url = '%s?%s' % (base_url, new_quert_dict.urlencode())
        return add_url

    def get_model_form_class(self, is_add, request, pk, *args, **kwargs):
        if self.model_form_class:
            return self.model_form_class

        class DynamicModelForm(BaseModelForm):
            class Meta:
                model = self.model_class
                fields = '__all__'

        return DynamicModelForm

    def get_url_name(self, param):
        app_label, model_name = self.model_class._meta.app_label, self.model_class._meta.model_name
        url_name = '%s_%s_%s_%s' % (app_label, model_name, self.prev, param) if self.prev else '%s_%s_%s' % (
            app_label, model_name, param)
        return url_name

    def reverse_list_url(self, request, *args, **kwargs):
        """
        跳转回列表页面
        解析带有源搜索条件的url
        :param url_name:
        :return:
        """
        _filter = self.request.GET.get('_filter')
        base_url = reverse('%s:%s' % (self.site.namespace, self.get_list_url_name), args=args, kwargs=kwargs)
        return base_url if not _filter else '%s?%s' % (base_url, _filter)

    @property
    def get_list_url_name(self):
        return self.get_url_name('list')

    @property
    def get_add_url_name(self):
        return self.get_url_name('add')

    @property
    def get_change_url_name(self):
        return self.get_url_name('change')

    @property
    def get_delete_url_name(self):
        return self.get_url_name('delete')

    def multi_delete(self, request, *args, **kwargs):
        """
        用户可以自定义批量操作函数，批量操作函数可以有返回值，如果有返回值则可以跳转到反省的对象
            如果没有返回值则跳转还列表页面
        定义了批量操作函数可以设置批量操作函数的名字并且将批量操作函数的函数名放到action_list内:
                multi_delete.text = '批量删除'
                action_list = [multi_delete,]
        :param request:
        :return:
        """
        pk_list = request.POST.getlist('pk')
        self.model_class.objects.filter(id__in=pk_list).delete()

    multi_delete.text = '批量删除'

    def wrapper(self, func):
        """
        利用函数的闭包原理，实现每个请求进来先执行self.request = request
        :param func:
        :return:
        """

        @functools.wraps(func)  # 保留原函数的源信息
        def inner(request, *args, **kwargs):
            self.request = request
            return func(request, *args, **kwargs)

        return inner

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
            url(r'^delete/(?P<pk>\d+)/$', self.wrapper(self.delete_view), name=self.get_delete_url_name),
        ]
        patterns.extend(self.extra_urls())
        return patterns

    def get_action_list(self):
        return self.action_list

    def get_list_display(self):
        """
        扩展显示字段，可以在子类中进行重写，不重写value为空
        :return:
        """
        value = []
        if self.list_display:
            value.extend(self.list_display)
            value.append(StarkHandler.display_edit)
            value.append(StarkHandler.display_remove)
        return value

    @staticmethod
    def get_choice_text(title, field):
        """
        通过闭包函数实现选择列显示中文
        :param title:需要在页面中显示的表头
        :param field:ORM中的字段
        :return:
        """

        def inner(self, obj, is_head, *args, **kwargs):
            if is_head:
                return title
            fun = 'get_%s_display' % field
            return getattr(obj, fun)()

        return inner

    @staticmethod
    def get_datetime_text(title, field, datetime_format='%Y年%m月%d日', ):
        """
        通过闭包函数实现选择列显示中文
        :param title:需要在页面中显示的表头
        :param field:ORM中的字段
        format 要格式话的时间格式
        :return:
        """

        def inner(self, obj, is_head, *args, **kwargs):
            if is_head:
                return title
            datetime = getattr(obj, field)
            return datetime.strftime(datetime_format)

        return inner

    @staticmethod
    def get_m2m_text(title, field):
        """
        通过闭包函数实现选择列显示中文
        :param title:需要在页面中显示的表头
        :param field:ORM中的字段
        format 要格式话的时间格式
        :return:
        """

        def inner(self, obj, is_head):
            if is_head:
                return title

            return ','.join([str(item) for item in getattr(obj, field).all()])

        return inner

    def extra_urls(self):
        """
        额外的增加url：
            假如对于单独这张表需要增加url，可以重写该方法，该方法的返回值是一个列表

        :return:
        """
        return []

    def display_edit(self, obj, is_head=None, *args, **kwargs):
        """
        自定义页面显示的列(表头和内容）
            编辑
        :param obj:
        :param is_head:
        :return:
        """
        if is_head:
            return '编辑'
        url = self.reverse_base_url(name=self.get_change_url_name, pk=obj.pk, *args, **kwargs)
        return mark_safe('<a href="%s">编辑</a>' % url)

    def display_remove(self, obj, is_head=None, *args, **kwargs):
        """
        自定义页面显示的列(表头和内容）
            删除
        :param obj:
        :param is_head:
        :return:
        """
        if is_head:
            return '删除'
        url = self.reverse_base_url(name=self.get_delete_url_name, pk=obj.pk, *args, **kwargs)
        return mark_safe('<a href="%s">删除</a>' % url)

    def display_checkbox(self, obj, is_head=None, *args, **kwargs):
        if is_head:
            return '选择'
        return mark_safe('<input type="checkbox" value="%s" name="pk"/>' % obj.pk)


class StarkSite(object):
    def __init__(self):
        self._registry = []
        self.app_name = 'stark'
        self.namespace = 'stark'

    def register(self, model_class, handler_class=None, prev=None):
        """

        :param model_class: 数据库中的相关参数
        :param handler_class: 处理请求的视图函数所在的类
        :param prev: 前缀，默认为空，如果传了prev参数的话会在表名后面增加一个前缀或者后缀
        :return:
        """
        if not handler_class:
            handler_class = StarkHandler
        self._registry.append(
            {
                'model_class': model_class,
                'handler': handler_class(self, model_class, prev),
                'prev': prev
            }
        )
        # self._registry的数据结构
        """
        [
            {
                'model_class': <class 'aliya.models.UserInfo'>,
                 'handler': <aliya.stark.UserInfoHandler object at 0x101cffcf8>
                 'prev':''
             }, 
             {
                'model_class': <class 'aliya.models.Depart'>, 
                'handler': <aliya.stark.DepartHandler object at 0x101cffd30>,
                 'prev':''
                }, 
            {
                'model_class': <class 'snow.models.Host'>, 
                'handler': <snow.stark.HostHandler object at 0x101d0bb70>,
                 'prev':''
            }
        ]
        """

    def get_urls(self):
        patterns = []
        for item in self._registry:
            """
                aliya userinfo
                aliya depart
                snow host
            # model_class._meta.app_label 获取的是模型表所在app的名称
            # model_class._meta.model_name 获取的是表名小写
            """
            model_class = item['model_class']
            handler = item['handler']
            prev = item['prev']
            app_label, model_name = model_class._meta.app_label, model_class._meta.model_name
            if prev:
                patterns.append(url(r'%s/%s/%s/' % (app_label, model_name, prev), (handler.get_urls(), None, None)))

            else:
                patterns.append(url(r'%s/%s/' % (app_label, model_name), (handler.get_urls(), None, None)))

        return patterns

    @property
    def urls(self):
        return self.get_urls(), self.app_name, self.namespace


site = StarkSite()
