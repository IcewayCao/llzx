# cat juli-start-iptables.sh 
#!/bin/sh
#创建一个叫SOCKS的链
 
iptables -t nat -N SOCKS
 
#忽略服务器的地址,如果不属于内网IP的话一定要注意加上.
 
#其实下面这句可以省略的, 因为它属于172.16.0.0/12
 
iptables -t nat -A SOCKS -d 172.23.45.19 -j RETURN
 
# 忽略本地地址
 
iptables -t nat -A SOCKS -d 0.0.0.0/8 -j RETURN
 
iptables -t nat -A SOCKS -d 10.0.0.0/8 -j RETURN
 
iptables -t nat -A SOCKS -d 127.0.0.0/8 -j RETURN
 
iptables -t nat -A SOCKS -d 169.254.0.0/16 -j RETURN
 
iptables -t nat -A SOCKS -d 172.16.0.0/12 -j RETURN
 
iptables -t nat -A SOCKS -d 192.168.0.0/16 -j RETURN
 
iptables -t nat -A SOCKS -d 224.0.0.0/4 -j RETURN
 
iptables -t nat -A SOCKS -d 240.0.0.0/4 -j RETURN

iptables -t nat -A SOCKS -p tcp --dport 2222 -j RETURN
 
# Anything else should be redirected to shadowsocks's local port
 
#除上面之外的所有流量都跳转到socks的本地端口(local_port),这里使用shadosock默认端口1080
 
iptables -t nat -A SOCKS -p tcp -d 223.3.93.231 -j REDIRECT --to-ports 12345
 
# 最后是应用上面的规则,将OUTPUT出去的tcp流量全部经过SOCKS链
 
#如果是在openwrt上实现透明代理的话,使用下面被注释了的规则
 
#iptables -t nat -A PREROUTING -p tcp -j SOCKS
#iptables -t nat -A PREROUTING -p udp -j SOCKS
#iptables -t nat -A PREROUTING -p icmp -j SOCKS
 
iptables -t nat -A OUTPUT -p tcp -j SOCKS