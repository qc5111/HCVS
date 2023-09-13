#生成一个rsa对秘钥，导出pem格式的私钥到字符串并生成二维码
import rsa
import base64
import qrcode
import os
import sys
import time
import hashlib

from HCVS_Server.tools import myqrcode


def gen_rsa_key():
    (pubkey, privkey) = rsa.newkeys(3072)
    pub = pubkey.save_pkcs1()
    pri = privkey.save_pkcs1()
    return pub, pri

pub, pri = gen_rsa_key()
print(pri)
img = myqrcode.gen_qrcode(pri)
img.save('rsa_pri.png')

