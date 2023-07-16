import base64
import json
import time

from django.forms import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader

from HCVS_Server.settings import dbRaw
from HCVS_Server.user.authorization import UserAuthorizationCheck
import db.models as db
from tools import ecc, mybase64
from tools.calc_vote import decompress_vote


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
    # 如果投票没有开始则返回首页
    if vote.start_time > time.time() * 1000:
        return HttpResponseRedirect("/user/index")
    head = loader.get_template('user/head.html').render({"username": id["str"]}, request)
    voteJson = {"id": vote.id, "name": vote.name, "start_time": vote.start_time, "end_time": vote.end_time,
                "min_choice": vote.min_choice, "max_choice": vote.max_choice, "choiceList": {}}
    if vote.max_choice == 1:
        voteJson["type"] = "radio"
    else:
        voteJson["type"] = "checkbox"
    for choice in vote.vote_choice_set.all():
        voteJson["choiceList"][choice.seq] = choice.name
    # 判断是否已经投过票，或者投票是否已经结束
    vote_result = dbRaw.select("SELECT * FROM vote_data_%d WHERE user_id = %d" % (vote.id, id["int"]))
    if len(vote_result) != 0 or vote.end_time < time.time() * 1000:
        # 解析投票数据
        choice_str = ""
        if len(vote_result) != 0:
            vote_result_int = vote_result[0]["vote_result"]
            vote_result_bin = bin(vote_result_int).zfill(32)
            for i in range(32):
                if vote_result_bin[i] == "1":
                    choice_str += voteJson["choiceList"][32 - i] + ", "
            # 去掉最后的逗号
            choice_str = choice_str[:-2]
            voteJson["choice_str"] = choice_str
            # 判断当前投票处于的区块高度
            shouldInHeight = (vote_result[0]["timestamp"] - vote.start_time) // 600000 + 1
            # 判断该区块是否已经被打包
            chain = dbRaw.select("SELECT * FROM vote_chain_%d WHERE height = %d" % (vote.id, shouldInHeight))
            if len(chain) == 0:
                voteJson["status"] = "Pending Confirmation"
            else:
                voteJson["status"] = "Confirmed by Height %d" % shouldInHeight
        else:
            voteJson["choice_str"] = "You didn't vote."
            voteJson["status"] = "Vote has ended."

        # 转换为二进制

        # 获取投票结果
        totalResult = db.vote_result.objects.get(vote_id=vote.id)
        # 获取当前投票高度
        print(vote.chain_height)
        voteJson["height"] = vote.chain_height
        # 计算投票最高高度
        voteJson["maxHeight"] = (vote.end_time - vote.start_time) // 600000
        # 获取最高高度的Hash值
        nowHash = dbRaw.select("SELECT md5,sha1 FROM vote_chain_%d WHERE height = %d" % (vote.id, voteJson["height"]))
        voteJson["nowHash"] = base64.b64encode(nowHash[0]["md5"] + nowHash[0]["sha1"]).decode("utf-8")
        # 获取投票总数
        voteJson["total"] = totalResult.get_choice_total()
        totalResult = model_to_dict(totalResult)
        # print(voteJson["total"])
        for key in voteJson["choiceList"]:
            voteJson["choiceList"][key] = {"name": voteJson["choiceList"][key]}
            voteJson["choiceList"][key]["count"] = totalResult["Choice_" + str(key)]
            voteJson["choiceList"][key]["percent"] = "{:.2f}".format(
                totalResult["Choice_" + str(key)] / voteJson["total"] * 100)

        # print(voteJson["choiceList"])
        body = loader.get_template('user/vote_result.html').render({"vote": voteJson, "userID": id["int"]}, request)
        return HttpResponse(head + body)

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
    # timestamp = int.from_bytes(vote_data[:8], byteorder="big")
    # user_id = int.from_bytes(vote_data[8:14], byteorder="big")
    # vote_id = int.from_bytes(vote_data[14:18], byteorder="big")
    # vote_result_int = int.from_bytes(vote_data[18:22], byteorder="big")
    # vote_result = bin(vote_result_int)[2:].zfill(32)
    vote_result = decompress_vote(vote_data)

    if vote_result["user_id"] != id["int"]:
        return HttpResponse("{\"success\": false, \"message\": \"User ID Error\"}",
                            content_type="application/json")
    # print(timestamp, user_id, vote_id, vote_result)
    # 检查投票是否存在
    try:
        vote = db.vote.objects.get(id=vote_result["vote_id"])
    except:
        return HttpResponse("{\"success\": false, \"message\": \"Vote Not Found\"}",
                            content_type="application/json")
    totalChoice = vote.vote_choice_set.all().count()
    # 后面是有效的投票结果，前面的0不计入
    validVoteResult = vote_result["vote_result"][32 - totalChoice:]
    # print(validVoteResult)
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
    dbResult = dbRaw.select(
        "SELECT * FROM vote_data_%d WHERE user_id = %d" % (vote_result["vote_id"], vote_result["user_id"]))
    if dbResult:
        return HttpResponse("{\"success\": false, \"message\": \"Vote Already\"}",
                            content_type="application/json")
    # 检查投票结果是否正确
    if vote_select < vote.min_choice or vote_select > vote.max_choice:
        return HttpResponse("{\"success\": false, \"message\": \"Vote Select Error\"}",
                            content_type="application/json")
    # 写入数据库
    keys = ["user_id", "timestamp", "vote_result", "signature"]
    values = [vote_result["user_id"], vote_result["timestamp"], vote_result["vote_result_int"], signature]
    dbRaw.insert("vote_data_%d" % vote_result["vote_id"], keys, values)

    return HttpResponse("{\"success\": true}", content_type="application/json")
