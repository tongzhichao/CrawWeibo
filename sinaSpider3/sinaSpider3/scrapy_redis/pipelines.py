#from scrapy.utils.misc import load_object
from scrapy.utils.serialize import ScrapyJSONEncoder
from twisted.internet.threads import deferToThread

from . import connection


#default_serialize = ScrapyJSONEncoder().encode


class RedisPipeline(object):
    """Pushes serialized item into a redis list/queue

    Settings
    --------
    REDIS_ITEMS_KEY : str
        Redis key where to store items.
    REDIS_ITEMS_SERIALIZER : str
        Object path to serializer function.

    """

    def __init__(self, server):
 
        """Initialize pipeline.

        Parameters
        ----------
        server : StrictRedis
            Redis client instance.
        key : str
            Redis key where to store items.
        serialize_func : callable
            Items serializer function.

 
       """
        print('----------------------------初始化redispipline---------------10')
        self.server = server
#        self.key = key
#        self.serialize = serialize_func
        self.encoder = ScrapyJSONEncoder()
    @classmethod
    def from_settings(cls, settings):
#        params = {
#            'server': connection.from_settings(settings),
#        }
        server = connection.from_settings(settings)
#        if settings.get('REDIS_ITEMS_KEY'):
#            params['key'] = settings['REDIS_ITEMS_KEY']
#        if settings.get('REDIS_ITEMS_SERIALIZER'):
#            params['serialize_func'] = load_object(
#                settings['REDIS_ITEMS_SERIALIZER']
#            )

#        return cls(**params)
        return cls(server)
    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    def process_item(self, item, spider):
        return deferToThread(self._process_item, item, spider)

    def _process_item(self, item, spider):
        key = self.item_key(item, spider)
        #data = self.serialize(item)
        data = self.encoder.encode(item)
        self.server.rpush(key, data)
        return item

    def item_key(self, item, spider):
        """Returns redis key based on given spider.

        Override this function to use a different key depending on the item
        and/or spider.

        """
        #return self.key % {'spider': spider.name}
        return '%s:items' % spider.name
