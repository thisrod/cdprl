from math import sqrt
from numpy.random import randn as normal_deviates
from numpy import array, mat, diagonal, diagflat as make_diagonal, zeros, identity as unit, logical_or
from InterpoList import InterpoList as Interpolation
from collections import MutableMapping, Callable



class Simulator:

	# I remember the physical parameters of the Fermi-Hubbard model, and compute the derivatives of the Greens' function and weight.

	def __init__(self, model = None, **parameters):
		if model is not None:
			self.__dict__ = model.__dict__.copy()
		self.__dict__.update(parameters)
		
	def repulsion_terms(self, normal_greens, spin):
		straight = diagonal(normal_greens[spin,:,:])
		flipped = diagonal(normal_greens[1-spin,:,:])
		return self.repulsion * flipped - abs(self.repulsion) * (0.5 - straight)

	def delta(self, normal_greens, spin, noise):
		sites = normal_greens.shape[1]
		if spin == 1:
			f = 1
		else:
			f = -self.repulsion/abs(self.repulsion)
		return \
			make_diagonal([self.hopping]*(sites-1), 1) \
			+ make_diagonal([self.hopping]*(sites-1), -1) \
			- make_diagonal( \
				self.repulsion_terms(normal_greens, spin) \
				- self.chemical_potential \
				+ f * sqrt(2*abs(self.repulsion)) * noise)
				
	def greens_dot(self, normal_greens, spin, noise):
		n = normal_greens[spin,:,:]
		noise1 = noise[:len(noise)//2]
		noise2 = noise[-(len(noise)//2):]
		particles = mat(n)
		holes = mat(unit_like(n) - n)
		delta1 = mat(self.delta(normal_greens, spin, noise1))
		delta2 = mat(self.delta(normal_greens, spin, noise2))
		return 0.5*(holes*delta1*particles + particles*delta2*holes)

	def weight_log_dot(self, normal_greens):
		return self.hopping * (diagonal(normal_greens[0,:,:], 1) + diagonal(normal_greens[0,:,:], -1) + diagonal(normal_greens[1,:,:], 1) + diagonal(normal_greens[1,:,:], -1)).sum() \
			+ self.repulsion * (normal_greens[0,:,:]*normal_greens[1,:,:]).sum() \
			- self.chemical_potential * ( diagonal(normal_greens[0,:,:]) + diagonal(normal_greens[1,:,:]) ).sum()
			
	def derivative(self, time, state, noise):
		# state is a tuple of weight and Greens' functions
		return (state[0]*self.weight_log_dot(state[1]), array([self.greens_dot(state[1], 0, noise), self.greens_dot(state[1], 1, noise)]))
		
	def noise_required(self, state):
		greens = state[1]
		return 2*greens.shape[2]
		
	def weight(self, state):
		return state[0]
		
	def moments(self, state):
		# The moments to be collected are the Green's functions
		return state[1]
	
	
class SemiImplicitIntegrator:

	# I stochastically integrate a single sample	

	def __init__(self, a_simulation, timestep):
		self.sltn = a_simulation
		self.timestep = timestep
		
	def integrate(self, start, finish, a_record, **run_labels): pass
	
	
class Record(MutableMapping, Callable):

	""" I average the results of trial runs """
	
	# results is a dictionary of run_labels
	# results[run_label] is an Interpolation from times to (weight, moments) pairs 
	# moments need to interpret + and * as elemental operations.  I.e., ndarrays are in, but lists and tuples are out.
	
	# self[t] is a tuple of weight and moments.  self[t] = moments implies the weight is 1.0

	# Python bogosity warning: x[2] means x.__getitem__(2), but x[2,3] means x.__getitem__((2,3))
	
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
			
	def __call__(self, time): pass
	
	def __delitem__(self, key): pass 
	
	def __iter__(self): pass
	
	def __len__(self): pass	# Presumably answer the number of items stored?
	
	def __setitem__(self, key, value):
		time, run_label = self.demux_key(key)
		weight, moments = self.demux_value(value)
		if run_label not in self.results:
			self.results[run_label] = Interpolation()
		self.results[run_label][time] = (weight, moments)
		
	def __getitem__(self, key):
		time, run_label = self.demux_key(key)
		return self.results[run_label][time]	# This could raise a genuine IndexError
	
	def after(self, time):
		return time + self.timestep

	def mean(self, time):
		return mean([self.value(time, i) for i in self.results])
		
	def value(self, time, run_label):
		# bug - should detect out of range
		# bug - look for a stable way to do interpolation (notebook 24/8/11)
		series = self.results[run_label]
		if time in series:
			return series[time]
		pre = max([t for t in series if t < time])
		post = min([t for t in series if t > time])
		return series[pre] + (series[post]-series[pre])*(t-pre)/(post-pre)
			
		

def noise(sites, timestep):
	return make_diagonal(normal_deviates(sites))/sqrt(timestep)
	
def is_diagonal(A):
	return (make_diagonal(diagonal(A)) == A).all()
	
def is_tridiagonal(A):
	return (make_diagonal(diagonal(A,-1),-1) + make_diagonal(diagonal(A)) + make_diagonal(diagonal(A,1),1) == A).all()
	
def zero(n):
	return zeros([n, n])

def unit_like(array):
	return unit(array.shape[0])
	
def mean(xs):
	return sum(xs)/len(xs)
