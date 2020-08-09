import web
import base64
import json
import os
import subprocess
import redis
import urllib.request

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


def sub_decode(address):
    with urllib.request.urlopen(address) as f:
        serverListLink = base64.b64decode(
            f.read()).splitlines()
        if serverListLink:
            r.delete("serverlist")
            for i in range(len(serverListLink)):
                serverNode = json.loads(base64.b64decode(
                    bytes.decode(serverListLink[i]).replace('vmess://', '')))
                print('[' + str(i) + ']' + serverNode['ps'])
                serverListLink[i] = serverNode
                r.rpush(serverNode)
            return serverListLink


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
                            "port": 1080,
                            "users": [
                                {
                                    "id": "uuid",
                                    "alterId": 0,
                                    "email": "@",
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
                        "path": "path",
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
    v2rayConf.replace("&address", "")
    v2rayConf.replace("&address", "")
    v2rayConf.replace("&address", "")
    v2rayConf.replace("&address", "")
    v2rayConf.replace("&address", "")
    v2rayConf.replace("&address", "")
    v2rayConf.replace("&address", "")

    json.dump(v2rayConf, open('/etc/v2ray/config.json', 'w'), indent=2)


def restart():
    subprocess.call('systemctl restart v2ray.service', shell=True)


def printStoredServer():
    r.get("serverlist")


if __name__ == "__main__":
    pass
