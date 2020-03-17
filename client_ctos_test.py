# -*- coding: UTF-8 -*-

import threading
import socket
import socks
import time
from tkinter import *
import tkinter.filedialog

sock = None


def server_calc(t_server):
    server = t_server.split(':')
    return server[0], server[1]


def connect():
    # SOCKS5_PROXY_HOST = '127.0.0.1'  # socks 代理IP地址
    # SOCKS5_PROXY_PORT = 35080  # socks 代理本地端口
    # socks.set_default_proxy(socks.SOCKS5, SOCKS5_PROXY_HOST, SOCKS5_PROXY_PORT)
    # socket.socket = socks.socksocket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    server_addr, server_port = server_calc(t_server.get())
    try:
        s.connect((server_addr, int(server_port)))
    except Exception as e:
        print(str(e))

    filename = t_file.get()
    freq = t_freq.get()
    mess = filename + '#' + freq
    s.sendall(mess.encode())

    n = 1
    while True:
        file = b''
        chunk = s.recv(4096)
        s.settimeout(0.5)
        while chunk:
            file += chunk
            try:
                chunk = s.recv(4096)
            except:
                break
        with open(filename, 'wb') as f:
            f.write(file)
            f.close()
        s.send(b'(' + str(n).encode() + b')File recv success.')
        print('(' + str(n) + ')File recv success.')
        n += 1
        s.settimeout(None)


if __name__ == '__main__':
    lock = threading.Lock()
    window = Tk()
    window.title('文件传输')
    # fm1
    fm1 = Frame(window)
    l_server = Label(fm1, text='输入服务器地址', font=('微软雅黑', 16))
    l_server.pack(side=LEFT, padx=20)
    t_server = Entry(fm1, width=30, font=('微软雅黑', 16))
    t_server.pack(side=RIGHT)
    fm1.pack(side=TOP)

    # fm2
    fm2 = Frame(window)
    l_file = Label(fm2, text='文件名', font=('微软雅黑', 16))
    l_file.pack(side=LEFT, padx=50)
    t_file = Entry(fm2, width=30, font=('微软雅黑', 16))
    t_file.pack(side=RIGHT)
    fm2.pack(side=TOP)

    # fm3
    fm3 = Frame(window)
    l_freq = Label(fm3, text='输入发送频率', font=('微软雅黑', 16))
    l_freq.pack(side=LEFT, padx=20)
    t_freq = Entry(fm3, width=10, font=('微软雅黑', 16))
    t_freq.pack(side=RIGHT)
    fm3.pack(side=TOP)

    # fm4
    fm4 = Frame(window)
    l_rec = Label(fm4, text='', font=('微软雅黑', 16))
    l_rec.pack(side=LEFT, padx=20)
    Button(fm4, text='传输', command=connect, font=('微软雅黑', 16)).pack(side=LEFT, padx=20)
    fm4.pack(side=TOP, pady=10)
    window.mainloop()
