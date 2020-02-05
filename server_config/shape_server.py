# -*- coding: UTF-8 -*-

import socket
import threading
import time
import configparser
import random

CLIENT_ADDR = ''
CLIENT_PORT = ''


def init():
    cf = configparser.ConfigParser()
    try:
        cf.read('conf.ini')
    except Exception as e:
        log('config wrong.')
        return False

    global CLIENT_ADDR, CLIENT_PORT
    CLIENT_ADDR = cf.get('CLIENT', 'CLIENT_ADDR')
    CLIENT_PORT = int(cf.get('CLIENT', 'CLIENT_PORT'))

    return True


def log(log_info):
    print('[' + time.asctime(time.localtime(time.time())) + ']----' + log_info)


def get_auth():
    file = '/var/lib/obfs4_usr/obfs4_bridgeline.txt'
    out = open(file, encoding='utf-8')
    lines = out.readlines()
    cert = lines[-1].split(' ')[-2]
    iat_mode = lines[-1].split(' ')[-1]
    auth = cert + ';' + iat_mode[:-1]
    return auth


def handle_connection(cs):
    port = str(cs.recv(128), encoding='utf-8')
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    server_sock.connect(('0.0.0.0', int(port)))

    cs.sendall(b'server connect ok.')
    th_recv = threading.Thread(target=handle_recv, args=(cs, server_sock))
    th_recv.start()

    # flag = chr(1).encode(encoding='utf-8')

    data = cs.recv(1024)
    while data:
        index = random.randint(0, len(data))
        if data[0:1] == b' ' and data[len(data) - 1:len(data)] == b' ' and data[index:index+1] == b' ':
            print('empty flow to ' + port)
        else:
            print('data to ' + port)
            server_sock.sendall(data)

        data = cs.recv(1024)

    log('connection ending.')


def handle_recv(cs, s):
    data = s.recv(1024)
    while data:
        cs.sendall(data)
        data = s.recv(1024)

    log('connection ending.')


if __name__ == '__main__':
    if not init():
        exit()
    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.connect((CLIENT_ADDR, CLIENT_PORT))

    # mess = get_auth().encode()
    # s.sendall(mess)
    # s.close()

    ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ls.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ls.bind(('0.0.0.0', 5500))
    log('Listening on port 5500... ')
    ls.listen(500)
    while True:
        clientSock, address = ls.accept()
        log('connect ok.')
        thread = threading.Thread(target=handle_connection, args=(clientSock,))
        thread.start()