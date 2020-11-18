import os
import sys
import socket
from tqdm import tqdm

sys.path.append(os.path.abspath('.'))
import zcs_util as zu

class ZXServer:
    def __init__(self, port=9999):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('', port))
        self.server_socket.listen(1)

    def start(self):
        while True:
            client_socket, client_addr = self.server_socket.accept()
            # print('received client:', client_addr)

            self.last_packet = None
            self.state = {'DONE':False, 'CLIENT':client_addr}
            self.pbar = None #tqdm(100)
            while not self.state['DONE']:
                try:
                    self.tackle(client_socket)
                except Exception as e:
                    print(e)
                    break

            if self.pbar is not None:
                self.pbar.close()

    def tackle(self, client_socket):
        packet = zu.receive_packet(client_socket)
        # print(packet)
        if packet['CMD'] == 1:
            feedback = self.tackle_receive_file(packet)
        elif packet['CMD'] == 100:
            feedback = self.tackle_exec_cmd(packet)
        else:
            raise Exception('unknown command {}'.format(packet['CMD']))
        try:
            zu.send_packet(client_socket, feedback)
        except Exception as e:
            pass

    def tackle_receive_file(self, packet):
        if abs(packet['ID']) == 1:
            if self.last_packet is not None:
                raise Exception('packet id is 0, but last packet is not None')
            self.state['FP'] = open('./data_cache/%s' % packet['FNAME'], 'wb')
            self.state['FP'].write(packet['DATA'])
            # print('receiving %s(%s): %2d%% ' % (packet['FNAME'], packet['MD5'], 0), end='')
            self.pbar = tqdm(total=packet['FSIZE'], bar_format='{l_bar}{bar}', dynamic_ncols=True)
            self.pbar.set_description('[%s](%s)' % (packet['FNAME'], packet['MD5']))
        else:
            if abs(packet['ID']) != self.last_packet['ID']+1:
                raise Exception('packet id is {}, but last packet id is {}'.format(packet['ID'], self.last_packet['ID']))
            if packet['FNAME'] != self.last_packet['FNAME']:
                raise Exception('FNAMEs are not equal, {} vs. {}'.format(packet['FNAME'], self.last_packet['FNAME']))
            if packet['FSIZE'] != self.last_packet['FSIZE']:
                raise Exception('FSIZEs are not equal, {} vs. {}'.format(packet['FSIZE'], self.last_packet['FSIZE']))
            if packet['MD5'] != self.last_packet['MD5']:
                raise Exception('MD5s are not equal, {} vs. {}'.format(packet['MD5'], self.last_packet['MD5']))
            if packet['OFFSET'] != self.last_packet['OFFSET']+self.last_packet['SIZE']:
                raise Exception('OFFSET error, {} {} {}'.format(packet['OFFSET'], self.last_packet['OFFSET'], self.last_packet['SIZE']))
            
            self.state['FP'].write(packet['DATA'])

        self.pbar.update(packet['SIZE'])
        if packet['ID'] < 0:
            # print('DONE')
            self.state['FP'].close()
            md5 = zu.md5sum('./data_cache/%s' % packet['FNAME'])
            if packet['MD5'] != md5:
                raise Exception('receive failed, md5s are not equal, {} vs. {}'.format(packet['MD5'], md5))
            self.state['DONE'] = True
        self.last_packet = packet
        return {'FB':'OK'}

    def tackle_exec_cmd(self, packet):
        # print(packet)
        cmd = packet['EXE']
        for arg in packet['ARGS']:
            cmd += (' ' + arg)
        print('EXEC [%s]' % cmd)
        p = os.popen(cmd, 'r')
        ret = p.read()
        p.close()
        # print(ret)

        self.state['DONE'] = True
        return {'FB':'OK', 'RET':ret}

if __name__ == '__main__':
    ZXServer().start()
    # a = b'123i'
    # print(a[-1:0])
    # task = os.popen('ls -al', 'r')
    # ret = task.read()
    # print('"%s"' % ret)
    # task.close()