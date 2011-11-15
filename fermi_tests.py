# python fermi_tests.py
from namespace import *
# FIXME delete following
from fermi_hubbard import *
from integration import *
from noise import *
from math import sqrt
from numpy import array, mat, diagonal, diagflat as make_diagonal, zeros, identity as unit, logical_or, isnan, allclose
from numpy.random import normal
from unittest import TestCase, main as run_tests
from weightings import Weighting
		
		
class OneDTest(TestCase):
		
	def setUp(self):
		self.moments = Record(timestep = 1)
		self.noise = DiscreteNoise()
		self.system = GreensFermiHubbard(sites = [2], repulsion = 0.5, hopping = 0, chemical_potential = 0)
		self.integrator = SemiImplicitIntegrator(self.system, self.noise, timestep = 0.01)
		
	def testSolution(self):
		self.integrator.integrate(self.system.initial(0.5), 3.1, self.moments)
		for t in range(3):
			computed = self.moments(t)
			self.assertFalse(isnan(computed).any())


class TwoDTest(TestCase):
		
	# case = TwoDTest('testSolution'); case.setUp()
	# Edit s/self/case/g
	def setUp(self):
		self.sites = [2,2]
		self.moments = Record(timestep = 1)
		self.noise = DiscreteNoise()
		self.system = GreensFermiHubbard(sites = self.sites, repulsion = 0.5, hopping = 0, chemical_potential = 0)
		self.integrator = SemiImplicitIntegrator(self.system, self.noise, timestep = 0.01)

	def testFilling(self):
		down = self.system.initial(0.3).mean[0,::]
		up = self.system.initial(0.3).mean[1,::]
		for i, j in cartesian_product(sites(self.sites), sites(self.sites)):
			expected = 0.3 if i == j else 0
			self.assertEqual(up[i+j], expected)
			self.assertEqual(down[i+j], expected)
		
		
	def testSolution(self):
		self.integrator.integrate(self.system.initial(0.5), 3.1, self.moments)
		for t in range(3):
			computed = self.moments(t)
			self.assertFalse(isnan(computed).any())
			
			
class TestDerivative(TestCase):
	
	def setUp(self):
		self.system = figure_1_system()
		
	def testZeroGreens(self):
		state = self.system.initial(0)
		no_noise = zeros(len(self.system.noise_required(state)))
		deriv = self.system.derivative(0, state, no_noise).mean
		self.assertTrue((deriv == 0).all())
		
	def testFullGreens(self):
		state = self.system.initial(1)
		no_noise = zeros(len(self.system.noise_required(state)))
		deriv = self.system.derivative(0, state, no_noise).mean
		self.assertTrue((deriv == 0).all())
		
		
class TestDerivativeScaling(TestCase):

	def setUp(self):
		self.original = FermiHubbardSystem(sites = [2,2], repulsion = 3, hopping = sqrt(3), chemical_potential = 0.5*3)
		self.U_scaled = FermiHubbardSystem(sites = [2,2], repulsion = 7, hopping = sqrt(7), chemical_potential = 0.5*7)
		offset = normal(0.1, 0.01, (2,2))
		self.state = self.original.initial(0.5) + Weighting(array([offset, offset]))
		self.no_noise = zeros(len(self.original.noise_required(self.state)))
		
	def testUScaling(self):
		deriv = self.original.derivative(0, self.state, self.no_noise).mean
		scaled = self.U_scaled.derivative(0, self.state, self.no_noise).mean
		self.assertTrue(allclose(scaled, deriv*sqrt(7./3.)))
		
		
## Manual testing assistance
		
def integrate_labels(integrator, initial, duration, record, labels):
	for i in labels:
		integrator.integrate(initial, duration, record, i)
		print i
		

if __name__ == '__main__':
	run_tests()
