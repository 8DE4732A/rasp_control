import subprocess

veth_start_shell = '''
ip netns add speed

ip link add veth0 type veth peer name veth1

ip link set veth0 netns speed
ip netns exec speed ip addr add 192.168.98.1/24 dev veth0
ip netns exec speed ip link set veth0 up
ip netns exec speed ip link set lo up
ip netns exec speed ip route add default via 192.168.98.1

ip addr add 192.168.98.2/24 dev veth1
ip link set veth1 up
iptables -I FORWARD -i veth1 -m state --state ESTABLISHED,RELATED -j ACCEPT
'''

veth_end_shell = '''
ip link set veth0 down
ip link set veth1 down
ip link delete veth0 type veth peer name veth1
'''

iptables_add = '''
#!/bin/bash
# 设置策略路由
sudo ip rule add fwmark 1 table 100
sudo ip route add local 0.0.0.0/0 dev lo table 100

# 代理局域网设备
sudo iptables -t mangle -N V2RAY_SPEED
sudo iptables -t mangle -A V2RAY_SPEED -d %s -j RETURN #proxy主机
sudo iptables -t mangle -A V2RAY_SPEED -d 255.255.255.255/32 -j RETURN
# 直连局域网，避免 V2Ray 无法启动时无法连网关的 SSH，如果你配置的是其他网段（如 10.x.x.x 等），则修改成自己的
sudo iptables -t mangle -A V2RAY_SPEED -d 0.0.0.0/8 -j RETURN
sudo iptables -t mangle -A V2RAY_SPEED -d 10.0.0.0/8 -j RETURN
sudo iptables -t mangle -A V2RAY_SPEED -d 127.0.0.0/8 -j RETURN
sudo iptables -t mangle -A V2RAY_SPEED -d 169.254.0.0/16 -j RETURN
sudo iptables -t mangle -A V2RAY_SPEED -d 172.16.0.0/12 -j RETURN
sudo iptables -t mangle -A V2RAY_SPEED -d 192.168.0.0/16 -j RETURN
sudo iptables -t mangle -A V2RAY_SPEED -d 224.0.0.0/4 -j RETURN
sudo iptables -t mangle -A V2RAY_SPEED -d 240.0.0.0/4 -j RETURN
sudo iptables -t mangle -A V2RAY_SPEED -d 192.168.0.0/16 -p udp ! --dport 53 -j RETURN # 直连局域网，53 端口除外（因为要使用 V2Ray 的
sudo iptables -t mangle -A V2RAY_SPEED -p udp -s 192.168.98.0/24 -j TPROXY --on-port 12345 --tproxy-mark 1 # 给 UDP 打标记 1，转发至 12345 端口
sudo iptables -t mangle -A V2RAY_SPEED -p tcp -s 192.168.98.0/24 -j TPROXY --on-port 12345 --tproxy-mark 1 # 给 TCP 打标记 1，转发至 12345 端口
sudo iptables -t mangle -A PREROUTING -j V2RAY_SPEED # 应用规则
'''

iptables_remove = '''
sudo iptables -t mangle -F V2RAY_SPEED
sudo iptables -t mangle -D PREROUTING 1
sudo iptables -t mangle -X V2RAY_SPEED
'''



def speedtest(vmess):
  '''
  use https://www.speedtest.net/apps/cli
  '''
  start_proxy_server(vmess)
  subprocess.run(veth_start_shell)
  #ip netns exec ns1 /bin/bash --rcfile <(echo "PS1=\"namespace ns1> \"")
  result = subprocess.run(["ip netns exec speed", "./speedtest", "-I", "veth0", "-f", "json"])
  subprocess.run(veth_end_shell)
  return result

def start_proxy_server(vmess):
  pass


if __name__ == "__main__":
    pass