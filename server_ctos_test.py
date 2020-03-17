# -*- coding: UTF-8 -*-

import os
import socket
import threading
import time


def log(log_info):
    print('[' + time.asctime(time.localtime(time.time())) + ']----' + log_info)


def handle_connection(cs, port):
    log('thread create ok')
    mess = cs.recv(1024)
    mess_s = str(mess, encoding='utf-8')
    filename = mess_s.split('#')[0]
    freq = mess_s.split('#')[1]

    with open(filename, 'rb') as f:
        f_content = f.read()
        # res = s.sendall(f_content)
        while True:
            cs.sendall(f_content)
            log(str(cs.recv(1024), encoding='utf-8'))

            time.sleep(float(freq))


if __name__ == '__main__':
    print('Enter the port:')
    port = input()
    ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ls.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ls.bind(('0.0.0.0', int(port)))
    log('Listening on port ' + port + ' ... ')
    ls.listen(500)
    while True:
        clientSock, address = ls.accept()
        log('connect ok.')
        thread = threading.Thread(target=handle_connection, args=(clientSock, port))
        thread.start()