
import hashlib
from functools import wraps
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
import db.models as db


def Login(request):
    template = loader.get_template('user/login.html')
    return HttpResponse(template.render())