from numpy.random import randn as normal_deviates
from numpy import array, mat, diagonal, diagflat as make_diagonal, zeros, identity as unit, logical_or
from weightings import Weighting
from adjacencies import *
from math import sqrt
from operator import mul


class FermiHubbardSystem:

	# I remember the physical parameters of the Fermi-Hubbard model, and compute the derivatives of the Greens' function and weight.

	"""Parameters: sites, repulsion, hopping, chemical_potential
	
	The state is represented as a Weighting, whose value is a 2x[sites]x[sites] array of the up and down greens functions.  Here [sites] is the dimensions of the grid."""

	def __init__(self, model = None, **parameters):
		if model is not None:
			self.__dict__ = model.__dict__.copy()
		self.__dict__.update(parameters)

	def delta(self, normal_greens, spin, noise):
		
		def repulsion(self, site):
			return self.repulsion * greens[(1-spin,)+2*site] \
				- abs(self.repulsion) * (0.5 - greens[(spin,)+2*site])

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
							
	def derivative(self, time, state, noise):
	
		greens = state.mean
	
		def greens_dot(spin):
			n = normal_greens[spin,:,:]
			noise1 = noise[:len(noise)//2]
			noise2 = noise[-(len(noise)//2):]
			particles = mat(n)
			holes = mat(unit_like(n) - n)
			delta1 = mat(self.delta(normal_greens, spin, noise1))
			delta2 = mat(self.delta(normal_greens, spin, noise2))
			return 0.5*(holes*delta1*particles + particles*delta2*holes)
	
		weight_log_dot = \
			self.hopping * sum([greens[(0,)+i+j] + greens[(1,)+i+j] for i, j in adjacencies(self.sites)]) \
				+ self.repulsion * (greens[0,::]*greens[1,::]).sum() \
				- self.chemical_potential * sum([greens[(0,)+i+i] + [greens[(1,)+i+i] for i in sites(self.sites)])
				
		return Weighting( \
			array([greens_dot(0), greens_dot(1)]), \
			weight = state.weight*weight_log_dot)
		
	def noise_required(self, state):
		return range(2*reduce(mul, self.sites))
		
	def moments(self, state):
		# The moments to be collected are the Green's functions
		return state.mean

	def initial(self):
		"Answer the state at infinite temperature"
		id = zeros(self.sites*2)
		for i in sites(self.sites):
			id[i*2] = 1
		return Weighting(array([id, id]))
		
			
		

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
