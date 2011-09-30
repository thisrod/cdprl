from numpy import allclose

class Weighting:
	
	def __init__(self, value, weight = 1):
		self.mean = value
		self.weight = weight
		
	def __repr__(self):
		return "Weighting(%s, weight = %f)" % (repr(self.mean), self.weight)
		
	def __eq__(self, other):
		return self.mean == other.mean and self.weight == other.weight
		
	def __add__(self, other):
		return Weighting(self.mean + other.mean, self.weight + other.weight)
		
	def __mul__(self, scalar):
		return Weighting(self.mean*scalar, self.weight*scalar)	
		
	def __rmul__(self, scalar):
		return Weighting(scalar*self.mean, scalar*self.weight)	
			
	def __div__(self, scalar):
		return Weighting(self.mean/scalar, self.weight/scalar)
		
	def combine(self, other):
		weight = self.weight + other.weight
		mean = (self.mean*self.weight + other.mean*other.weight) / weight
		return Weighting(mean, weight)
		
		
def weightclose(self, other):
	return allclose(self.mean, other.mean) and allclose(self.weight, other.weight)