
from django import forms
class DateTimeInput(forms.TextInput):
    input_type = 'text'
    template_name = 'stark/forms/widgets/datatime.html'



# 要用这个日期选择插件的时候只需要将下面代码新建一个html文件，然后template_name指向该文件


"""

<div class="form-group">
{#                <label for="dtp_input2" class="col-md-2 control-label">日期</label>#}
                <div class="input-group date form_date " data-date="" data-date-format="yyyy MM dd  "
                     data-link-field="dtp_input2" data-link-format="yyyy-mm-dd">
                        <input class="form-control" readonly type="{{ widget.type }}" name="{{ widget.name }}"{% if widget.value != None %} value="{{ widget.value|stringformat:'s' }}"{% endif %}{% include "django/forms/widgets/attrs.html" %}>
                    <span class="input-group-addon"><span class="glyphicon glyphicon-calendar"></span></span>
                </div>
            </div>

"""
# 然后在layout中引入datetimepicker需要的css和js，以及配置文件

"""
css文件
<link rel="stylesheet" href="{% static 'plugins/datetimepicker/css/bootstrap-datetimepicker.css' %} "/>
js文件
<script src="{% static 'plugins/datetimepicker/js/bootstrap-datetimepicker.js' %} "></script>
<script src="{% static 'plugins/datetimepicker/js/locales/bootstrap-datetimepicker.zh-CN.js' %} "></script>
js配置
<script>
    $('.form_date').datetimepicker({
        language:  'zh-CN',
		startView: 2,
		minView: 'month',
		forceParse: 0,
        startDate:new Date(),
        autoclose: true,
        pickerPosition:'bottom-left',
        format:'yyyy-mm-dd',
        sideBySide:true,
        bootcssVer:3,
    });
</script>
"""