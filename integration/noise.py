from namespace import *
from numpy.random.mtrand import RandomState
from copy import copy


class Noise(object):

	"""I am the abstract base class for noise sources.
	
	If x is a noise source, x[i,j,...] is a Wiener process, and x[i,j,...](t, dt) is its average derivative from t to t+dt.  This can also be written x(t, dt)[i, j, ...], because x(t, dt) is a collection of the derivatives of all processes.  When a time interval and a finite sub-array have been specified, the noise source returns an ndarray of derivatives.  Note that subscripting a single process returns a singleton ndarray, not a float.
	
	As a special case, x(t, 0) is zero.  This ensures dx = 0 when dt = 0, when there's a 0*Infinity ambiguity.  
	
	Subclasses need to extend __init__, to handle their seeds and numerical parameters, and derivatives, to generate the noise."""

	def __init__(self):
		self.start = None
		self.duration = None
		self.bounds = None

	def __call__(self, start, duration):
		instance = copy(self)
		instance.start, instance.duration = start, duration
		return instance.eval()
		
	def __getitem__(self, indices):
		# FINDOUT the standard way of normalising indices to slices.
		if not isinstance(indices, tuple):
			indices = (indices,)
		instance = copy(self)
		instance.bounds = indices
		return instance.eval()
		
	def eval(self):
		if self.start is None or self.duration is None or self.bounds is None:
			return self
		else:
			return self.derivatives(self.bounds, self.start, self.duration)
		
	def derivatives(self, bounds, start, duration):
		"""Return an ndarray of average derivatives for processes within bounds, from start, over duration.  Bounds is a tuple of integers or strides."""
		raise(NotImplementedError)
		
		
class DiscreteNoise(Noise):

	"""This noise source lazily seeds a Python PRNG for each process, which generates independent derivatives for intervals of length timestep, starting from time 0.  I've given up on making this reproducible for now."""

	def __init__(self):
		Noise.__init__(self)
		self.rng = RandomState()
		
	def set_labels(self, labels): pass
	
	def derivatives(self, bounds, tstart, duration):
		def deoffset(i):
			if isinstance(i, slice):
				return i.stop - i.start
			else:
				return None
		bounds = [i for i in map(deoffset, bounds) if i is not None]
		return normal_deviates(0, 1/sqrt(duration), bounds)
