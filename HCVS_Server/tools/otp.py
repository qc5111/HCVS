import base64

import pyotp
from tools import myqrcode


def gen_code(name, issuer="Vote System"):
    secret_key = pyotp.random_base32()
    print(secret_key)

    totp_auth = pyotp.totp.TOTP(
        secret_key).provisioning_uri(
        name=name,
        issuer_name=issuer)
    secret_key = base64.b32decode(secret_key)

    return secret_key, myqrcode.gen_qrcode(totp_auth)
