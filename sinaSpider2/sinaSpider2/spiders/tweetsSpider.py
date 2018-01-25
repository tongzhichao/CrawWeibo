#coding= utf-8

import re
import datetime
import sys
#sys.path.append('..')
import  requests
from lxml import etree
from scrapy_redis.spiders import RedisSpider
from sinaSpider2.weiboID import weiboID

from scrapy.selector import Selector
from scrapy.http import Request
sys.path.append('..')
from sinaSpider2.items import  TweetsItem
#import ssl
#ssl._create_default_https_context = ssl._create_unverified_context
class Spider(RedisSpider):

	name = 'tweetsSpider'
	host = 'http://weibo.cn'
	#start_urls = [
        #5235640836, 5676304901, 5871897095, 2139359753, 5579672076, 2517436943, 5778999829, 5780802073, 2159807003,
        #1756807885, 3378940452, 5762793904, 1885080105, 5778836010, 5722737202, 3105589817, 5882481217, 5831264835,
        #2717354573, 3637185102, 1934363217, 5336500817, 1431308884, 5818747476, 5073111647, 5398825573, 2501511785,
	#]
	redis_key = 'tweetsSpider:start_urls'
	start_urls = []
	for ID in weiboID:
		url =  "http://weibo.cn/%s/profile?filter=1&page=1" % ID
		start_urls.append(url)

	

	def start_requests(self):
		for url in self.start_urls:
			yield Request(url=url,callback=self.parse)

		
	def parse(self,response):
		'''抓取微博数据'''
		selector = Selector(response)
		ID = re.findall('weibo\.cn/(\d+)',response.url)[0]
		tweets = selector.xpath('body/div[@class="c" and @id]')
		print('tweets的数据是：')
		print(tweets)
		items =[]
		for tweet in tweets:
			tweetsItems = TweetsItem()
			id = tweet.xpath('@id').extract_first()  # 微博ID
			content = tweet.xpath('div/span[@class="ctt"]/text()').extract_first()  # 微博内容
			print('微博内容为：',content)
			#cooridinates = tweet.xpath('div/a/@href').extract_first()  # 定位坐标
			like = re.findall('赞\[(\d+)\]', tweet.extract())  # 点赞数		
			transfer = re.findall('转发\[(\d+)\]', tweet.extract())  # 转载数
			comment = re.findall('评论\[(\d+)\]', tweet.extract())  # 评论数
			others = tweet.xpath('div/span[@class="ct"]/text()').extract_first()  # 求时间和使用工具（手机或平台）
			tweetsItems["ID"] = ID  
			tweetsItems["_id"] = ID  + "-" + id
			if content:
				tweetsItems["Content"] = content.strip("[位置]")  # 去掉最后的"[位置]"
			#if cooridinates:
			#	cooridinates = re.findall('center=([\d|.|,]+)', cooridinates)
			#	if cooridinates:
			#		tweetsItems["Co_oridinates"] = cooridinates[0]
			if like:
				tweetsItems["Like"] = int(like[0])
			if transfer:
				tweetsItems["Transfer"] = int(transfer[0])
			if comment:
				tweetsItems["Comment"] = int(comment[0])
			if others:
				others = others.split("来自")
				tweetsItems["PubTime"] = others[0]
				if len(others) == 2:
					tweetsItems["Tools"] = others[1]
			print('tweetsitems的数据是：')
			print(tweetsItems)
			print(isinstance(tweetsItems,TweetsItem))
			yield tweetsItems
#			items.append(tweetsItems)
#		return items
		
			url_next = selector.xpath('//div[@class="pa" and @id="pagelist"]/form/div/a[text()="下页"]/@href').extract()
			if url_next:
				yield Request(url=self.host + url_next[0], callback=self.parse)
			else:
				urlFollows = "http://weibo.cn/%s/follow" % ID
				idFollows = self.getNextID(urlFollows,response.request.cookies)
				for ID in idFollows:
					url = "http://weibo.cn/%s/profile?filter=1&page=1" % ID
					yield Request(url=url,callback=self.parse)



	def getNextID(self,url,cookies):
			IDs = []
			r = requests.get(url=url,cookies = cookies)
			if r.status_code == 200:
				selector = etree.HTML(r.content)
				texts = selector.xpath('body/table/tr/td/a[text()="关注他"or text()="关注她"]/@href')
				IDs = re.findall('uid=(\d+)',';'.join(texts),re.S)
			return IDs

