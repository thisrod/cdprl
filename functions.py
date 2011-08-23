from math import sqrt
from numpy.random import randn as normal_deviates
from numpy import array, mat, diagonal, diagflat as make_diagonal, zeros, identity as unit, logical_or



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
		return (state[0]*self.weight_log_dot(state[1]), (self.greens_dot(state[1], 0, noise), self.greens_dot(state[1], 1, noise)))
		
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
	
	
class Record:

	# I average the results of trial runs
	
	def __init__(self, a_simulation, timestep):
		self.sltn = a_simulation
		self.timestep = timestep
		
	def enter(self, time, state, **run_labels): pass
	
	def delay(self, time):
		return self.timestep
	

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
