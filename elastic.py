#!/usr/bin/env python
# -*- coding: utf-8 -*-

#LINK
{
	"url":"www.link.com",
	"factory":"http://www.factory.com",
	"from":[
		{"user_object_id":"xxx", "post_id":"xxx"}
	],
	"shared":1,
	"total":1
}

#FACTORY/TRUSTABLE/HUMAN
{
	"host":"https://voxnews.info",
	"expire":"19 10 2017"
}

#USER
{
	"social_user_id":0,
	"name":"name",
	"social":"facebook/twitter",
	"rate":1,
	"clock":7,
	"stima":7,
	"posts":[
		{"post_id":"xxx", "timestamp":"xxx", "link":"link_id"}	
	]
}

#WRAPPER
{
	"_index" : "db",
	"_type" : "factory",
	"_id" : "xxx",
	"_score" : 1.0,
	"_source" : {
	
	}
}