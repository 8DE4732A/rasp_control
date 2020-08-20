import web
import json
import urllib
import base64
import logging
import subprocess
import subscription

subscription_url = 'file:///var/www/v2panel/V2RayN_1597068639.txt'
config_path = '/var/www/v2panel/config.json'
control_path = '/var/www/v2panel/control.json'

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
d = {}
logger = logging.getLogger('server')

urls = (
    '/v1/control', 'ctr',
    '/v1/config', 'cfg',
    '/v1/subscription', 'sub'
)
web.config.debug = True
app = web.application(urls, globals())
db = web.database(dbn="sqlite", db="vmess.db")

class ctr:
    def GET(self):
        with open(control_path, 'r') as f:
            return f.read()
    def POST(self):
        data = json.loads(web.data())
        name = data["name"]
        with open(control_path, 'r') as f:
            control = json.loads(f.read())
            for ctrl in control:
                if ctrl["name"] == name:
                    print(ctrl["script"])
                    logger.info("execute %s", ctrl["script"],  extra=d)
                    return subprocess.call(ctrl["script"], shell=True)

class cfg:
    def GET(self):
        with open(config_path, 'r') as f:
            return  f.read()


class sub:
    def GET(self):
        results = db.select("vmess")
        print(results)
        data = []
        for v in results:
            print(v)
            vmess = {"index": v["id"], "name": v["name"], "used": v["used"], "ping": v["ping"], "bandwidth": v["bandwidth"]}
            data.append(vmess)
        return json.dumps(data)
    def POST(self):
        datastr = web.data()
        print(datastr)
        data = json.loads(datastr)
        if(data["action"] == "update"):
            req = urllib.request.Request(subscription_url)
            req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36")
            with urllib.request.urlopen(req) as f:
                serverListLink = base64.b64decode(
                    f.read()).splitlines()
                if serverListLink:
                    logger.warning('server list: %s', serverListLink, extra=d)
                    db.delete('vmess', where="1=1")
                    for i in range(len(serverListLink)):
                        serverNode = json.loads(base64.b64decode(
                            bytes.decode(serverListLink[i]).replace('vmess://', '')))
                        print('[' + str(i) + ']' + serverNode['ps'])
                        serverListLink[i] = serverNode
                        db.insert('vmess', id=i,name=serverNode['ps'],vmess=json.dumps(serverNode))
            return json.dumps({"code": 0})
        elif(data["action"] == "set"):
            index = data["index"]
            vars = dict(index=index)
            results = db.select("vmess", vars=vars, what="vmess", where="id = $index")
            print(results)
            subscription.export(json.loads(results[0]["vmess"]), config_path)
            subscription.restart()
            db.update('vmess', where="1=1", used=0)
            db.update('vmess', vars=vars, where="id = $index", used=1)
            return json.dumps({"code": 0})

if __name__ == "__main__":
    app.run()
