import qrcode


def gen_qrcode(data):
    if type(data) == str:
        data = data.encode('utf-8')

    # 创建QRCode对象
    qr = qrcode.QRCode(
        version=1,  # QR码的版本（1到40）
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # 容错级别
        box_size=10,  # 每个点的像素大小
        border=4,  # 边框的像素大小
    )

    qr.add_data(data)
    qr.make(fit=True)

    # 获取图像
    image = qr.make_image(fill_color="black", back_color="white")
    return image


