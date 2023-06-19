import hashlib
from functools import wraps
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
import db.models as db


def AuthorizationCheck(func):
    @wraps(func)
    def wrapTheFunction(request):
        if "Username" in request.session:
            dbResult = db.adminUser.objects.filter(username=request.session["Username"])
            if dbResult.count() != 0:
                return func(request, dbResult[0])
        return HttpResponseRedirect("/admin/login")

    return wrapTheFunction


def Login(request):
    template = loader.get_template('admin/login.html')
    return HttpResponse(template.render())


def AjaxLogin(request):
    dbResult = db.adminUser.objects.filter(username=request.POST.get('Username'))
    if dbResult.count() == 0:
        return HttpResponse("ERROR")
    print(dbResult[0])
    if hashlib.sha1(request.POST.get('Password').encode()).hexdigest() == dbResult[0].password:
        request.session["Username"] = request.POST.get('Username')
        return HttpResponse("OK")
    else:
        return HttpResponse("ERROR")
