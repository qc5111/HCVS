import base64
import json
import time

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from HCVS_Server.user.authorization import UserAuthorizationCheck
import db.models as db


@UserAuthorizationCheck
def index(request, id):
    head = loader.get_template('user/head.html').render({"username": id["str"]}, request)
    body = loader.get_template('user/index.html').render({}, request)
    return HttpResponse(head + body)


def getVoteList(request):
    #过滤进行中的投票
    now = time.time()*1000
    returnJson = {"nowVoteList": [], "comingVoteList": [], "endVoteList": []}

    dbResult = db.vote.objects.filter(start_time__lt=now, end_time__gt=now).order_by("-id")
    for vote in dbResult:
        voteJson = {"id": vote.id, "name": vote.name}
        returnJson["nowVoteList"].append(voteJson)

    dbResult = db.vote.objects.filter(start_time__gt=now).order_by("-id")[:10]
    for vote in dbResult:
        voteJson = {"id": vote.id, "name": vote.name}
        returnJson["comingVoteList"].append(voteJson)

    dbResult = db.vote.objects.filter(end_time__lt=now).order_by("-id")[:10]
    for vote in dbResult:
        voteJson = {"id": vote.id, "name": vote.name}
        returnJson["endVoteList"].append(voteJson)

    return HttpResponse(json.dumps(returnJson, ensure_ascii=False), content_type="application/json")


@UserAuthorizationCheck
def vote(request, id):
    head = loader.get_template('user/head.html').render({"username": id["str"]}, request)
    body = loader.get_template('user/vote.html').render({}, request)

    return HttpResponse(head + body)