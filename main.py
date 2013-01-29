#!/usr/bin/env python
from datatable import *
from start import *
from vote import *
from result import *
import webapp2
import jinja2
from google.appengine.api import memcache
from google.appengine.ext import db
import logging
import os
from datetime import datetime

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MainHandler(webapp2.RequestHandler):
  
  def get(self):
    template = jinja_environment.get_template('index.html')
    template_values = {}
    self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([
  ('/', MainHandler),
  ('/start', StartHandler),
  ('/result', ResultHandler),
  ('/vote', VoteHandler)],
  debug=True)
