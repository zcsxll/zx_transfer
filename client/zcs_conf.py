import os
import json

class ZcsConf:
    def __init__(self, path):
        with open(os.path.join(path, './client.conf'), 'r') as fp:
            json_str = fp.read()
            if len(json_str) < 2:
                json_str = '{}'
            # print(json_str)
        self.conf = json.loads(json_str)
        # print(self.conf)

    def __getitem__(self, key):
        return self.conf[key]

    def __setitem__(self, key, value):
        self.conf[key] = value

    def keys(self):
        return self.conf.keys()

    def save(self):
        with open('./client.conf', 'w') as fp:
            fp.write(json.dumps(self.conf))

if __name__ == '__main__':
    zf = ZcsConf()
    zf['server ip'] = '111.222'
    print(zf['server ip'])
    zf.save()

