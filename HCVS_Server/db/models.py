from django.db import models


# Create your models here.


class adminUser(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=40)
    name = models.CharField(max_length=20)
    # 权限定义
    is_super = models.BooleanField(default=False)
    can_GenNewCode = models.BooleanField(default=False)


"""ID
投票名
开始时间
结束时间
持续时间（计算得出）
选项（独立在其他表）
最少选择数量
最大选择数量"""


class vote(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64)
    start_time = models.BigIntegerField()
    end_time = models.BigIntegerField()
    min_choice = models.IntegerField()
    max_choice = models.IntegerField()
    createUser = models.ForeignKey(adminUser, on_delete=models.CASCADE, default=1)


class vote_choice(models.Model):
    vote = models.ForeignKey(vote, on_delete=models.CASCADE)
    seq = models.IntegerField()
    name = models.CharField(max_length=32)

    # 组合索引
    class Meta:
        unique_together = ("vote", "seq")


# otp请求失败记录
class otpFailRecord(models.Model):
    user_id = models.BigIntegerField()
    ipAddress = models.CharField(max_length=15)
    time = models.BigIntegerField()

    class Meta:
        unique_together = ("user_id", "time")
