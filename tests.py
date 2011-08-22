from functions import *
from math import sqrt
from numpy import array, mat, diagonal, diagflat as make_diagonal, zeros, identity as unit, logical_or
from unittest import TestCase, main as run_tests
		
		
# Test data

def greens_specimens():
	for it in [unit(2), unit(2)], [zero(2), unit(2)], [unit(2), zero(2)]:
		yield array(it)
		
def simulator_specimens():
	yield Simulator(repulsion = 1, chemical_potential = 0.5, hopping = 2, timestep = 0.1)
	
def noise_specimens(sites):
	yield zeros(sites)
	
def specimens():
	for sltr in simulator_specimens():
		for greens in greens_specimens():
			for spin in 0, 1:
				yield sltr, greens, spin


class TestAccessing(TestCase):

	def setUp(self):
		self.original = Simulator(repulsion = 1, chemical_potential = 0.5, hopping = 2, timestep = 0.1)
		self.copy = Simulator(self.original, hopping = 5)
		
	def testRepulsion(self):
		self.assertEqual(self.original.repulsion, 1)
		self.assertEqual(self.copy.repulsion, 1)
		
	def testCP(self):
		self.assertEqual(self.original.chemical_potential, 0.5)
		self.assertEqual(self.copy.chemical_potential, 0.5)
		
	def testHopping(self):
		self.assertEqual(self.original.hopping, 2)
		self.assertEqual(self.copy.hopping, 5)
		
	def testTimestep(self):
		self.assertEqual(self.original.timestep, 0.1)
		self.assertEqual(self.copy.timestep, 0.1)
	
	
class TestRepulsionTerms(TestCase):

	"Simulator.repulsion_terms(n, spin) computes |U|(s n_jj(-spin) - n_jj,spin + 1/2)"
	
	def testShape(self):
		for sltr, greens, spin in specimens():
			self.assertEqual(sltr.repulsion_terms(greens, spin).shape, greens.shape[1:2])

	def testSpinFlip(self):
		"Flipping the spin of all particles doesn't change the repulsion"
		
		for sltr, greens, spin in specimens():
			straight = sltr.repulsion_terms(greens, spin)
			flipped = sltr.repulsion_terms(greens[::-1, :, :], spin)
			self.assertTrue((straight == flipped).all())
				
	def testScaling(self):
		"Tripling U triples the repulsion term"
		
		for sltr, greens, spin in specimens():
			triple_sltr = Simulator(sltr, repulsion = 3*sltr.repulsion)
			weak = sltr.repulsion_terms(greens, spin)
			strong = triple_sltr.repulsion_terms(greens, spin)
			self.assertTrue((3*weak == strong).all())
				
	def testOverlap(self):
		"All repulsion terms are 1/2 unless two particles share a site."
		
		for sltr, greens, spin in specimens():
			if logical_or(greens[0,:,:] == 0, greens[1,:,:] == 0).all():
				self.assertTrue((sltr.repulsion_terms(greens, spin) == 0.5).all())


class TestDelta(TestCase):

	def testShape(self):
		for sltr, greens, spin in specimens():
			for noise in noise_specimens(greens.shape[1]):
				self.assertTrue(sltr.delta(greens, spin, noise).shape == greens[spin,:,:].shape)
	
	def testTridiagonal(self):
		for sltr, greens, spin in specimens():
			for noise in noise_specimens(greens.shape[1]):
				self.assertTrue(is_tridiagonal(sltr.delta(greens, spin, noise)))
				
				
class TestDerivative(TestCase):

	def testShape(self):
		for sltr, greens, spin in specimens():
			for noise1 in noise_specimens(greens.shape[1]):
				for noise2 in noise_specimens(greens.shape[1]):
					self.assertTrue(sltr.greens_dot(greens, spin, noise1, noise2).shape == greens[spin,:,:].shape)
					
	def testScaling(self):
		"Tripling U and scaling the noise input by 1/sqrt(3) cancel out."
		for sltr, greens, spin in specimens():
			scaled_sltr = Simulator(sltr, repulsion = sltr.repulsion * 3)
			for noise1 in noise_specimens(greens.shape[1]):
				for noise2 in noise_specimens(greens.shape[1]):
					self.assertTrue((scaled_sltr.greens_dot(greens, spin, noise1, noise2) == scaled_sltr.greens_dot(greens, spin, noise1/sqrt(3), noise2/sqrt(3))).all())
								

class TestNoise(TestCase):

	"noise(n, dt)*dt is a n*n matrix with Wiener increments on the diagonal, and zeros elsewhere." 

	def setUp(self):
		self.sites = 10
		
	def testShape(self):
		self.assertEqual(noise(self.sites, 1).shape, (self.sites,))
			
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

if __name__ == '__main__':
    run_tests()
