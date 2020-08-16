import web
import json
import urllib
import base64
import logging
import subscription

subscription_url = 'http://localhost/V2RayN_1597068639.txt'
config_path = 'F:/config.json'

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
d = {}
logger = logging.getLogger('server')

urls = (
    '/v1/control', 'ctr',
    '/v1/config', 'cfg',
    '/v1/subscription', 'sub'
)
web.config.debug = False
app = web.application(urls, globals())
db = web.database(dbn="sqlite", db="vmess.db")

class ctr:
    pass
class cfg:
    pass

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
        elif(data["action"] == "set"):
            index = data["index"]
            vars = dict(index=index)
            results = db.select("vmess", vars=vars, what="vmess", where="id = $index")
            subscription.export(results[0])
            subscription.restart()

if __name__ == "__main__":
    app.run()