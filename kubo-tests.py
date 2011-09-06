# Tests that a stochastic integrator gives the right answers for a Kubo oscillator.

from unittest import TestCase, main as run_tests

class KuboOscillator:
	# A simulator.  States are the number x.

	def __init__(self, resonance_frequency):
		self.resonance_frequency = resonance_frequency
		
	def noise_required(self, state):
		return 1
	
	def derivative(self, time, state, noise):
		return 1j*state*(resonance_frequency + noise[0])
		

def exact_kubo(initial_position, duration, noise):
	return initial_position * \
		exp(1j * (self.resonance_frequency + noise[0](0, duration)) * duration)