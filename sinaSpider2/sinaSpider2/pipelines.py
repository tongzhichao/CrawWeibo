# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sys
sys.path.append('/home/tzc/weibo/sinaSpider2/')


import pymongo
from sinaSpider2.items import InformationItem,TweetsItem

class MongoDBPipleline(object):
	def __init__(self):
		try:
			print('链接数据库')
			client = pymongo.MongoClient('localhost',27017)
			db = client['Sina']
			self.Information = db['Information']
			self.Tweets = db['Tweets']
			self.Follows = db['Follows']
			self.Fans = db['Fans']
		except Exception:
			print('链接数据库失败')

	def process_item(self, item, spider):
		print('进入pipeline函数')
		print(isinstance(item,InformationItem))	
		print(isinstance(item,TweetsItem))	
		print(item)
		print(type(item))	
		if isinstance(item,InformationItem):
			try:
				print('准备插入information数据库')
				self.Information.insert(dict(item))
			except Exception:
				print('插入失败')
				pass

		elif isinstance(item,TweetsItem):
			try:
				print('准备插入tweetitem数据库')
				self.Tweets.insert(dict(item))
			except Exception:
				print('插入失败')
				pass
		return item
		'''
		elif isinstance(item,FollowsItem):
			followsItems = dict(item)
			follows = followsItems.pop('follows')
			for i in range(len(follows)):
				followsItems[str(i+1)] = follows[i]
			try:
				self.Follows.insert(followsItems)
			except Exception:
				pass

		elif isinstance(item,FansItem):
			fansItems = dict(item)
			fans = fansItems.pop('fans')
			for i in range(len(fans)):
				fansItems[str(i+1)] = fans[i]
			try:
				self.Fans.insert(fansItems)
			except Exception:
				pass
		'''
#		return item	
	
