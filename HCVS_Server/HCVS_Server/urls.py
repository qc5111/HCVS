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

from tools import gen_new_code
from HCVS_Server.admin import authorization, admin
from HCVS_Server.user import login, user

urlpatterns = [
    # path("gen_new_code", gen_new_code.gen_new_code),
    path('admin/login', authorization.Login),
    path('admin/AjaxLogin', authorization.AjaxLogin),
    path('admin/index', admin.index),
    path('admin', admin.index),
    path('admin/', admin.index),
    path('admin/user-management', admin.userManagement),
    path('admin/gen-new-code', admin.genNewCode),
    path('admin/get-user-list', admin.getUserList),
    path('admin/active-user', admin.activeUser),
    path('admin/inactive-user', admin.inactiveUser),
    path('admin/vote-management', admin.voteManagement),
    path('admin/create-vote', admin.createVote),
    path('admin/get-vote-list', admin.getVoteList),
    path("login", login.Login),
    path("", user.index),
    path("index", user.index),
    path("vote", user.vote),
    path("get-vote-list", user.getVoteList),

]
