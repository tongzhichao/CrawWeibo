#import importlib
#import six

from scrapy.utils.misc import load_object

from . import connection
from .dupefilter import RFPDupeFilter

SCHEDULER_PERSIST = False
QUEUE_KEY = '%(spider)s:requests'
QUEUE_CLASS = 'scrapy_redis.queue.SpiderPriorityQueue'
DUPEFILTER_KEY = '%(spider)s:dupefilter'
IDLE_BEFORE_CLOSE = 0 

# TODO: add SCRAPY_JOB support.
class Scheduler(object):
    """Redis-based scheduler

    Settings
    --------
    SCHEDULER_PERSIST : bool (default: False)
        Whether to persist or clear redis queue.
    SCHEDULER_FLUSH_ON_START : bool (default: False)
        Whether to flush redis queue on start.
    SCHEDULER_IDLE_BEFORE_CLOSE : int (default: 0)
        How many seconds to wait before closing if no message is received.
    SCHEDULER_QUEUE_KEY : str
        Scheduler redis key.
    SCHEDULER_QUEUE_CLASS : str
        Scheduler queue class.
    SCHEDULER_DUPEFILTER_KEY : str
        Scheduler dupefilter redis key.
    SCHEDULER_DUPEFILTER_CLASS : str
        Scheduler dupefilter class.
    SCHEDULER_SERIALIZER : str
        Scheduler serializer.

    """

    def __init__(self, server,
                 server_filter,
                 persist, 
                 queue_key,
                 queue_cls,
                 dupefilter_key,
                 idle_before_close,
                 queue_name):
        """Initialize scheduler.

        Parameters
        ----------
        server : Redis
            The redis server instance.
        persist : bool
            Whether to flush requests when closing. Default is False.
        flush_on_start : bool
            Whether to flush requests on start. Default is False.
        queue_key : str
            Requests queue key.
        queue_cls : str
            Importable path to the queue class.
        dupefilter_key : str
            Duplicates filter key.
        dupefilter_cls : str
            Importable path to the dupefilter class.
        idle_before_close : int
            Timeout before giving up.

        """
#        if idle_before_close < 0:
#            raise TypeError("idle_before_close cannot be negative")

        self.server = server
        self.server_filter = server_filter
        self.persist = persist
        self.queue_key = queue_key
        self.queue_cls = queue_cls
        self.dupefilter_key = dupefilter_key
        self.idle_before_close = idle_before_close
        self.queue_name = queue_name
        self.stats = None

    def __len__(self):
        return len(self.queue)

    @classmethod
    def from_settings(cls, settings):
#        kwargs = {
#            'persist': settings.getbool('SCHEDULER_PERSIST'),
#            'flush_on_start': settings.getbool('SCHEDULER_FLUSH_ON_START'),
#            'idle_before_close': settings.getint('SCHEDULER_IDLE_BEFORE_CLOSE'),
#        }

        # If these values are missing, it means we want to use the defaults.
#        optional = {
            # TODO: Use custom prefixes for this settings to note that are
#            # specific to scrapy-redis.
#            'queue_key': 'SCHEDULER_QUEUE_KEY',
#            'queue_cls': 'SCHEDULER_QUEUE_CLASS',
#            'dupefilter_key': 'SCHEDULER_DUPEFILTER_KEY',
            # We use the default setting name to keep compatibility.
#            'dupefilter_cls': 'DUPEFILTER_CLASS',
#            'serializer': 'SCHEDULER_SERIALIZER',
#        }
#        for name, setting_name in optional.items():
#            val = settings.get(setting_name)
#            if val:
 #               kwargs[name] = val

        # Support serializer as a path to a module.
#        if isinstance(kwargs.get('serializer'), six.string_types):
#            kwargs['serializer'] = importlib.import_module(kwargs['serializer'])

#        server = connection.from_settings(settings)
        # Ensure the connection is working.
#        server.ping()

#        return cls(server=server, **kwargs)
        persist = settings.get('SCHEDULER_PERSIST',SCHEDULER_PERSIST)
        queue_key = settings.get('SCHEDULER_QUEUE_KEY',QUEUE_KEY)
        queue_cls = load_object(settings.get('SCHEDULER_QUEUE_CLASS',QUEUE_CLASS))
        queue_name = settings.get('REDIS_QUEUE_NAME',None)
        dupefilter_key = settings.get('DUPEFILTER_KEY',DUPEFILTER_KEY)
        idle_before_close = settings.get('SCHEDULER_IDLE_BEFORE_CLOSE',IDLE_BEFORE_CLOSE)
        server = connection.from_settings(settings)
        server_filter = connection.from_settings_filter(settings)
        return cls(server,server_filter,persist,queue_key,queue_cls,dupefilter_key,idle_before_close,queue_name)
    @classmethod
    def from_crawler(cls, crawler):
        instance = cls.from_settings(crawler.settings)
        # FIXME: for now, stats are only supported from this constructor
        instance.stats = crawler.stats
        return instance

    def open(self, spider):
        self.spider = spider
        self.queue = self.queue_cls(self.server,spider,self.queue_key,(self.queue_name if self.queue_name else spider.name))
        self.df = RFPDupeFilter(self.server_filter,self.dupefilter_key %{'spider':(self.queue_name if self.queue_name else spider.name)})
        if self.idle_before_close < 0:
            self.idle_before_close = 0
            
#        try:
#            self.queue = load_object(self.queue_cls)(
#                server=self.server,
#                spider=spider,
#                key=self.queue_key % {'spider': spider.name},
#                serializer=self.serializer,
#            )
#        except TypeError as e:
#            raise ValueError("Failed to instantiate queue class '%s': %s",
#                             self.queue_cls, e)
#
#        try:
#            self.df = load_object(self.dupefilter_cls)(
#                server=self.server,
#                key=self.dupefilter_key % {'spider': spider.name},
#                debug=spider.settings.getbool('DUPEFILTER_DEBUG'),
#            )
#        except TypeError as e:
#            raise ValueError("Failed to instantiate dupefilter class '%s': %s",
#                             self.dupefilter_cls, e)

#        if self.flush_on_start:
#            self.flush()
        # notice if there are requests already in the queue to resume the crawl
        if len(self.queue):
            spider.log("Resuming crawl (%d requests scheduled)" % len(self.queue))

    def close(self, reason):
        if not self.persist:
            #self.flush()
            self.df.clear()
            self.queue.clear()

#    def flush(self):
#        self.df.clear()
#        self.queue.clear()

    def enqueue_request(self, request):
        print('------------------------------------队列调度-------------------12----------')
        if not request.dont_filter and self.df.request_seen(request):
            
            return  
        if self.stats:
            self.stats.inc_value('scheduler/enqueued/redis', spider=self.spider)
        self.queue.push(request)
        

    def next_request(self):
        block_pop_timeout = self.idle_before_close
        request = self.queue.pop(block_pop_timeout)
        if request and self.stats:
            self.stats.inc_value('scheduler/dequeued/redis', spider=self.spider)
        return request

    def has_pending_requests(self):
        return len(self) > 0
