from django.shortcuts import render,redirect
from stock.models import *
from .models import *
from django.forms import widgets as wid
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms import ModelForm
from django.db import transaction
from django.core.exceptions import ValidationError


class OrderForm(ModelForm):
    class Meta:
        model = Order
        # fields = "__all__"
        exclude = ["status","money"]
        labels = {
            "customer": "客户",
            "type": "入库/出库",
            "address": "地址",
            "phone": "电话",
            "user_name": "操作员",


        }
        error_messages = {
            'customer': {'required': "客户名称不能为空", },
            'address': {'required': "地址不能为空", },
            "phone": {'required':"电话不能为空"},
        }

        widgets = {
            "type": wid.Select(choices=(("出库", '出库'), ("入库", '入库')),attrs={"class": "form-control"}),
            "customer": wid.TextInput(attrs={"class": "form-control"}),
            "address": wid.TextInput(attrs={"class": "form-control"}),
            "phone": wid.TextInput(attrs={"class": "form-control"}),
            "user_name": wid.Select(attrs={"class": "form-control"}),
        }


class OrderDetailForm(ModelForm):
    class Meta:
        model = OrderDetail
        exclude = ["order"]
        labels = {
            "fruit": "名称",
            "price": "价格",
            "number": "数量",

        }
        error_messages = {
            'fruit': {'required': "名称不能为空", },
            'price': {'required': "价格不能为空", },
            "number": {'required': "数量不能为空"},
        }

        widgets = {
            "fruit": wid.Select(attrs={"class": "form-control"}),
            "price": wid.TextInput(attrs={"class": "form-control"}),
            "number": wid.TextInput(attrs={"class": "form-control"}),

        }
    # def clean(self):
    #     fruit = self.cleaned_data.get("fruit")
    #     number = self.cleaned_data.get("number")
    #     if fruit:
    #         if number > fruit.user_number:
    #             self.add_error("number", ValidationError("库存不足！"))
    #             raise ValidationError("库存不足！")
    #     return self.cleaned_data


def order_list(request):
    order_list = Order.objects.filter(status=0).order_by("date")
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
    return render(request, "order/order_list.html", locals())


def order_add(request):
    form = OrderForm()
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/order/")

    return render(request, "order/order_add.html", locals())


def order_content_add(request, id):
    order_id = id
    form = OrderDetailForm()
    if request.method == "POST":
        form = OrderDetailForm(request.POST)
        if form.is_valid():
            fruit = form.cleaned_data["fruit"]
            price = form.cleaned_data["price"]
            number = form.cleaned_data["number"]
            order = Order.objects.filter(pk=id).first()
            order_detail = OrderDetail.objects.create(fruit=fruit, order=order,
                                                      price=price, number=number)
            return redirect("/order/content/{}".format(id))

    order_detail_list1 = Order.objects.filter(pk=id).first().details.all()

    paginator = Paginator(order_detail_list1, 5)
    page = request.GET.get('page')
    try:
        order_detail_list = paginator.page(page)  # 获取某页对应的记录
    except PageNotAnInteger:  # 如果页码不是个整数
        order_detail_list = paginator.page(1)  # 提取第一页的记录
    except EmptyPage:  # 如果页码太大，没有相应的记录
        order_detail_list = paginator.page(paginator.num_pages)  # 提取最后一页的记录

    return render(request, "order/order_content_add.html", locals())


def order_content_delete(request, id):
    OrderDetail.objects.filter(pk=id).first().delete()
    order_id = request.GET.get("order")
    return redirect("/order/content/{}".format(order_id))


def order_content_edit(request,id):
    detail = OrderDetail.objects.filter(pk=id).first()
    form = OrderDetailForm(instance=detail)
    if request.method == "POST":
        form = OrderDetailForm(request.POST, instance=detail)
        order_id = request.GET.get("order")
        print(order_id)

        if form.is_valid():
            form.save()
            return redirect("/order/content/{}".format(order_id))

    detail_id = id
    order_id = request.GET.get("order")
    return render(request, "order/order_content_edit.html", locals())


def order_detail(request, id):
    order = Order.objects.filter(pk=id).first()
    order_detail_list = order.details.all()
    money = 0
    for detail in order_detail_list:
        detail_money = detail.price*detail.number
        money += detail_money
    order.money = money
    order.save()

    return render(request, "order/order_detail.html", locals())


def order_delete(request, id):
    Order.objects.filter(pk=id).delete()
    return redirect("/order/")


@transaction.atomic()
def order_confirm(request, id):
    order = Order.objects.filter(pk=id).first()
    order_detail_list = order.details.all()
    tran = transaction.savepoint()  # 保存事务发生点
    try:
        if order.type == "出库":
            for detail in order_detail_list:
                use_number = detail.fruit.user_number
                if detail.number <= use_number:
                    detail.fruit.user_number = use_number - detail.number
                    detail.fruit.save()
                else:
                    transaction.savepoint_rollback(tran)
                    order.status = 1      # 错误订单
                    order.save()
                    return redirect("/order/errors/")

            order.status = 2             # 确认成功
            order.save()
            transaction.savepoint_commit(tran)
            return redirect("/order/finish/")

        else:
            for detail in order_detail_list:
                use_number = detail.fruit.user_number
                detail.fruit.user_number = use_number + detail.number
                detail.fruit.save()

            order.status = 2
            order.save()
            transaction.savepoint_commit(tran)
            return redirect("/order/finish/")

    except Exception as e:
        transaction.savepoint_rollback(tran)  # 事务全部取消
        order.status = 1  # 错误订单
        order.save()
        return redirect("/order/errors/")



def order_errors(request):
    order_queryset = Order.objects.filter(status=1).order_by("date")
    paginator = Paginator(list(order_queryset), 5)
    page = request.GET.get('page')
    try:
        orders = paginator.page(page)  # 获取某页对应的记录
    except PageNotAnInteger:  # 如果页码不是个整数
        orders = paginator.page(1)  # 提取第一页的记录
    except EmptyPage:  # 如果页码太大，没有相应的记录
        orders = paginator.page(paginator.num_pages)  # 提取最后一页的记录
    path = request.path_info
    request.session["pre_path"] = path

    return render(request, "order/order_errors_list.html", locals())


def order_finish(request):
    order_queryset = Order.objects.filter(status=2).order_by("date")
    paginator = Paginator(list(order_queryset), 5)
    page = request.GET.get('page')
    try:
        orders = paginator.page(page)  # 获取某页对应的记录
    except PageNotAnInteger:  # 如果页码不是个整数
        orders = paginator.page(1)  # 提取第一页的记录
    except EmptyPage:  # 如果页码太大，没有相应的记录
        orders = paginator.page(paginator.num_pages)  # 提取最后一页的记录

    path = request.path_info
    request.session["pre_path"] = path
    return render(request, "order/order_finish_list.html", locals())
