import os
import sys
import socket
import time
import tqdm

sys.path.append(os.path.join(os.path.abspath('.'), '..'))
import zcs_util as zu

class ZXClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, ip, port=9999):
        self.sock.connect((ip, port))

    def send_file(self, file_path):
        packet = {
            'CMD':1,
            'FNAME':os.path.basename(file_path),
            'FSIZE':os.path.getsize(file_path),
            'MD5':zu.md5sum(file_path),
        }
        with open(file_path, 'rb') as fp:
            id = 1
            offset = 0
            while True:
                data = fp.read(10240)
                if len(data) <= 0:
                    break
                # print(type(data), len(data))
                if len(data) < 10240:
                    id = -id
                packet['ID'] = id
                print(id)
                id += 1
                packet['SIZE'] = len(data)
                packet['OFFSET'] = offset
                offset += len(data)
                packet['DATA'] = data

                zu.send_packet(self.sock, packet)
                fb_packet = zu.receive_packet(self.sock)
                if fb_packet['FB'] != 'OK':
                    break
                # time.sleep(0.001)
                # if id > 2:
                #     break

if __name__ == '__main__':
    zxc = ZXClient()
    time.sleep(2)
    zxc.connect('127.0.0.1', 9999)
    zxc.send_file('/Users/cszhao/Music/ラムジ-PLANET.flac')
    # zxc.send_file('/Users/cszhao/study/MLY-zh-cn.pdf')
    # zxc.send_file('/Users/cszhao/study/SNR.png')
    # zxc.send_file('/Users/cszhao/project/python/zx_transfer/zcs_util.py')
    # print(zu.md5sum('/Users/cszhao/Music/ラムジ-PLANET.flac'))