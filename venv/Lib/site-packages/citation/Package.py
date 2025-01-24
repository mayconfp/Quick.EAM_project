

class Package:
	def __init__(self, name, version):
		self._name = name
		self._version = version
		self._is_native = None

	@property
	def name(self):
		return self._name

	@property
	def version(self):
		return self._version

	@property
	def is_native(self):
		return self._is_native

	def __str__(self):
		return f'{self.name} {self.version}'

	def __repr__(self):
		return str(self)