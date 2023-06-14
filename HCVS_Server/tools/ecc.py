from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature, decode_dss_signature
from cryptography.hazmat.primitives.serialization import load_der_public_key


class ECC:
    def __init__(self):
        self.public_key = None
        self.private_key = None

    def generate_key(self):
        # 生成 ECC 密钥对
        self.private_key = ec.generate_private_key(ec.SECP256R1())
        self.public_key = self.private_key.public_key()

    def test(self):
        print(self.private_key.private_numbers().private_value)
        print(self.public_key.public_numbers().x)
        print(self.public_key.public_numbers().y)

    def export_private_key_and_public_key_raw(self):
        return self.export_private_key_raw() + self.export_public_key_raw()

        # private_key_y = private_key_pkcs8[68:]

    def export_private_key_raw(self):

        return self.private_key.private_numbers().private_value.to_bytes(32, byteorder="big")

    def export_public_key_raw(self, split=False):
        if split:
            return self.public_key.public_numbers().x.to_bytes(32, byteorder="big"), \
                   self.public_key.public_numbers().y.to_bytes(32, byteorder="big")
        return self.public_key.public_numbers().x.to_bytes(32, byteorder="big") + \
               self.public_key.public_numbers().y.to_bytes(32, byteorder="big")

    def load_public_key_raw(self, publick_key_raw):
        public_key_x = int.from_bytes(publick_key_raw[:32], byteorder="big")
        public_key_y = int.from_bytes(publick_key_raw[32:], byteorder="big")
        self.public_key = ec.EllipticCurvePublicNumbers(public_key_x, public_key_y, ec.SECP256R1()).public_key(
            default_backend())

    def load_private_key_raw(self, private_key_raw):
        if len(private_key_raw) == 32:
            private_key = int.from_bytes(private_key_raw, byteorder="big")
            self.private_key = ec.derive_private_key(private_key, ec.SECP256R1(), default_backend())
            self.public_key = self.private_key.public_key()

    def load_private_key_der(self, private_key_pkcs8):
        self.private_key = serialization.load_der_private_key(
            private_key_pkcs8,
            password=None,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()

    def load_public_key_der(self, public_key_skpi):
        self.public_key = load_der_public_key(public_key_skpi, backend=default_backend())

    def sign(self, data):  # default signature format: IEEE P1363
        # 对数据进行签名
        signature = self.private_key.sign(
            data,
            ec.ECDSA(hashes.SHA256())
        )
        signature = self.sign_RFC3279_to_IEEEP1363(signature)
        return signature

    def sign_IEEEP1363_to_RFC3279(self, signature, curveBitSize=256):
        curveByteSize = curveBitSize // 8
        r = int.from_bytes(signature[:curveByteSize], byteorder="big")
        s = int.from_bytes(signature[curveByteSize:], byteorder="big")
        signature = encode_dss_signature(r, s)
        return signature

    def sign_RFC3279_to_IEEEP1363(self, signature, curveBitSize=256):
        curveByteSize = curveBitSize // 8
        r, s = decode_dss_signature(signature)
        signature = r.to_bytes(curveByteSize, byteorder="big") + s.to_bytes(curveByteSize, byteorder="big")
        return signature

    def verify(self, signature, data):  # default signature format: IEEE P1363
        # 转换签名格式
        signature = self.sign_IEEEP1363_to_RFC3279(signature)
        # 验证签名
        try:
            self.public_key.verify(
                signature,
                data,
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except InvalidSignature:
            return False
