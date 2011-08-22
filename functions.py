from math import sqrt
from numpy.random import randn as normal_deviates
from numpy import array, mat, diagonal, diagflat as make_diagonal, zeros, identity as unit, logical_or



class Simulator:

	"Noise inputs are scaled by timestep, but not by U.  Think about that some more."

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
				
	def greens_dot(self, normal_greens, spin, noise1, noise2):
		n = normal_greens[spin,:,:]
		particles = mat(n)
		holes = mat(unit_like(n) - n)
		delta1 = mat(self.delta(normal_greens, spin, noise1))
		delta2 = mat(self.delta(normal_greens, spin, noise2))
		return 0.5*(holes*delta1*particles + particles*delta2*holes)
	

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
