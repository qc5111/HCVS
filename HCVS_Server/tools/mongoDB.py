import time

from pymongo import MongoClient

from tools import myhash


def test():
    # 连接到MongoDB服务器
    client = MongoClient('mongodb://localhost:27017')

    # 选择数据库
    db = client['hcvs_server']

    # 选择集合
    collection = db['chain_1']

    # 要插入的数据
    chainData = [

        {
            'index': 1,
            'timestamp': 1234567890,
            "user": "0x1234567890abcdef",
            "action": "Hello, World!",
            "sign": "0x1234567890abcdef",
            "hash": "0x1234567890abcdef",
        },
        {
            'index': 2,
            'timestamp': 1234567890,
            "user": "0x1234567890abcdef",
            "action": "Hello, World!",
            "sign": "0x1234567890abcdef",
            "hash": "0x1234567890abcdef",
        },

    ]
    print(myhash.md5(chainData, 'hex'))
    data = {
        'seq': 1,
        'data': chainData,
        'starttime': int(time.time() * 1000),
        'endtime': int(time.time() * 1000),
        "this_hash_md5": myhash.md5(chainData),
        "this_hash_sha1": myhash.sha1(chainData),
        "hash_md5": myhash.md5(chainData),
        "hash_sha1": myhash.sha1(chainData),
    }

    # 在集合中插入数据
    result = collection.insert_one(data)

    # 打印插入的数据ID
    print('插入的数据ID:', result.inserted_id)

    # 关闭连接
    client.close()


class Mongo:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017')
        self.db = self.client['hcvs_server']

    def createChain(self, headData):
        data = {
            '_id': 0,
            'data': headData,
            'starttime': int(time.time() * 1000),
            'endtime': int(time.time() * 1000),
            "this_hash_md5": myhash.md5(headData),
            "this_hash_sha1": myhash.sha1(headData),
            "hash_md5": myhash.md5(headData),
            "hash_sha1": myhash.sha1(headData),
        }
        # 随机生成一个
        collectionName = "chain_" + myhash.md5(headData, 'hex')
        # 选择集合
        collection = self.db[collectionName]
        # collection.create_index([('seq', 1)], unique=True)

        collection.insert_one(data)

        return collectionName

    def getChain(self, collectionName, seq=0, limit=1000):
        collection = self.db[collectionName]
        dbResult = collection.find({'_id': {
            '$gte': seq,
            '$lt': seq + limit
        }})
        return list(dbResult)


Mongo1 = Mongo()
collectionName = Mongo1.createChain({"test": "test", "time": int(time.time() * 1000)})
dbResult = Mongo1.getChain(collectionName)
print(dbResult)