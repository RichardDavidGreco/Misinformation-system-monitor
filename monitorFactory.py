#!/usr/bin/env python
# -*- coding: utf-8 -*-

import elasticSearch as elastic
import requests as req
import re
import json
from datetime import datetime
from bs4 import BeautifulSoup as bs

class MonitorFactory(object):
	def __init__(self, factory_obj):
		self.now = datetime.now()
		self.factory = factory_obj

	#CONTROLLA CHE LA DATA DI 'EXPIRE' OTTENUTA SIA VERITIERA
	def _onest(self, verify):
		return ((((self.now.year == verify.year
				   and
				   ((self.now.month == verify.month
					 and
					 self.now.day < verify.day)
					or
					self.now.month < verify.month))
				  or
				  (self.now.year+1 == verify.year
				   and
				   (self.now.month%12)+1 == verify.month))
				 and '{} {} {}'.format(verify.day, verify.month, verify.year))
				or datetime.strptime(self._create_expire(), '%d %m %Y'))

	#CREA UNA DATA DI 'EXPIRE' VERITIERA (1 SETTIMANA CIRCA)
	def _create_expire(self):
		return '{} {} {}'.format(
			(self.now.day+7)%28+1,
			((self.now.day>21 and (self.now.month%12)+1) or self.now.month),
			((self.now.month==12 and self.now.year+1) or self.now.year))

	#SETTA LA DATA DI EXPIRE NELL'OGGETTO FACTORY
	def _set_expire(self):
		try:
			expire = self._onest(datetime.strptime(dict(req.get(self.factory['_source']['host']).headers)['expires'], '%a, %d %b %Y %H:%M:%S %Z'))
			return elastic.update_expire(expire, self.factory).status_code==200
	
		#EXCEPT NEL CASO NON ESISTA UNA DATA DI 'EXPIRE' NELL'HEADER DELLA RISPOSTA O NON SIA CONFORME
		except (KeyError, ValueError) :
			expire = datetime.strptime(self._create_expire(), '%d %m %Y')
			return elastic.update_expire(expire, self.factory).status_code==200
	
	#OTTIENE L'URL SENZA PROTOCOLLO
	def _get_url(self, href):
		if len(href.split('http://'))==2:
			return href.split('http://')[1]
		else:
			return href.split('https://')[1]

	#OTTIENE TUTTI I LINK DELLA PAGINA SCARICATA E CARICA I NUOVI LINK TROVATI
	def _crawl(self):
		links = set([
			self._get_url(true_link.get('href')) for true_link in
					 [link for link in bs(req.get(self.factory['_source']['host']).text, "lxml").findAll('a') if link.has_attr('href')]
			if re.match(self.factory['_source']['host']+'*', true_link.get('href'))
		])
		return all([elastic.store_link(link, self.factory['_source']['host']) for link in links if link not in elastic.get_links()])
	
	#CONTROLLA CHE LA DATA DI 'EXPIRE' SIA SCADUTA E NEL CASO EFFETTUA LA RICERCA DI NUOVI LINK
	def monitor(self):
		print('\033[37mInizio monitoraggio della factory:- {}'.format(self.factory['_source']['host']))
		if self.now > datetime.strptime(self.factory['_source']['expire'], '%d %m %Y'):
			print('\033[37mMonitoraggio terminato:- {}'.format(self._set_expire() and self._crawl()))















