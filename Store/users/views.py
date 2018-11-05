from django.shortcuts import render,redirect
from fruitStore.models import *
from django.forms import ModelForm
from django.forms import widgets as wid
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class UserForm(ModelForm):
    # gender = forms.ChoiceField(choices=((1, '男'), (2, '女')),label="性别",)
    class Meta:
        model= UserInfo
        fields = ["username","gender","phone","roles"]
        labels = {
            "username": "姓名",
            # "password": "密码",
            "gender": "性别",
            "phone": "电话",
            "roles": "角色",
        }
        error_messages = {
            'username': {'required': "用户名不能为空", },
            'roles': {'required': "角色不能为空", },
        }

        widgets = {
            "username": wid.TextInput(attrs={"class": "form-control"}),
            # "password": wid.PasswordInput(attrs={"class": "form-control"}),
            "gender": wid.Select(choices=(("男", '男'), ("女", '女')),attrs={"class": "form-control"}),
            "phone": wid.NumberInput(attrs={"class": "form-control"}),

        }


def user_list(request):

    user_list1 = UserInfo.objects.all().order_by("id")
    paginator = Paginator(user_list1, 5)
    page = request.GET.get('page')
    try:
        user_list = paginator.page(page)  # 获取某页对应的记录
    except PageNotAnInteger:            # 如果页码不是个整数
        user_list = paginator.page(1)  # 提取第一页的记录
    except EmptyPage:                  # 如果页码太大，没有相应的记录
        user_list = paginator.page(paginator.num_pages)  # 提取最后一页的记录

    return render(request, "users/user_list.html",locals())


def user_add(request):
    form = UserForm()
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            # password = form.cleaned_data["password"]
            gender = form.cleaned_data["gender"]
            phone = form.cleaned_data["phone"]
            roles = form.cleaned_data["roles"]
            password = request.POST.get("password")
            # print(roles)

            user = UserInfo.objects.create_user(username=username,password=password,
                                                gender=gender,phone=phone)
            user.roles.add(*roles)
            # form.save()
            return redirect("/users/")

    return render(request, "users/user_add.html", locals())


def edit(request, id):

    user = UserInfo.objects.filter(id=id).first()
    form = UserForm(instance=user)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("/users/")

    return render(request, "users/user_edit.html", locals())


def delete(request, id):
    UserInfo.objects.filter(id=id).first().delete()
    return redirect("/users/")