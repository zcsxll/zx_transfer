import hashlib

import zcs_codec

def receive_data(sock, length):
    data = b''
    while len(data) < length:
        tmp = sock.recv(length - len(data))
        if len(tmp) == 0:
            break
        data += tmp
    return data

def receive_packet(sock):
    # data = sock.recv(8)
    data = receive_data(sock, 8)
    if len(data) < 8:
        raise Exception('receive data failed, %d bytes got, %d bytes expected' % (len(data), 8))

    if bytes.decode(data[0:2], encoding='utf-8') != 'ZX':
        raise Exception('data[0:2] must be ZX')

    packet_len = int.from_bytes(data[4:8], byteorder='big', signed=True)
    # print(packet_len)
    # data = sock.recv(packet_len)
    data = receive_data(sock, packet_len)
    if len(data) < packet_len:
        raise Exception('receive data failed, %d bytes got, %d bytes expected' % (len(data), packet_len))
    return zcs_codec.ZcsDecoder()(data)

def send_packet(sock, packet):
    bytes_packet = zcs_codec.ZcsEncoder()(packet)
    data = 'ZX'.encode(encoding='utf-8')
    data += b'00'
    data += len(bytes_packet).to_bytes(length=4, byteorder='big', signed=False)
    data += bytes_packet
    # print(data, len(data))
    sock.send(data)
    # time.sleep(1)

def md5sum(file_path):
    h = hashlib.md5()
    with open(file_path, 'rb') as fp:
        for line in fp:
            h.update(line)
    md5 = h.hexdigest()
    return md5

if __name__ == '__main__':
    pass
