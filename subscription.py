import base64
import json
import os
import subprocess
import sqlite3
import urllib.request

subscription_url = 'http://localhost/V2RayN_1597068639.txt'
config_path = 'F:/config.json'

conn = sqlite3.connect('vmess.db')
conn.execute('''CREATE TABLE IF NOT EXISTS "vmess" (
	"id"	INTEGER NOT NULL UNIQUE,
    "name"  TEXT,
	"vmess"	TEXT,
	"used"	INTEGER DEFAULT 0,
    "ping"  INTEGER DEFAULT 0,
    "bandwidth" INTEGER DEFAULT 0,
	PRIMARY KEY("id")
) ''')
conn.commit()


def update_subscription(address):
    req = urllib.request.Request(address)
    req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36")
    with urllib.request.urlopen(req) as f:
        serverListLink = base64.b64decode(
            f.read()).splitlines()
        if serverListLink:
            conn.execute('''delete from vmess where 1 = 1''')
            conn.commit()
            print("#######server list:")
            for i in range(len(serverListLink)):
                serverNode = json.loads(base64.b64decode(
                    bytes.decode(serverListLink[i]).replace('vmess://', '')))
                print('[' + str(i) + ']' + serverNode['ps'])
                serverListLink[i] = serverNode
                conn.execute(
                    '''insert into vmess (id, name, vmess) values (?, ?, ?)''', ( i, serverNode['ps'], json.dumps(serverNode)))
            conn.commit()
            print("#######")


def print_stored_server():
    cur = conn.cursor()
    print("#######server list:")
    for row in cur.execute("select * from vmess order by id"):
        print('[' + str(row[0]) + ']' , row[1])
    print("#######")
    cur.close()

def list_stored_server():
    cur = conn.cursor()
    cur.execute("select * from vmess order by id")
    data = []
    for v in cur.fetchall():
        vmess = {"index": v[0], "name": v[1], "used": v[3], "ping": v[4], "bandwidth": v[5]}
        data.append(vmess)
    cur.close()
    return data



def export(vmess):
    v2rayConf = '''{
        "log": {},
        "dns": {},
        "stats": {},
        "inbounds": [
            {
                "port": "1080",
                "protocol": "socks",
                "settings": {
                    "auth": "noauth",
                    "udp": true
                },
                "tag": "in-0"
            },
            {
                "port": "1081",
                "protocol": "http",
                "settings": {},
                "tag": "in-1"
            }
        ],
        "outbounds": [
            {
                "tag": "proxy",
                "protocol": "vmess",
                "settings": {
                    "vnext": [
                        {
                            "address": "&address",
                            "port": &port,
                            "users": [
                                {
                                    "id": "&uuid",
                                    "alterId": &alterId,
                                    "email": "t@t.tt",
                                    "security": "auto"
                                }
                            ]
                        }
                    ],
                    "servers": null,
                    "response": null
                },
                "streamSettings": {
                    "network": "ws",
                    "security": null,
                    "tlsSettings": null,
                    "tcpSettings": null,
                    "kcpSettings": null,
                    "wsSettings": {
                        "connectionReuse": true,
                        "path": "&path",
                        "headers": null
                    },
                    "httpSettings": null,
                    "quicSettings": null
                },
                "mux": {
                    "enabled": true,
                    "concurrency": 8
                }
            },
            {
                "tag": "direct",
                "protocol": "freedom",
                "settings": {}
            },
            {
                "tag": "blocked",
                "protocol": "blackhole",
                "settings": {}
            }
        ],
        "routing": {
            "domainStrategy": "IPOnDemand",
            "rules": [
                {
                    "type": "field",
                    "ip": [
                        "geoip:private"
                    ],
                    "outboundTag":"direct"
                }
            ]
        },
        "policy": {},
        "reverse": {},
        "transport": {}
    }'''
    v2rayConf = v2rayConf.replace("&address", vmess["add"])
    v2rayConf = v2rayConf.replace("&port", str(vmess["port"]))
    v2rayConf = v2rayConf.replace("&alterId", str(vmess["aid"]))
    v2rayConf = v2rayConf.replace("&uuid", vmess["id"])
    v2rayConf = v2rayConf.replace("&path", vmess["path"])

    with open(config_path, 'w') as f:
        f.write(v2rayConf)


def restart():
    subprocess.call('systemctl restart v2ray.service', shell=True)

def set_subscription(index):
    curr = conn.cursor()
    curr.execute("select id, name, vmess from vmess where id = ?", (index,))
    row = curr.fetchone()
    if row:
        vmess = json.loads(row[2])
        print("\n")
        print('[' + str(row[0]) + ']' , row[1])
        export(vmess)
        print('exported:', config_path)
        restart()


if __name__ == "__main__":
    while True:
        print("")
        print(">>>>>>>>>>>>>>>>>>>>>")
        print("1:subscription update")
        print("2:show all subscription")
        print("3:select server and reboot server")
        print("4:reboot server")
        print("5:exit")
        index = input("choose:")
        if index == "1":
            update_subscription(subscription_url)
        elif index == "2":
            print_stored_server()
        elif index == "3":
            print_stored_server()
            index = input("choose:")
            set_subscription(index)
        elif index == "4":
            pass
        elif index == "5":
            exit(0)
