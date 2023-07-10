import base64
import json

from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader

from HCVS_Server.admin.authorization import AuthorizationCheck
from tools import gen_new_code, mybase64
from HCVS_Server.settings import dbRaw
import db.models as db
from tools.hash_chain import writeChain


@AuthorizationCheck
def index(request, user):
    print(user)
    head = loader.get_template('admin/head.html').render({"username": user.name}, request)
    body = loader.get_template('admin/index.html').render({}, request)
    return HttpResponse(head + body)


@AuthorizationCheck
def userManagement(request, user):
    head = loader.get_template('admin/head.html').render({"username": user.name}, request)
    body = loader.get_template('admin/user-management.html').render({}, request)
    return HttpResponse(head + body)


@AuthorizationCheck
def genNewCode(request, user):
    idStr, image_private_key, image_otp = gen_new_code.gen_new_code()
    body = loader.get_template('admin/gen-new-code.html').render(
        {"idStr": idStr, "image_private_key": image_private_key, "image_otp": image_otp}, request)
    return HttpResponse(body)


@AuthorizationCheck
def getUserList(request, user):
    Page = int(request.GET.get("page"))
    filter = request.GET.get("filter")
    # 尝试转为int，如果失败则说明是字符串
    try:
        filter = int(filter)
    except:
        filter = int.from_bytes(mybase64.b64decode(filter), byteorder="big")
    if filter == 0:
        dbResult = dbRaw.select("SELECT id, active FROM user_key ORDER BY id desc LIMIT %s, 10" % ((Page - 1) * 10))
        totalUser = dbRaw.select("SELECT count(*) FROM user_key")
    else:
        dbResult = dbRaw.select(
            "SELECT id, active FROM user_key  WHERE id = %d ORDER BY id desc LIMIT %s, 10" % (filter, (Page - 1) * 10))
        totalUser = dbRaw.select("SELECT count(*) FROM user_key WHERE id = %d" % filter)
    returnJson = {"totalUser": totalUser[0]["count(*)"], "userList": dbResult}

    return HttpResponse(json.dumps(returnJson, ensure_ascii=False), content_type="application/json")


@AuthorizationCheck
def activeUser(request, user):
    id = int(request.POST.get("id"))
    dbRaw.update("user_key", [{"id": id, "active": 1}], "id")
    return HttpResponse("ok")


@AuthorizationCheck
def inactiveUser(request, user):
    id = int(request.POST.get("id"))
    dbRaw.update("user_key", [{"id": id, "active": 0}], "id")
    return HttpResponse("ok")


@AuthorizationCheck
def voteManagement(request, user):
    head = loader.get_template('admin/head.html').render({"username": user.name}, request)
    body = loader.get_template('admin/vote-management.html').render({}, request)
    return HttpResponse(head + body)


@AuthorizationCheck
def createVote(request, user):
    createData = json.loads(request.body)
    # print(len(createData["voteName"]))
    # 时间规划到10分钟
    createData["startTime"] = createData["startTime"] - createData["startTime"] % 600000
    createData["endTime"] = createData["endTime"] - createData["endTime"] % 600000
    new_vote = db.vote.objects.create(name=createData["voteName"],
                                      start_time=createData["startTime"],
                                      end_time=createData["endTime"],
                                      min_choice=createData["minChoice"],
                                      max_choice=createData["maxChoice"],
                                      createUser=user,
                                      )
    for key in createData["choiceList"]:
        db.vote_choice.objects.create(vote=new_vote, seq=int(key), name=createData["choiceList"][key])
    cursor = dbRaw.conn.cursor()
    cursor.execute("CREATE TABLE vote_data_%d AS SELECT * FROM vote_data_template WHERE 1 = 0;" % new_vote.id)
    cursor.execute("CREATE TABLE vote_chain_%d AS SELECT * FROM vote_chain_template WHERE 1 = 0;" % new_vote.id)
    dbRaw.conn.commit()
    cursor.close()
    # 写入0号区块
    # 0号区块数据
    blockData = b"\x00"  # 版本
    blockData += len(createData["voteName"]).to_bytes(1, byteorder="big") + createData[
        "voteName"].encode()  # 投票名称长度 + 投票名称
    blockData += b"\x08" + createData["startTime"].to_bytes(8, byteorder="big")  # 开始时间长度 + 开始时间
    blockData += b"\x08" + createData["endTime"].to_bytes(8, byteorder="big")  # 结束时间长度 + 结束时间
    blockData += b"\x01" + createData["minChoice"].to_bytes(1, byteorder="big")  # 最小选择长度 + 最小选择
    blockData += b"\x01" + createData["maxChoice"].to_bytes(1, byteorder="big")  # 最大选择长度 + 最大选择
    for key in createData["choiceList"]:
        blockData += len(createData["choiceList"][key]).to_bytes(1, byteorder="big") + createData["choiceList"][
            key].encode()  # 选项长度 + 选项
    # 写入0号区块
    writeChain(new_vote.id, blockData, 0, createData["startTime"]-1)
    # 创建投票数据表
    db.vote_result.objects.create(vote=new_vote)
    returnJson = {"success": True, "voteId": new_vote.id}
    return HttpResponse(json.dumps(returnJson, ensure_ascii=False), content_type="application/json")


@AuthorizationCheck
def getVoteList(request, user):
    Page = int(request.GET.get("page"))
    filter = request.GET.get("filter")
    if filter is None:
        dbResult = db.vote.objects.all().order_by("-id")
    else:
        dbResult = db.vote.objects.filter(name__contains=filter).order_by("-id")
    returnJson = {"totalVote": dbResult.count(), "voteList": []}
    dbResult = dbResult[(Page - 1) * 10:Page * 10]
    for vote in dbResult:
        voteJson = {"id": vote.id, "name": vote.name, "start_time": vote.start_time, "end_time": vote.end_time,
                    "min_choice": vote.min_choice, "max_choice": vote.max_choice, "createUser": vote.createUser.name,
                    "choiceList": {}}
        for choice in vote.vote_choice_set.all():
            voteJson["choiceList"][choice.seq] = choice.name
        returnJson["voteList"].append(voteJson)

    return HttpResponse(json.dumps(returnJson, ensure_ascii=False), content_type="application/json")
