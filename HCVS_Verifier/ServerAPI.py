import os
import threading
import time

import requests

import config
import globalVar
import hash_chain
from public import thread_decorator


def getVoteList():
    URL = "https://hcvs.gtvps.com/verifier/getVoteList"
    response = requests.get(URL)
    # 遍历并存储到配置文件
    voteData = response.json()
    for vote in voteData["voteList"]:
        NodeName = "Vote_" + str(vote["id"])
        config.setConfig(NodeName, "id", vote["id"])
        config.setConfig(NodeName, "name", vote["name"])
        config.setConfig(NodeName, "start_time", vote["start_time"])
        config.setConfig(NodeName, "end_time", vote["end_time"])
        config.setConfig(NodeName, "min_choice", vote["min_choice"])
        config.setConfig(NodeName, "max_choice", vote["max_choice"])
        config.setConfig(NodeName, "chain_height", vote["chain_height"])
        config.setConfig(NodeName, "total_choice", len(vote["choiceList"]))
        for choice in vote["choiceList"]:
            config.setConfig(NodeName, "choice_"+str(choice["seq"]), choice["name"])

    if response.status_code == 200:
        return voteData
    else:
        return None


def getUserList(startId):
    URL = "https://hcvs.gtvps.com/verifier/getUserList"
    data = {"startId": startId}
    response = requests.get(URL, params=data)
    if response.status_code == 200:
        return response.content
    else:
        return None


def getVoteData(voteId, startTime):
    # https://hcvs.gtvps.com/verifier/getVoteData?voteId=18&startTime=0
    URL = "https://hcvs.gtvps.com/verifier/getVoteData"
    data = {"voteId": voteId, "startTime": startTime}
    response = requests.get(URL, params=data)
    if response.status_code == 200:
        return response.content
    else:
        return None


def syncGlobalTime():
    # 获取服务器时间
    URL = "https://hcvs.gtvps.com/verifier/getGlobalTime"
    response = requests.get(URL)
    if response.status_code == 200:
        globalVar.ServerTime = response.json()["ServerTime"]
        # print(globalVar.ServerTime)
    else:
        print("获取服务器时间失败")


@thread_decorator
def syncUserList(stop_flag, UI):
    # 从本地缓存中获取最大用户id
    configs = config.getConfig()
    DataPath = configs["Data"]["path"]
    if not os.path.exists(DataPath):
        os.makedirs(DataPath, exist_ok=True)
    UserFilePath = os.path.join(DataPath, "UserList.bin")
    globalVar.UserListBinLock.acquire()
    if not os.path.exists(UserFilePath):
        # 如果没有该文件，则创建该文件
        with open(UserFilePath, "wb") as f:
            f.write(b"")
            startId = 1
    else:
        # 如果有该文件，则根据文件大小计算startId，每个用户信息占用70字节
        startId = os.path.getsize(UserFilePath) // 70 + 1
    globalVar.UserListBinLock.release()
    # print(startId)

    while not stop_flag.is_set():
        # 获取用户列表
        # print(startId)
        userList = getUserList(startId)
        # print(userList.hex())
        if userList is None:
            print("获取用户列表失败")
            time.sleep(2)
            continue
        # 将用户列表写入文件
        # 前6字节为最大用户id，需要将其从二进制转换为整数
        maxUserID = int.from_bytes(userList[:6], byteorder="big")
        WriteCache = b""
        # 从第6字节开始，每70字节为一个用户信息
        for i in range(6, len(userList), 70):
            # 每个用户包含一个6字节的int，代表用户id，一个64字节的公钥。
            userID = int.from_bytes(userList[i:i + 6], byteorder="big")
            publicKey = userList[i + 6:i + 70]
            while startId < userID:
                # 如果用户id大于startId，则说明需要空用户补全
                WriteCache += b"\x00" * 70
                startId += 1
            # 如果用户id等于startId，则说明该用户应当直接被写入文件
            WriteCache += userList[i:i + 70]
            startId += 1

            # print(userID, publicKey)
        # 将WriteCache写入文件
        globalVar.UserListBinLock.acquire()
        with open(UserFilePath, "ab") as f:
            f.write(WriteCache)
        globalVar.UserListBinLock.release()
        UI.userSyncProgressLabel.setText(str(startId - 1) + "\\" + str(maxUserID))
        if maxUserID == startId - 1:
            # 如果最大用户id等于startId - 1，则说明用户列表已经同步完成
            # 可以休眠一段时间后再次同步
            time.sleep(10)
    print("Startup tasks done.")
    # 执行其他启动任务


@thread_decorator
def syncVoteData(stop_flag, UI, voteID):
    # 该函数用于同步投票原始数据，投票原始数据不能被轻易修改
    # 从本地缓存中获取最大投票timestamp
    configs = config.getConfig()
    VoteRawPath = os.path.join(configs["Data"]["path"], "VoteRaw")
    if not os.path.exists(VoteRawPath):
        os.makedirs(VoteRawPath, exist_ok=True)
    VoteFilePath = os.path.join(VoteRawPath, "%d.bin" % voteID)

    # 判断是否存在该投票文件的锁
    if voteID not in globalVar.VoteRawBinLock:
        # 如果不存在，则创建该锁
        globalVar.VoteRawBinLock[voteID] = threading.Lock()
    globalVar.VoteRawBinLock[voteID].acquire()
    if not os.path.exists(VoteFilePath):
        # 如果没有该文件，则创建该文件
        with open(VoteFilePath, "wb") as f:
            f.write(b"")
            startTimestamp = 0
    else:
        if os.path.getsize(VoteFilePath) == 0:
            # 如果文件大小为0，则说明没有投票数据
            startTimestamp = 0
        else:
            # 如果有该文件，则根据文件大小计算startTimestamp，每个投票信息占用86字节,取最后一个投票的timestamp
            # 每个投票包含时间戳，User_ID，Vote_ID，投票结果，实际签名
            # 8字节，6字节，4字节，4字节，64字节
            with open(VoteFilePath, "rb") as f:
                f.seek(-86, 2)
                startTimestamp = int.from_bytes(f.read(8), byteorder="big") + 1
    globalVar.VoteRawBinLock[voteID].release()
    # print(startTimestamp)
    while not stop_flag.is_set():
        # 获取投票数据
        # print(startTimestamp)
        voteData = getVoteData(voteID, startTimestamp)
        # print(voteData)
        # 直接将投票数据写入文件
        if voteData != b"":
            globalVar.VoteRawBinLock[voteID].acquire()
            with open(VoteFilePath, "ab") as f:
                f.write(voteData)
            globalVar.VoteRawBinLock[voteID].release()
            startTimestamp = int.from_bytes(voteData[-86:-78], byteorder="big") + 1
        else:
            # 数据同步完成，准许计算区块
            # 先同步ServerTime
            syncGlobalTime()
            # 计算区块
            hash_chain.calcVote(voteID, UI)
            # 如果没有投票数据，则休眠一段时间后再次尝试
            time.sleep(10)
