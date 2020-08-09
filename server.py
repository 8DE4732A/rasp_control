import web
import subscription

urls = {
    '/', 'home',
    '/control', 'control'
    '/config', 'config'
}

app = web.application(urls, globals())

class home:
    def GET(self):
        return ""

