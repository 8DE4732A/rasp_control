* 情况1
```shell
ip netns add speed
ip link add veth0 type veth peer name veth1
ip link set veth0 netns speed

ip addr add 192.168.98.2/24 dev veth1
ip link set veth1 up

ip netns exec speed ip addr add 192.168.98.1/24 dev veth0
ip netns exec speed ip link set veth0 up
ip netns exec speed ip link set lo up
ip netns exec speed ip route add default via 192.168.98.2 #使用对端ip

echo 1 > /proc/sys/net/ipv4/ip_forward

iptables -P FORWARD DROP
iptables -F FORWARD
iptables -t nat -F
iptables -t nat -A POSTROUTING -s 192.168.98.1/24 -o enp0s3 -j MASQUERADE
iptables -A FORWARD -i enp0s3 -o veth1 -j ACCEPT
iptables -A FORWARD -o veth1 -i enp0s3 -j ACCEPT

#ping不通
ip netns exec speed ping www.baidu.com 
```
* 情况2
```shell
ip netns add speed
ip link add veth0 type veth peer name veth1
ip link set veth1 netns speed

ip addr add 192.168.98.2/24 dev veth0
ip link set veth0 up

ip netns exec speed ip addr add 192.168.98.1/24 dev veth1
ip netns exec speed ip link set veth1 up
ip netns exec speed ip link set lo up
ip netns exec speed ip route add default via 192.168.98.2  #使用对端ip

echo 1 > /proc/sys/net/ipv4/ip_forward

iptables -P FORWARD DROP
iptables -F FORWARD
iptables -t nat -F
iptables -t nat -A POSTROUTING -s 192.168.98.1/24 -o enp0s3 -j MASQUERADE
iptables -A FORWARD -i enp0s3 -o veth0 -j ACCEPT
iptables -A FORWARD -o enp0s3 -i veth0 -j ACCEPT

#ping通
ip netns exec speed ping www.baidu.com 
```

参考 [https://gist.github.com/dpino/6c0dca1742093346461e11aa8f608a99](https://gist.github.com/dpino/6c0dca1742093346461e11aa8f608a99)