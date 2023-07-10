from django.db import models
from django.db.models import F


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
    chain_height = models.IntegerField(default=0)
    createUser = models.ForeignKey(adminUser, on_delete=models.CASCADE, default=1)


class vote_choice(models.Model):
    vote = models.ForeignKey(vote, on_delete=models.CASCADE)
    seq = models.IntegerField()
    name = models.CharField(max_length=32)

    # 组合索引
    class Meta:
        unique_together = ("vote", "seq")


class vote_result(models.Model):
    vote = models.ForeignKey(vote, on_delete=models.CASCADE, primary_key=True)
    Choice_1 = models.BigIntegerField(default=0)
    Choice_2 = models.BigIntegerField(default=0)
    Choice_3 = models.BigIntegerField(default=0)
    Choice_4 = models.BigIntegerField(default=0)
    Choice_5 = models.BigIntegerField(default=0)
    Choice_6 = models.BigIntegerField(default=0)
    Choice_7 = models.BigIntegerField(default=0)
    Choice_8 = models.BigIntegerField(default=0)
    Choice_9 = models.BigIntegerField(default=0)
    Choice_10 = models.BigIntegerField(default=0)
    Choice_11 = models.BigIntegerField(default=0)
    Choice_12 = models.BigIntegerField(default=0)
    Choice_13 = models.BigIntegerField(default=0)
    Choice_14 = models.BigIntegerField(default=0)
    Choice_15 = models.BigIntegerField(default=0)
    Choice_16 = models.BigIntegerField(default=0)
    Choice_17 = models.BigIntegerField(default=0)
    Choice_18 = models.BigIntegerField(default=0)
    Choice_19 = models.BigIntegerField(default=0)
    Choice_20 = models.BigIntegerField(default=0)
    Choice_21 = models.BigIntegerField(default=0)
    Choice_22 = models.BigIntegerField(default=0)
    Choice_23 = models.BigIntegerField(default=0)
    Choice_24 = models.BigIntegerField(default=0)
    Choice_25 = models.BigIntegerField(default=0)
    Choice_26 = models.BigIntegerField(default=0)
    Choice_27 = models.BigIntegerField(default=0)
    Choice_28 = models.BigIntegerField(default=0)
    Choice_29 = models.BigIntegerField(default=0)
    Choice_30 = models.BigIntegerField(default=0)
    Choice_31 = models.BigIntegerField(default=0)
    Choice_32 = models.BigIntegerField(default=0)

    def get_choice_total(self):
        return sum([getattr(self, 'Choice_%s' % i) for i in range(1, 33)])

    def add_choice(self, choice_array):
        # 补全数组到32个
        choice_array += [0] * (32 - len(choice_array))
        self.Choice_1 = F('Choice_1') + choice_array[0]
        self.Choice_2 = F('Choice_2') + choice_array[1]
        self.Choice_3 = F('Choice_3') + choice_array[2]
        self.Choice_4 = F('Choice_4') + choice_array[3]
        self.Choice_5 = F('Choice_5') + choice_array[4]
        self.Choice_6 = F('Choice_6') + choice_array[5]
        self.Choice_7 = F('Choice_7') + choice_array[6]
        self.Choice_8 = F('Choice_8') + choice_array[7]
        self.Choice_9 = F('Choice_9') + choice_array[8]
        self.Choice_10 = F('Choice_10') + choice_array[9]
        self.Choice_11 = F('Choice_11') + choice_array[10]
        self.Choice_12 = F('Choice_12') + choice_array[11]
        self.Choice_13 = F('Choice_13') + choice_array[12]
        self.Choice_14 = F('Choice_14') + choice_array[13]
        self.Choice_15 = F('Choice_15') + choice_array[14]
        self.Choice_16 = F('Choice_16') + choice_array[15]
        self.Choice_17 = F('Choice_17') + choice_array[16]
        self.Choice_18 = F('Choice_18') + choice_array[17]
        self.Choice_19 = F('Choice_19') + choice_array[18]
        self.Choice_20 = F('Choice_20') + choice_array[19]
        self.Choice_21 = F('Choice_21') + choice_array[20]
        self.Choice_22 = F('Choice_22') + choice_array[21]
        self.Choice_23 = F('Choice_23') + choice_array[22]
        self.Choice_24 = F('Choice_24') + choice_array[23]
        self.Choice_25 = F('Choice_25') + choice_array[24]
        self.Choice_26 = F('Choice_26') + choice_array[25]
        self.Choice_27 = F('Choice_27') + choice_array[26]
        self.Choice_28 = F('Choice_28') + choice_array[27]
        self.Choice_29 = F('Choice_29') + choice_array[28]
        self.Choice_30 = F('Choice_30') + choice_array[29]
        self.Choice_31 = F('Choice_31') + choice_array[30]
        self.Choice_32 = F('Choice_32') + choice_array[31]
        self.save()


# otp请求失败记录
class otpFailRecord(models.Model):
    user_id = models.BigIntegerField()
    ipAddress = models.CharField(max_length=15)
    time = models.BigIntegerField()

    class Meta:
        unique_together = ("user_id", "time")
