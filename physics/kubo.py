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

	def set_amplitude(self, x0):
		self.representations = empty_array(self.size)
		self.representations[:] = x0
		
	def derivative(self, noise):
		return 1j*self.representations*(self.system.w + noise[0:self.size])
		
	def weight_log_derivative(self, noise):
		return zeros_like(self.weights)
		
	def advanced_exactly(self, duration):
		final = copy(self)
		final.time += duration
		noise = self.noise.derivative(self.time, duration)	# CHECKME
		final.representations =  self.representations * \
			exp(1j * (self.system.w + noise[0:self.size]) * duration)
		return final
		
	def amplitude_moment(self, power):
		total = self.weights*self.amplitudes**power
		w = sum(self.weights)
		return weighting(total/w, w)
