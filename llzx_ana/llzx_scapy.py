# coding: utf-8

from scapy.all import *

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
#
# for k in sorted_tab:
#     if tab[k] == 74 or tab[k] == 54:
#         continue
#     count += 1
#     print(str(count) + ' ' + str(k) + ' ' + str(tab[k]))


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

