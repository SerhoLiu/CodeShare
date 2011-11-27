import sae
import tornado.wsgi

from urls import urls
from settings import settings

app = tornado.wsgi.WSGIApplication(urls,**settings)

application = sae.create_wsgi_app(app)