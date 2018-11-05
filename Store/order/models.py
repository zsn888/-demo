from django.db import models

# Create your models here.


class Order(models.Model):
    type = models.CharField(max_length=12)
    date = models.DateTimeField(auto_now_add=True)
    customer = models.CharField(max_length=32)
    address = models.CharField(max_length=128,null=True)
    phone = models.IntegerField()
    user_name = models.ForeignKey(to="fruitStore.UserInfo")
    status = models.IntegerField(default=0)    # 0未处理 1错误 2已确认 3仓库处理完成
    money = models.DecimalField(max_digits=8, decimal_places=2,null=True)

    def __str__(self):
        return self.customer


class OrderDetail(models.Model):
    fruit = models.ForeignKey(to="stock.Fruit")
    order = models.ForeignKey(to="Order", related_name="details")
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    number = models.IntegerField()

    def __str__(self):
        return self.fruit.name