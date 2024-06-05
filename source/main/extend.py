import base64


def byteToString(byte):
    if byte:
        base64_string = base64.b64encode(byte).decode('utf-8')
        return str(base64_string)
    return None

def base64ToByte(base64data):
    if base64data:
        image = base64.b64decode(base64data)
        return image 
    return None