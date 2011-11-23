
def integrate_exactly(state, duration, record):
	"record.after rounds up, record.next assumes time is close to recording time"
	state = state.advanced_exactly(record.after(state))
	while record.next(state) <= end:
		record.add(state)
		state = state.advanced_exactly(record.next(state))
	if state.time <= end:
		record.add(state)
		

class stepwise_integrator(object):

	def __init__(self, timestep):
		self.step = timestep

	def __call__(self, state, duration, record)
		final_time = state.time + duration
		sample_time = record.after(state.time)
		while state.time < final_time:
			while state.time < min(final_time, sample_time):
				state = self.advance(state)
			if state.time >= sample_time:
				record.add(state)
			sample_time = record.next(state.time)

	
class semi_implicit_integrator(stepwise_integrator):
		
	def advance(self, state):
		halfstep = state
		for i in range(4):
			halfstep = state.advanced(0.5*self.step, halfstep)
		return state.advanced(self.step, halfstep)
