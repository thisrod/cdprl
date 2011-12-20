"""System and representation for the Kubo oscillator.  To be made parallel, as a CUDA exercise."""

from dynamics import *

class KuboOscillator(object):
	def __init__(self, resonance_frequency):
		self.w = resonance_frequency


class KuboAmplitudes(ensemble):

	def set_amplitude(self, x0):
		self.initial_amplitude = x0
		self.representations = empty_array(self.size)
		self.representations[:] = x0
		
	def derivative(self, noise):
		return 1j*self.representations*(self.system.w + noise[0:self.size])
		
	def advanced_exactly(self, duration):
		final = copy(self)
		final.time += duration
		noise = self.noise[0:self.size](self.time, duration)
		final.representations =  self.representations * \
			exp(1j * (self.system.w + noise[0:self.size]) * duration)
		return final
		
	def amplitude_moment(self):
		return weightings(self.representations, ones(self.size))

	def expected_amplitude(self):
		x = self.initial_amplitude * exp(self.time*(1j*self.w-0.5))
		return weightings(x, 1)
