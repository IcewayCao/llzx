# coding: utf-8

from scapy.all import *
from matplotlib import pyplot as plt


class Pacpp(object):
    def __init__(self, time, len, port):
        self.time = time
        self.len = len
        self.port = port


pacps = rdpcap("llzx.pcap")
packets_send = list()
packets_recv = list()
# print(pacps[0].show())
for pacp in pacps:
    if pacp.haslayer("IP") and pacp['IP'].src == '192.168.36.129' and pacp['IP'].dst == '47.101.223.60':
        packets_send.append(pacp)
    if pacp.haslayer("IP") and pacp['IP'].src == '47.101.223.60' and pacp['IP'].dst == '192.168.36.129':
        packets_recv.append(pacp)

pacpps = []
time_start = 0
i = 0
for packet in packets_send:

    if time_start == 0:
        time_start = packet.time
        pacpps.append(Pacpp(0, len(packet), packet['TCP'].sport))
    else:
        time_ap = packet.time - time_start
        pacpps.append(Pacpp(time_ap, len(packet), packet['TCP'].sport))
    i += 1

combine_pacpps = []
count = 0
tmp_k = 0
tmp_t = 0
tmp_v = 0
tmp_p = 41824

for pacpp in pacpps:
    if pacpp.len == 74 or pacpp.len == 54:
        continue
    count += 1
    print(str(count) + ' ' + str(pacpp.time) + ' ' + str(pacpp.len) + ' ' + str(pacpp.port))

for pacpp in pacpps:
    if pacpp.len == 74 or pacpp.len == 54:
        continue
    if pacpp.time-tmp_t < 0.1 and pacpp.time > 0:
        tmp_v += pacpp.len
        continue
    if pacpp.time-tmp_t >= 0.1:
        combine_pacpps.append(Pacpp(tmp_k, tmp_v, tmp_p))
        tmp_v = pacpp.len
        tmp_k = pacpp.time
        tmp_p = pacpp.port

    tmp_t = pacpp.time

count = 0
for combine_pacpp in combine_pacpps:
    count += 1
    print(str(count) + ' ' + str(combine_pacpp.time) + ' ' + str(combine_pacpp.len) + ' ' + str(combine_pacpp.port))


pacp_x_1 = []
pacp_x_2 = []
pacp_x_3 = []
pacp_y_1 = []
pacp_y_2 = []
pacp_y_3 = []

for pacpp in pacpps:
    if pacpp.len == 74 or pacpp.len == 54:
        continue
    if pacpp.port == 41824:
        pacp_x_1.append(pacpp.time)
        pacp_y_1.append(pacpp.len)
    elif pacpp.port == 41832:
        pacp_x_2.append(pacpp.time)
        pacp_y_2.append(pacpp.len)
    elif pacpp.port == 41840:
        pacp_x_3.append(pacpp.time)
        pacp_y_3.append(pacpp.len)

plt.plot(pacp_x_1, pacp_y_1)
plt.plot(pacp_x_2, pacp_y_2)
plt.plot(pacp_x_3, pacp_y_3)

combine_pacp_x_1 = []
combine_pacp_x_2 = []
combine_pacp_x_3 = []
combine_pacp_y_1 = []
combine_pacp_y_2 = []
combine_pacp_y_3 = []

for pacpp in combine_pacpps:
    if pacpp.port == 41824:
        combine_pacp_x_1.append(pacpp.time)
        combine_pacp_y_1.append(pacpp.len)
    elif pacpp.port == 41832:
        combine_pacp_x_2.append(pacpp.time)
        combine_pacp_y_2.append(pacpp.len)
    elif pacpp.port == 41840:
        combine_pacp_x_3.append(pacpp.time)
        combine_pacp_y_3.append(pacpp.len)

plt.plot(combine_pacp_x_1, combine_pacp_y_1)
plt.plot(combine_pacp_x_2, combine_pacp_y_2)
plt.plot(combine_pacp_x_3, combine_pacp_y_3)


plt.show()