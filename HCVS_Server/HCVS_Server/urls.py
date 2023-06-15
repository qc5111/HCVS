"""HCVS_Server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from HCVS_Server import gen_new_code
from HCVS_Server.admin import authorization, admin
from HCVS_Server.user import login

urlpatterns = [
    path("gen_new_code", gen_new_code.gen_new_code),
    path('admin/Login', authorization.Login),
    path('admin/AjaxLogin', authorization.AjaxLogin),
    path('admin/index', admin.index),
    path("login", login.Login),
]
