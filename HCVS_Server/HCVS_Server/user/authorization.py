import base64
import hashlib
from functools import wraps
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
import db.models as db


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