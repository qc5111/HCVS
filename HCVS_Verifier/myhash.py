import hashlib
import json
from operator import itemgetter


def format_data(data):
    if type(data) == str:
        data = data.encode('utf-8')
    elif type(data) == list:
        # 对数据排序
        data = sorted(data, key=itemgetter('index'))
        # 将数据转换为字符串
        data = json.dumps(data, separators=(',', ':')).encode('utf-8')
    elif type(data) == dict:
        # 将数据转换为字符串
        data = json.dumps(data, separators=(',', ':')).encode('utf-8')
    return data


def md5(data, format='bin'):
    data = format_data(data)
    md5_hash = hashlib.md5()
    md5_hash.update(data)
    if format == 'hex':
        return md5_hash.hexdigest()
    else:
        return md5_hash.digest()


def sha1(data, format='bin'):
    data = format_data(data)
    sha1_hash = hashlib.sha1()
    sha1_hash.update(data)
    if format == 'hex':
        return sha1_hash.hexdigest()
    else:
        return sha1_hash.digest()
