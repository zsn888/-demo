from django.shortcuts import render,redirect
from .models import *
from django.contrib import auth
from django import forms
from django.forms import widgets
from django.core.exceptions import ValidationError
# Create your views here.


class LoginForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=50)
    password = forms.CharField(label='密码', widget=widgets.PasswordInput(),
                               min_length=6, error_messages={"min_length": "用户密码最短6位!", "required": "密码不能为空!"})

    def clean_username(self):
        username = self.cleaned_data.get('username')
        result = UserInfo.objects.filter(username=username)
        if not result:
            raise forms.ValidationError("用户名不存在!")
        return username

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = auth.authenticate(username=username, password=password)
        if not user:
            self.add_error("password", ValidationError("密码错误！"))
            raise ValidationError("密码错误！")

        return self.cleaned_data


def login(request):
    if request.method == "POST":
        form_obj = LoginForm(request.POST)

        if form_obj.is_valid():

            username = form_obj.cleaned_data['username']
            password = form_obj.cleaned_data.get('password')
            user = auth.authenticate(username=username, password=password)

            # if user:
            auth.login(request, user)
            permissions = user.roles.all().values("permissions__url").distinct()
            permisssion_list = []
            for item in permissions:
                permisssion_list.append(item['permissions__url'])
            request.session['permission_list'] = permisssion_list
            print(permisssion_list)

            return redirect('/index/')
        else:
            return render(request, 'login.html', {'form': form_obj})
    form_obj = LoginForm()

    return render(request, "login.html", {'form':form_obj})


def index(request):
    return render(request, "index.html")


def logout(request):
    auth.logout(request)
    return redirect("/index/")