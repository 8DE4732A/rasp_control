#!/usr/bin/python3
import subprocess
import json

add = '''
#!/bin/bash
# 设置策略路由
echo $0
echo $1

sudo ip rule add fwmark 1 table 100
sudo ip route add local 0.0.0.0/0 dev lo table 100

# 代理局域网设备
sudo iptables -t mangle -N V2RAY
sudo iptables -t mangle -A V2RAY -d $1 -j RETURN
sudo iptables -t mangle -A V2RAY -d 255.255.255.255/32 -j RETURN
 # 直连局域网，避免 V2Ray 无法启动时无法连网关的 SSH，如果你配置的是其他网段（如 10.x.x.x 等），则修改成自己的
sudo iptables -t mangle -A V2RAY -d 0.0.0.0/8 -j RETURN
sudo iptables -t mangle -A V2RAY -d 10.0.0.0/8 -j RETURN
sudo iptables -t mangle -A V2RAY -d 127.0.0.0/8 -j RETURN
sudo iptables -t mangle -A V2RAY -d 169.254.0.0/16 -j RETURN
sudo iptables -t mangle -A V2RAY -d 172.16.0.0/12 -j RETURN
sudo iptables -t mangle -A V2RAY -d 192.168.0.0/16 -j RETURN
sudo iptables -t mangle -A V2RAY -d 224.0.0.0/4 -j RETURN
sudo iptables -t mangle -A V2RAY -d 240.0.0.0/4 -j RETURN
sudo iptables -t mangle -A V2RAY -d 192.168.0.0/16 -p udp ! --dport 53 -j RETURN # 直连局域网，53 端口除外（因为要使用 V2Ray 的
sudo iptables -t mangle -A V2RAY -p udp -j TPROXY --on-port 12345 --tproxy-mark 1 # 给 UDP 打标记 1，转发至 12345 端口
sudo iptables -t mangle -A V2RAY -p tcp -j TPROXY --on-port 12345 --tproxy-mark 1 # 给 TCP 打标记 1，转发至 12345 端口
sudo iptables -t mangle -A PREROUTING -j V2RAY # 应用规则

# 代理网关本机
sudo iptables -t mangle -N V2RAY_MASK
sudo iptables -t mangle -A V2RAY_MASK -d 255.255.255.255/32 -j RETURN
sudo iptables -t mangle -A V2RAY_MASK -d $1 -j RETURN
sudo iptables -t mangle -A V2RAY_MASK -d 255.255.255.255/32 -j RETURN
 # 直连局域网，避免 V2Ray 无法启动时无法连网关的 SSH，如果你配置的是其他网段（如 10.x.x.x 等），则修改成自己的
sudo iptables -t mangle -A V2RAY_MASK -d 0.0.0.0/8 -j RETURN
sudo iptables -t mangle -A V2RAY_MASK -d 10.0.0.0/8 -j RETURN
sudo iptables -t mangle -A V2RAY_MASK -d 127.0.0.0/8 -j RETURN
sudo iptables -t mangle -A V2RAY_MASK -d 169.254.0.0/16 -j RETURN
sudo iptables -t mangle -A V2RAY_MASK -d 172.16.0.0/12 -j RETURN
sudo iptables -t mangle -A V2RAY_MASK -d 192.168.0.0/16 -j RETURN
sudo iptables -t mangle -A V2RAY_MASK -d 224.0.0.0/4 -j RETURN
sudo iptables -t mangle -A V2RAY_MASK -d 240.0.0.0/4 -j RETURN
sudo iptables -t mangle -A V2RAY_MASK -d 192.168.0.0/16 -p tcp -j RETURN # 直连局域网
sudo iptables -t mangle -A V2RAY_MASK -d 192.168.0.0/16 -p udp ! --dport 53 -j RETURN # 直连局域网，53 端口除外（因为要使用 V2Ray 的 DNS）
sudo iptables -t mangle -A V2RAY_MASK -j RETURN -m mark --mark 0xff    # 直连 SO_MARK 为 0xff 的流量(0xff 是 16 进制数，数值上等同与上面V2Ray 配置的 255)，此规则目的是避免代理本机(网关)流量出现回环问题
sudo iptables -t mangle -A V2RAY_MASK -p udp -j MARK --set-mark 1   # 给 UDP 打标记,重路由
sudo iptables -t mangle -A V2RAY_MASK -p tcp -j MARK --set-mark 1   # 给 TCP 打标记，重路由
sudo iptables -t mangle -A OUTPUT -j V2RAY_MASK # 应用规则
'''

remove = '''
sudo iptables -t mangle -F V2RAY
sudo iptables -t mangle -F V2RAY_MASK
sudo iptables -t mangle -D PREROUTING 1
sudo iptables -t mangle -D OUTPUT 1
sudo iptables -t mangle -X V2RAY
sudo iptables -t mangle -X V2RAY_MASK
'''

if __name__ == "__main__":
    pass