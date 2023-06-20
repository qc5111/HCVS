import base64
import json
import time

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader

from HCVS_Server.settings import dbRaw
from HCVS_Server.user.authorization import UserAuthorizationCheck
import db.models as db
from tools import ecc, mybase64


@UserAuthorizationCheck
def index(request, id):
    head = loader.get_template('user/head.html').render({"username": id["str"]}, request)
    body = loader.get_template('user/index.html').render({}, request)
    return HttpResponse(head + body)


def getVoteList(request):
    # 过滤进行中的投票
    now = time.time() * 1000
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
    try:
        vote = db.vote.objects.get(id=int(request.GET.get("id")))
    except:
        return HttpResponseRedirect("/user/index")

    voteJson = {"id": vote.id, "name": vote.name, "start_time": vote.start_time, "end_time": vote.end_time,
                "min_choice": vote.min_choice, "max_choice": vote.max_choice, "choiceList": {}}
    if vote.max_choice == 1:
        voteJson["type"] = "radio"
    else:
        voteJson["type"] = "checkbox"
    for choice in vote.vote_choice_set.all():
        voteJson["choiceList"][choice.seq] = choice.name

    head = loader.get_template('user/head.html').render({"username": id["str"]}, request)
    body = loader.get_template('user/vote.html').render({"vote": voteJson, "userID": id["int"]}, request)

    return HttpResponse(head + body)


@UserAuthorizationCheck
def submitVote(request, id):
    # vote_data: Uint8Array_to_base64(voteData),
    # signature: Uint8Array_to_base64(signature),
    requestData = json.loads(request.body.decode("utf-8"))
    vote_data = mybase64.b64decode(requestData["vote_data"])
    signature = mybase64.b64decode(requestData["signature"])
    # 获取公钥
    dbResult = dbRaw.select("SELECT * FROM user_key WHERE id = %d" % id["int"])
    if not dbResult:
        return HttpResponse("{\"success\": false, \"message\": \"User Error\"}", content_type="application/json")
    if dbResult[0]["active"] == 0:
        return HttpResponse("{\"success\": false, \"message\": \"User Not Active\"}",
                            content_type="application/json")
    user = dbResult[0]
    # 验证签名
    ecc1 = ecc.ECC()
    ecc1.load_public_key_raw(user["public_key_x"] + user["public_key_y"])
    verifySuccess = ecc1.verify(signature, vote_data)
    if not verifySuccess:
        return HttpResponse("{\"success\": false, \"message\": \"Signature Error\"}",
                            content_type="application/json")
    # 解析投票数据
    # 时间戳，User_ID，Vote_ID，投票结果，实际签名
    # 8字节，6字节，4字节，4字节，64字节
    timestamp = int.from_bytes(vote_data[:8], byteorder="big")
    user_id = int.from_bytes(vote_data[8:14], byteorder="big")
    vote_id = int.from_bytes(vote_data[14:18], byteorder="big")
    vote_result_int = int.from_bytes(vote_data[18:22], byteorder="big")
    vote_result = bin(vote_result_int)[2:].zfill(32)

    if user_id != id["int"]:
        return HttpResponse("{\"success\": false, \"message\": \"User ID Error\"}",
                            content_type="application/json")
    print(timestamp, user_id, vote_id, vote_result)
    # 检查投票是否存在
    try:
        vote = db.vote.objects.get(id=vote_id)
    except:
        return HttpResponse("{\"success\": false, \"message\": \"Vote Not Found\"}",
                            content_type="application/json")
    totalChoice = vote.vote_choice_set.all().count()
    # 后面是有效的投票结果，前面的0不计入
    validVoteResult = vote_result[32 - totalChoice:]
    print(validVoteResult)
    vote_select = validVoteResult.count("1")
    # 检查投票是否已经结束
    now = time.time() * 1000
    if vote.end_time < now:
        return HttpResponse("{\"success\": false, \"message\": \"Vote End\"}",
                            content_type="application/json")
    # 检查投票是否已经开始
    if vote.start_time > now:
        return HttpResponse("{\"success\": false, \"message\": \"Vote Not Start\"}",
                            content_type="application/json")
    # 检查投票是否已经投过
    vote_result = dbRaw.select("SELECT * FROM vote_data_%d WHERE user_id = %d" % (vote_id, user_id))
    if vote_result:
        return HttpResponse("{\"success\": false, \"message\": \"Vote Already\"}",
                            content_type="application/json")
    # 检查投票结果是否正确
    if vote_select < vote.min_choice or vote_select > vote.max_choice:
        return HttpResponse("{\"success\": false, \"message\": \"Vote Select Error\"}",
                            content_type="application/json")
    # 写入数据库
    keys = ["user_id", "timestamp", "vote_result", "signature"]
    values = [user_id, timestamp, vote_result_int, signature]
    dbRaw.insert("vote_data_%d" % vote_id, keys, values)

    return HttpResponse("{\"success\": true}", content_type="application/json")
