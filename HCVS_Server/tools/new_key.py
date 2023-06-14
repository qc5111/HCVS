from HCVS_Server.settings import dbRaw
from tools import ecc
print(2)

def new_key():
    # 生成ecc密钥对
    ecc1 = ecc.ECC()
    ecc1.generate_key()
    # 生成密钥对
    x, y = ecc1.export_public_key_raw(True)
    d = ecc1.export_private_key_raw()
    # 生成一个AES密钥

    # 将公钥存储到数据库
    key = ["public_key_x", "public_key_y"]
    value = [x, y]
    dbResult = dbRaw.insert("user_key", key, value)
    if dbResult:
        return dbResult[1]

    
