from django.shortcuts import render,redirect
from .models import *
from django.forms import widgets as wid
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms import ModelForm
from order.models import *
from django.db import transaction
# Create your views here.


class FruitForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FruitForm, self).__init__(*args, **kwargs)
        self.fields['comment'].required = False

    class Meta:
        model = Fruit
        # fields = "__all__"
        exclude = ["price"]
        labels = {
            "name": "名称",
            "total": "总数量",
            "user_number": "可用数量",
            "unit": "单位",
            "comment": "备注",
        }
        error_messages = {
            'name': {'required': "名称不能为空", },
            'total': {'required': "数量不能为空", },
            'user_number': {'user_number': "数量不能为空", },
            "unit": {'required': "单位不能为空"},
        }

        widgets = {
            "name": wid.TextInput(attrs={"class": "form-control"}),
            "total": wid.TextInput(attrs={"class": "form-control"}),
            "user_number": wid.TextInput(attrs={"class": "form-control"}),
            "unit": wid.TextInput(attrs={"class": "form-control"}),
            "comment": wid.TextInput(attrs={"class": "form-control"}),


        }


def stock_list(request):
    fruits = Fruit.objects.all()
    paginator = Paginator(list(fruits), 5)
    page = request.GET.get('page')
    try:
        fruit_list = paginator.page(page)  # 获取某页对应的记录
    except PageNotAnInteger:  # 如果页码不是个整数
        fruit_list = paginator.page(1)  # 提取第一页的记录
    except EmptyPage:  # 如果页码太大，没有相应的记录
        fruit_list = paginator.page(paginator.num_pages)  # 提取最后一页的记录

    return render(request, "stock/stock_list.html", locals())


def stock_add(request):
    form = FruitForm()
    if request.method == "POST":
        form = FruitForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/stock/")

    return render(request, "stock/stock_add.html", locals())


def stock_edit(request, id):
    fruit = Fruit.objects.filter(pk=id).first()
    form = FruitForm(instance=fruit)
    if request.method == "POST":
        print(fruit)
        form = FruitForm(request.POST, instance=fruit)

        if form.is_valid():
            form.save()
            return redirect("/stock/")


    return render(request, "stock/stock_edit.html", locals())


def stock_delete(request,id):
    Fruit.objects.filter(pk=id).delete()
    return redirect("/stock/")


def stock_agenda(request):
    order_list = Order.objects.filter(status=2).order_by("date")
    paginator = Paginator(list(order_list), 5)
    page = request.GET.get('page')
    try:
        orders = paginator.page(page)  # 获取某页对应的记录
    except PageNotAnInteger:  # 如果页码不是个整数
        orders = paginator.page(1)  # 提取第一页的记录
    except EmptyPage:  # 如果页码太大，没有相应的记录
        orders = paginator.page(paginator.num_pages)  # 提取最后一页的记录
    path = request.path_info
    request.session["pre_path"] = path
    return render(request, "stock/stock_agenda.html", locals())


@transaction.atomic()
def stock_confirm(request, id):
    order = Order.objects.filter(pk=id).first()
    order_detail_list = order.details.all()
    tran = transaction.savepoint()  # 保存事务发生点
    try:
        if order.type == "出库":

            for detail in order_detail_list:
                total = detail.fruit.total
                if detail.number <= total:
                    detail.fruit.total = total - detail.number
                    detail.fruit.save()
                else:
                    transaction.savepoint_rollback(tran)
                    order.status = 1
                    order.save()
                    return redirect("/stock/agenda")
        else:
            for detail in order_detail_list:
                total = detail.fruit.total
                detail.fruit.total = total + detail.number
                detail.fruit.save()

        order.status = 3  # 订单处理完成
        order.save()
        transaction.savepoint_commit(tran)
    except Exception as e:
        transaction.savepoint_rollback(tran)  # 事务全部取消

    return redirect("/stock/agenda")


def stock_finish(request):
    order_list = Order.objects.filter(status=3).order_by("date")
    paginator = Paginator(list(order_list), 5)
    page = request.GET.get('page')
    try:
        orders = paginator.page(page)  # 获取某页对应的记录
    except PageNotAnInteger:  # 如果页码不是个整数
        orders = paginator.page(1)  # 提取第一页的记录
    except EmptyPage:  # 如果页码太大，没有相应的记录
        orders = paginator.page(paginator.num_pages)  # 提取最后一页的记录

    path = request.path_info
    request.session["pre_path"] = path
    return render(request, "stock/stock_finish.html", locals())