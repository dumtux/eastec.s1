class Singleton(object):
    _instance = None

    def __init__(self):
        raise Error('call instance()')

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            # more init operation here
        return cls._instance
