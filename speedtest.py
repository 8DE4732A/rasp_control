import subprocess

veth_start_shell = '''
ip link add veth0 type veth peer name veth1
ip addr add 10.100.1.1/24 dev veth0
ip link set veth0 up
ip addr add 10.100.1.2/24 dev veth1
ip link set veth1 up
#iptables forward veth1 to v2ray dokodemo
iptables -t nat -A POSTROUTING -s 10.100.1.0/255.255.255.0 -o wlan0
iptables -A FORWARD -i wlan0 -o veth1 -j ACCEPT
iptables -A FORWARD -o wlan0 -i veth1 -j ACCEPT
'''

veth_end_shell = '''

'''

def speedtest(vmess):
  '''
  use https://www.speedtest.net/apps/cli
  '''
  start_proxy_server(vmess)
  subprocess.run(veth_start_shell)
  result = subprocess.run(["./speedtest", "-I", "veth0", "-f", "json"])
  subprocess.run(veth_end_shell)
  return result

def start_proxy_server(vmess):
  pass


if __name__ == "__main__":
    pass