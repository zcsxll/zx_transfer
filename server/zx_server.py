import os
import sys
import socket
from tqdm import tqdm

sys.path.append(os.path.join(os.path.abspath('.'), '..'))
import zcs_util as zu

'''
协议：
data[0:2] ZX
data[2:4] not used
data[4:8] 长度，是bytes，调用zcs_bytes2dict转dict
'''

class ZXServer:
    def __init__(self, port=9999):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('', port))
        self.server_socket.listen(1)

        self.state = 'IDLE'

    def start(self):
        while True:
            client_socket, client_addr = self.server_socket.accept()
            # print('received client:', client_addr)

            self.last_packet = None
            self.state = {'DONE':False, 'CLIENT':client_addr}
            self.pbar = None #tqdm(100)
            while not self.state['DONE']:
                try:
                    self.handle_command(client_socket)
                except Exception as e:
                    print(e)
                    break
            self.pbar.close()

    def handle_command(self, client_socket):
        packet = zu.receive_packet(client_socket)
        # print(packet)
        if packet['CMD'] == 1:
            feedback = self.handle_command_receive_file(packet)
        else:
            raise Exception('unknown command {}'.format(packet['CMD']))
        zu.send_packet(client_socket, feedback)

    def handle_command_receive_file(self, packet):
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

if __name__ == '__main__':
    ZXServer().start()
    # a = b'123i'
    # print(a[-1:0])