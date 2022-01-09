from django.shortcuts import render,redirect
from management.utils.md5 import gen_md5
from management import models
from django.urls import reverse
from rbac.service.init_permission import init_permission
def login(request):
    if request.method == 'GET':
        return render(request,'login.html')

    username = request.POST.get('user')
    password = request.POST.get('pwd')
    user = models.UserInfo.objects.filter(username=username,password=gen_md5(password)).first()
    if user:
        # 将登陆成功后保存登陆用户信息到session中
        request.session['user'] = {'id':user.id,'username':user.username,'name':user.name,'depart':user.depart.title}
        init_permission(request,current_user=user)
        return redirect(reverse('index'))
    else:
        return render(request,'login.html',{"msg":'账号或者密码错误'})


def logout(request):
    request.session.delete()
    return redirect('/login/')


def index(request):
    return render(request,'index.html')