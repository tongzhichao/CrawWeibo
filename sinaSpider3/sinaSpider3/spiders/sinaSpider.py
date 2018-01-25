#coding= utf-8
#import ssl
import re,logging
import datetime
import sys
#sys.path.append('..')
import requests
from lxml import etree
from scrapy_redis.spiders import RedisSpider


from scrapy.selector import Selector
from scrapy.http import Request
sys.path.append('/home/tzc/weibo/sinaSpider3')
#from items import InformationItem, TweetsItem, FollowsItem, FansItem
from sinaSpider3.weiboID import weiboID
from sinaSpider3.items import InformationItem,TweetsItem,RelationshipsItem
#ssl._create_default_https_context = ssl._create_unverified_context
#reload(sys)
#sys.setdefaultencoding('utf8')
class Spider(RedisSpider):
	name = 'sinaSpider'
	host = 'https://weibo.cn'
	#start_urls = [
        #5235640836, 5676304901, 5871897095, 2139359753, 5579672076, 2517436943, 5778999829, 5780802073, 2159807003,
        #1756807885, 3378940452, 5762793904, 1885080105, 5778836010, 5722737202, 3105589817, 5882481217, 5831264835,
        #2717354573, 3637185102, 1934363217, 5336500817, 1431308884, 5818747476, 5073111647, 5398825573, 2501511785,
	#]
	redis_key = 'sinaSpider:start_urls'
	start_urls = list(set(weiboID))
	logging.getLogger('request').setLevel(logging.WARNING)


	

	def start_requests(self):
		i = 0
		for url in self.start_urls:
			i = i+1
			print('进入循环后，加1得到i的值：%s' % i)
			yield Request(url= 'https://weibo.cn/%s/info' % url,callback=self.parse_information)

	
		


	

	def parse_information(self,response):
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

		
		urlothers = "https://weibo.cn/attgroup/opening?uid=%s" % ID
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
		yield Request(url ="https://weibo.cn/%s/profile?filter=1&page=1" % ID, callback=self.parse_tweets, dont_filter=True)
		yield Request(url = "https://weibo.cn/%s/follow" % ID, callback=self.parse_relationship, dont_filter=True)
		yield Request(url = "https://weibo.cn/%s/fans" % ID,   callback=self.parse_relationship, dont_filter=True)

	def parse_tweets(self,response):
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
			
			yield tweetsItems

		url_next = selector.xpath('//div[@class="pa" and @id="pagelist"]/form/div/a[text()="下页"]/@href').extract()
		if url_next:
			yield Request(url=self.host + url_next[0], callback=self.parse_tweets,dont_filter=True)
	def parse_relationship(self,response):
			
			selector = Selector(response)
			if '/follow' in response.url:
				ID = re.findall('(\d+)/follow',response.url)[0]
				flag = True
			else:
				ID = re.findall('(\d+)/fans',response.url)[0]
				flag = False
			urls = selector.xpath('body/table/tr/td/a[text()="关注他"or text()="关注她"]/@href').extract()
			uids = re.findall('uid=(\d+)',';'.join(urls),re.S)
			for uid in uids:
				relationshipsItem = RelationshipsItem()
				relationshipsItem['Host1'] = ID if flag else uid
				relationshipsItem['Host2'] = uid if flag else ID
				yield relationshipsItem
				yield Request(url = "https://weibo.cn/%s/info" % uid, callback=self.parse_information)
			next_url = selector.xpath('//a[text()="下页"]/@href').extract()
			if next_url:
				yield Request(url = self.host + next_url[0],callback=self.parse_relationship,dont_filter=True)

'''
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
'''
