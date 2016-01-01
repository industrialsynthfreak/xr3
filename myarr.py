class TList(list):

	def __init__(self, value_type, *args):
		list.__init__(self, *args)
		self.value_type = value_type

	def __add__(self, other):
		if type(other) == Array:
			super(TList, self).__add__(other)
		elif type(other) == self.value_type:
			super(TList, self).append(other)
		else:
			raise TypeError

	def append(self, other):
		if type(other) == self.value_type:
			super(TList, self).append(other)
		else:
			raise TypeError
