#!/usr/bin/env python
# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup as bs
import requests as req
from time import sleep
import json

def construct_url(query, max_position=None):
	return (max_position is None
			and 'https://www.twitter.com/i/search/timeline?q="{}"&f=tweets'.format(query)
			or 'https://www.twitter.com/i/search/timeline?q="{}"&f=tweets&max_position={}'.format(query, max_position))

def single_search(url):
	try:
		res = req.get(url, headers={'user-agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'})
		return json.loads(res.text)
	except:
		sleep(3)
		print('\033[91merror sleep')
		return single_search(url)

def run_search(query):
	min_tweet = None
	ids = []
	url = construct_url(query)
	res = single_search(url)
	while res is not None and res['items_html'] is not None:
		tmp = [li['data-item-id'] for li in bs(res['items_html']).findAll("li") if li.get('data-item-id')]
		[ids.append(t) for t in tmp]
		
		if len(tmp)==0:
			break
		
		if min_tweet is None:
			min_tweet = tmp[0]
		max_tweet = tmp[-1]
		
		if min_tweet is not max_tweet:
			if "min_position" in res.keys():
				max_position = res['min_position']
			else:
				max_position = "TWEET-{}-{}".format(max_tweet, min_tweet)
			url = construct_url(query, max_position=max_position)
			print('\033[94mdelay sleep')
			sleep(3)
			res = single_search(url)
	return ids