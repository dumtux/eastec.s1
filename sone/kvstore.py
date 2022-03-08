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
		self._fpath = fpath

	def exists(self, key: str) -> bool:
		with vedis.Vedis(self._fpath) as db:
			return db.exists(key)

	def get(self, key: str) -> str:
		with vedis.Vedis(self._fpath) as db:
			return db.get(key).decode()

	def set(self, key: str, value: str) -> str:
		with vedis.Vedis(self._fpath) as db:
			db.set(key, value)
		return value

	def pop(self, key: str) -> str:
		with vedis.Vedis(self._fpath) as db:
			value = db.get(key)
			db.delete(key)
		return value
