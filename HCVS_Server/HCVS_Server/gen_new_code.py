import base64
from io import BytesIO

from django.http import HttpResponse

from HCVS_Server.settings import dbRaw
from tools import ecc, aes, myqrcode, otp
from tools.new_key import new_key


def gen_new_code(request):
    # 生成ecc密钥对
    ecc1 = ecc.ECC()
    ecc1.generate_key()
    x, y = ecc1.export_public_key_raw(True)
    d = ecc1.export_private_key_raw()
    # 生成一个AES密钥，并用其加密私钥
    aesKey, enData = aes.encrypt_aes_256(d)

    # 将公钥和aeskey存储到数据库，返回id
    key = ["public_key_x", "public_key_y", "private_key_code"]
    value = [x, y, aesKey]
    dbResult = dbRaw.insert("user_key", key, value)
    if not dbResult:
        return HttpResponse("Database error")
    id = dbResult[1]
    # 将id转换为4字节的bytes
    idBytes = id.to_bytes(4, byteorder="big")
    # 生成一个otp密钥，用于做二次验证时间密码
    otpKey, otpImage = otp.gen_code(name="Vote System", issuer=base64.b64encode(idBytes))
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
    image = myqrcode.gen_qrcode(data)
    # 保存图像到流
    image_stream = BytesIO()
    image.save(image_stream, format='PNG')
    image_stream.seek(0)
    return HttpResponse(image_stream.getvalue(), content_type='image/png')

