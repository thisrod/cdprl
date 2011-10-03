# Tests that a stochastic integrator gives the right answers for a Kubo oscillator.

from unittest import TestCase, main as run_tests
from integration import *
from noise import DiscreteNoise
from cmath import exp

class KuboOscillator:
	# A simulator.  States are the number x.

	def __init__(self, resonance_frequency):
		self.resonance_frequency = resonance_frequency
		
	def noise_required(self, state):
		return range(1)
	
	def derivative(self, time, state, noise):
		return 1j*state*(self.resonance_frequency + noise[0])
		
	def moments(self, state):
		return state
		
	def initial(self):
		return 1.0

	def exact(self, duration, noise):
		return self.initial() * \
			exp(1j * (self.resonance_frequency + noise[0](0, duration)) * duration)
		

		
class IntegrationTest(TestCase):
	
	def setUp(self):
		self.moments = Record(timestep = 1)
		self.noise = DiscreteNoise(timestep = 0.01)
		self.system = KuboOscillator(resonance_frequency = 1)
		self.integrator = SemiImplicitIntegrator(self.system, self.noise, timestep = 0.01)
		self.integrator.integrate(self.system.initial(), 3.1, self.moments)
		
	def testSolution(self):
		for t in range(3):
			exact = self.system.exact(t, self.noise)
			computed = self.moments(t)
			self.assertTrue(abs(computed - exact) < 0.05*abs(exact))
			

if __name__ == '__main__':
	run_tests()
