import hashlib

def zcs_dict2bytes(d):
    ret = b''
    for key, val in d.items():
        key_ = key.encode(encoding='utf-8')
        ret += len(key_).to_bytes(length=4, byteorder='big', signed=True)
        ret += key_
        if isinstance(val, str):
            ret += b's'
            val_ = val.encode(encoding='utf-8')
            ret += len(val_).to_bytes(length=4, byteorder='big', signed=True)
            ret += val_
        elif isinstance(val, int):
            ret += b'i'
            ret += val.to_bytes(length=4, byteorder='big', signed=True)
        elif isinstance(val, bytes):
            ret += b'b'
            ret += len(val).to_bytes(length=4, byteorder='big', signed=True)
            ret += val
        else:
            raise Exception('unknown value type %s' % (type(val)))
    return ret

def zcs_bytes2dict(b):
    ret = {}
    off = 0
    while off < len(b):
        key_len = int.from_bytes(b[off:off+4], byteorder='big', signed=True)
        off += 4
        key = b[off:off+key_len].decode(encoding='utf-8')
        off += key_len
        val_type = b[off:off+1] #这里如果直接使用b[off]，则val_type是int类型
        off += 1
        if val_type == b's':
            val_len = int.from_bytes(b[off:off+4], byteorder='big', signed=True)
            off += 4
            val = b[off:off+val_len].decode(encoding='utf-8')
            off += val_len
        elif val_type == b'i':
            val = int.from_bytes(b[off:off+4], byteorder='big', signed=True)
            off += 4
        elif val_type == b'b':
            val_len = int.from_bytes(b[off:off+4], byteorder='big', signed=True)
            off += 4
            val = b[off:off+val_len]
            off += val_len
        else:
            raise Exception('unknown value type %s' % (val_type))
        # print(key, end=':')
        # if isinstance(val, bytes):
        #     print(len(val))
        # else:
        #     print(val)
        assert key not in ret.keys()
        ret[key] = val
    return ret

def md5sum(file_path):
    h = hashlib.md5()
    with open(file_path, 'rb') as fp:
        for line in fp:
            h.update(line)
    md5 = h.hexdigest()
    return md5
