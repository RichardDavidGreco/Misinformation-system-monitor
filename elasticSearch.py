#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests as req
from time import sleep
import json
import re
	
class error(object):
	def __init__(self):
		self.status_code = None
		
		def __str__():
			return (self.status_code==777 and 'requests.ConnectionError')
		
		def _set_status(self, code):
			self.status_code = code
			
		def _get_status(self):
			return self.status_code
		
		status_code = property(_get_status, _set_status)

def handleConnectionError(func):
	e = error()
	e.status_code = 777
	def wrap(*args, **kwargs):
		try:
			print('\033[92mFunction name:- {}'.format(func.__name__))
			result = func(*args, **kwargs)
			print('\033[92mResult:- {}'.format(result))
			return result 
		except req.ConnectionError:
			print('\033[91mrequest.ConnectionError')
			return e
		except KeyError as key:
			print '\033[91mKeyError:-',
			print key
			e.status_code = 200
			return re.match(r'exist_*', func.__name__) and True or e
	return wrap

@handleConnectionError
def get_factories():
	da = 0
	totalFact = []
	tot = -1
	while(tot != 0):
		fact = [f for f in json.loads(req.get('http://localhost:9200/db/factory/_search', data='{{\"from\":{}}}'.format(da), headers={'content-type':'application/json'}).text)['hits']['hits']]
		[totalFact.append(f) for f in fact]
		da = len(totalFact)
		tot = len(fact)
	return totalFact

@handleConnectionError
def get_factory(_id = None, host = None):
	if _id or host:
		return ((_id and json.loads(req.get('http://localhost:9200/db/factory/{}'.format(_id)).text))
				or json.loads(req.get('http://localhost:9200/db/factory/_search?q=host:{}'.format('/'+host)).text)['hits']['hits'][0])
	else:
		raise ValueError("Inserire '_id'=_id oppure 'url'=url")

@handleConnectionError
def get_trustables():
	da = 0
	totalTrust = []
	tot = -1
	while(tot != 0):
		trust = [t for t in json.loads(req.get('http://localhost:9200/db/trustable/_search', data='{{\"from\":{}}}'.format(da), headers={'content-type':'application/json'}).text)['hits']['hits']]
		[totalTrust.append(t) for t in trust]
		da = len(totalTrust)
		tot = len(trust)
	return totalTrust

@handleConnectionError
def get_links(obj=False):
	da = 0
	totalLinks = []
	tot = -1
	if obj:
		while(tot != 0):
			links = [link for link in json.loads(req.get('http://localhost:9200/db/link/_search', data='{{\"from\":{}}}'.format(da), headers={'content-type':'application/json'}).text)['hits']['hits']]
			[totalLinks.append(l) for l in links]
			da = len(totalLinks)
			tot = len(links)
		return totalLinks
	else:
		while(tot != 0):
			links = [link['_source']['url'] for link in json.loads(req.get('http://localhost:9200/db/link/_search', data='{{\"from\":{}}}'.format(da), headers={'content-type':'application/json'}).text)['hits']['hits']]
			[totalLinks.append(l) for l in links]
			da = len(totalLinks)
			tot = len(links)
		return totalLinks

@handleConnectionError
def get_link(_id = None, url = None):
	if _id or url:
		return ((_id and json.loads(req.get('http://localhost:9200/db/link/{}'.format(_id)).text))
				or json.loads(req.get('http://localhost:9200/db/link/_search?q=url:{}'.format('/'+url)).text)['hits']['hits'][0])
	else:
		raise ValueError("Inserire '_id' = _id oppure 'url' = url")

@handleConnectionError
def get_users():
	da = 0
	totalUsers = []
	tot = -1
	while(tot != 0):
		users = [user for user in json.loads(req.get('http://localhost:9200/db/user/_search', data='{{\"from\":{}}}'.format(da), headers={'content-type':'application/json'}).text)['hits']['hits']]
		[totalUsers.append(u) for u in users]
		da = len(totalUsers)
		tot = len(users)
	return totalUsers

@handleConnectionError
def get_user(_id = None, social_id = None):
	if _id or type((None, None))==type(social_id):
		return ((_id and json.loads(req.get('http://localhost:9200/db/user/{}'.format(_id)).text))
				or json.loads(req.get('http://localhost:9200/db/user/_search?q=social_id:{} AND social:{}'.format(social_id[0], social_id[1])).text)['hits']['hits'][0])
	else:
		raise ValueError("Valid arguments: [ _id='object id', social_id=('social id', 'social type') ]")

@handleConnectionError
def store_link(link, host):
	data = '{{\"url\":"{}", \"factory\":\"{}\", \"from\":[], \"shared\":0, \"total\":0}}'.format(link, '/'+host)
	return req.post('http://localhost:9200/db/link', data=data, headers={'content-type':'application/json'}).status_code==201

@handleConnectionError
def store_user(status, social, link):
	store = '{{"user_social_id":"{}", "name":"{}", "social":"{}", "rate":1, "clock":7, "stima":7, "posts":[{{"post_id":"{}", "timestamp":"{}", "link":"{}"}}]}}'.format(
		status['user_social_id'],
		status['name'].encode('utf-8'),
		social,
		status['post_id'],
		status['timestamp'],
		link['_id'])
	return req.post('http://localhost:9200/db/user', data=store, headers={'content-type':'application/json'})

@handleConnectionError
def store_human_control(url):
	store = '{{"url":"{}"}}'.format('/'+url)
	return req.post('http://localhost:9200/db/trustable', data=store, headers={'content-type':'application/json'})

@handleConnectionError
def update_expire(expire, factory):
	return req.post('http://localhost:9200/db/factory/{}/_update'.format(factory['_id']), data='{{"doc":{{"expire":"{0}"}}}}'.format(expire), headers={'content-type':'application/json'})

@handleConnectionError
def update_total(link):
	update_total = '{"script":{"source":"ctx._source.total += 1"}}'
	return req.post('http://localhost:9200/db/link/{}/_update'.format(link['_id']), data=update_total, headers={'content-type':'application/json'})

@handleConnectionError
def update_shared(link):
	update_shared = '{"script":{"source":"ctx._source.shared += 1"}}'
	return req.post('http://localhost:9200/db/link/{}/_update'.format(link['_id']), data=update_shared, headers={'content-type':'application/json'})

@handleConnectionError
def update_from(link, user_obj_id, status):
	update_from = '{{"script":{{"source":"ctx._source.from.add(params.user)", "params":{{"user":{{"user_object_id":"{0}","post_id":"{1}"}}}}}}}}'.format(user_obj_id, status['post_id'])
	return req.post('http://localhost:9200/db/link/{}/_update'.format(link['_id']), data=update_from, headers={'content-type':'application/json'})

@handleConnectionError
def update_posts(status, user, link):
	update_post = '{{"script":{{"source":"ctx._source.posts.add(params.post)", "params":{{"post":{{"post_id":"{}","timestamp":"{}", "link":{}}}}}}}}}'.format(
		status['post_id'],
		status['timestamp'], link['_id'])
	return req.post('http://localhost:9200/db/user/{}/_update'.format(user['_id']), data=update_post, headers={'content-type':'application/json'})

@handleConnectionError
def update_rate(user):
	update_rate = '{"script":{"source":"ctx_source.rate += 1"}}'
	return req.post('http://localhost:9200/db/user/{}/_update'.format(user['_id']), data=update_rate, headers={'content-type':'application/json'})

@handleConnectionError
def update_clock(user, stima = False):
	if stima:
		update_clock = '{{"doc":{{"clock":{}}}}}'.format(stima)
		update_stima = '{{"doc":{{"stima":{}}}}}'.format(stima)
		return (req.post('http://localhost:9200/db/user/{}/_update'.format(user['_id']), data=update_clock, headers={'content-type':'application/json'})
				and req.post('http://localhost:9200/db/user/{}/_update'.format(user['_id']), data=update_stima, headers={'content-type':'application/json'}))
	else:
		update_clock = '{"script":{"source":"ctx_source.clock -= 1"}}'
		return req.post('http://localhost:9200/db/user/{}/_update'.format(user['_id']), data=update_clock, headers={'content-type':'application/json'})

@handleConnectionError
def exist_user(_id = False, social_id = False):
	if _id or type((None, None))==type(social_id):
		return ((social_id
				 and json.loads(req.get('http://localhost:9200/db/user/_search?q=user_social_id:{} AND social:{}'.format(social_id[0], social_id[1])).text)['hits']['total']!=0)
				or (_id and not req.get('http://localhost:9200/db/user/{}'.format(_id)).status_code==404))
	else:
		raise ValueError("Valid arguments: [ _id = 'object id', social_id = ('social id', 'social type') ]")

#PROBLEMIIIIIIIII
@handleConnectionError
def exist_link(_id = False, url = False):
	if _id or url:
		print('/'+url)
		return ((url and json.loads(req.get('http://localhost:9200/db/link/_search?q=url:{}'.format(url)).text)['hits']['total']!=0)
				or (_id and not req.get('http://localhost:9200/db/link/{}'.format(_id)).status_code==404))
	else:
		raise ValueError("Inserire '_id' = _id oppure 'url' = url")
#PROBLEMIIIIIIIII

@handleConnectionError
def exist_factory(_id = False, host = False):
	if _id or host:
		return ((host and json.loads(req.get('http://localhost:9200/db/factory/_search?q=host:{}'.format(host)).text)['hits']['total']!=0)
				or (_id and not req.get('http://localhost:9200/db/factory/{}'.format(_id)).status_code==404))
	else:
		raise ValueError("Inserire '_id' = _id oppure 'host' = host")

@handleConnectionError		
def exist_trustable(_id = False, host = False):
	if _id or host:
		return ((host and json.loads(req.get('http://localhost:9200/db/trustable/_search?q=host:{}'.format(host)).text)['hits']['total']!=0)
				or (_id and not req.get('http://localhost:9200/db/trustable/{}'.format(_id)).status_code==404))
	else:
		raise ValueError("Inserire '_id' = _id oppure 'host' = host")

@handleConnectionError		
def clear_all():
	return req.delete('http://localhost:9200/db')

