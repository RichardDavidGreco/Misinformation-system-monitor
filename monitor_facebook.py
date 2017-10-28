#!/usr/bin/env python
# -*- coding: utf-8 -*-

import elasticSearch as el
import requests as req
import json

token_short = 'EAAD7MBgxZABcBABcZB3vBnVU22WevATMl6ZAYLlojzZAd9X9daPJRfWBUMtVzCUfZCw4X2ZAA6wCQNCY79LVTLn31yKegiDBeRQ5M8tTXXs3g3L7Mg5MPFe7CvQYS2wUZCIZCHMYGgBoMZA1ZCccnm1MlDkVl4mJxtXYCZCO2jVFrNsjMKiUCTcxAf1Yizy46sjOAtAyFMnXTI6QgZDZD'
token_long = None
coockie = {'act':'1508751274568/13', 'c_user':'100005177442962', 'datr':'xSS7VzDLAfQ4IWoP9gNbYHpj', 'dpr':'1', 'fr':'0u9XE58ua00WomfoS.AWVAVamC6HPKHAfnuXPUznWqpDE.BXuyTO.bf.Fnn.0.0.BZ7bf3.AWUAGw51', 'presence':'EDvF3EtimeF1508751344EuserFA21B05177442962A2EstateFDutF1508751344092CEchFDp_5f1B05177442962F5CC', 'sb':'ziS7V_s1B_TAaI8hfIAXQk-P', 'wd':'1301x250', 'xs':'21:LRG6awA0v8kgnw:2:1471893159:966:10282'}

def get_long_token():
	return json.loads(req.get('https://graph.facebook.com/oauth/access_token?', params={'grant_type':'fb_exchange_token', 'client_id':'276183982892055', 'client_secret':'6dfa8e4bedc15b07f61458df2e1b5139', 'fb_exchange_token':token_short}).text)['access_token']

def monitor_facebook(link):
	found = search(link)