#!/usr/bin/env python
from datatable import *
import webapp2
import jinja2
from google.appengine.api import memcache
from google.appengine.ext import db
import logging
import os

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class StartHandler(webapp2.RequestHandler):
  
  def get_vote(self, name):
    all_data = db.GqlQuery("SELECT * "
      "FROM Election WHERE name = :1",
      name)
    logging.info('fetch data from election')
    exists = False
    for d in all_data:
      exists = True
      break
    return exists

  def get(self):
    duplicate = self.request.get('duplicate')
    if not duplicate:
      duplicate = False
    else:
      duplicate = True
    template = jinja_environment.get_template('start.html')
    template_values = {}
    template_values['duplicate'] = duplicate
    self.response.out.write(template.render(template_values))

  def post(self):
    name = self.request.get('election').lower().strip()
    candidate = self.request.get('candidates').lower()
    if self.get_vote(name):
      self.redirect('/start?duplicate=1')
    else:
      logging.info(name)
      candidates = candidate.strip().replace('\n', ',').split(',')
      logging.info(candidates)
      candidate_set = set()
      for i in range(0, len(candidates)):
        candidates[i] = candidates[i].strip()
        if not candidates[i]:
          continue
        candidate_set.add(candidates[i])
      index = 1
      for candidate in candidate_set:
        logging.info('new candidate %s' % candidate)
        election = Election()
        election.name = name
        election.candidate = candidate
        election.cid = index
        election.put()
        index += 1
      self.redirect('/electionsuccess.html')
    return

