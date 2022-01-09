
from management import models
from stark.service.stark import site

from management.views.userinfo import UserInfoHandler #用户的视图
from management.views.school import SchoolHandler   #学校的视图
from management.views.depart import DepartHandler   #部门的视图
from management.views.classes import ClassesHandler #班级的视图
from management.views.private_customer import PrivateCustomerHandler   #客户的视图，包含公户和私户
from management.views.public_customer import PublicCustomerHandler #班级的视图
from management.views.consult_record import ConsultRecordHandler
from management.views.payment_record import PaymentHandler
from management.views.check_payment import CheckPaymentHandler
from management.views.student import StudentHandler
from management.views.score_record import ScordHandler
from management.views.course_record import CourseRecordHandler
from management.views.study_record import StudyRecordHandler
# 注册到stark组件中

site.register(models.UserInfo, UserInfoHandler)
site.register(models.Depart, DepartHandler)
site.register(models.School, SchoolHandler)
site.register(models.ClassList, ClassesHandler)

site.register(models.Customer, PublicCustomerHandler, 'pub') #公户
site.register(models.Customer, PrivateCustomerHandler, 'priv') # 私户
site.register(models.ConsultRecord,ConsultRecordHandler)
site.register(models.PaymentRecord,PaymentHandler)
site.register(models.PaymentRecord,CheckPaymentHandler,'check')# 财务用的，查看所有的缴费申请与缴费记录
site.register(models.Student,StudentHandler)
site.register(models.ScoreRecord,ScordHandler)
site.register(models.CourseRecord,CourseRecordHandler)
site.register(models.StudyRecord,StudyRecordHandler)
# 跟进记录
