# -*- coding: UTF-8 -*-

import socket
import threading
import time
import configparser
import random
import queue

# CLIENT_ADDR = ''
# CLIENT_PORT = ''

f = 0
size_max = 0
size_min = 0
ctos = True


def init():
    cf = configparser.ConfigParser()
    try:
        cf.read('conf.ini')
    except Exception as e:
        log('config wrong.')
        return False

    # global CLIENT_ADDR, CLIENT_PORT
    global f, size_max, size_min, ctos
    # CLIENT_ADDR = cf.get('CLIENT', 'CLIENT_ADDR')
    # CLIENT_PORT = int(cf.get('CLIENT', 'CLIENT_PORT'))
    f = int(cf.get('params', 'f'))
    size_max = int(cf.get('params', 'size_max'))
    size_min = int(cf.get('params', 'size_min'))
    c_s = cf.get('params', 'ctos')
    if not c_s == '1':
        ctos = False

    return True


def log(log_info):
    print('[' + time.asctime(time.localtime(time.time())) + ']----' + log_info)

#
# def get_auth():
#     file = '/var/lib/obfs4_usr/obfs4_bridgeline.txt'
#     out = open(file, encoding='utf-8')
#     lines = out.readlines()
#     cert = lines[-1].split(' ')[-2]
#     iat_mode = lines[-1].split(' ')[-1]
#     auth = cert + ';' + iat_mode[:-1]
#     return auth


def handle_connection(cs):
    port = str(cs.recv(128), encoding='utf-8')
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    server_sock.connect(('0.0.0.0', int(port)))

    cs.sendall(b'server connect ok.')
    if ctos:
        th_recv = threading.Thread(target=handle_recv, args=(cs, server_sock))
        th_recv.start()

        # flag = chr(1).encode(encoding='utf-8')

        data = cs.recv(1024)
        while data:
            index = random.randint(0, len(data))
            if data[0:1] == b' ' and data[len(data) - 1:len(data)] == b' ' and data[index:index + 1] == b' ':
                print('empty flow to ' + port)
            else:
                print('data to ' + port)
                server_sock.sendall(data)

            data = cs.recv(1024)

        log('connection ending.')
        return
    else:
        flow_queue = queue.Queue()
        thread = threading.Thread(target=handle_sc_send, args=(cs, server_sock))
        thread.start()
        log('thread recv create ok')
        thread = threading.Thread(target=handle_sc_recv, args=(cs, flow_queue))
        thread.start()
        log('thread send create ok')

        data = server_sock.recv(1024)
        while data:
            flow_queue.put(data)
            data = server_sock.recv(1024)

        log('connection ending.')
        return


def empty_flow_create():
    size = random.randint(size_min, size_max)
    empty_flow = ''
    for i in range(0, size):
        empty_flow += ' '

    return empty_flow.encode(encoding='utf-8')


def handle_sc_recv(cs, flow_queue):
    while True:
        if flow_queue.empty():
            cs.sendall(empty_flow_create())
        else:
            while not flow_queue.empty():
                data = flow_queue.get()
                cs.sendall(data)
        time.sleep(f / 2)


def handle_sc_send(cs, s):
    data = cs.recv(1024)
    while data:
        s.sendall(data)
        data = cs.recv(1024)

    log('connection ending.')
    return


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