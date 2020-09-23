import subprocess


class SpeedTest(object):
    def before(self):
        raise NotImplementedError

    def after(self):
        raise NotImplementedError

    def speed_test(self):
        raise NotImplementedError

    def call(self, vmess):
        self.before()
        result = self.speed_test()
        self.after()
        return result


class VethSpeedTest(SpeedTest):
    before_shell = '''
    ip netns add speed
    ip link add veth0 type veth peer name veth1
    ip link set veth1 netns speed

    ip addr add 192.168.98.2/24 dev veth0
    ip link set veth0 up

    ip netns exec speed ip addr add 192.168.98.1/24 dev veth1
    ip netns exec speed ip link set veth1 up
    ip netns exec speed ip link set lo up
    ip netns exec speed ip route add default via 192.168.98.2

    ip rule add fwmark 1 table 100
    ip route add local 0.0.0.0/0 dev lo table 100
    iptables -t mangle -N V2RAY_SPEED
    iptables -t mangle -A V2RAY_SPEED -d 255.255.255.255/32 -j RETURN
    iptables -t mangle -A V2RAY_SPEED -d 0.0.0.0/8 -j RETURN
    iptables -t mangle -A V2RAY_SPEED -d 10.0.0.0/8 -j RETURN
    iptables -t mangle -A V2RAY_SPEED -d 127.0.0.0/8 -j RETURN
    iptables -t mangle -A V2RAY_SPEED -d 169.254.0.0/16 -j RETURN
    iptables -t mangle -A V2RAY_SPEED -d 172.16.0.0/12 -j RETURN
    iptables -t mangle -A V2RAY_SPEED -d 224.0.0.0/4 -j RETURN
    iptables -t mangle -A V2RAY_SPEED -d 240.0.0.0/4 -j RETURN
    iptables -t mangle -A V2RAY_SPEED -d 192.168.0.0/16 -p tcp -j RETURN
    iptables -t mangle -A V2RAY_SPEED -d 192.168.0.0/16 -p udp ! --dport 53 -j RETURN
    iptables -t mangle -A V2RAY_SPEED -p udp -s 192.168.98.0/24 -j TPROXY --on-port 12345 --tproxy-mark 1
    iptables -t mangle -A V2RAY_SPEED -p tcp -s 192.168.98.0/24 -j TPROXY --on-port 12345 --tproxy-mark 1
    iptables -t mangle -A PREROUTING -s 192.168.98.1/24 -j V2RAY_SPEED
    '''

    after_shell = '''
    ip link set veth0 down
    ip link set veth1 down
    ip link delete veth0 type veth peer name veth1

    
    '''

    def before(self):
        subprocess.call(VethSpeedTest.before_shell, shell=True)

    def after(self):
        subprocess.call(VethSpeedTest.after_shell, shell=True)


class TunSpeedTest(SpeedTest):
    ""
    before_shell = '''
    A
    '''

    after_shell = '''
    B
    '''

    def before(self):
        subprocess.call(VethSpeedTest.before_shell, shell=True)

    def after(self):
        subprocess.call(VethSpeedTest.after_shell, shell=True)
