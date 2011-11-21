"""System and representation for the Kubo oscillator.  To be made parallel, as a CUDA exercise."""

from namespace import *
from physics import *

class KuboOscillator(physicalSystem):
	def __init__(self, resonance_frequency):
		self.w = resonance_frequency

	def expected_amplitude(self, order):
		def moment(state):
			pass		# Kubo formula goes here
		return moment


class KuboAmplitudes(stateEnsemble):
	def __init__(self, system, initial_amplitude, size):
		self.system = system
		self.time = 0
		self.amplitudes = array((initial_amplitude,)*size)
		self.weights = ones(size)
		
	def amplitude_moment(self, power):
		total = self.weights*self.amplitudes**power
		w = sum(self.weights)
		return weighting(total/w, w)
		
	def weight_log_derivative(self):
		return zeros_like(self.weights)
		
		
		
		
class ExactKuboIntegrator(integrator):
	"""I advance the amplitudes by the exact exponential of W(t)."""
	
	pass