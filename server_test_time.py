# -*- coding: UTF-8 -*-

import os
import socket
import threading
import time


def log(log_info):
    print('[' + time.asctime(time.localtime(time.time())) + ']----' + log_info)


def handle_connection(cs, port):
    log('thread create ok')
    n = 1
    while True:
        file = b''
        chunk = cs.recv(4096)
        cs.settimeout(0.5)
        while chunk:
            file += chunk
            try:
                chunk = cs.recv(4096)
            except:
                break
        with open('recv' + port, 'wb') as f:
            f.write(file)
            f.close()
        # cs.send(b'(' + str(n).encode() + b')File recv success.')
        print('(' + str(n) + ')File recv success.')
        n += 1
        cs.settimeout(None)


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