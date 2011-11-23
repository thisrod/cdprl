"""Data types and integration procedures for physical systems."""

from namespace import *

class ensemble(object):
	"""I store a weighted ensemble of states of a physical system, and context such as the time and noise processes corresponding to my elements.  I compute derivatives and moments of the states."""
	
	def __init__(self, system, size):
		"""System is an object that holds the physical parameters of the system, independent of representations.  Size is the number of elements in the ensemble."""
		
		# FIXME look in system in case of cantUnderstand
		
		self.system = system
		self.size = size
		self.time = 0.
		self.noise = None			# To be initialised before integration
		self.representations = None	# Subclasses will set this to a weightings
		
	def derivative(self, noise):
		"The derivatives of the state representations, given that noise is the derivatives of their Wiener processes."
		raise "Subclass responsibility"
				
	def weight_log_derivative(self, noise):
		"Subclasses may override this."
		return zeros_like(self.representations.weights)

	def advanced(self, step, state = None):
		"""An ensemble of my elements, at a time step in the future.

		If an ensemble state is given, the derivatives are evaluated in that state instead of me.  This is useful for implicit integration."""
		if state is None: state = self
		final = copy(self)
		final.time += step
		xi = self.noise.derivative(self.time, step)
		final.representations = self.representations.scale_adapt_add(step, state.derivative(xi), state.weight_log_derivative(xi))
		return final


class record(object):	
	"""I store moments of a system being integrated.  Ensembles are incorporated with add(state).
	
	I am initialised with a timestep, and a list of moments.  The moments are methods of the state, which should return weightings of moments."""
	
	def __init__(self, timestep, methods):
		self.timestep = timestep
		self.results = {}
		for method in methods:
			self.results[method] = {}	# To become mappings of times to moment weightings
		
	def add(self, state):
		t = self.nearest(state.time)
		for method in self.results:
			m = state.getattr(method)()	# FIXME look for state.system.method too
			self.results[method][t] = self.results[method][t].combine(m) if t in self.results[method] else m
			
	def nearest(self, t):
		"Answer recording time nearest t"
		pass
	
	def next(self, t):
		"Answer recording time after self.nearest(t)"
		pass
		
	def after(self, t):
		"Answer recording time at or after t"
		pass


class weightings(object):

	"""Stores an ndarray of values, and one of weights.  The weights correspond to slices of the values along the leading dimension."""
	
	# This could be made polymorphic with unweightings, if necessary for efficiency.
	
	def __init__(self, values, weights = None):
		if weights is None:
			weights = ones(values.shape[0])
		assert weights.shape == values.shape[0:1]
		self.values = values
		self.weights = weights
		
	def reduced(self):
		mean, net = average(self.values, 0, self.weights, True)
		mean.shape.insert(0,1)
		net.shape.insert(0,1)
		return weightings(mean, net)
		
	def mean(self):
		self.reduced().values[0,::]
		
	def scale_adapt_add(self, scalar, absolute_values, relative_weights):
		return weightings(self.values + scalar*absolute_values, self.weights*(scalar*relative_weights+1))
		
	def combine(self, other):
		return weightings(concat(self.values, other.values), concat(self.weights, other.weights))


class noise(object):

	"""Infinite array of Wiener processes.  This can be subscripted, to select specific processes.  It can also be called, to set the time and duration.  When enough parameters have been set, an ndarray of derivatives is returned."""
	
	def __init__(self):
		self.start = None
		self.duration = None
		self.bounds = None		# This will become a slice object
		
	def eval(self):
		if self.start is None or self.duration is None or not self.finite():
			return self
		else:
			return self.derivatives(self.bounds, self.start, self.duration)
			
	def derivatives(self, bounds, start, duration):
		raise "Subclass responsibility"
		
	def __call__(self, start, duration):
		assert self.start is None or start != self.start
		assert self.duration is None or duration != self.duration
		instance = copy(self)
		instance.start, instance.duration = start, duration
		return instance.eval()
		
	def __getitem__(self, indices):
		"I only support indexing by slices.  Access to individual elements is though the ndarray I generate."
		if isinstance(indices, int) or isinstance(indices, slice):
			indices = (indices,)
		assert all([isinstance(i, slice) for i in indices])
		instance = copy(self)
		if self.bounds is None:
			instance.bounds = indices
		else:
			assert len(self.bounds) == len(indices)
			instance.bounds = copy(self.bounds)
			for i in range(len(indices)):
				instance.subbound(i, indices[i])
		return instance.eval()

	def finite(self):
		return self.bounds is not None and all([isinstance(s, int) or (s.start is not None and s.stop is not None) for s in self.bounds])
		
	def subbound(self, i, index):
		"Restrict my ith dimension by index"
		# see assertions for implementation restrictions
		assert index.step is None
		assert self.bounds[i].stop - self.bounds[i].start <= index.stop - index.start
		self.bounds[i] = slice(index.start + self.bounds[i].start, index.stop + self.bounds[i].start)

class numpyNoise(noise):

	"""Draws fresh normal deviates with every call.  This works provided no interval overlaps with any previously drawn interval."""
	
	def derivatives(self, bounds, start, duration):
		dims = [(s if isinstance(s, int) else s.stop - s.start) for s in self.bounds]
		return normal_deviates(0, 1/sqrt(duration), dims)