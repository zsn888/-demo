from django.conf.urls import url
from . import views
urlpatterns =[
    url(r'^$', views.stock_list),
    url(r'add$', views.stock_add),
    url(r'edit/(\d+)$', views.stock_edit),
    url(r'delete/(\d+)$', views.stock_delete),
    url(r'agenda/$', views.stock_agenda),
    url(r'confirm/(\d+)$', views.stock_confirm),
    url(r'finish/$', views.stock_finish),

]