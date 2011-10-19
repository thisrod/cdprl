from random import getstate, setstate, seed, normalvariate
from math import sqrt


class Noise:

	"""I am the abstract base class for noise sources.
	
	If x is a noise source, x[i] is the ith process, and x[i](t, dt) is its average derivative from t to t+dt.  This can also be written x(t, dt)[i], because x(t, dt) is a sequence of the derivatives of all processes.
	
	As a special case, x(t, 0) is zero.  This ensures dx = 0 when dt = 0, when there's a 0*Infinity ambiguity.  
	
	Subclasses need to override __init__, to handle their run labels, and derivatives, to generate the noise."""

	def __init__(self):
		raise(NotImplementedError)

	def __call__(self, start, duration):
		return IntervalSpecialisedNoise(self, start, duration)
		
	def __getitem__(self, indices):
		return ProcessSpecialisedNoise(self, indices)
		
	def derivatives(self, indices, start, duration):
		"""Return a tuple of average derivatives for processes in the stride or number indices, from start, over duration."""
		raise(NotImplementedError)
		

class IntervalSpecialisedNoise:

	def __init__(self, noise, start, duration):
		self.noise = noise
		self.start = start
		self.duration = duration
		
	def __getitem__(self, indices):
		return self.noise.derivatives(indices, self.start, self.duration)
		
	
class ProcessSpecialisedNoise:

	def __init__(self, noise, indices):
		self.noise = noise
		self.indices = indices
	
	def __call__(self, start, duration):
		return self.noise.derivatives(self.indices, start, duration)
		
		
class DiscreteNoise(Noise):

	"""This noise source seeds a Python PRNG for each process and run_labels, which generates independent derivatives for intervals of length timestep, starting from time 0."""

	def __init__(self, timestep):
		self.timestep = timestep
		self.rngs = {}
		self.installed_indices = self.step = None
		
	def set_labels(self, labels):
		self.run_labels = labels
	
	def derivatives(self, index, start_time, duration):
		if duration == 0: return 0
		start = int(round(start_time / self.timestep))
		steps = int(round(duration / self.timestep))
		
		# only handle one index for now
		self.install(index)
		self.advance(start)
		mean = sum([self.step_derivative() for i in range(steps)]) / steps
		return mean
		
	def install(self, indices):
		if self.installed_indices == indices: return
		self.rngs[self.installed_indices] = (getstate(), self.step)
		if indices not in self.rngs:
			self.initialize(indices)
		else:
			state, self.step = self.rngs[indices]
			setstate(state)
			self.installed_indices = indices
				
	def advance(self, start):
		if self.step > start:
			self.initialize(self.installed_indices)
		while self.step < start:
			normalvariate(0, 1)
			self.step = self.step + 1
			
	def initialize(self, indices):
		seed((self.run_labels, indices))
		self.installed_indices = indices
		self.step = 0
		
	def step_derivative(self):
		self.step = self.step + 1
		return normalvariate(mu = 0, sigma = 1/sqrt(self.timestep))
