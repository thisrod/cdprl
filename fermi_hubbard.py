from numpy.random import randn as normal_deviates
from numpy import array, zeros, identity as unit, logical_or
from weightings import Weighting
from ndmat import ndmat
from adjacencies import *
from math import sqrt, copysign
from operator import mul
from itertools import product


class FermiHubbardSystem:

	# I remember the physical parameters of the Fermi-Hubbard model, and compute the derivatives of the Greens' function and weight.
	# Moments are a subclass responsibility.

	"""Parameters: sites, repulsion, hopping, chemical_potential
	
	The state is represented as a Weighting, whose value is a 2x[sites]x[sites] array of the up and down greens functions.  Here [sites] is the dimensions of the grid, stored as a tuple."""

	def __init__(self, model = None, **parameters):
		if model is not None:
			self.__dict__ = model.__dict__.copy()
		self.__dict__.update(parameters)
		
		self.sites = tuple(self.sites)
							
	def derivative(self, time, state, noise):
	
		greens = state.mean
		noise = array(noise).reshape((2,)+self.sites)
	
		def greens_dot(spin):
			n = greens[spin,::]
			
			particles = ndmat(n)
			holes = ndmat(unit_like(n) - n)
			
			return 0.5*(holes*delta(spin, 0)*particles + particles*delta(spin, 1)*holes)
	
		def delta(spin, r):
			
			def repulsion(site):
				"Compute |U|(sn_jj-n_jj+1/2)"
				# FIXME: I'm slow
				return self.repulsion * greens[(1-spin,)+2*site] \
					+ abs(self.repulsion) * (0.5 - greens[(spin,)+2*site])
	
			f = 1 if spin == 1 else copysign(1, -self.repulsion)
				
			result = ndmat(zeros(2*self.sites))
			for i in sites(self.sites):
				result[2*i] = -repulsion(i) \
					- f * sqrt(2*abs(self.repulsion)) * noise[(r,)+i] \
					+ self.chemical_potential
			for i, j in adjacencies(self.sites):
				assert(i != j)
				result[i+j] = self.hopping
			return result

		weight_log_dot = \
			self.hopping * sum([greens[(0,)+i+j] + greens[(1,)+i+j] for i, j in adjacencies(self.sites)]) \
				+ self.repulsion * (greens[0,::]*greens[1,::]).sum() \
				- self.chemical_potential * sum([ greens[(0,)+i+i] + greens[(1,)+i+i] for i in sites(self.sites)])
				
		return Weighting( \
			array([greens_dot(0), greens_dot(1)]), \
			weight = state.weight*weight_log_dot)
		
	def noise_required(self, state):
		return range(2*reduce(mul, self.sites))
		
	def moments(self, state):
		raise 'Subclass responsibility'

	def initial(self, filling):
		"Answer the state at infinite temperature for given filling"
		id = zeros(self.sites*2)
		for i in sites(self.sites):
			id[i*2] = filling
		return Weighting(array([id, id]))


class CorrelationFermiHubbard(FermiHubbardSystem):
		
	def moments(self, state):
		# The moments to be collected are a 2x2 matrix of spin correlation functions, averaged over sites
		corr = zeros([2,2])
		for i in range(2):
			for j in range(2):
				corr[i,j] = (state.mean[i,::]*state.mean[j,::]).sum()
		return corr / corr.size
	
	
class GreensFermiHubbard(FermiHubbardSystem):
		
	def moments(self, state):
		return state.mean

def figure_1_system():
	return CorrelationFermiHubbard(sites = [2], repulsion = 2, hopping = 0, chemical_potential = 1)

def figure_1_g2(matrix):
	return matrix[0,1]/matrix[0,0]
	
		
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

def print_greens(greens):
	print "\t\tUP\t\t"
	for i in range(greens.shape[1]):
		for ii in range(greens.shape[2]):
			for j in range(greens.shape[3]):
				for jj in range(greens.shape[4]):
					print "%.2f\t" % (greens[0, i, j, ii, jj]),
				print "\t",
			print
		print
	print "\t\tDOWN\t\t"
	for i in range(greens.shape[1]):
		for ii in range(greens.shape[2]):
			for j in range(greens.shape[3]):
				for jj in range(greens.shape[4]):
					print "%.2f\t" % (greens[1, i, j, ii, jj]),
				print "\t",
			print
		print
