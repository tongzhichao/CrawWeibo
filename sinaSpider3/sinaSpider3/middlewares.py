# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import json,random,os,json,logging,redis
from scrapy import signals
import random
import sys
sys.path.append('/home/tzc/weibo/sinaSpider3/sinaSpider3')
from cookies import initCookie,updateCookie,removeCookie
from scrapy.exceptions import IgnoreRequest
from scrapy.utils.response import response_status_message
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from user_agents import agents

logger = logging.getLogger(__name__)
class UserAgentMiddleware(object):
	'''随机换User-Agent'''
	def process_request(self,request,spider):
		print('-----------------------------随机替换user-agent------------4------')
		agent = random.choice(agents)
		
		request.headers['User-Agent'] = agent

class CookiesMiddleware(RetryMiddleware):
	'''换cookie'''
	def __init__(self,settings,crawler):
		RetryMiddleware.__init__(self,settings)
		self.rconn = settings.get('RCONN',redis.Redis(crawler.settings.get('REDIS_HOST','192.168.195.1'),crawler.settings.get('REDIS_PORT',6379)))
		initCookie(self.rconn,crawler.spider.name)
	@classmethod
	def from_crawler(cls,crawler):
		return cls(crawler.settings,crawler)

	def process_request(self,request,spider):
		print('---------------随机选择cookies-------------5----------')
		redisKeys = self.rconn.keys('*Cookies*')
		print('rediskeys的值：',redisKeys)
		while len(redisKeys) > 0:
			elem = random.choice(redisKeys).decode()
			print(elem)
			if 'sinaSpider:Cookies' in elem:
				cookie = json.loads(self.rconn.get(elem).decode())
				request.cookies = cookie
				request.meta['accountText'] = elem.split('Cookies:')[-1]
				print(elem.split('Cookies')[-1])
				break
			else:
				redisKeys.remove(elem)

	def process_response(self,request,response,spider):
		print('--------------------------中间件启动response---------------6-------')
		if response.status in [301,302,300,303]:
			try:
				redirect_url = response.headers['location']
				if 'login.weibo' in redirect_url or 'login.sina' in redirect_url:
					logger.warning('One  Cookie need to updating..')
					updateCookie(request.meta['accountText'],self.rconn,spider.name)
				elif 'weibo.cn/security' in redirect_url:#账户被限制
					logger.warning('One Account is locked! Remove it')
					removeCookie(request.meta['accountText'],self.rconn,spider.name)
				elif 'weibo.cn/pub' in redirect_url:
					logger.warning('Redirect to "http://weibo.cn/pub"!(Account:%s)' %  request.meta['accountText'].split('--')[0])
				reason = response_status_message(reponse.status)
				return  self._retry(request,reason,spider) or response
			except Exception as e:
				raise IgnoreRequest

		elif response.status in [403,414]:
			logger.error('%s! stopping..' % response.status)
			os.system('pause')
		else:
			return response
           
     
    
   
  
'''
class SinaSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
'''
