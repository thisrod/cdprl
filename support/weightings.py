from namespace import *

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
		# FIXME: The next two lines show why it's better to store mean*weight than mean (except that it adds a round-trip problem).  Maybe the correct answer is to store the value on construction, then coerce to a total if combined with a different mean and non-zero weight.  This could be done as three subclasses: ZeroWeighting, SingleValueWeighting, CombinedValueWeighting
		if self.weight == 0: return other
		if other.weight == 0: return self
		weight = self.weight + other.weight
		mean = (self.mean*self.weight + other.mean*other.weight) / weight
		return Weighting(mean, weight)
		
		
def weightclose(self, other):
	return allclose(self.mean, other.mean) and allclose(self.weight, other.weight)