import web
import json
import subscription
import config
import control

urls = {
    '/', 'home',
    '/control', control.app,
    '/config', config.app,
    '/subscription', 'subscription'
}
web.config.debug = False
app = web.application(urls, globals())
render = web.template.render('templates/', cache=False)

class home:
    def GET(self):
        return render.response(code)

class subscription:
    def POST(self):
        pass

if __name__ == "__main__":
    app.run()