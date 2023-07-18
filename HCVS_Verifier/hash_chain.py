import base64
import os
import threading
import time

from PyQt5.QtWidgets import QTableWidgetItem

import config
import ecc
import globalVar
from myhash import md5, sha1
from PyQt5 import QtWidgets


def verifyVote(Data):  # 传入一个Raw数据，86字节
    # 每个投票包含时间戳，User_ID，Vote_ID，投票结果，实际签名
    # 8字节，6字节，4字节，4字节，64字节
    # 根据User_ID在UserList中查找公钥
    configs = config.getConfig()
    DataPath = configs["Data"]["path"]
    if not os.path.exists(DataPath):
        os.makedirs(DataPath, exist_ok=True)
    UserFilePath = os.path.join(DataPath, "UserList.bin")
    User_ID = int.from_bytes(Data[8:14], byteorder="big")
    globalVar.UserListBinLock.acquire()
    with open(UserFilePath, "rb") as f:
        # 每个用户占用70字节，前6字节为用户id，后64字节为公钥
        # 根据用户id计算用户在文件中的位置
        f.seek((User_ID - 1) * 70)
        # 读取用户信息
        User = f.read(70)
    globalVar.UserListBinLock.release()
    # 对比用户id是否相同
    if User_ID != int.from_bytes(User[:6], byteorder="big"):
        # 如果不同，则说明用户不存在
        return False
    # 如果相同，则说明用户存在，获取用户公钥
    publicKey = User[6:]
    # 根据公钥验证签名
    ecc1 = ecc.ECC()
    ecc1.load_public_key_raw(publicKey)
    # 总共86字节，前22字节为投票信息，后64字节为签名
    return ecc1.verify(Data[22:], Data[:22])


# 文件格式
# 8个字节当前计算截止的VoteRaw的文件位置
# 每个区块：this_md5(16字节) + this_sha1(20字节) + md5(16字节) + sha1(20字节)
# 每个区块72字节
def calcVote(voteID, UI):
    # 处理原始文件和结果文件
    configs = config.getConfig()
    VoteRawPath = os.path.join(configs["Data"]["path"], "VoteRaw")
    VoteChainPath = os.path.join(configs["Data"]["path"], "VoteChain")
    VoteResultPath = os.path.join(configs["Data"]["path"], "VoteResult")
    if not os.path.exists(VoteRawPath):
        os.makedirs(VoteRawPath, exist_ok=True)
    if not os.path.exists(VoteChainPath):
        os.makedirs(VoteChainPath, exist_ok=True)
    if not os.path.exists(VoteResultPath):
        os.makedirs(VoteResultPath, exist_ok=True)
    VoteFilePath = os.path.join(VoteRawPath, "%d.bin" % voteID)
    VoteChainFilePath = os.path.join(VoteChainPath, "%d.bin" % voteID)
    VoteResultFilePath = os.path.join(VoteResultPath, "%d.bin" % voteID)
    # 只有原始文件需要锁
    if voteID not in globalVar.VoteRawBinLock:
        # 如果不存在，则创建该锁
        globalVar.VoteRawBinLock[voteID] = threading.Lock()
    globalVar.VoteRawBinLock[voteID].acquire()
    if not os.path.exists(VoteFilePath):
        # 如果没有该文件，则创建该文件
        with open(VoteFilePath, "wb") as f:
            f.write(b"")
    globalVar.VoteRawBinLock[voteID].release()
    if not os.path.exists(VoteChainFilePath):
        # 如果没有该文件，则创建该文件
        with open(VoteChainFilePath, "wb") as f:
            # print(VoteChainFilePath)
            f.write(b"\x00" * 8)  # 8个字节当前计算截止的VoteRaw的文件位置
            endPos = 0
        # 写入0号区块
        # 0号区块数据
        blockData = b"\x00"  # 版本
        blockData += len(configs["Vote_" + str(voteID)]["name"]).to_bytes(1, byteorder="big") + \
                     configs["Vote_" + str(voteID)]["name"].encode()  # 投票名称长度 + 投票名称
        blockData += b"\x08" + int(configs["Vote_" + str(voteID)]["start_time"]).to_bytes(8,
                                                                                          byteorder="big")  # 开始时间长度 + 开始时间
        blockData += b"\x08" + int(configs["Vote_" + str(voteID)]["end_time"]).to_bytes(8,
                                                                                        byteorder="big")  # 结束时间长度 + 结束时间
        blockData += b"\x01" + int(configs["Vote_" + str(voteID)]["min_choice"]).to_bytes(1,
                                                                                          byteorder="big")  # 最小选择长度 + 最小选择
        blockData += b"\x01" + int(configs["Vote_" + str(voteID)]["max_choice"]).to_bytes(1,
                                                                                          byteorder="big")  # 最大选择长度 + 最大选择
        seq = 1
        while True:
            vote_seq = "choice_" + str(seq)
            if vote_seq not in configs["Vote_" + str(voteID)]:
                break
            blockData += len(configs["Vote_" + str(voteID)][vote_seq]).to_bytes(1, byteorder="big") + \
                         configs["Vote_" + str(voteID)][vote_seq].encode()  # 选项长度 + 选项
            seq += 1
        writeChain(voteID, blockData)
    else:
        # 如果有则读取头部信息，8个字节当前计算截止的VoteRaw的文件位置
        with open(VoteChainFilePath, "rb") as f:
            f.seek(0)
            endPos = int.from_bytes(f.read(8), byteorder="big")

    if not os.path.exists(VoteResultFilePath):
        # 如果没有该文件，则创建该文件
        with open(VoteResultFilePath, "wb") as f:
            f.write(b"\x00" * 8 * 32)  # 32个投票选项，每个8个字节int64

    # 读取投票选项
    with open(VoteResultFilePath, "rb") as f:
        f.seek(0)
        voteResult = f.read(8 * 32)
        # 转换为32个int64数组
        total_vote_result = [int.from_bytes(voteResult[i * 8:(i + 1) * 8], byteorder="big") for i in range(32)]
    # 此处根据全局ServerTime来计算需要计算的区块最高高度

    # 等待ServerTime更新
    while globalVar.ServerTime == 0:
        time.sleep(0.1)
    # print(globalVar.ServerTime)

    maxCalcHeight = (min(globalVar.ServerTime - 300000, int(configs["Vote_" + str(voteID)]["end_time"])) - int(
        configs["Vote_" + str(voteID)]["start_time"])) // 600000
    # print(maxCalcHeight)
    # 根据VoteChainFile的大小计算当前计算的区块高度
    # 计算VoteChainFile的大小
    # 从第一个需要计算的区块开始计算
    NowHeight = (os.path.getsize(VoteChainFilePath) - 8) // 72

    while True:
        # 判断是否需要计算
        if NowHeight > maxCalcHeight:
            break
        block_data = b""
        # 获取区块数据
        globalVar.VoteRawBinLock[voteID].acquire()
        with open(VoteFilePath, "rb") as f:
            f.seek(endPos)
            while True:  # 此循环每次读取一整个区块需要的数据
                # 计算当前区块的最大时间戳
                maxTS = int(configs["Vote_" + str(voteID)]["start_time"]) + NowHeight * 600000 - 1
                # print(NowHeight, maxTS)
                this_block_data = f.read(86)
                if len(this_block_data) != 86:
                    break
                # 读取该投票的时间戳
                timestamp = int.from_bytes(this_block_data[0:8], byteorder="big")
                # 如果该区块的时间戳大于当前计算的最大时间戳，则跳出循环

                if timestamp > maxTS:
                    break
                # 验证投票
                verifyVote(this_block_data)
                # 统计投票结果
                # 每个投票包含时间戳，User_ID，Vote_ID，投票结果，实际签名
                # 8字节，6字节，4字节，4字节，64字节
                vote_result_int = int.from_bytes(this_block_data[18:22], byteorder="big")
                vote_result_str = bin(vote_result_int)[2:].zfill(32)
                # 后面是有效的投票结果，前面的0不计入
                vote_result_str = vote_result_str[32 - int(configs["Vote_" + str(voteID)]["total_choice"]):]
                # 反转字符串
                vote_result_str = vote_result_str[::-1]
                for i in range(len(vote_result_str)):
                    if vote_result_str[i] == "1":
                        total_vote_result[i] += 1
                # 加入区块数据
                block_data += this_block_data
                endPos += 86
        # 区块数据读取完毕，写入VoteChainFile
        # print(block_data)
        # print(len(block_data))
        nowHash = writeChain(voteID, block_data)
        # 调试
        # if NowHeight >= 1:
        #   exit(0)
        globalVar.VoteRawBinLock[voteID].release()
        # 写入VoteResultFile
        with open(VoteResultFilePath, "wb") as f:
            for i in range(32):
                f.write(total_vote_result[i].to_bytes(8, byteorder="big"))
        # 写入VoteChainFile的最新位置
        with open(VoteChainFilePath, "r+b") as f:
            # 修改头上的8个字节
            f.seek(0)
            f.write(endPos.to_bytes(8, byteorder="big"))
        # 匹配对应的UI组件并更新区块高度
        UI.tableWidget.setItem(globalVar.VoteID2RowID[voteID], 7, QTableWidgetItem(str(NowHeight)))
        # print(nowHash)
        UI.tableWidget.setItem(globalVar.VoteID2RowID[voteID], 8, QtWidgets.QTableWidgetItem(nowHash))
        # 刷新显示
        UI.tableWidget.viewport().update()
        NowHeight += 1


def writeChain(voteID, data):
    configs = config.getConfig()
    VoteChainPath = os.path.join(configs["Data"]["path"], "VoteChain")
    VoteChainFilePath = os.path.join(VoteChainPath, "%d.bin" % voteID)
    # 根据文件长度计算应当计算的区块高度
    height = (os.path.getsize(VoteChainFilePath) - 8) // 72
    blockData = b""
    if height != 0:
        # 获取上一个区块的hash
        # 每个区块：this_md5(16字节) + this_sha1(20字节) + md5(16字节) + sha1(20字节)
        with open(VoteChainFilePath, "rb") as f:
            # 读取上一个区块的数据,定位到文件的最后36个字节，md5(16字节) + sha1(20字节)
            f.seek(-36, 2)
            blockData = f.read(36)

    # 计算区块hash
    blockData += data
    his_md5 = md5(blockData)
    his_sha1 = sha1(blockData)
    now_md5 = md5(data)
    now_sha1 = sha1(data)
    # 写入区块
    with open(VoteChainFilePath, "ab") as f:
        # 每个区块：this_md5(16字节) + this_sha1(20字节) + md5(16字节) + sha1(20字节)
        # print(len(now_md5+now_sha1+his_md5+his_sha1))
        # print(now_md5.hex(), now_sha1.hex(), his_md5.hex(), his_sha1.hex())
        f.write(now_md5+now_sha1+his_md5+his_sha1)
    return base64.b64encode(his_md5+his_sha1).decode("utf-8")

