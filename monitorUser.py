#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tweepy
from datetime import datetime
import elasticSearch as elastic
import requests as req
import json
import math

class MonitorUser(object):
	def __init__(self, social, user):
		self.user = user
		self.social = social
		self._alpha = 0.5
		self._update_clock = True
	
	def _get_url(self, href):
		if len(href.split('http://'))==2:
			return href.split('http://')[1]
		else:
			return href.split('https://')[1]
	
	def _get_recent_posts(self):
		pass
	
	def _control_post(self, post):
		pass
	
	def _create_status(self, post):
		pass
	
	def _update_clock(self, first_post_timestamp):
		if self._update_clock:
			self._update_clock = False
			last_timestamp = datetime.strptime(self.user['posts'][-1]['timestamp'], '%d %m %Y')
			delta = math.sqrt((first_post_timestamp-last_timestamp)**2)
			t = self.user['_source']['stima']
			t = (t*self._aplha + delta*self._alpha)<1 and int(floor((t*self._aplha + delta*self._alpha))) or 1
			return elastic.update_clock(self.user, stima = t)
		else:
			return True
		
	def _update_user(self, status, link):
		return elastic.update_posts(status, self.user, link) and elastic.update_rate(self.user)
	
	def _update_link(self, status, link):
		return ((link['_id'] not in [post['link'] for post in self.user['posts']] and elastic.update_shared(link))
				or
				(elastic.update_total(link) and elastic.update_from(link, self.user['_id'], status)))
		
	def _control_factory(self, status, url):
		host = url.split(req.get(url).request.path_url)[0]
		return ((elastic.exist_factory(host = host)
				 and elastic.store_link(link, host)
				 and elastic.update_from(link, self.user['_id'], status)
				 and self._update_user(status, elastic.get_link(url = url))
				 and self._update_clock())
				or elastic.exist_trustable(host = host)
				or elastic.store_human_control(url).status_code == 201)
	
	def _control_link(self, status, url):
		if status['post_id'] not in [post['post_id'] for post in self.user['posts']]:
			return (elastic.exist_link(url = url)
					and self._update_clock(datetime.strptime(status['timestamp'], '%d %m %Y')))
					and self._update_link(status, elastic.get_link(url = url))
					and self._update_user(status, elastic.get_link(url = url))
					or self._control_factory(status, url)
		else:
			return True
			
	def _control_user(self):
		posts = self._get_recent_posts()
		return all([self._control_post(post) for post in posts])
	
	def monitor():
		return (self.user['_source']['clock']==0 and self._control_user(self.user)) or elastic.update_clock(self.user).status_code==200

class MonitorUserTwitter(MonitorUser):
	def __init__(self, user):
		MonitorUser.__init__(self, 'twitter', user)
		twitter = {
			'CONSUMER_KEY' : 'DTSUlnbrAkkO2dT7tmhN5vzvL',
			'CONSUMER_SECRET' : 'CRCK1CN4ut0pbj0jSDKBox7haj2VhTY4w0fyMh5a8kj0ubcGfV',
			'ACCESS_TOKEN' : '840195867919470592-h02K9CVpswdYwuEWlwHEsWEKicP85g9',
			'ACCESS_TOKEN_SECRET' : 'scoDvuv7tkggxpCxSvE0R0FDYATAQElslIYwOoH8SUUZD'
		}
		auth = tweepy.OAuthHandler(twitter['CONSUMER_KEY'], twitter['CONSUMER_SECRET'])
		auth.set_access_token(twitter['ACCESS_TOKEN'], twitter['ACCESS_TOKEN_SECRET'])
		self.api = tweepy.API(auth)
	
	def _get_recent_posts(self):
		last_tweet = max([post['post_id'] for post in self.user['posts']])
		stats = []
		while(True):
			tweets = self.api.user_timeline(self.user['social_id'], since_id = last_tweet)
			if len(tweets)==0:
				break
			[stats.append(self._create_status(tweet)) for tweet in tweets]
			last_post = tweets[0].id
		return stats
	
	def _create_status(self, post):
		return {'name':post.user.name, 'social_user_id':post.user.id_str, 'post_id':post.id_str, 'timestamp':'{} {} {}'.format(post.created_at.day, post.created_at.month, post.created_at.year)}

	def _control_post(self, post):
		return (len(post.entities['urls'])==0
				or all([self._control_link(self._create_status(post), self._get_url(url['expanded_url'])) for url in post.entities['urls']]))

	


	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	