import base64
from io import BytesIO

from django.http import HttpResponse

from HCVS_Server.settings import dbRaw
from tools import ecc, aes, myqrcode, otp


def gen_new_code():  # 最好为3的倍数
    # 生成ecc密钥对
    ecc1 = ecc.ECC()
    ecc1.generate_key()
    x, y = ecc1.export_public_key_raw(True)
    d = ecc1.export_private_key_raw()
    # 生成一个AES密钥，并用其加密私钥
    aesKey, enData = aes.encrypt_aes_256(d)  # enData为加密后的私钥，长度固定为32位

    # 将公钥和aeskey存储到数据库，返回id
    key = ["public_key_x", "public_key_y", "private_key_code"]
    value = [x, y, aesKey]
    dbResult = dbRaw.insert("user_key", key, value)
    if not dbResult:
        return HttpResponse("Database error")
    id = dbResult[1]
    # 将id转换为4字节的bytes
    idBytes = id.to_bytes(6, byteorder="big")  # 为了容量足够大，id取4字节太少，8字节生成base64时会多4个字符，所以取6字节，容量足够
    idStr = base64.b64encode(idBytes).replace(b"=", b"").decode()
    # 生成一个otp密钥，用于做二次验证时间密码
    otpKey, image_otp = otp.gen_code(name=idStr)
    # 将otp密钥存储到数据库
    updateValue = {"id": id, "otp_key": otpKey}
    dbRaw.update("user_key", [updateValue], "id")

    # 将id和加密后的私钥拼接
    data = idBytes + enData
    # 将数据转换为base64
    data = base64.b64encode(data)
    # print(data)
    # print(len(data))
    # 生成二维码
    image_private_key = myqrcode.gen_qrcode(data)
    # 打印图片的二进制数据

    # 保存图像到流
    image_private_key_stream = BytesIO()
    image_private_key.save(image_private_key_stream, format='PNG')
    image_private_key_stream.seek(0)

    image_otp_stream = BytesIO()
    image_otp.save(image_otp_stream, format='PNG')
    image_otp_stream.seek(0)
    # 返回base64编码的图片
    return idStr, base64.b64encode(image_private_key_stream.read()).decode(), base64.b64encode(image_otp_stream.read()).decode()
    # 返回图像
    # return HttpResponse(image_stream.getvalue(), content_type='image/png')
