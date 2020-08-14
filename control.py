import web
import json

urls = {
    '/', 'control'
}
web.config.debug = False
app = web.application(urls, globals())
render = web.template.render('templates/', cache=False)

class control: 
  def POST(self):
    pass
