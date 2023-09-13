# 软件测试
# post请求和get请求的方法
import requests


def send_request(way, url, cookies=None, data=None, headers=None):
    if way == 'post':
        res = requests.post(url=url, data=data, headers=headers, cookies=cookies)
    elif way == 'get':
        res = requests.get(url=url, params=data, headers=headers, cookies=cookies)
    else:
        print('请求方式错误')
        res = None
    # 返回响应结果
    return res.text
