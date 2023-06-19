import base64


def pad_base64(base64_string):
    padding_length = (4 - len(base64_string) % 4) % 4
    padded_string = base64_string + "=" * padding_length
    return padded_string


def b64decode(base64_string):
    padded_string = pad_base64(base64_string)
    return base64.b64decode(padded_string)
