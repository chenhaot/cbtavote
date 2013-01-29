#!/usr/bin/env python
from datatable import *
import webapp2
import jinja2
from google.appengine.api import memcache
from google.appengine.ext import db
import logging
import collections
from operator import itemgetter
import os

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class ResultHandler(webapp2.RequestHandler):
  
  def get_vote(self, name):
    logging.info(name)
    all_data = db.GqlQuery("SELECT * "
        "FROM Vote where election = :1", name)
    logging.info('fetch votes from database')
    data = collections.defaultdict(dict)
    count = {}
    for d in all_data:
      rank = d.rank
      if d.candidate not in count:
        count[d.candidate] = collections.defaultdict(int)
      count[d.candidate][rank] += 1
      if rank > 0:
        data[d.vid][d.candidate] = rank
    votes = []
    for v in data:
      sorted_dict = sorted(data[v].iteritems(), key=itemgetter(1))
      votes.append([k[0] for k in sorted_dict])
    return (votes, count)


  def eliminate(self, votes, all_possible, logs, candidates):
    result = collections.defaultdict(int)
    for v in votes:
      chosen = None
      for c in v:
        if c in all_possible:
          chosen = c
          break
      if chosen:
        result[chosen] += 1
    for c in all_possible:
      if c not in result:
        result[c] = 0
    sorted_dict = sorted(result.iteritems(), key=itemgetter(1),
        reverse=True)
    total = sum([k[1] for k in sorted_dict])
    if sorted_dict[0][1] > total / 2:
      # selected, it is already majority
      for c in all_possible:
        if c != sorted_dict[0][0]:
          candidates.append(c)
      for c in candidates:
        if c in all_possible:
          all_possible.remove(c)
      candidates.append(sorted_dict[0][0])
    else:
      candidates.append(sorted_dict[-1][0])
      all_possible.remove(sorted_dict[-1][0])
      if len(sorted_dict) == 2:
        # tie exists
        candidates.append(sorted_dict[0][0])
    log_str = []
    for (k, v) in sorted_dict:
      log_str.append('<tr><td>%s</td><td>%d</td></tr>' % (k, v))
    logs.append('\n'.join(log_str))
    return

  def run_instant_off(self, votes):
    candidates = []
    all_possible = set()
    # get all possible candidates
    for v in votes:
      for c in v:
        all_possible.add(c)
    logs = []
    while len(all_possible) > 1:
      self.eliminate(votes, all_possible, logs, candidates)
      logging.info(all_possible)
    logging.info(candidates)
    candidates.reverse()
    return (candidates, logs)

  def get(self):
    name = self.request.get('name').lower().strip()
    (result, count) = self.get_vote(name)
    if not result:
      self.redirect('/noelection.html')
      return
    template = jinja_environment.get_template('result.html')
    (candidates, logs) = self.run_instant_off(result) 
    template_values = {}
    template_values['total'] = len(candidates)
    template_values['candidates'] = candidates
    template_values['count'] = count
    template_values['logs'] = logs
    self.response.out.write(template.render(template_values))


