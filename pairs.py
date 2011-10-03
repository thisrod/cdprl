# Lisp in Python, all because some clever dick overrode + for list concatenation.
# I was only using this for (weight, value) pairs, which are now the class Weighting.

from numbers import Number

class Pair:
	def __init__(self, car, cdr):
		self.car, self.cdr = car, cdr
		
	def __coerce__(self, other):
		if isinstance(other, Number):
			return self, cons(other, other)
		
	def __add__(self, other):
		return Pair(self.car + other.car, self.cdr + other.cdr)
		
	def __radd__(self, other):
		return self + other
		
	def __sub__(self, other):
		return Pair(self.car-other.car, self.cdr-other.cdr)
		
	def __rsub__(self, other):
		return Pair(other.car-self.car, other.cdr-self.cdr)
		
	def __mul__(self, other):
		return Pair(self.car * other.car, self.cdr * other.cdr)
		
	def __rmul__(self, other):
		return self * other
		
	def __div__(self, other):
		return Pair(self.car/other.car, self.cdr/other.cdr)
		
	def __rdiv__(self, other):
		return Pair(other.car/self.car, other.cdr/self.cdr)
					
	def __repr__(self):
		return 'Pair(' + repr(self.car) + ', ' + repr(self.cdr) + ')'
	
	def astuple(self):
		return self.car, self.cdr
		

def cons(car, cdr):
	return Pair(car, cdr)