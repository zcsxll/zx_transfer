import os
import sys
import socket
import time

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
            print('received clien:', client_addr)

            self.last_packet = None
            self.state = {'DONE':False, 'CLIENT':client_addr}
            while not self.state['DONE']:
                try:
                    self.handle_command(client_socket)
                except Exception as e:
                    print(e)
                    break

    def handle_command(self, client_socket):
        packet = self.receive_packet(client_socket)
        # print(packet)
        if packet['CMD'] == 1:
            feedback = self.handle_command_receive_file(packet)
        else:
            raise Exception('unknown command {}'.format(packet['CMD']))
        self.send_packet(client_socket, feedback)

    def handle_command_receive_file(self, packet):
        if abs(packet['ID']) == 1:
            if self.last_packet is not None:
                raise Exception('packet id is 0, but last packet is not None')
            self.state['FP'] = open('./data_cache/%s' % packet['FNAME'], 'wb')
            self.state['FP'].write(packet['DATA'])
            print('receiving %s(%s): ' % (packet['FNAME'], packet['MD5']), end='')
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

        if packet['ID'] < 0:
            print('DONE')
            self.state['FP'].close()
            md5 = zu.md5sum('./data_cache/%s' % packet['FNAME'])
            if packet['MD5'] != md5:
                raise Exception('receive failed, md5s are not equal, {} vs. {}'.format(packet['MD5'], md5))
            self.state['DONE'] = True
        self.last_packet = packet
        return {'FB':'OK'}

    def receive_packet(self, client_socket):
        data = client_socket.recv(8)
        if len(data) < 8:
            raise Exception('receive data from client failed, %d bytes got, %d bytes expected' % (len(data), 8))

        if bytes.decode(data[0:2], encoding='utf-8') != 'ZX':
            raise Exception('data[0:2] must be ZX')

        packet_len = int.from_bytes(data[4:8], byteorder='big', signed=True)
        # print(packet_len)
        data = client_socket.recv(packet_len)
        if len(data) < packet_len:
            raise Exception('receive data from client failed, %d bytes got, %d bytes expected' % (len(data), packet_len))
        return zu.zcs_bytes2dict(data)

    def send_packet(self, client_socket, packet):
        bytes_packet = zu.zcs_dict2bytes(packet)
        data = 'ZX'.encode(encoding='utf-8')
        data += b'00'
        data += len(bytes_packet).to_bytes(length=4, byteorder='big', signed=False)
        data += bytes_packet
        # print(data, len(data))
        client_socket.send(data)
        # time.sleep(1)

if __name__ == '__main__':
    ZXServer().start()
    # a = b'123i'
    # print(a[-1:0])