#!/usr/bin/env python
from datatable import *
import webapp2
import jinja2
from google.appengine.api import memcache
from google.appengine.ext import db
import logging
import os
import uuid

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class VoteHandler(webapp2.RequestHandler):
  
  def get_vote(self, name):
    all_data = db.GqlQuery("SELECT * "
      "FROM Election WHERE name = :1",
      name)
    logging.info('fetch data from database')
    data = {}
    for d in all_data:
      data[d.cid] = d.candidate
    result = []
    for i in range(1, len(data) + 1):
      result.append(data[i])
    return result

  def get(self):
    name = self.request.get('name').lower()
    result = self.get_vote(name)
    if not result:
      self.redirect('/noelection.html')
      return
    template = jinja_environment.get_template('vote.html')
    template_values = {}
    template_values['candidates'] = result
    template_values['election'] = name
    self.response.out.write(template.render(template_values))

  def post(self):
    name = self.request.get('name').lower()
    candidates = self.get_vote(name)
    if not candidates:
      self.redirect('/noelection.html')
      return
    logging.info(name)
    vid = str(uuid.uuid1())
    for i in range(0, len(candidates)):
      vote = Vote()
      vote.election = name
      vote.candidate = candidates[i]
      vote.cid = i + 1
      vote.vid = vid
      try:
        vote.rank = int(self.request.get('election_%d' % i))
      except:
        vote.rank = 0
      logging.info('%s %d' % (vote.candidate, vote.rank))
      vote.put()
    self.redirect('/votesuccess.html')
    return

