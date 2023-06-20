import base64
import hashlib
import json
import time
from functools import wraps
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
import db.models as db
from HCVS_Server.settings import dbRaw
from tools import otp


def UserAuthorizationCheck(func):
    @wraps(func)
    def wrapTheFunction(request):
        id = {}
        id["int"] = int(request.COOKIES.get('id', 0))
        if id["int"] == 0:
            return HttpResponseRedirect("/login")
        else:
            id["bytes"] = id["int"].to_bytes(6, byteorder="big")
            id["str"] = base64.b64encode(id["bytes"]).replace(b"=", b"").decode()
            return func(request, id)

    return wrapTheFunction


@UserAuthorizationCheck
def Otp(request, id):
    nowTime = int(time.time()*1000)
    otpCode = request.POST.get("otp")
    dbResult = dbRaw.select("SELECT * FROM user_key WHERE id = %d" % id["int"])
    if not dbResult:
        return HttpResponse("{\"success\": false, \"message\": \"User Error\"}", content_type="application/json")
    if dbResult[0]["active"] == 0:
        return HttpResponse("{\"success\": false, \"message\": \"User Not Active\"}",
                            content_type="application/json")
    user = dbResult[0]
    # 检查OTP错误次数一小时内是否超过3次
    errorCount = db.otpFailRecord.objects.filter(user_id=id["int"], time__gte=nowTime - 3600000).count()
    if errorCount >= 3:
        return HttpResponse("{\"success\": false, \"message\": \"Dynamic Password Error Too Many Times\"}",
                            content_type="application/json")
    if otp.verify(user["otp_key"], otpCode):
        # 此处返回public key和private key的aes密码
        returnValue = {
            "success": True,
            "public_key": base64.b64encode(user["public_key_x"]+user["public_key_y"]).decode(),
            "private_key_code": base64.b64encode(user["private_key_code"]).decode(),
        }
        return HttpResponse(json.dumps(returnValue, ensure_ascii=False), content_type="application/json")
        pass
    else:
        db.otpFailRecord.objects.create(user_id=id["int"], ipAddress=request.META.get("REMOTE_ADDR"), time=nowTime)


