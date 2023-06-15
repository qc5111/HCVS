from django.db import models


# Create your models here.


class adminUser(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=40)
    name = models.CharField(max_length=20)
    # 权限定义
    is_super = models.BooleanField(default=False)
    can_GenNewCode = models.BooleanField(default=False)


