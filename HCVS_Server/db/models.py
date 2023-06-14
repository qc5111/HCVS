from django.db import models

# Create your models here.

class User(models.Model):
    name = models.CharField(max_length=20)
    id_tpye = models.IntegerField()
    id_number = models.CharField(max_length=20)
    public_key = models.CharField(max_length=100)


class Admin(User):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    #权限定义
    is_super = models.BooleanField(default=False)
