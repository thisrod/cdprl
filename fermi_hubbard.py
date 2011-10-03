from numpy.random import randn as normal_deviates
from numpy import array, mat, diagonal, diagflat as make_diagonal, zeros, identity as unit, logical_or
from pairs import Pair, cons
from math import sqrt


class Simulator:

	# I remember the physical parameters of the Fermi-Hubbard model, and compute the derivatives of the Greens' function and weight.

	"""Parameters: repulsion, hopping, chemical_potential
	
	The state is represented as a tuple of the weight, and a 2xsitesxsites array of the up and down greens functions"""

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
		# state is a pair of weight and Greens' functions
		return Pair(state.car*self.weight_log_dot(state.cdr), array([self.greens_dot(state.cdr, 0, noise), self.greens_dot(state.cdr, 1, noise)]))
		
	def noise_required(self, state):
		greens = state.cdr
		return range(2*greens.shape[2])
		
	def weight(self, state):
		return state[0]
		
	def moments(self, state):
		# The moments to be collected are the Green's functions
		return state.cdr

	def initial(self):
		id = unit(self.sites[0])
		return Pair(1.0, array([id, id]))
		
			
		

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
