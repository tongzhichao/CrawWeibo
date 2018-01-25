# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import json
from scrapy import signals
import random
from .cookies import cookies
from .user_agents import agents

class UserAgentMiddleware(object):
        '''随机换User-Agent'''
        def process_request(self,request,spider):
            agent = random.choice(agents)
            request.headers['User-Agent'] = agent

class CookiesMiddleware(object):
        '''换cookie'''
        def process_request(self,request,spider):
            cookie = random.choice(cookies)
            print('cookie的值是：')
            print(cookie)
            cookie = json.loads(cookie)
            request.cookies = cookie


class ProxyMiddleware(object):
	proxylist = ['https://202.98.197.243:3128', 'https://27.38.96.122:9999', 'https://120.26.14.14:3128', 'https://123.138.89.133:9999', 'https://121.43.178.58:3128', 'https://113.99.218.66:9797', 'https://14.117.209.108:9797', 'https://223.242.131.242:52311', 'https://119.123.178.41:9000', 'https://101.81.106.155:9797', 'https://112.95.205.28:8888', 'https://27.46.39.117:9797', 'https://113.116.142.249:9797', 'https://113.89.53.35:9999', 'https://116.17.124.216:9999', 'https://101.201.71.241:3128', 'https://139.224.24.26:8888', 'https://101.37.79.125:3128', 'https://122.72.18.34:80', 'https://112.74.94.142:3128', 'https://122.72.18.61:80', 'https://182.121.203.242:9999', 'https://183.15.27.132:9797', 'https://122.72.18.35:80', 'https://218.29.111.106:9999', 'https://218.18.10.229:9797', 'https://222.56.21.113:53281', 'https://119.90.63.3:3128', 'https://112.250.65.222:53281', 'https://119.122.28.221:9000', 'https://59.44.244.14:9797', 'https://222.132.145.126:80', 'https://125.93.193.214:3128', 'https://27.44.197.188:9999', 'https://171.37.30.13:9797', 'https://58.17.125.215:53281', 'https://221.223.138.142:9000', 'https://113.77.240.10:9797', 'https://202.96.142.2:3128', 'https://218.18.10.190:9000', 'https://113.13.185.130:53281', 'https://180.76.134.106:3128', 'https://61.155.164.106:3128', 'https://121.13.165.107:9797', 'https://112.67.160.204:9797', 'https://222.208.209.219:8080', 'https://58.247.127.145:53281', 'https://14.211.123.146:9797', 'https://113.87.161.75:808', 'https://58.60.32.56:9797', 'https://112.95.205.63:8888', 'https://27.46.49.63:9797', 'https://101.224.239.18:9000', 'https://120.78.78.141:8888', 'https://175.17.158.200:8080', 'https://123.139.56.238:9999', 'https://14.29.84.50:8080', 'https://113.65.8.221:9999', 'https://222.222.169.60:53281', 'https://120.9.76.55:9999', 'https://222.222.169.60:53281', 'https://120.9.76.55:9999', 'https://119.129.98.130:9797', 'https://218.64.119.216:53281', 'https://171.37.53.113:9797', 'https://114.255.212.14:808', 'https://219.135.164.245:3128', 'https://101.6.50.214:8123', 'https://123.112.19.37:53281', 'https://117.65.44.111:52311', 'https://27.46.74.31:9999', 'https://59.38.60.46:9797', 'https://113.65.20.35:9999', 'https://14.211.116.73:9797', 'https://113.88.177.243:8088', 'https://113.83.240.173:53281']

	def process_request(self,request,spider):
		pro_adr = random.choice(self.proxylist)
		print('随机选择IP代理')
		request.meta['proxy'] = pro_adr
	
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
