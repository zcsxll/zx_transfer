import socket

'''
协议
data[0:2] ZX
data[2:4] not used
data[4:8] command type
data[8:] 取决于command type

command type 0x00000001 --> set file name to write
[8:12] length of name
[12:] name string

command type 0x00000002 --> append file data
[8:12] length of data
[12:16] offset
[16:20] packet id, 负数表示最后一包，且绝对值是上一包+1
[20:] data

'''

class TcpServer:
    def __init__(self, port=9999):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('', port))
        self.server_socket.listen(1)

        self.state = 'IDLE'

    def start(self):
        while True:
            client_socket, client_addr = self.server_socket.accept()
            print(client_addr)
            # client_socket.recv(64)
            # client_socket.send()
            self.handle_command(client_socket)

    def handle_command(self, client_socket):
        data = client_socket.recv(8)
        if len(data) < 8:
            raise Exception('receive data from client failed, %d bytes got' % len(data))

        if bytes.decode(data[0:2], encoding='utf-8') != 'ZX':
            raise Exception('data[0:2] must be ZX')

        command_type = int.from_bytes(data[4:8], byteorder='big', signed=False)
        if command_type == 0x00000001: #set file name to write
            if self.state != 'IDLE':
                raise Exception('cannot set file name to write when state(%s) is not IDLE' % self.state)
            name_len = int.from_bytes(client_socket.recv(4), byteorder='big', signed=False)
            file_name = bytes.decode(client_socket.recv(name_len), encoding='utf-8')
            file_size = int.from_bytes(client_socket.recv(4), byteorder='big', signed=False)
            self.state = 'RECEIVING_FILE %s %d 0 0' % (file_name, file_size) #file_name file_size cur_id cur_size
            print('set file name to write [%s, %d Bytes]' % (file_name, file_size))

        elif command_type == 0x00000002: #append file data
            pass

if __name__ == '__main__':
    TcpServer().start()