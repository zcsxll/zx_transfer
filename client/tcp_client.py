import os
import socket

class ZXClient:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, ip, port=9999):
        self.socket.connect((ip, port))

    def send_file(self, file_path):
        data = 'ZX'.encode('utf-8')
        data += b'00'
        data += 0x00000001.to_bytes(length=4, byteorder='big', signed=False)
        file_name = os.path.basename(file_path)
        file_name = file_name.encode('utf-8')
        data += len(file_name).to_bytes(length=4, byteorder='big', signed=False)
        data += file_name
        data += os.path.getsize(file_path).to_bytes(length=4, byteorder='big', signed=False)
        print(data)
        self.socket.send(data)


if __name__ == '__main__':
    zxc = ZXClient()
    zxc.connect('127.0.0.1', 9999)
    zxc.send_file('/Users/cszhao/Music/ラムジ-PLANET.flac')

