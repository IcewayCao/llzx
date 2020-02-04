﻿# coding: utf-8

import socks
import socket
import time
import threading
import random
import queue
import configparser

IsNeedAuth = ''
Username = ''
Password = ''

SERVER_ADDR = ''
SERVER_PORT = ''

OBFS_USRNAME = ''

f = ''
size_max = ''
size_min = ''


def init():
    cf = configparser.ConfigParser()
    cf.read('conf.ini')

    global IsNeedAuth, Username, Password, SERVER_ADDR, SERVER_PORT, f, size_max, size_min
    isneedauth = cf.get('socks5', 'IsNeedAuth')
    if isneedauth == "False":
        IsNeedAuth = False
    else:
        IsNeedAuth = True

    Username = cf.get('socks5', 'Username')
    Password = cf.get('socks5', 'Password')
    SERVER_ADDR = cf.get('SERVER', 'SERVER_ADDR')
    SERVER_PORT = int(cf.get('SERVER', 'SERVER_PORT'))
    f = int(cf.get('params', 'f'))
    size_max = int(cf.get('params', 'size_max'))
    size_min = int(cf.get('params', 'size_min'))
    cert = cf.get('code', 'cert')
    iat_mode = cf.get('code', 'iat-mode')
    global OBFS_USRNAME
    OBFS_USRNAME = 'cert=' + cert + ';iat-mode=' + iat_mode


def log(log_info):
    print('[' + time.asctime(time.localtime(time.time())) + ']----' + log_info)


def proxy(sock):
    cs = sock
    dsp_port = 0
    dsp_addr = ''
    try:
        recv = cs.recv(512)
        ver = recv[0:1]
        # MethodNum=ord(recv[1:2])
        # Methods=[]
        # for i in range(0,MethodNum):
        # Methods.append(ord(recv[2+i:3+i]))
        if (IsNeedAuth):  # Need AUTHENICATION
            cs.send(b'\x05\x02')  # Reply
            recv = cs.recv(1024)
            Ver = recv[0:1]
            user_len = ord(recv[1:2])
            User = recv[2:2 + user_len]
            pass_len = ord(recv[2 + user_len:3 + user_len])
            Pass = recv[3 + user_len:3 + user_len + pass_len]
            if (User == Username and Pass == Password):
                cs.send(Ver + '\x00')
            else:
                cs.send(Ver + '\xff')
                cs.close()
                return
        else:
            cs.send(ver + b'\x00')  # NO AUTHENICATION REQUEST
        try:
            recv = cs.recv(1024)
        except Exception as ex:
            print('Client is Closed')
            return
        CMD = ord(recv[1:2])
        ATYP = ord(recv[3:4])
        if (CMD == 0x01):  # CONNECT CMD
            if (ATYP == 0x03):  # DOMAINNAME
                AddrLen = ord(recv[4:5])
                dsp_port = 256 * ord(recv[5 + AddrLen:5 + AddrLen + 1]) + ord(recv[1 + 5 + AddrLen:5 + AddrLen + 2])
                dsp_addr = socket.gethostbyname(recv[5:5 + AddrLen])
            elif (ATYP == 0x01):  # IPV4
                if (recv.count(b'.') == 4):  # Asiic  format  split by  '.'
                    AddrLen = ord(recv[4:5])
                    dsp_addr = recv[5:5 + AddrLen]
                    dsp_port = 256 * ord(recv[5 + AddrLen:5 + AddrLen + 1]) + ord(recv[5 + AddrLen + 1:5 + AddrLen + 2])
                else:  # four hex number format
                    dsp_addr = recv[4:8]
                    dsp_addrr = ''
                    for i in dsp_addr:
                        dsp_addrr += str(i) + '.'
                    dsp_addr = dsp_addrr[:-1]
                    dsp_port = 256 * ord(recv[4 + 4:4 + 4 + 1]) + ord(recv[4 + 4 + 1:4 + 4 + 2])
            else:
                print("IPV6 is not support")
                return
            s = auth_socks(dsp_port)
            cs.send(ver + b'\x00\x00\x01\x00\x00\x00\x00\x00\x00')  # REPLY
            handle_connection(cs, s)
        else:
            print("Don't support  this Cmd", CMD)
    except Exception as e:
        print(e)


def empty_flow_create():
    size = random.randint(size_min, size_max)
    empty_flow = ''
    for i in range(0, size):
        empty_flow += ' '

    return empty_flow.encode(encoding='utf-8')


def auth_socks(port):
    SOCKS5_PROXY_HOST = '127.0.0.1'  # socks 代理IP地址
    SOCKS5_PROXY_PORT = 35090  # socks 代理本地端口
    global OBFS_USRNAME
    SOCKS5_PROXY_USERNAME = OBFS_USRNAME[:-1]
    SOCKS5_PROXY_PASSWD = OBFS_USRNAME[-1]
    socks.set_default_proxy(socks.SOCKS5, SOCKS5_PROXY_HOST, SOCKS5_PROXY_PORT, username=SOCKS5_PROXY_USERNAME,
                            password=SOCKS5_PROXY_PASSWD)
    socket.socket = socks.socksocket
    obfs_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    obfs_sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    obfs_sock.connect((SERVER_ADDR, SERVER_PORT))

    obfs_sock.sendall(str(port).encode())
    log(str(obfs_sock.recv(128), encoding='utf-8'))
    return obfs_sock


def handle_connection(cs, s):
    flow_queue = queue.Queue()
    thread = threading.Thread(target=handle_recv, args=(cs, s))
    thread.start()
    log('thread recv create ok')
    thread = threading.Thread(target=handle_send, args=(s, flow_queue))
    thread.start()
    log('thread send create ok')

    data = cs.recv(1024)
    while data:
        flow_queue.put(data)
        data = cs.recv(1024)

    log('connection ending.')


def handle_send(s, flow_queue):
    while True:
        if flow_queue.empty():
            s.sendall(empty_flow_create())
        else:
            while not flow_queue.empty():
                data = flow_queue.get()
                s.sendall(data)
        time.sleep(f / 2)


def handle_recv(cs, s):
    data = s.recv(4096)
    while data:
        cs.sendall(data)
        data = s.recv(4096)

    log('connection ending.')


def flow_recv():
    cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cs.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    cs.bind(('0.0.0.0', 35080))
    log('Listening on port 35080...')
    cs.listen(500)

    while True:
        clientSock, address = cs.accept()
        log('connect ok.')
        thread = threading.Thread(target=proxy, args=(clientSock,))
        thread.start()


if __name__ == "__main__":
    init()
    # ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # ls.bind(('0.0.0.0', 35070))
    # log('Listening on port 35070... ')
    # ls.listen(500)

    # cs, address = ls.accept()
    # recv_str = str(cs.recv(128), encoding='utf-8')
    # global OBFS_USRNAME
    # OBFS_USRNAME = recv_str
    # cs.close()
    flow_recv()