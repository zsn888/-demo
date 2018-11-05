from django.db import models
# Create your models here.


class Fruit(models.Model):
    name = models.CharField(max_length=32, unique=True)
    total = models.IntegerField()     #总数
    user_number = models.IntegerField()  #可用数
    unit = models.CharField(max_length=32)
    comment = models.CharField(max_length=128, null=True, default='')
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True)

    def __str__(self):
        return self.name




