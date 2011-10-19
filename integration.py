from collections import MutableMapping, Callable
from InterpoList import InterpoList as Interpolation
from weightings import Weighting
from numpy import array

# StepwiseIntegrator computes steps with the increment method, which must be overridden by subclasses.

class Integrator:

	def __init__(self, a_simulation, a_noise_source, timestep):
		self.system = a_simulation
		self.timestep = float(timestep)
		self.noise = a_noise_source
		
	def integrate(self, initial_state, duration, record, *run_labels):
		"""stochastically integrate a single sample, starting at time 0"""
		self.noise.set_labels(run_labels)
		t = 0
		state = initial_state
		next_sample_time = 0
		while t <= duration:
			if t > (next_sample_time - 0.5*self.timestep):
				record[(t,) + run_labels] = self.system.moments(state)
				next_sample_time = record.after(next_sample_time)
			t, state = t + self.timestep, state + self.increment(t, state)

	
class SemiImplicitIntegrator(Integrator):
		
	def increment(self, t, state):
		halfstep = state
		xis = array([self.noise[i](t, self.timestep) for i in self.system.noise_required(state)])
		for i in range(4):
			halfstep = state + 0.5*self.timestep*self.system.derivative(t, halfstep, xis)
		return self.timestep*self.system.derivative(t, halfstep, xis)
		

	
class Record(MutableMapping, Callable):

	""" I average the results of trial runs """
	
	# results is a dictionary of run_labels
	# results[run_label] is an Interpolation from times to Weightings
	# moments need to interpret + and * as elemental operations.  I.e., ndarrays are in, but lists and tuples are out.
	
	# self[t] is a tuple of weight and moments.  self[t] = moments implies the weight is 1.0

	# warning: Python ad-hocity: x[2] means x.__getitem__(2), but x[2,3] means x.__getitem__((2,3))
	
	def __init__(self, timestep):
		self.timestep = timestep
		self.results = {}
		
	def demux_key(self, key):
		# Split key into time and run_label
		if type(key) is tuple:
			return float(key[0]), key[1:]
		else:
			return float(key), ()
		
	def demux_value(self, value):
		# Split value into weight and moments
		# Storing moments in tuples ist verboten: see class comment.
		if type(value) is tuple:
			return float(value[0]), value[1]
		else:
			return 1.0, value
			
	def __call__(self, key):
		time, prefix = self.demux_key(key)
		total = Weighting(0, 0)
		for x in [self.results[label](time) for label in self.results if label[0:len(prefix)]==prefix]:
			total = total.combine(x)
		return total.mean
	
	def __delitem__(self, key): pass 
	
	def __iter__(self): pass
	
	def __len__(self): pass	# Presumably answer the number of items stored?
	
	def __setitem__(self, key, value):
		time, run_label = self.demux_key(key)
		weight, moments = self.demux_value(value)
		if run_label not in self.results:
			self.results[run_label] = Interpolation()
		self.results[run_label][time] = Weighting(moments, weight)
		
	def __getitem__(self, key):
		time, run_label = self.demux_key(key)
		w = self.results[run_label][time]
		return w.weight, w.mean 
	
	def after(self, time):
		return time + self.timestep
