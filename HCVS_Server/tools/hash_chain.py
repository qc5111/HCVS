# md5
import time

from django.db.models import F

import db.models as db
from HCVS_Server.settings import dbRaw
from tools.calc_vote import compress_vote
from tools.myhash import md5, sha1


def calcVote(vote, timestamp):
    end_ts = timestamp * 1000 - 300000
    # 获取投票选项总数
    totalChoice = vote.vote_choice_set.all().count()
    # 从第一个需要计算的区块开始计算
    dbResult = dbRaw.select("SELECT MAX(height) FROM vote_chain_%d" % vote.id)
    if dbResult[0]["MAX(height)"] is None:
        height = 0
    else:
        height = dbResult[0]["MAX(height)"] + 1
    start_ts = vote.start_time + (height-1) * 600000

    while True:
        total_vote_result = [0] * 32
        block_data = b""
        # print(start_ts, end_ts)
        # print(start_ts - end_ts)
        if start_ts + 600000 > end_ts or start_ts + 600000 > vote.end_time:
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



def writeChain(vote_id, data, start_ts, end_ts):
    dbResult = dbRaw.select("SELECT MAX(height) FROM vote_chain_%d" % vote_id)
    if dbResult[0]["MAX(height)"] is None:
        height = 0
    else:
        height = dbResult[0]["MAX(height)"] + 1
    blockData = b""
    if height != 0:
        # 获取上一个区块的hash
        dbResult = dbRaw.select("SELECT * FROM vote_chain_%d WHERE height = %d" % (vote_id, height - 1))
        blockData += dbResult[0]["md5"]
        blockData += dbResult[0]["sha1"]
    # 计算区块hash
    blockData += data
    his_md5 = md5(blockData)
    his_sha1 = sha1(blockData)
    now_md5 = md5(data)
    now_sha1 = sha1(data)
    # 写入区块

    key = ["height", "startTime", "endTime", "chain_time", "this_md5", "this_sha1", "md5", "sha1"]
    value = [height, start_ts, end_ts, int(time.time() * 1000), now_md5, now_sha1, his_md5, his_sha1]
    dbRaw.insert("vote_chain_%d" % vote_id, key, value)
    # 更新投票表区块高度
    db.vote.objects.filter(id=vote_id).update(chain_height=height)


def calcVotes(timestamp):
    # 10分钟一个区块
    min_ts = timestamp * 1000 - 900000
    max_ts = timestamp * 1000 - 300000
    # start_time__lte=max_ts
    # print(F('end_time'))
    votes = db.vote.objects.exclude(chain_height=(F('end_time') - F('start_time')) / 600000)
    for vote in votes:
        # 筛选出未计算的投票
        should_chain_height = (max_ts - vote.start_time) / 600000 + 1
        max_chain_height = (vote.end_time - vote.start_time) / 600000
        if should_chain_height > max_chain_height:
            should_chain_height = max_chain_height
        # print(should_chain_height, vote.chain_height)
        # print(should_chain_height, vote.chain_height)
        if should_chain_height > vote.chain_height:
            # print("vote: %s" % vote.name)
            # print(should_chain_height - vote.chain_height)

            calcVote(vote, timestamp)


def scheduled_task():
    last_job_time = 0
    while True:
        nowTime = int(time.time())
        if int(nowTime) % 300 == 0 and int(nowTime) % 600 != 0 and nowTime != last_job_time:
            last_job_time = nowTime
            calcVotes(nowTime)
        time.sleep(0.5)
        # print("等待！%d" % nowTime)
