import os
import sys
import socket
import time

sys.path.append(os.path.join(os.path.abspath('.'), '..'))
import zcs_util as zu

class ZXClient:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, ip, port=9999):
        self.socket.connect((ip, port))

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

                self.send_packet(packet)
                fb_packet = self.receive_packet()
                if fb_packet['FB'] != 'OK':
                    break
                # if id > 2:
                #     break

    def receive_packet(self):
        data = self.socket.recv(8)
        if len(data) < 8:
            raise Exception('receive data from client failed, %d bytes got, %d bytes expected' % (len(data), 8))

        if bytes.decode(data[0:2], encoding='utf-8') != 'ZX':
            raise Exception('data[0:2] must be ZX')

        packet_len = int.from_bytes(data[4:8], byteorder='big', signed=True)
        # print(packet_len)
        data = self.socket.recv(packet_len)
        if len(data) < packet_len:
            raise Exception('receive data from client failed, %d bytes got, %d bytes expected' % (len(data), packet_len))
        return zu.zcs_bytes2dict(data)

    def send_packet(self, packet):
        bytes_packet = zu.zcs_dict2bytes(packet)
        data = 'ZX'.encode(encoding='utf-8')
        data += b'00'
        data += len(bytes_packet).to_bytes(length=4, byteorder='big', signed=False)
        data += bytes_packet
        # print(data, len(data))
        self.socket.send(data)
        # time.sleep(1)

if __name__ == '__main__':
    zxc = ZXClient()
    zxc.connect('127.0.0.1', 9999)
    # zxc.send_file('/Users/cszhao/Music/ラムジ-PLANET.flac')
    # zxc.send_file('/Users/cszhao/study/MLY-zh-cn.pdf')
    zxc.send_file('/Users/cszhao/study/SNR.png')
    # zxc.send_file('/Users/cszhao/project/python/zx_transfer/zcs_util.py')
    # print(zu.md5sum('/Users/cszhao/Music/ラムジ-PLANET.flac'))