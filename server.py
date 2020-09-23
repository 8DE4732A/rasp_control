import sqlite3
import subprocess
import json
import urllib
import base64
import io
import time
import random
import psutil
from threading import Lock
from flask import Flask, render_template, abort, g, request, jsonify
from jinja2 import TemplateNotFound
from flask_socketio import SocketIO, emit


app = Flask(__name__)
socketio = SocketIO(app)

thread = None
thread_lock = Lock()

DATABASE = 'rasp.db'
CONTROL_PATH = 'control.json'
CONFIG_PATH = 'config.json'
SUBSCRIPTION_URL = 'http://localhost/V2RayN_1597068639.txt'


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = make_dicts
    return db


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


init_db()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def delete_db():
    get_db().execute("delete from vmess where 1 = 1")
    get_db().commit()


def insert_many_db(sql, args=[]):
    get_db().executemany(sql, args)
    get_db().commit()


def update_db(sql, args=()):
    get_db().execute(sql, args)
    get_db().commit()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/', defaults={'page': 'index'})
@app.route('/<page>')
def index(page):
    try:
        return render_template('%s.html' % page)
    except TemplateNotFound:
        abort(404)


@app.route('/v1/subscription', methods=['GET', 'POST'])
def subscription():
    if request.method == 'GET':
        results = query_db("select * from vmess where 1 = 1;")
        print(results)
        data = []
        for v in results:
            print(v)
            vmess = {"index": v["id"], "name": v["name"], "used": v["used"],
                     "ping": 0, "bandwidth": 0}
            data.append(vmess)
        return jsonify(data)
    elif request.method == 'POST':
        print(request.form.get("action"))
        if(request.form.get("action") == "update"):
            req = urllib.request.Request(SUBSCRIPTION_URL)
            req.add_header(
                "User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36")
            with urllib.request.urlopen(req) as f:
                serverListLink = base64.b64decode(
                    f.read()).splitlines()
                if serverListLink:
                    app.logger.info(serverListLink)
                    delete_db()
                    data = []
                    for i in range(len(serverListLink)):
                        serverNode = json.loads(base64.b64decode(
                            bytes.decode(serverListLink[i]).replace('vmess://', '')))
                        print('[' + str(i) + ']' + serverNode['ps'])
                        serverListLink[i] = serverNode
                        data.append(
                            (i, serverNode['ps'], json.dumps(serverNode)))
                    app.logger.info(data)
                    insert_many_db(
                        "insert into vmess(id, name, vmess) values(?,?,?)", data)
            return jsonify({"code": 0})
        elif(request.form.get("action") == "set"):
            index = request.form.get("index")
            result = query_db(
                "select vmess from vmess where id = ?", (index, ), one=True)
            print(result)
            vmess = json.loads(result["vmess"])
            export(vmess, CONFIG_PATH, 'v2config.json')
            export(vmess, '/etc/v2ray/config-ns.json', 'v2config-ns.json')
            restart()
            update_db("update vmess set used = ? where 1 = 1", (0,))
            update_db("update vmess set used = 1 where id = ?", (index,))
            return jsonify({"code": 0})


def export(vmess, path=CONFIG_PATH, template='v2config.json'):
    with open(template, 'r') as t:
        v2rayConf = t.read()
        v2rayConf = v2rayConf.replace("&address", vmess["add"])
        v2rayConf = v2rayConf.replace("&port", str(vmess["port"]))
        v2rayConf = v2rayConf.replace("&alterId", str(vmess["aid"]))
        v2rayConf = v2rayConf.replace("&uuid", vmess["id"])
        v2rayConf = v2rayConf.replace("&path", vmess["path"])
        with open(path, 'w+') as f:
            f.write(v2rayConf)


def restart():
    subprocess.call('systemctl restart v2ray-ns.service', shell=True)
    subprocess.call('systemctl restart v2ray.service', shell=True)


@app.route('/v1/control', methods=['GET', 'POST'])
def control():
    if request.method == 'GET':
        with open(CONTROL_PATH, 'r') as f:
            return f.read()
    elif request.method == 'POST':
        control = request.get_json()
        name = control["name"]
        with open(CONTROL_PATH, 'r') as f:
            control = json.loads(f.read())
            for ctrl in control:
                if ctrl["name"] == name:
                    print(ctrl["script"])
                    return subprocess.call(ctrl["script"], shell=True)


@app.route('/v1/config', methods=['GET', ])
def config():
    with open(CONFIG_PATH, 'r') as f:
        return f.read()


@socketio.on('disconnect', namespace='/ws/status')
def test_disconnect():
    app.logger.info('ws disconnected')


@socketio.on('connect', namespace='/ws/status')
def status_connect():
    app.logger.info("ws connect")


@socketio.on('status', namespace='/ws/status')
def status_all(status):
    app.logger.info("get all status")
    result = {"cpu": psutil.cpu_percent(
        interval=0.2, percpu=True),
        "cpuAve": psutil.cpu_percent(
        interval=0.2),
        "mem": psutil.virtual_memory()._asdict(),
        "swap": psutil.swap_memory()._asdict(),
        "temp": psutil.sensors_temperatures(),
        "uuid": status}
    app.logger.info("emit")
    emit("message", json.dumps(result), namespace="/ws/status")


if __name__ == '__main__':
    socketio.run(app=app, port=8080, debug=True)
