import base64
import json
import time

from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader

from HCVS_Server.admin.authorization import AuthorizationCheck
from HCVS_Server.urls import ChainBuilderThread
from tools import gen_new_code, mybase64
from HCVS_Server.settings import dbRaw
import db.models as db
from tools.calc_vote import compress_vote
from tools.hash_chain import writeChain


def getVoteList(request):
    retunData = {}
    retunData["ServerTime"] = int(time.time() * 1000)  # 服务器毫秒级时间戳
    if ChainBuilderThread.is_alive():
        retunData["ChainBuilderStatus"] = True  # 链构建器状态
    else:
        retunData["ChainBuilderStatus"] = False  # 链构建器状态
    retunData["voteList"] = []
    voteList = db.vote.objects.all().order_by("-id")
    for voteItem in voteList:
        voteItemDict = {}
        voteItemDict["id"] = voteItem.id
        voteItemDict["name"] = voteItem.name
        voteItemDict["start_time"] = voteItem.start_time
        voteItemDict["end_time"] = voteItem.end_time
        voteItemDict["min_choice"] = voteItem.min_choice
        voteItemDict["max_choice"] = voteItem.max_choice
        voteItemDict["chain_height"] = voteItem.chain_height
        # 添加选项列表
        voteItemDict["choiceList"] = []
        optionList = db.vote_choice.objects.filter(vote=voteItem).order_by("seq")
        for optionItem in optionList:
            optionItemDict = {}
            optionItemDict["seq"] = optionItem.seq
            optionItemDict["name"] = optionItem.name
            voteItemDict["choiceList"].append(optionItemDict)
        retunData["voteList"].append(voteItemDict)

    return HttpResponse(json.dumps(retunData, ensure_ascii=False), content_type="application/json")


def getGlobalTime(request):
    retunData = {"ServerTime": int(time.time() * 1000)}
    return HttpResponse(json.dumps(retunData, ensure_ascii=False), content_type="application/json")


def getUserList(request):
    # 返回二进制数据
    returnData = b""
    # 从请求中获取起始用户id
    startId = int(request.GET.get("startId"))
    # Max Page Size 256MB
    maxPageSize = 256 * 1024 * 1024
    # maxPageSize = 70 # 测试用
    # 每个用户的数据长度
    # 每个用户包含一个6字节的int，代表用户id，一个64字节的公钥。
    userLength = 6 + 64
    # 计算最大返回用户数量
    maxUserCount = maxPageSize // userLength
    # 读取User_id的max值
    maxUserId = dbRaw.select("SELECT MAX(id) FROM user_key")[0]["MAX(id)"]
    # 添加最大用户id
    returnData += maxUserId.to_bytes(6, byteorder="big")
    # 从数据库中获取用户数据
    userList = dbRaw.select("SELECT id, public_key_x,public_key_y FROM user_key WHERE id >= %d ORDER BY id LIMIT %d" % (
        startId, maxUserCount))
    # 遍历用户数据，并加入returnData
    for userItem in userList:
        returnData += userItem["id"].to_bytes(6, byteorder="big")
        returnData += userItem["public_key_x"]
        returnData += userItem["public_key_y"]
    # print(returnData)
    return HttpResponse(returnData, content_type="application/octet-stream")


def getVoteData(request):
    # 返回二进制数据
    returnData = b""
    # Max Page Size 256MB
    maxPageSize = 256 * 1024 * 1024
    # 每个投票包含时间戳，User_ID，Vote_ID，投票结果，实际签名
    # 8字节，6字节，4字节，4字节，64字节
    voteDataLength = 8 + 6 + 4 + 4 + 64
    # 计算最大返回用户数量
    maxVoteDatCount = maxPageSize // voteDataLength
    voteID = int(request.GET.get("voteId"))
    startTime = int(request.GET.get("startTime"))
    # 从数据库中获取用户数据
    SQL = "SELECT * FROM vote_data_%d WHERE timestamp >= %d ORDER BY timestamp ASC, signature ASC LIMIT %d" % (
        voteID, startTime, voteDataLength)
    dbResult = dbRaw.select(SQL)
    # 如果返回的数据大小和最大数据大小相同，则说明需要根据最后一个timestamp舍弃对应的全部数据
    maxTimeStamp = 0
    if len(dbResult) == maxVoteDatCount:
        maxTimeStamp = dbResult[-1]["timestamp"]

    # print(SQL)
    # print("getVoteData", dbResult)
    for vote_data in dbResult:
        if vote_data["timestamp"] == maxTimeStamp:  # 如果时间戳和最大时间戳相同，则跳过
            break  # 由于排序，后面的数据也不可能满足条件，直接跳出循环
        vote_result_dict = {
            "vote_id": voteID,
            "timestamp": vote_data["timestamp"],
            "user_id": vote_data["user_id"],
            "vote_result": vote_data["vote_result"],
        }
        returnData += compress_vote(vote_result_dict)
        returnData += vote_data["signature"]
    return HttpResponse(returnData, content_type="application/octet-stream")
