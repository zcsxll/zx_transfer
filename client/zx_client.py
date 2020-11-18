import os
import sys
import socket

path, basename = os.path.split(sys.argv[0])
sys.path.append(os.path.join(path, '..'))
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
                response = zu.receive_packet(self.sock)
                if response['FB'] != 'OK':
                    print('send file failed')
                    break
                # time.sleep(0.001)
                # if id > 2:
                #     break

    def send_cmd(self, cmd, *args):
        # print(cmd, args)
        packet = {
            'CMD':100,
            'EXE':cmd,
            'ARGS':args,
        }
        zu.send_packet(self.sock, packet)
        response = zu.receive_packet(self.sock)
        print(response)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage: %s cmd args' % (sys.argv[0]))
        print('\tvalid cmd: send_file send_cmd')
        sys.exit()
    cmd = sys.argv[1]
    try:
        zxc = ZXClient()
        zxc.connect('10.129.27.102', 9999)
        if cmd == 'send_file':
            zxc.send_file(sys.argv[2])
        elif cmd == 'send_cmd':
            args = sys.argv[2:]
            zxc.send_cmd(args[0], *args[1:])
        else:
            raise Exception('unknown cmd [%s]' % cmd)
    except Exception as e:
        print(e)