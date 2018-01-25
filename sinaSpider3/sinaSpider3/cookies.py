#encoding = utf-8
import json
import base64
import requests
import sys,os
import time
from selenium import webdriver

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import logging

import sys
#reload(sys)
sys.getdefaultencoding()

IDENTIFY = 1

COOKIE_GETWAY = 1

dcap = dict(DesiredCapabilities.PHANTOMJS)

dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (Linux; U; Android 2.3.6; en-us; Nexus S Build/GRK39F) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"
)
logger = logging.getLogger(__name__)
logging.getLogger('selenium').setLevel(logging.WARNING)

myWeiBo=[
	('710567233@qq.com','tongzhifu12'),
	('381368314@qq.com','tongzhifu12'),
]

def getCookie(account,password):
	if COOKIE_GETWAY == 0:
		return get_cookie_from_login_sina_com_cn(account,password)
	elif COOKIE_GETWAY == 1:
		return get_cookie_from_weibo_cn(account,password)
	else:
		logger.error('COOKIE_GETWAY Error!')


def get_cookie_from_login_sina_com_cn(account,password):
	'''获取一个账号的cookie'''
	loginURL = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
	username = base64.b64encode(account.encode('utf-8')).decode('utf-8')
	postData = {
	"entry": "sso",
	"gateway": "1",
	"from": "null",
	"savestate": "30",
	"useticket": "0",
	"pagerefer": "",
	"vsnf": "1",
	"su": username,
	"service": "sso",
	"sp": password,
	"sr": "1440*900",
	"encoding": "UTF-8",
	"cdult": "3",
	"domain": "sina.com.cn",
	"prelt": "0",
	"returntype": "TEXT",
	}
	session = requests.Session()
	r = session.post(loginURL,data= postData)
	jsonStr = r.content.decode('gbk')
	info = json.loads(jsonStr)
	if info['retcode'] == '0':
		logger.warning('Get cookie success!(Account:%s)' % account)
		cookie = session.cookies.get_dict()
		return json.dumps(cookie)

	else:
		logger.warning('Failed! (Reason:%s)' %info['reason'])

		return ''
def get_cookie_from_weibo_cn(account,password):
#		'''获取一个账号的cookie,从另一个地方'''
#		try:
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
				'''
				try:
					code =  browser.find_element_by_name('code')
					code.clear()
					if IDENTIFY == 1:
						code_txt = raw_input('请查看路径新生成的check.png，然后输入验证码：')
					else:
						from PIL import Image
						img = browser.find_element_by_xpath('//form[@method="post"]/div/img[@alt="请打开图片显示"]')
						x = img.location['x']
						y = img.location['y']
						im = Image.open('check.png')
						im.crop((x,y,100 + x,y+22)).save('check_ab.png')
						code_txt = identify()
					code.send_keys(code_txt)
				except Exception:
					pass
				'''
				commit = browser.find_element_by_id('loginAction')
				commit.click()
				time.sleep(3)
				print('点击成功登陆微博')	
				if '我的首页' not in browser.title:
					time.sleep(4)
				if '未激活微博' in browser.page_source:
					print('账号未开通微博')
					return {}
			cookie = {}
			if "我的首页" in browser.title:
				for elem in browser.get_cookies():
					cookie[elem['name']] = elem['value']
					logger.warning('get cookie sucess!(Account: %s) ' % account)
			browser.quit()
			return json.dumps(cookie)

#		except Exception:
#			logger.warning('Failed %s' % account)
#			return ''
#		finally:
#			try:
#				browser.quit()
#			except Exception:
#				pass

def initCookie(rconn,spiderName):
	print('-------------------------------------------初始化cookies-----------------------1---')
	#获取所有账户的cookies，存入redis,如果redis已有该账号的cookie，则不再获取
	for weibo in myWeiBo:
		if rconn.get('%s:Cookies:%s--%s' % (spiderName,weibo[0],weibo[1])) is None:
			print('未找到cookies的key')
			cookie = getCookie(weibo[0],weibo[1])
#			print(cookie)
			if len(cookie) > 0:
				rconn.set('%s:Cookies:%s--%s' % (spiderName,weibo[0],weibo[1]),cookie)
	cookieNum = ''.join(str(s) for s in rconn.keys()).count("sinaSpider:Cookies")
	logger.warning("The num of the cookies is %s" % cookieNum)
	if cookieNum == 0:
		logger.warning('Stoping...')
		os.system('pause')

def updateCookie(accountText,rconn,spiderName):
	print('---------------------------------更新cookies-----------------------2-----')
	account = accountText.split('--')[0]
	password = accountText.split('--')[1]
	cookie = getCookie(account,password)
	if len(cookie) > 0:
		logger.warning('The cookie of %s has been updated successfully '% account)
		rconn.set('%s:Cookies:%s' % (spiderName,accountText),cookie)
	else:
		logger.warning('The cookie of %s updated failed! Remove it ' % accountText)
		removeCookie(accountText,rconn,spiderName)

def removeCookie(accountText,rconn,spiderName):
	print('-------------------------------删除cookies--------------------3-------')
	rconn.delete('%s:Cookies:%s' % (spiderName,accountText))
	#cookieNum = ''.join(rconn.keys()).count('SinaSpider:Cookies')
	cookieNum = ''.join(str(s) for s in rconn.keys()).count("sinaSpider:Cookies")
	logger.warning('The num of the cookies left is %s ' % cookieNum)
	if cookieNum == 0:
		logger.warning('Stoping...')
		os.system('pause')


'''
def getCookies(weibo):
		cookies = []
		for elem in weibo:
			account = elem['no']
			password = elem['psw']
			cookie = getCookie(account,password)
			if cookie != None:
				cookies.append(cookie)
		return cookies


cookies = getCookies(myWeiBo)
logger.warning('get Cookies finish!(num:%d)' % len(cookies))
'''
