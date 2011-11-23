from namespace import *

class Weightings(object):

	"""Stores an ndarray of values, and one of weights.  The weights correspond to slices of the values along the leading dimension."""
	
	def __init__(self, values, weights = None):
		assert values.shape[0:1] == weights.shape
		self.means = values
		self.weights = weights
		
	def __repr__(self):
		return "Weightings(%s, weights = %s)" % (repr(self.means), repr(self.weights))
		
	def __eq__(self, other):
		# We care about permutations because of elemental arithmetic
		return self.means == other.means and self.weights == other.weights
		
	def __add__(self, other):
		return Weighting(self.means + other.means, self.weights + other.weights)
		
	def __mul__(self, scalar):
		return Weighting(self.means*scalar, self.weights*scalar)	
		
	def __rmul__(self, scalar):
		return Weighting(scalar*self.means, scalar*self.weights)	
			
	def __div__(self, scalar):
		return Weighting(self.means/scalar, self.weights/scalar)
		
	def combine(self, other):
		# Fails on zero weights.  Note the argument at http://alvyray.com/Memos/MemosCG.htm#ImageCompositing, re alpha channels.  Zero weight implies the value doesn't matter, so the round-trip error is spurious.
		broadcast = weights.shape + (len(self.means.shape)-1) * (1,)
		ws = self.weights.copy().reshape(broadcast)
		wo = other.weights.copy().reshape(broadcast)
		weights = ws + wo
		means = (self.means*ws + other.means*wo) / weights
		return Weighting(means, weights.reshape(self.weights))
		

class WeightingIncrement(object):
	
	"""An increment to a Weighting, stored as an absolute change to the mean, and a relative change to the weight.  When called with a Weighting as argument, it returns an Weighting to be added."""
	
	def __init__(self, values, weights):
		assert values.shape[0:1] == weights.shape
		self.means = values
		self.weights = weights
		
	def __eq__(self, other):
		return self.means == other.means and self.weights == other.weights
		
	def __call__(self, ws):
		return Weightings(self.means + ws.means, (1+self.weights)*ws.weights)
		
		
def weightclose(self, other):
	return allclose(self.means, other.means) and allclose(self.weights, other.weights)