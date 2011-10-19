# python fermi_tests.py
from fermi_hubbard import *
from integration import *
from noise import *
from math import sqrt
from numpy import array, mat, diagonal, diagflat as make_diagonal, zeros, identity as unit, logical_or, isnan
from unittest import TestCase, main as run_tests
from pairs import Pair
from weightings import Weighting
		
		
# Test data

def greens_specimens():
	for it in [unit(2), unit(2)], [zero(2), unit(2)], [unit(2), zero(2)]:
		yield array(it)
		
def simulator_specimens():
	yield FermiHubbardSystem(sites = [2], repulsion = 1, chemical_potential = 0.5, hopping = 2)
	
def noise_specimens(sites):
	yield zeros(2*sites)
	
def specimens():
	for sltr in simulator_specimens():
		for greens in greens_specimens():
			for spin in 0, 1:
				yield sltr, Weighting(greens), spin
				

		


class OneDTest(TestCase):
		
	def setUp(self):
		self.moments = Record(timestep = 1)
		self.noise = DiscreteNoise(timestep = 0.01)
		self.system = FermiHubbardSystem(sites = [2], repulsion = 0.5, hopping = 0, chemical_potential = 0)
		self.integrator = SemiImplicitIntegrator(self.system, self.noise, timestep = 0.01)
		
	def testSolution(self):
		self.integrator.integrate(self.system.initial(), 3.1, self.moments)
		for t in range(3):
			computed = self.moments(t)
			self.assertFalse(isnan(computed).any())


class TwoDTest(TestCase):
		
	def setUp(self):
		self.moments = Record(timestep = 1)
		self.noise = DiscreteNoise(timestep = 0.01)
		self.system = FermiHubbardSystem(sites = [2,2], repulsion = 0.5, hopping = 0, chemical_potential = 0)
		self.integrator = SemiImplicitIntegrator(self.system, self.noise, timestep = 0.01)
		
	def testSolution(self):
		self.integrator.integrate
		for t in range(3):
			computed = self.moments(t)
			self.assertFalse(isnan(computed).any())

if __name__ == '__main__':
	run_tests()
