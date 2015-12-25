class V3:
	
	def __init__(self, x, y, z):
		self.x, self.y, self.z = float(x), float(y), float(z)

	def __call__(self):
		return self.x, self.y, self.z

	def __dec_arithm_error_handling(f):

		def wrapper(self, other):
			if type(other)!=V3:
				raise TypeError
			else:
				return f(self, other)
		return wrapper

	@__dec_arithm_error_handling
	def __add__(self, other):
		return V3(self.x + other.x, self.y + other.y, self.z + other.z)

	@__dec_arithm_error_handling
	def __sub__(self, other):
		return V3(self.x - other.x, self.y - other.y, self.z - other.z)

	@__dec_arithm_error_handling
	def __pow__(self, other):
		_dv = self.__sub__(other)
		return ( _dv.x**2 + _dv.y**2 + _dv.z**2 )**.5