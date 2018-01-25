# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import sys
sys.path.append('..')
from sina.items import InformationItem,TweetsItem,FollowsItem,FansItem
import pymysql

class MysqlDBPipeline(object):
	def __init__(self):
		self.count = 1
		#self.conn = pymysql.connect(host='localhost',port=3306,user='root',passwd='123456',db='SinaWeibo',use_unicode=True,charset='utf-8',)
		self.conn = pymysql.connect('localhost','root','123456','InformationItem',use_unicode=True,charset='utf8')
		self.cur = self.conn.cursor()


	def process_item(self,item,spider):
	#	print(spider.name)
		print(item)		
		if isinstance(item,InformationItem):
			try:
				print('准备保存至mysql数据库')
				sql = ''
				sql += str('insert into Information(NickName,Gender,City,Url,Num_Fans,Num_Follows,Num_Tweets,Province,Signature)')
				sql += str(' values(\'')
				sql += str(item['NickName'])
				sql += str('\',\'')
				sql += str(item['Gender'])
				sql += str('\',\'')
				sql += str(item['City'])
				sql += str('\',\'')
				sql += str(item['URL'])
				sql += str('\',\'')
				sql += str(item['Num_Fans'])
				sql += str('\',\'')
				sql += str(item['Num_Follows'])
				sql += str('\',\'')
				sql += str(item['Num_Tweets'])
				sql += str('\',\'')
				sql += str(item['Province'])
				sql += str('\',\'')
				sql += str(item['Signature'])
				sql += str('\')')
				print('准备执行的SQL语句')
				print(sql)
				self.cur.execute(sql)
				self.conn.commit()
			except Exception:
				print('执行失败')
				pass
			
				 

class SinaPipeline(object):
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
		print(isinstance(item,InformationItem))
		print(isinstance(item,TweetsItem))
		print(isinstance(item,FollowsItem))
		print(isinstance(item,FansItem))
		if isinstance(item,InformationItem):
			try:
				self.Information.insert(dict(item))
			except Exception:
				pass

		elif isinstance(item,TweetsItem):
			print('微博数据，准入插入数据库')
			try:
				self.Tweets.insert(dict(item))
			except Exception:
				pass
		elif isinstance(item,FollowsItem):
			print('follows的数据是：')
			print(item)
			try:
				self.Follows.insert(dict(item))
			except Exception:
				pass

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

		return item	
	def close_spider(self,spider):
		pass	
'''
