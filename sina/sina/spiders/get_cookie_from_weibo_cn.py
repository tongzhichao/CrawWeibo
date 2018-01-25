
import json
import requests
import sys
import time
from selenium import webdriver

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
dcap = dict(DesiredCapabilities.PHANTOMJS)

dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (Linux; U; Android 2.3.6; en-us; Nexus S Build/GRK39F) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"
)


def get_cookie_from_weibo_cn(account,password):
	browser = webdriver.PhantomJS(desired_capabilities=dcap)
	browser.get("https://weibo.cn/login/")
	time.sleep(2)
	failure = 0
	while '微博' in browser.title and failure<5:
		failure += 1
		browser.save_screenshot('check.png')
		username = browser.find_element_by_id('loginName')
		username.clear()
		username.send_keys(account)
		psd = browser.find_element_by_id('loginPassword')
		psd.clear()
		psd.send_keys(password)
		commit = browser.find_element_by_id('loginAction')
		commit.click()
		time.sleep(3)
		if '我的首页' not in browser.title:
			time.sleep(4)
		if '未激活微博' in browser.page_source:
			print('账号未开通微博')
			return {}
	cookie = {}
	if "我的首页" in browser.title:
		print(browser.get_cookies())
		for elem in browser.get_cookies():
			cookie[elem['name']] = elem['value']

		return json.dumps(cookie)
	#browser.quit()
if __name__=='__main__':
	cookies = get_cookie_from_weibo_cn('710567233@qq.com','tongzhifu12')
	print(cookies)
