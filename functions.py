from math import sqrt
from numpy.random import randn as normal_deviates
from numpy import array, diagonal, diagflat as make_diagonal, zeros, identity as unit, logical_or
from unittest import TestCase, main as run_tests


class TestAccessing(TestCase):

	def setUp(self):
		self.specimen = Simulator(repulsion = 1, chemical_potential = 0.5, hopping = 2, timestep = 0.1)
		
	def testRepulsion(self):
		self.assertEqual(self.specimen.repulsion, 1)
		
	def testCP(self):
		self.assertEqual(self.specimen.chemical_potential, 0.5)
		
	def testHopping(self):
		self.assertEqual(self.specimen.hopping, 2)
		
	def testTimestep(self):
		self.assertEqual(self.specimen.timestep, 0.1)
		
		
# Test data

def greens_specimens():
	return {
		"full": array( [unit(2), unit(2)] ),
		"all up": array( [zero(2), unit(2)] ),
		"all down": array( [unit(2), zero(2)] ) }
	
	
class TestRepulsionTerms(TestCase):

	"Simulator.repulsion_terms(n, spin) computes |U|(s n_jj(-spin) - n_jj,spin + 1/2)"

	def setUp(self):
		self.sltr = Simulator(repulsion = 1, chemical_potential = 0.5, hopping = 2, timestep = 0.1)
		self.sltr_strong = Simulator(repulsion = 3, chemical_potential = 0.5, hopping = 2, timestep = 0.1)

	def testSpinFlip(self):
		"Flipping the spin of all particles doesn't change the repulsion"
		
		for specimen in greens_specimens().values():
			for spin in range(2):
				straight = self.sltr.repulsion_terms(specimen, spin)
				flipped = self.sltr.repulsion_terms(specimen[::-1, :, :], spin)
				self.assertTrue((straight == flipped).all())
				
	def testScaling(self):
		"Tripling U triples the repulsion term"
		
		for specimen in greens_specimens().values():
			for spin in range(2):
				weak = self.sltr.repulsion_terms(specimen, spin)
				strong = self.sltr_strong.repulsion_terms(specimen, spin)
				self.assertTrue((3*weak == strong).all())
				
	def testOverlap(self):
		"Repulsion term is uniformly 1/2 unless two particles share a site."
		
		for specimen in greens_specimens().values():
			for spin in range(2):
				if logical_or(specimen[0,:,:] == 0, specimen[1,:,:] == 0).all():
					self.assertTrue((self.sltr.repulsion_terms(specimen, spin) == 0.5).all())


class TestDelta(TestCase): pass
	
	
				

class TestNoise(TestCase):

	"noise(n, dt)*dt is a n*n matrix with Wiener increments on the diagonal, and zeros elsewhere." 

	def setUp(self):
		self.sites = 10
		
	def testDiagonal(self):
		self.assertTrue(is_diagonal(noise(self.sites, 1)))
	
	def testIndependentElements(self):
		samples = noise(self.sites, 1).diagonal()
		self.assertEqual(len(set(samples)), self.sites)
		
	def testOrderMagnitude(self):
		"The mean square noise probably has the same order of magnitude as the timestep.  (Try again if it doesn't)"
		for step in 1, 0.1, 1e-5:
			samples = noise(self.sites, step).diagonal()
			variance = (step*samples).var()
			self.assertTrue(step/3 < variance and variance < 3*step)


# Implementation

class Simulator:

	def __init__(self, repulsion, hopping, chemical_potential, timestep):
		self.repulsion = repulsion
		self.hopping = hopping
		self.chemical_potential = chemical_potential
		self.timestep = timestep
		
	def repulsion_terms(self, normal_greens, spin):
		straight = diagonal(normal_greens[spin,:,:])
		flipped = diagonal(normal_greens[1-spin,:,:])
		return self.repulsion * flipped - abs(self.repulsion) * (0.5 - straight)

	def delta(self, normal_greens, spin, noise): pass
		
	

def noise(sites, timestep):
	return make_diagonal(normal_deviates(sites))/sqrt(timestep)
	
def is_diagonal(A):
	return (make_diagonal(diagonal(A)) == A).all()
	
def zero(n):
	return zeros([n, n])


if __name__ == '__main__':
    run_tests()
