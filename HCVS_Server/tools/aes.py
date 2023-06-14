import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


# 加密函数
def encrypt_aes_256(plaintext, key=None):
    # 生成随机初始化向量
    if key is None:
        key = os.urandom(48)

    # 创建 AES 密钥对象
    cipher = Cipher(algorithms.AES(key[16:]), modes.CBC(key[:16]), backend=default_backend())
    encryptor = cipher.encryptor()

    # 执行加密
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    return key, ciphertext


# 解密函数
def decrypt_aes_256(key, ciphertext):
    # 创建 AES 密钥对象
    cipher = Cipher(algorithms.AES(key[16:]), modes.CBC(key[:16]), backend=default_backend())
    deCryptor = cipher.decryptor()

    # 执行解密
    plaintext = deCryptor.update(ciphertext) + deCryptor.finalize()

    # 返回解密结果
    return plaintext


