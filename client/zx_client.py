import os
import sys
import socket
from tqdm import tqdm

g_path, basename = os.path.split(sys.argv[0])
sys.path.append(os.path.join(g_path, '..'))
import zcs_util as zu
import zcs_conf as zc

class ZXClient:
    def __init__(self, conf):
        self.server_ip = conf['server ip']
        self.server_port = 9999

    def connect(self, ip=None, port=None):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if ip is not None and port is not None:
            self.sock.connect((ip, port))
        else:
            self.sock.connect((self.server_ip, self.server_port))

    def send_file(self, file_path):
        packet = {
            'CMD':1,
            'FNAME':os.path.basename(file_path),
            'FSIZE':os.path.getsize(file_path),
            'MD5':zu.md5sum(file_path),
        }
        pbar = tqdm(total=os.path.getsize(file_path), bar_format='{l_bar}{bar}', dynamic_ncols=True)
        pbar.set_description('[%s]' % (packet['FNAME']))
        with open(file_path, 'rb') as fp:
            id = 1
            offset = 0
            while True:
                data = fp.read(10240)
                if len(data) <= 0:
                    break
                pbar.update(len(data))
                # print(type(data), len(data))
                if len(data) < 10240:
                    id = -id
                packet['ID'] = id
                # print(id)
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
        pbar.close()

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

    def close(self):
        self.sock.close()

def send_file(zxc, *files):
    for f in files:
        if not os.path.isfile(f):
            print('[%s] is not file like path or not existed' % f)
            continue
        zxc.connect()
        zxc.send_file(f)
        zxc.close()
    #print(path, basename)

def send_cmd(zxc, *args):
    zxc.connect()
    zxc.send_cmd(args[0], *args[1:])
    zxc.close()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage: %s cmd args' % (sys.argv[0]))
        print('\tvalid cmd: sf(send file) sc(send cmd) si(set server ip)')
        sys.exit()
    conf = zc.ZcsConf(g_path)
    cmd = sys.argv[1]
    try:
        if cmd == 'sf': #send file
            if 'server ip' not in conf.keys():
                print('server ip is not set, pls exec "%s" si SERVER_IP' % sys.argv[0])
                sys.exit()
            zxc = ZXClient(conf)
            send_file(zxc, *sys.argv[2:])
        elif cmd == 'sc': #send cmd
            if 'server ip' not in conf.keys():
                print('server ip is not set, pls exec "%s" si SERVER_IP' % sys.argv[0])
                sys.exit()
            zxc = ZXClient(conf)
            send_cmd(zxc, *sys.argv[2:])
        elif cmd == 'si': #set server ip
            conf['server ip'] = sys.argv[2]
            conf.save()
        else:
            raise Exception('unknown cmd [%s]' % cmd)
    except Exception as e:
        print(e)
