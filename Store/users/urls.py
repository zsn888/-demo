from django.conf.urls import url
from . import views
urlpatterns =[
    url(r'^$', views.user_list),
    url(r'add$', views.user_add),
    url(r'edit/(\d+)$', views.edit),
    url(r'delete/(\d+)$', views.delete),

]