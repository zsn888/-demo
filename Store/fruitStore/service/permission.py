import re
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse,redirect


def reg(request,current_path):

    permission_list = request.session.get("permission_list", [])
    flag = False
    for permission in permission_list:
        ret = re.match(permission, current_path)
        if ret:
            flag = True
            break
    return flag


class ValidPermission(MiddlewareMixin):

    def process_request(self,request):

        current_path = request.path_info

        # 检查是否属于白名单
        valid_url_list=["/login/","/admin/.*","/logout/","/index/"]

        for valid_url in valid_url_list:
            ret=re.match(valid_url,current_path)
            if ret:
                return None

        # 校验是否登录,必须先登录

        if not request.user.username:
            print("1111111111")
            return redirect("/login/")

        # 校验权限
        flag=reg(request,current_path)

        if not flag:
            return HttpResponse("没有访问权限！")

        return None