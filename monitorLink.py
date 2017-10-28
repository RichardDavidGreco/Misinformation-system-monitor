#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tweepy
import twitter_scraper
from time import sleep
from BeautifulSoup import BeautifulSoup as bs
import elasticSearch as elastic
import requests as req
import json

class MonitorLink(object):
	def __init__(self, social, link):
		self.link = link
		self.social = social
	
	#TO OVERRIDE FOR TWITTER AND FACEBOOK
	def _search(self):
		return []
	
	#AGGIORNA LE INFORMAZIONI DEL LINK: TOTAL, SHARED E FROM
	def _update_link(self, status, user_obj_id, same_link=False):
		if same_link:
			print('\033[37m\t\t\tUn utente ha ricondiviso il link, aggiornamento...')
			sleep(1)
			return elastic.update_total(self.link).status_code==200
		else:
			print('\033[37m\t\t\tUn nuovo utente ha condiviso il link, aggiornamento...')
			sleep(1)
			return (elastic.update_total(self.link).status_code==200
					and elastic.update_shared(self.link).status_code==200
					and elastic.update_from(self.link, user_obj_id, status).status_code==200)
	
	#AGGIORNA LE INFORMAZIONI SULL'USER: RATE E POST, NEL CASO NON SIA LO STESSO POST
	def _update_user(self, user, status, same_post = False, same_link = False):
		if same_post:
			print('\033[37m\t\tFalso allarme, stesso post!')
			sleep(1)
			return True
		else:
			print('\033[37m\t\tNuovo post, inizio aggiornamento...')
			sleep(1)
			return (elastic.update_posts(status, user, self.link).status_code==200
					and elastic.update_rate(user).status_code==200
					and self._update_link(status, user['_source']['object_id'], same_link = same_link))
	
	#CARICA NUOVO USER
	def _store_user(self, status):
		print('\033[37m\t\tNuovo utente "{}" beccato! Salvataggio...'.format(status['name'].encode('utf-8')))
		sleep(1)
		created = elastic.store_user(status, self.social, self.link)
		return created.status_code==201 and self._update_link(status, json.loads(created.text)['_id'])
	
	#CONTROLLA SE IL POST E' STATO GIA' CONDIVISO OPPURE SE E' ESATTAMENTE LO STESSO POST
	def _shared_yet(self, status):
		user = elastic.get_user(social_id = (status['user_social_id'], self.social))
		print('\033[37m\t\tQuesto utente è già in database "{}", inizio controllo per aggiornamento...'.format(user['_source']['name'].encode('utf-8')))
		sleep(1)
		return self._update_user(
			user,
			status,
			same_post = status['post_id'] in [post['post_id'] for post in user['_source']['posts']],
			same_link = self.link['_id'] in [post['link'] for post in user['_source']['posts']])
	
	def monitor(self):
		print('\033[37mInizio monitoraggio del link "{}" su {}...'.format(self.link['_source']['url'].encode('utf-8'), self.social))
		print('\033[37m\tRicerca delle condivisioni...')
		sleep(1)
		found = self._search()
		print('\033[37m\tFinito!')
		sleep(1)
		# yet = STATUS DI UTENTI GIA' IN STORE
		yet = [status for status in found if elastic.exist_user(social_id = (status['user_social_id'], self.social))]
		# found = STATUS DI UTENTI NON ANCORA IN STORE
		[found.remove(status) for status in yet]
		print(len(found), len(yet))
		print('\033[37mMonitoraggio terminato :-{}'.format(all([self._store_user(status) for status in found]) and all([self._shared_yet(status) for status in yet])))


	
class MonitorLinkTwitter(MonitorLink):
	def __init__(self, link):
		MonitorLink.__init__(self, 'twitter', link)
		twitter = {
			'CONSUMER_KEY' : 'DTSUlnbrAkkO2dT7tmhN5vzvL',
			'CONSUMER_SECRET' : 'CRCK1CN4ut0pbj0jSDKBox7haj2VhTY4w0fyMh5a8kj0ubcGfV',
			'ACCESS_TOKEN' : '840195867919470537-h02K9CVpswdYwuEWlwHEsWEKicP85g9',
			'ACCESS_TOKEN_SECRET' : 'scoDvuv7tkggxpCxSvE0R0FDYATAQElslIYwOoH8SUUZD'
		}
		auth = tweepy.OAuthHandler(twitter['CONSUMER_KEY'], twitter['CONSUMER_SECRET'])
		auth.set_access_token(twitter['ACCESS_TOKEN'], twitter['ACCESS_TOKEN_SECRET'])
		self.api = tweepy.API(auth)

	#CERCA I TWEET CONTENENTI IL LINK
	def _search(self):
		tweets = [self.api.get_status(_id) for _id in twitter_scraper.run_search(self.link['_source']['url'])]
		return [{'name':tweet.user.name, 'user_social_id':tweet.user.id_str, 'post_id':tweet.id_str, 'timestamp':'{} {} {}'.format(tweet.created_at.day, tweet.created_at.month, tweet.created_at.year)} for tweet in tweets]
		





