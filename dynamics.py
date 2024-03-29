"""Data types and integration procedures for physical systems."""

from namespace import *

class ensemble(object):
	"""I store a weighted ensemble of states of a physical system, and context such as the time and noise processes corresponding to my elements.  I compute derivatives and moments of the states."""
	
	def __init__(self, system, size):
		"""System is an object that holds the physical parameters of the system, independent of representations.  Size is the number of elements in the ensemble."""
		
		self.system = system
		self.size = size
		self.time = 0.
		self.noise = None			# To be initialised before integration
		self.representations = None	# Subclasses will set these
		
	def __getattr__(self, name):
		# Python's __getattr__ is the same as Smalltalk's notUnderstood:
		return getattr(self.system, name)
		
	def derivative(self, noise):
		"The derivatives of the state representations, given that noise is the derivatives of their Wiener processes."
		raise "Subclass responsibility"
		
	def advanced(self, step, state = None):
		"""An ensemble of my elements, at a time step in the future.

		If an ensemble state is given, the derivatives are evaluated in that state instead of me.  This is useful for implicit integration.  The noise is always taken from me."""

		if state is None: state = self
		# FIXME Python's copy breaks when you override getattr, and prints warnings.  Wouldn't happen in Smalltalk.
		final = copy(self)
		final.time += step
		xi = self.noise(self.time, step)
		final.representations = self.representations + step * state.derivative(xi)
		return final

			
class VCMEnsemble(ensemble):

	"""I store a superposition of weighted coherent states, for variational propagation.  Systems that will be simulated in this manner need to define methods ev_H and ev_a, that compute the matrices <H_ij>/rho_ij and <\dot a_ij>/rho_ij.

	The representation for ensemble size N and M modes is an Nx(M+1) ndarray."""

	def phis(self):
		return self.representations[:,0]
		
	def alphas(self):
		return self.representations[:,1:]
		
	def V(self):
		edge = self.representations.copy()
		edge[:,0] = 1
		result = outer(edge, edge.conj())	# Flattens automatically
		# TODO rewrite when numpy gets shared subarrays right
		n, mpp = self.representations.shape
		r, c = result.strides
		here_be_dragons = ndarray((n,n,mpp-1), dtype=result.dtype, buffer=result, offset=r+c, strides=(mpp*r, mpp*c, r+c))
		here_be_dragons += 1
		return result

	def H(self):
		edge = self.representations.copy()
		edge[:,0] = 1
		Hij = self.system.ev_H(self.alphas())*exp(self.logrho())
		result = empty_like(self.representations)
		result = (Hij[:,:,newaxis]*edge[newaxis,:,:]).sum(1)
		return result
		
		
	def logrho(self):
		n = self.phis().size
		phii = self.phis().conj().reshape((n,1))
		phij = self.phis().reshape((1,n))
		return phii + phij + tensordot(self.alphas(), self.alphas().conj(), ((0),(0)))


class QuarticOscillator(object):

	"""Intended to be used as a state.
	
from dynamics import *
state = VCMEnsemble(QuarticOscillator(), 5)
state.representations = zeros((5,2))
	"""
	
	def ev_H(self, alphas):
		return outer(alphas.conj()**2, alphas**2)
		
	def ev_a(self):
		pass


class weightedEnsemble(ensemble):
	"""I store an ensemble with weights"""
					
	def weight_log_derivative(self, noise):
		"Subclasses may override this."
		raise "Subclass responsibility"
		
	def advanced(self, step, state = None):
		"""An ensemble of my elements, at a time step in the future.

		If an ensemble state is given, the derivatives are evaluated in that state instead of me.  This is useful for implicit integration."""

		if state is None: state = self
		final = copy(self)
		final.time += step
		xi = self.noise(self.time, step)
		final.representations, final.weights = self.scale_adapt_add(step, state.derivative(xi), state.weight_log_derivative(xi))
		return final
		
	def scale_adapt_add(self, scalar, absolute_values, relative_weights):
		if self.weights is None:
			return self.representations + scalar*absolute_values, None
		else:
			return self.representations + scalar*absolute_values, self.weights*(scalar*relative_weights+1)
	


class record(object):	
	"""I store moments of a system being integrated.  Ensembles are incorporated with add(state).
	
	I am initialised with a timestep, and a list of moments.  The moments are methods of the state, which should return weightings of moments.
	
	If the state doesn't have a certain moment, I ignore it.  This allows e.g. one run for exact results, and another for computed results."""
	
	def __init__(self, timestep, methods):
		self.timestep = timestep
		self.results = {}
		for method in methods:
			self.results[method] = {}	# To become mappings of times to moment weightings
		
	def add(self, state):
		t = self.nearest(state.time)
		mtds = [m for m in self.results if hasattr(state, m)]
		for method in mtds:
			m = getattr(state, method)()
			self.results[method][t] = self.results[method][t].combine(m) if t in self.results[method] else m
			
	# FIXME: get rid of home-rolled rounding
	def nearest(self, t):
		"Answer recording time nearest t"
		return self.timestep * round(t/self.timestep)
	
	def next(self, t):
		"Answer recording time after self.nearest(t)"
		return self.nearest(t) + self.timestep
		
	def after(self, t):
		"Answer recording time at or after t"
		return t if self.nearest(t) == t else self.next(t)


class weightings(object):

	"""Stores an ndarray of values, and one of weights.  The weights correspond to slices of the values along the leading dimension."""
	
	# This could be made polymorphic with unweightings, if necessary for efficiency.
	
	def __init__(self, values, weights = None):
		# handle singletons
		if not isinstance(values, ndarray):
			values = array([values])
		if weights is None:
			weights = ones(values.shape[0])
		if not isinstance(weights, ndarray):
			weights = array([weights])
		assert weights.shape == values.shape[0:1]
		self.values = values
		self.weights = weights
		
	def reduced(self):
		mean, net = average(self.values, 0, self.weights, True)
		mean = mean.reshape((1,) + mean.shape)
		net = net.reshape((1,) + net.shape)
		return weightings(mean, net)
		
	def mean(self):
		self.reduced().values[0,::]
				
	def combine(self, other):
		return weightings(append(self.values, other.values), append(self.weights, other.weights))


class noise(object):

	"""Infinite array of Wiener processes.  This can be subscripted, to select specific processes.  It can also be called, to set the time and duration.  When enough parameters have been set, an ndarray of derivatives is returned."""
	
	def __init__(self):
		self.start = None
		self.duration = None
		self.bounds = None		# This will become a slice object
		self.parent = self		# Where to memoise parameters
		
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

	"""Draws fresh normal deviates with every new interval.  Repeating the last call returns the same results, so that semi-implicit methods converge."""
	
	def __init__(self, *args):
		noise.__init__(self, *args)
		self.last_bounds = None
		self.last_start = None
		self.last_duration = None
	
	def derivatives(self, bounds, start, duration):
		if (bounds, start) == (self.parent.last_bounds, self.parent.last_start):
			return self.parent.last_result / sqrt(duration / self.parent.last_duration)
		dims = [(s if isinstance(s, int) else s.stop - s.start) for s in bounds]
		if duration == 0.:
			result = ones(dims)
		else:
			result = normal_deviates(0, 1/sqrt(duration), dims)
		self.parent.last_bounds, self.parent.last_start, self.parent.last_duration, self.parent.last_result = bounds, start, duration, result
		return result
