
import redis
#from scrapy.utils.misc import load_object

#from . import defaults


# Shortcut maps 'setting name' -> 'parmater name'.
#SETTINGS_PARAMS_MAP = {
#    'REDIS_URL': 'url',
#    'REDIS_HOST': 'host',
#    'REDIS_PORT': 'port',
#    'REDIS_ENCODING': 'encoding',
#}
REDIS_URL = None
REDIS_HOST = '192.168.195.1'
REDIS_PORT = 6379

FILTER_URL = None
FILTER_HOST = '192.168.195.1'
FILTER_PORT = 6379
FILTER_DB = 0

def from_settings(settings):
	print('------------------------链接种子队列--------------7------------------')
	url = settings.get('REDIS_URL',REDIS_URL)
	host = settings.get('REDIS_HOST',REDIS_HOST)
	port = settings.get('REDIS_PORT',REDIS_PORT)
	if url:
		return redis.from_url(url)
	else:
		return redis.Redis(host=host,port=port)

def from_settings_filter(settings):
	print('-------------------链接去重队列--------------------8----------')
	url = settings.get('FILTER_URL',FILTER_URL)
	host = settings.get('FILTER_HOST',FILTER_HOST)
	port = settings.get('FILTER_PORT',FILTER_PORT)
	db = settings.get('FILTER_DB',FILTER_DB)
	if url:
		return redis.from_url(url)
	else:
		return redis.Redis(host=host,port=port,db=db)



'''
def get_redis_from_settings(settings):
    """Returns a redis client instance from given Scrapy settings object.

    This function uses ``get_client`` to instantiate the client and uses
    ``defaults.REDIS_PARAMS`` global as defaults values for the parameters. You
    can override them using the ``REDIS_PARAMS`` setting.

    Parameters
    ----------
    settings : Settings
        A scrapy settings object. See the supported settings below.

    Returns
    -------
    server
        Redis client instance.

    Other Parameters
    ----------------
    REDIS_URL : str, optional
        Server connection URL.
    REDIS_HOST : str, optional
        Server host.
    REDIS_PORT : str, optional
        Server port.
    REDIS_ENCODING : str, optional
        Data encoding.
    REDIS_PARAMS : dict, optional
        Additional client parameters.

    """
    params = defaults.REDIS_PARAMS.copy()
    params.update(settings.getdict('REDIS_PARAMS'))
    # XXX: Deprecate REDIS_* settings.
    for source, dest in SETTINGS_PARAMS_MAP.items():
        val = settings.get(source)
        if val:
            params[dest] = val

    # Allow ``redis_cls`` to be a path to a class.
    if isinstance(params.get('redis_cls'), six.string_types):
        params['redis_cls'] = load_object(params['redis_cls'])

    return get_redis(**params)


# Backwards compatible alias.
from_settings = get_redis_from_settings


def get_redis(**kwargs):
    """Returns a redis client instance.

    Parameters
    ----------
    redis_cls : class, optional
        Defaults to ``redis.StrictRedis``.
    url : str, optional
        If given, ``redis_cls.from_url`` is used to instantiate the class.
    **kwargs
        Extra parameters to be passed to the ``redis_cls`` class.

    Returns
    -------
    server
        Redis client instance.

    """
    redis_cls = kwargs.pop('redis_cls', defaults.REDIS_CLS)
    url = kwargs.pop('url', None)
    if url:
        return redis_cls.from_url(url, **kwargs)
    else:
        return redis_cls(**kwargs)
'''

