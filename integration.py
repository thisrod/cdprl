"""Example:
from integration import *
from kubo import *
state = KuboAmplitudes(KuboOscillator(0.5), 10)
state.set_amplitude(1.5)
state.noise = numpyNoise()
integrate = semi_implicit_integrator(0.01)
numerical = record(1, ["amplitude_moment", "expected_amplitude"])
integrate(state, 5, numerical)
numerical.results['amplitude_moment'][2.0].values
"""

def integrate_exactly(state, duration, record):
	"record.after rounds up, record.next assumes time is close to recording time"
	end = state.time + duration
	final = state.advanced_exactly(record.after(state.time))
	while final.time <= end:
		record.add(final)
		final = state.advanced_exactly(record.next(final.time))
	if final.time <= end:
		record.add(final)
		

class stepwise_integrator(object):

	def __init__(self, timestep):
		self.step = timestep

	def __call__(self, state, duration, record):
		final_time = state.time + duration
		sample_time = record.after(state.time)
		while state.time < final_time:
			while state.time < min(final_time, sample_time):
				state = self.advance(state)
			if state.time >= sample_time:
				record.add(state)
			sample_time = record.next(state.time)

	
class semi_implicit_integrator(stepwise_integrator):

	# This requires noise be somewhat reproducible.  See testTwice in noise_tests.py.
		
	def advance(self, state):
		halfstep = state
		for i in range(4):
			halfstep = state.advanced(0.5*self.step, halfstep)
		return state.advanced(self.step, halfstep)
