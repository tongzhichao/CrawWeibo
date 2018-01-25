#coding= utf-8
import requests
import re
import datetime
import sys
#sys.path.append('..')
from lxml import etree
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request
sys.path.append('..')
from sina.items import InformationItem, TweetsItem, FollowsItem, FansItem

class Spider(CrawlSpider):

	name = 'sinaSpider'
	host = 'http://weibo.cn'
	#start_urls = [
        #5235640836, 5676304901, 5871897095, 2139359753, 5579672076, 2517436943, 5778999829, 5780802073, 2159807003,
        #1756807885, 3378940452, 5762793904, 1885080105, 5778836010, 5722737202, 3105589817, 5882481217, 5831264835,
        #2717354573, 3637185102, 1934363217, 5336500817, 1431308884, 5818747476, 5073111647, 5398825573, 2501511785,
	#]
	start_urls = [5871897095,5778999829]
	scrawl_ID = set(start_urls)
	finish_ID = set()

	def start_requests(self):
		while self.scrawl_ID.__len__():
#			print('未爬取的列表长度为：')
#			print(self.scrawl_ID.__len__())
			ID = self.scrawl_ID.pop() #取出用户ID
#			self.finish_ID.add(ID) #标志已爬取
			ID = str(ID)
#			follows = []
#			followsItems = FollowsItem()
#			followsItems['_id'] = ID 
#			followsItems['follows'] = 
#			fans = []
#			fansItems = FansItem()
#			fansItems['_id'] = ID 
#			fansItems['fans'] = fans 
#			
	#		url_follows = 'http://weibo.cn/%s/follow' % ID #该用户的关注人页面
	#		url_fans = "http://weibo.cn/%s/fans" % ID #该用户的粉丝人页面
	#		url_tweets = "http://weibo.cn/%s/profile?filter=1&page=1" % ID #该用户发的微博列表页面
	#		url_information0 = "http://weibo.cn/attgroup/opening?uid=%s" % ID #该用户的分组页
			url_info = 'http://weibo.cn/%s/info' % ID
			yield Request(url= url_info,callback=self.parse1)
	#		yield Request(url=url_follows,meta={"item": followsItems, "result": follows},callback = self.parse3) #爬关注人

	#		yield Request(url=url_fans,meta={"item": fansItems, "result": fans},callback=self.parse3)
	#		yield Request(url=url_information0,meta={"ID":ID},callback=self.parse0)
	#		yield Request(url=url_tweets,meta={"ID":ID},callback=self.parse2)

	#		print('奇怪为什么没有执行循环')			
	


#	def parse0(self,response):
#		'''爬取个人信息1'''
#		informationItems = InformationItem()
#		selector = Selector(response)
#		text0 = selector.xpath('body/div[@class="u"]/div[@class="tip2"]').extract_first()
#		print('text0匹配的数据是：')
#		print(text0)
#		if text0:
#			num_tweets = re.findall('微博\[(\d+)\]', text0)#微博数
#			num_follows = re.findall('关注\[(\d+)\]', text0) #关注数
#			num_fans = re.findall('粉丝\[(\d+)\]', text0)#粉丝数
#			if num_tweets:
#				informationItems['Num_Tweets'] = int(num_tweets[0])
#			if num_follows:
##				informationItems['Num_Follows'] = int(num_follows[0])
#			if num_fans:
#				informationItems['Num_Fans'] = int(num_fans[0])
#			
#			informationItems['_id'] = response.meta['ID']
#			url_information1 = "http://weibo.cn/%s/info" % response.meta["ID"]
#			yield Request(url=url_information1,meta={'item':informationItems},callback = self.parse1)

	def parse1(self,response):
		'''抓取个人信息2'''
		#因为有的字段不存在，而mysql需要提取字段，为保存不出错，先统一默认为空，monogodb不存在这个问题，是因为mongodb直接将dict插入数据库，不需要对每个字段赋值
		informationItems = InformationItem()
		informationItems['NickName'] = ''
		informationItems['Gender'] = ''
		informationItems['City'] = ''
		informationItems['URL'] = ''
		informationItems['Num_Fans'] = ''
		informationItems['Num_Follows'] = ''
		informationItems['Num_Tweets'] = ''
		informationItems['Province'] = ''
		informationItems['Signature'] = ''
#		informationItems = response.meta["item"]
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
		yield informationItems
		
		contents = []
		tweets = TweetsItem()
		tweets['_id'] = ID
		tweets['Content'] = contents	
			
		yield Request(url ="https://weibo.cn/%s/profile?filter=1&page=1" % ID,meta={'item':tweets,'contents':contents}, callback=self.parse_tweets)
#		follows = []
#		followsItems = FollowsItem()
#		followsItems['_id'] = ID
#		followsItems['follows'] = follows
#		yield Request(url = "https://weibo.cn/%s/follow" % ID,meta={'item':followsItems,'follows':follows}, callback=self.parse_follows)
#		yield Request(url = "https://weibo.cn/%s/fans" % ID,   callback=self.parse_fans)


	def parse_tweets(self,response):
		'''抓取微博数据'''
		items = response.meta['item']
#		tweetsItems = response.meta['contents']
		selector = Selector(response)
		ID = re.findall('weibo\.cn/(\d+)',response.url)[0]
		tweets = selector.xpath('body/div[@class="c" and @id]')
		print('tweets的数据是：')
		print(tweets)

		for tweet in tweets:
			tweetsItems = {}	
#			tweetsItems = TweetsItem()
			id = tweet.xpath('@id').extract_first()  # 微博ID
			content = tweet.xpath('div/span[@class="ctt"]/text()').extract_first()  # 微博内容
			print('微博内容为：',content)
			#cooridinates = tweet.xpath('div/a/@href').extract_first()  # 定位坐标
			like = re.findall('赞\[(\d+)\]', tweet.extract())  # 点赞数		
			transfer = re.findall('转发\[(\d+)\]', tweet.extract())  # 转载数
			comment = re.findall('评论\[(\d+)\]', tweet.extract())  # 评论数
			others = tweet.xpath('div/span[@class="ct"]/text()').extract_first()  # 求时间和使用工具（手机或平台）
#			tweetsItems["ID"] = ID
#			tweetsItems["_id"] = ID + "-" + id
			if id:
				tweetsItems['id'] = ID + '-' + id
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
			response.meta['contents'].append(tweetsItems)
#			yield items
		
		url_next = selector.xpath(u'body/div[@class="pa" and @id="pagelist"]/form/div/a[text()="下页"]/@href').extract()
		if url_next:
			yield Request(url=self.host + url_next[0],meta={'item':items,'contents':response.meta['contents']}, callback=self.parse_tweets)
		else:
			yield items
			
	def parse_follows(self,response):
	
		#followsItems = FollowsItem()
		items = response.meta['item']
		selector = Selector(response)
#		ID = re.findall('(\d+)/follow',response.url)[0]
		
	
		urls = selector.xpath('body/table/tr/td/a[text()="关注他"or text()="关注她"]/@href').extract()
		uids = re.findall('uid=(\d+)',';'.join(urls),re.S)
		for uid  in uids:
#			followsItems['follows'] = uid
			response.meta['follows'].append(uid)
#			yield followsItems
			yield Request(url = "https://weibo.cn/%s/info" % uid,callback=self.parse1)
		next_url = selector.xpath('//a[text()="下页"]/@href').extract()
		if next_url:
			yield Request(url = self.host + next_url[0],meta={'item':items,'follows':response.meta['follows']},callback=self.parse_follows)
		else:
			yield items
			
#	def parse3(self,response):
#		'''抓取关注或粉丝'''
#
#		items = response.mta['item']
#		selector = Selector(response)
#		text2 = selector.xpath('body//table/tr/td/a[text()="关注他" or text()="关注她"]/@href').extract()
#		print('text2的数据是')
#		print(text2)
#		for elem in text2:
#			elem = re.findall('uid=(\d+)', elem)#用户ID
#			if elem:
#				response.meta["result"].append(elem[0])#用户ID存放到数组follows和fans内
#				ID = int(elem[0])
#				print('找到关注人或粉丝的ID：')
#				print(ID)
#				if ID not in self.finish_ID:
#					self.scrawl_ID.add(ID)
#					print('ID加入到未爬取的列表内')
#					print(self.scrawl_ID.__len__())
#		url_next = selector.xpath('body//div[@class="pa" and @id="pagelist"]/form/div/a[text()="下页"]/@href').extract()
#		if url_next:
#			yield Request(url=self.host + url_next[0], meta={"item": items, "result": response.meta["result"]},callback=self.parse3)
#		else:
#			yield items
#	
	
#	def getNextID(self,url,cookies):
#		IDs = []
#		r = requests.get(url=url,cookies=cookies)
#		if r.status_code = 200:
#			selector = etree.HTML(r.content)
#				
