import os
import threading

import config
import ecc
import globalVar


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
        f.seek((User_ID-1) * 70)
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
def calcVote(voteID):
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
            f.write(b"")
            endPos = 0
    else:
        # 如果有则读取头部信息，8个字节当前计算截止的VoteRaw的文件位置
        with open(VoteChainFilePath, "rb") as f:
            f.seek(0)
            endPos = int.from_bytes(f.read(8), byteorder="big")

    if not os.path.exists(VoteResultFilePath):
        # 如果没有该文件，则创建该文件
        with open(VoteResultFilePath, "wb") as f:
            f.write(b"0" * 8 * 32)  # 32个投票选项，每个8个字节int64
    # 读取投票选项
    with open(VoteResultFilePath, "rb") as f:
        f.seek(0)
        voteResult = f.read(8 * 32)
        # 转换为32个int64数组
        voteResult = [int.from_bytes(voteResult[i * 8:(i + 1) * 8], byteorder="big") for i in range(32)]
    # 此处根据全局ServerTime来计算需要计算的区块最高高度
    configs = config.getConfig()
    print(globalVar.ServerTime)

    maxCalcHeight = (min(globalVar.ServerTime - 300000, int(configs["Vote_" + str(voteID)]["end_time"])) - int(
        configs["Vote_" + str(voteID)]["start_time"])) // 600000
    print(maxCalcHeight)

    # 从第一个需要计算的区块开始计算
    dbResult = dbRaw.select("SELECT MAX(height) FROM vote_chain_%d" % vote.id)
    if dbResult[0]["MAX(height)"] is None:
        height = 0
    else:
        height = dbResult[0]["MAX(height)"] + 1
    start_ts = vote.start_time + (height - 1) * 600000

    while True:
        total_vote_result = [0] * 32
        block_data = b""
        # print(start_ts, end_ts)
        # print(start_ts - end_ts)
        if start_ts > end_ts or start_ts >= vote.end_time:
            break
        # 获取区块数据
        dbResult = dbRaw.select(
            "SELECT * FROM vote_data_%d WHERE timestamp >= %d AND timestamp < %d ORDER BY timestamp ASC, signature ASC" % (
                vote.id, start_ts, start_ts + 600000))
        # print(dbResult)
        for vote_data in dbResult:
            # 计算投票结果
            vote_result_int = vote_data["vote_result"]
            # print(vote_result_int)
            vote_result_str = bin(vote_result_int)[2:].zfill(32)
            # 后面是有效的投票结果，前面的0不计入
            vote_result_str = vote_result_str[32 - totalChoice:]
            # 反转字符串
            vote_result_str = vote_result_str[::-1]
            for i in range(len(vote_result_str)):
                if vote_result_str[i] == "1":
                    total_vote_result[i] += 1
            vote_result_dict = {
                "vote_id": vote.id,
                "timestamp": vote_data["timestamp"],
                "user_id": vote_data["user_id"],
                "vote_result": vote_result_int,
            }
            # 每个签名：
            # 时间戳，User_ID，Vote_ID，投票结果，实际签名
            # 8字节，6字节，4字节，4字节，64字节
            # 固定86字节

            block_data += compress_vote(vote_result_dict)
            block_data += vote_data["signature"]
        # 写入区块
        writeChain(vote.id, block_data, start_ts, start_ts + 600000 - 1)
        # 更新投票结果
        # print(total_vote_result)
        db.vote_result.objects.filter(vote_id=vote.id)[0].add_choice(total_vote_result)
        # 更新区块高度
        db.vote.objects.filter(id=vote.id).update(chain_height=height)
        height += 1
        # 增加start_ts
        start_ts += 600000
