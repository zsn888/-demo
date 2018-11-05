from django.conf.urls import url
from . import views
urlpatterns =[
    url(r'^$', views.order_list),
    url(r'add$', views.order_add),
    url(r'content/(\d+)$', views.order_content_add),
    url(r'content/delete/(\d+)$', views.order_content_delete),
    url(r'content/edit/(\d+)$', views.order_content_edit),
    url(r'detail/(\d+)$', views.order_detail),
    url(r'delete/(\d+)$', views.order_delete),
    url(r'confirm/(\d+)$', views.order_confirm),
    url(r'errors/$', views.order_errors),
    url(r'finish/$', views.order_finish),

]