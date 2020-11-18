class ZcsEncoder:
    def __call__(self, obj):
        if obj is None:
            return b''
        return self.obj2bytes(obj)

    def obj2bytes(self, obj):
        ret = b''
        if isinstance(obj, str):
            ret += self.str2bytes(obj)
        elif isinstance(obj, int):
            ret += self.int2bytes(obj)
        elif isinstance(obj, bytes):
            ret += self.bytes2bytes(obj)
        elif isinstance(obj, tuple):
            ret += self.tuple2bytes(obj)
        elif isinstance(obj, list):
            ret += self.list2bytes(obj)
        elif isinstance(obj, dict):
            ret += self.dict2bytes(obj)
        else:
            raise Exception('unknown value type %s' % (type(obj)))
        return ret

    def str2bytes(self, s):
        ret = b's'
        s_ = s.encode(encoding='utf-8')
        ret += len(s_).to_bytes(length=4, byteorder='big', signed=True)
        ret += s_
        return ret

    def int2bytes(self, i):
        ret = b'i'
        ret += i.to_bytes(length=4, byteorder='big', signed=True)
        return ret

    def bytes2bytes(self, b):
        ret = b'b'
        ret += len(b).to_bytes(length=4, byteorder='big', signed=True)
        ret += b
        return ret

    def tuple2bytes(self, t):
        ret = b't'
        ret += len(t).to_bytes(length=4, byteorder='big', signed=True)
        for item in t:
            ret += self.obj2bytes(item)
        return ret

    def list2bytes(self, l):
        ret = b'l'
        ret += len(l).to_bytes(length=4, byteorder='big', signed=True)
        for item in l:
            ret += self.obj2bytes(item)
        return ret

    def dict2bytes(self, d):
        ret = b'd'
        ret += len(d).to_bytes(length=4, byteorder='big', signed=True)
        for key, val in d.items():
            ret += self.obj2bytes(key)
            ret += self.obj2bytes(val)
        return ret

class ZcsDecoder:
    def __call__(self, b):
        self.b = b
        return self.bytes2obj()

    def bytes2obj(self):
        val_type = self.b[0:1] #这里如果直接使用b[off]，则val_type是int类型
        self.b = self.b[1:]
        if val_type == b's':
            return self.bytes2str()
        if val_type == b'i':
            return self.bytes2int()
        if val_type == b'b':
            return self.bytes2bytes()
        if val_type == b't':
            return self.bytes2tuple()
        if val_type == b'l':
            return self.bytes2list()
        if val_type == b'd':
            return self.bytes2dict()
        raise Exception('unknown value type {}'.format(val_type))

    def bytes2str(self):
        str_len = int.from_bytes(self.b[0:4], byteorder='big', signed=True)
        s = self.b[4:4+str_len].decode(encoding='utf-8')
        self.b = self.b[4+str_len:]
        return s

    def bytes2int(self):
        i = int.from_bytes(self.b[0:4], byteorder='big', signed=True)
        self.b = self.b[4:]
        return i

    def bytes2bytes(self):
        bytes_len = int.from_bytes(self.b[0:4], byteorder='big', signed=True)
        b = self.b[4:4+bytes_len]
        self.b = self.b[4+bytes_len:]
        return b

    def bytes2tuple(self):
        ret = []
        tuple_len = int.from_bytes(self.b[0:4], byteorder='big', signed=True)
        self.b = self.b[4:]
        for i in range(tuple_len):
            val = self.bytes2obj()
            # print(key, val)
            ret.append(val)
        return tuple(ret)

    def bytes2list(self):
        ret = []
        list_len = int.from_bytes(self.b[0:4], byteorder='big', signed=True)
        self.b = self.b[4:]
        for i in range(list_len):
            val = self.bytes2obj()
            # print(key, val)
            ret.append(val)
        return ret

    def bytes2dict(self):
        ret = {}
        dict_len = int.from_bytes(self.b[0:4], byteorder='big', signed=True)
        self.b = self.b[4:]
        for i in range(dict_len):
            key = self.bytes2obj()
            val = self.bytes2obj()
            # print(key, val)
            ret[key] = val
        return ret

if __name__ == '__main__':
    a = {'ss':123, 'dd':'dddd', 'kkk':b'gghhjj', 123:((1, 2, 3), 'ff', {222:('2',)})}
    # a = (2, 3, {2:3})
    # a = 1234
    # a = '22ddffttgg'
    # a = [1, 2, 3]
    aa = ZcsEncoder()(a)
    print(aa)
    bb = ZcsDecoder()(aa)
    print(bb)