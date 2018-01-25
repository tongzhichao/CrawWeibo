# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
from  scrapy.item import Item,Field 


class InformationItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #pass
	'''个人信息'''
	_id = Field()
	NickName = Field()
	Gender = Field()
	Province = Field()
	City = Field()
	Signature = Field()
	Birthday = Field()
	Num_Tweets = Field()
	Num_Follows = Field()
	Num_Fans = Field()
	Sex_Orientation = Field()
	Marriage = Field()
	URL = Field()

class TweetsItem(Item):
	'''微博信息'''

	_id = Field()
#	ID  = Field()
	Content = Field()
#	PubTime = Field()
#	Tools = Field()
#	Like = Field()
#	Comment = Field()
#	Transfer = Field()

class  FollowsItem(Item):
	'''关注人列表'''
	_id = Field()
	follows = Field()
	

class FansItem(Item):
	'''粉丝列表'''
#	_id = Field()
	fans = Field()

