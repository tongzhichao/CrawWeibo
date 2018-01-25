from scrapy.utils.reqser import request_to_dict, request_from_dict
from scrapy.http import Request
try:
   import cPickle as pickle
except ImportError:
   import pickle


class Base(object):
    """Per-spider base queue class"""

    def __init__(self, server, spider, key, queue_name):
        """Initialize per-spider redis queue.

        Parameters
        ----------
        server : StrictRedis
            Redis client instance.
        spider : Spider
            Scrapy spider instance.
        key: str
            Redis key where to put and get messages.
        serializer : object
            Serializer object with ``loads`` and ``dumps`` methods.

        """
#        if serializer is None:
#            # Backward compatibility.
#            # TODO: deprecate pickle.
#            serializer = picklecompat
#        if not hasattr(serializer, 'loads'):
#            raise TypeError("serializer does not implement 'loads' function: %r"
#                            % serializer)
#        if not hasattr(serializer, 'dumps'):
#            raise TypeError("serializer '%s' does not implement 'dumps' function: %r"
#                            % serializer)

        self.server = server
        self.spider = spider
        self.key = key % {'spider': queue_name}
#        self.serializer = serializer

    def _encode_request(self, request):
        """Encode a request object"""
#        obj = request_to_dict(request, self.spider)
#        return self.serializer.dumps(obj)
        return pickle.dumps(request_to_dict(request,self.spider),protocol=-1)

    def _decode_request(self, encoded_request):
        """Decode an request previously encoded"""
#        obj = self.serializer.loads(encoded_request)
#        return request_from_dict(obj, self.spider)
        return request_from_dict(pickle.loads(encoded_request),self.spider)
    def __len__(self):
        """Return the length of the queue"""
        raise NotImplementedError

    def push(self, request):
        """Push a request"""
        raise NotImplementedError

    def pop(self, timeout=0):
        """Pop a request"""
        raise NotImplementedError

    def clear(self):
        """Clear queue/stack"""
        self.server.delete(self.key)

class SpiderQueue(Base):
    def __len__(self):
        return self.server.llen(self.key)
    def push(self,request):
        self.server.lpush(self.key,self._encode_request(request))
    def pop(self,timeout =0):
        if timeout > 0:
            data = self.server.brpop(self.key,timeout)
            if isinstance(data,tuple):
                 data = data[1]
        else:
            data = self.server.rpop(self.key)
        if data:
            return self._decode_request(data)

class SpiderPriorityQueue(Base):
     def __len__(self):
        
         return self.server.zcard(self.key)
     def push(self,request):
         print('--------------写入redis种子队列操作---------------11------------')
         print(request)
         print('self.key的数据是：')
         print(self.key)
         data = self._encode_request(request)
         print('data的数据是：')
         print(data)
         #pairs = {data: -request.priority}
         score = -request.priority
         print('pairs的数据是：')
         print(score)
         self.server.zadd(self.key,data,int(score))
     def pop(self,timeout=0):
         pipe = self.server.pipeline()
         pipe.multi()
         pipe.zrange(self.key,0,0).zremrangebyrank(self.key,0,0)
         results,count = pipe.execute()
         if results:
             return self._decode_request(results[0])

class SpiderSimpleQueue(Base):
    def __len__(self):
        return self.server.llen(self.key)
    def push(self,request):
        self.server.lpush(self.key,request.url[16:])
    def pop(self,timeout=0):
        if timeout > 0:
            url = self.server.brpop(self.key,timeout=timeout)
            if isinstance(url,tuple):
                 url = url[1]
        else:
            url = self.server.rpop(self.key)
        if url:
            try:
                 if '/follow' in url or '/fans' in url:
                     cb = getattr(self.spider,'parse_relationship')
                 elif '/profile' in url:
                     cb = getattr(self.spider,'parse_tweets')
                 elif '/info' in url:
                     cb = getattr(self.spider,'parse_information')
                 else:
                     raise ValueError('Method not found in: %s (URL: %s) ' % (self.spider,url))
                 return Request(url = 'https://weibo.cn%s' % url,callback=cb)
            except AttributeError:
                 raise ValueError('Method not found in: %s (URL:%s)' % (self.spider,url))

class SpiderStack(Base):
    def __len_(self):
        return self.server.llen(self.key)
    def push(self,request):
        self.server.lpush(self.key,self._encode_request(request))
    def pop(self,timeout=0):
        if timeout > 0:
            data = self.server.blpop(self.key,timeout)
            if isinstance(data,tuple):
                data = data[1]
        else:
            data = self.server.lpop(self.key)
        if data:
            return self._decode_request(data)


class FifoQueue(Base):
    """Per-spider FIFO queue"""

    def __len__(self):
        """Return the length of the queue"""
        return self.server.llen(self.key)

    def push(self, request):
        """Push a request"""
        self.server.lpush(self.key, self._encode_request(request))

    def pop(self, timeout=0):
        """Pop a request"""
        if timeout > 0:
            data = self.server.brpop(self.key, timeout)
            if isinstance(data, tuple):
                data = data[1]
        else:
            data = self.server.rpop(self.key)
        if data:
            return self._decode_request(data)


class PriorityQueue(Base):
    """Per-spider priority queue abstraction using redis' sorted set"""

    def __len__(self):
        """Return the length of the queue"""
        return self.server.zcard(self.key)

    def push(self, request):
        """Push a request"""
        data = self._encode_request(request)
        score = -request.priority
        # We don't use zadd method as the order of arguments change depending on
        # whether the class is Redis or StrictRedis, and the option of using
        # kwargs only accepts strings, not bytes.
        self.server.execute_command('ZADD', self.key, score, data)

    def pop(self, timeout=0):
        """
        Pop a request
        timeout not support in this queue class
        """
        # use atomic range/remove using multi/exec
        pipe = self.server.pipeline()
        pipe.multi()
        pipe.zrange(self.key, 0, 0).zremrangebyrank(self.key, 0, 0)
        results, count = pipe.execute()
        if results:
            return self._decode_request(results[0])


class LifoQueue(Base):
    """Per-spider LIFO queue."""

    def __len__(self):
        """Return the length of the stack"""
        return self.server.llen(self.key)

    def push(self, request):
        """Push a request"""
        self.server.lpush(self.key, self._encode_request(request))

    def pop(self, timeout=0):
        """Pop a request"""
        if timeout > 0:
            data = self.server.blpop(self.key, timeout)
            if isinstance(data, tuple):
                data = data[1]
        else:
            data = self.server.lpop(self.key)

        if data:
            return self._decode_request(data)


# TODO: Deprecate the use of these names.
#SpiderQueue = FifoQueue
#SpiderStack = LifoQueue
#SpiderPriorityQueue = PriorityQueue


__all__ = ['SpiderQueue', 'SpiderPriorityQueue', 'SpiderSimpleQueue', 'SpiderStack']
