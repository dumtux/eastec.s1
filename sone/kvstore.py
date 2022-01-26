import abc
import vedis


class KVStore(abc.ABC):

    '''Interface for normal key-value store operations'''

    @abc.abstractmethod
    def exists(self, key: str) -> bool:
        '''raise NotImplementedError()'''

    @abc.abstractmethod
    def get(self, key: str) -> str:
        '''raise NotImplementedError()'''

    @abc.abstractmethod
    def set(self, key: str, value: str) -> str:
        '''raise NotImplementedError()'''

    @abc.abstractmethod
    def pop(self, key: str) -> str:
        '''raise NotImplementedError()'''


class Vedis(KVStore):

    '''For Vedis embedded key-value store'''

    def __init__(self, fpath):
        self._engine = vedis.Vedis(fpath)

    def exists(self, key: str) -> bool:
        return self._engine.exists(key)

    def get(self, key: str) -> str:
        return self._engine.get(key).decode()

    def set(self, key: str, value: str) -> str:
        self._engine.set(key, value)
        return value

    def pop(self, key: str) -> str:
        value = self.get(key)
        self._engine.delete(key)
        return value

    def commit(self):
        self._engine.commit()
