#coding= utf-8
#import ssl
import re
import datetime
import sys
#sys.path.append('..')
import requests
from lxml import etree
from scrapy_redis.spiders import RedisSpider
from sinaSpider2.weiboID import weiboID

from scrapy.selector import Selector
from scrapy.http import Request
#sys.path.append('..')
#from items import InformationItem, TweetsItem, FollowsItem, FansItem
from sinaSpider2.items import InformationItem
#ssl._create_default_https_context = ssl._create_unverified_context
class Spider(RedisSpider):

	name = 'informationSpider'
	host = 'http://weibo.cn'
	#start_urls = [
        #5235640836, 5676304901, 5871897095, 2139359753, 5579672076, 2517436943, 5778999829, 5780802073, 2159807003,
        #1756807885, 3378940452, 5762793904, 1885080105, 5778836010, 5722737202, 3105589817, 5882481217, 5831264835,
        #2717354573, 3637185102, 1934363217, 5336500817, 1431308884, 5818747476, 5073111647, 5398825573, 2501511785,
	#]
	redis_key = 'informationSpider:start_urls'
	start_urls = []
	for ID in weiboID:
		url = url_information1 = 'http://weibo.cn/%s/info' % ID
		start_urls.append(url)

	

	def start_requests(self):
		i = 0
		for url in self.start_urls:
			i = i+1
			print('进入循环后，加1得到i的值：%s' % i)
			yield Request(url= url,callback=self.parse)

	
		


	

	def parse(self,response):
		'''抓取个人信息2'''
		informationItems = InformationItem()
		selector = Selector(response)
		ID = re.findall('weibo\.cn/(\d+)',response.url)[0]
		text1 = ";".join(selector.xpath('body/div[@class="c"]/text()').extract())
		print('text1的数据是：')
		print(text1)
		nickname = re.findall('昵称[:|：](.*?);', text1)  # 昵称
		gender = re.findall('性别[:|：](.*?);', text1)  # 性别
		place = re.findall('地区[:|：](.*?);', text1)  # 地区（包括省份和城市）
		signature = re.findall('简介[:|：](.*?);', text1)  # 个性签名
		birthday = re.findall('生日[:|：](.*?);', text1)  # 生日
		sexorientation = re.findall('性取向[:|：](.*?);', text1)  # 性取向
		marriage = re.findall('感情状况[:|：](.*?);', text1)  # 婚姻状况
		url = re.findall('互联网[:|：](.*?);', text1)  # 首页链接
		print('nieckname和gender的数据是：')
		print(nickname)
		print(gender)
		if nickname:
			informationItems["NickName"] = nickname[0]
		if gender:
			informationItems['Gender'] = gender[0]
		if place:
			place = place[0].split(' ')
			informationItems['Province'] = place[0]
			if len(place) > 1:
				informationItems['City'] = place[1]
		if signature:
			informationItems['Signature'] = signature[0]
		if birthday:
			try:
				birthday = datatime.datetime.strptime(birthday[0],"%Y-%m-%d")
				informationItems["Birthday"] = birthday - datetime.timedelta(hours=8)
			except Exception:
				pass

		if sexorientation:
			if sexorientation[0] == gender[0]:
				informationItems["Sex_Orientation"] = "gay"
			else:
				informationItems["Sex_Orientation"] = "Heterosexual"
		if marriage:
			informationItems['Marriage'] = marriage[0]
		
		if url:
			informationItems["URL"] = url[0]

		
		urlothers = "http://weibo.cn/attgroup/opening?uid=%s" % ID
		r = requests.get(urlothers, cookies=response.request.cookies)
		if r.status_code == 200:
			selector = etree.HTML(r.content)
			texts = ';'.join(selector.xpath('//div[@class="tip2"]/a/text()'))
			print('texts的数据是')
			print(texts)
			if texts:
				num_tweets = re.findall('微博\[(\d+)\]', texts)#微博数
				num_follows = re.findall('关注\[(\d+)\]', texts) #关注数
				num_fans = re.findall('粉丝\[(\d+)\]', texts)#粉丝数
				if num_tweets:
					informationItems['Num_Tweets'] = int(num_tweets[0])
				if num_follows:
					informationItems['Num_Follows'] = int(num_follows[0])
				if num_fans:
					informationItems['Num_Fans'] = int(num_fans[0])
		print('informationItems的数据是：')
		print(informationItems)
		print(type(informationItems))
		print(isinstance(informationItems,InformationItem))
		yield informationItems

		urlFollows = 'http://weibo.cn/%s/follow' % ID
		idFollows = self.getNextID(urlFollows,response.request.cookies)
		for ID in idFollows:
			url = 'http://weibo.cn/%s/info' % ID
			yield Request(url= url,callback = self.parse)

	def getNextID(self,url,cookies):
		
		IDs = []
		r = requests.get(url=url,cookies = cookies)
		if r.status_code == 200:
			selector = etree.HTML(r.content)
			texts = selector.xpath('body/table/tr/td/a[text()="关注他"or text()="关注她"]/@href')
			IDs = re.findall('uid=(\d+)',';'.join(texts),re.S)
		return IDs

