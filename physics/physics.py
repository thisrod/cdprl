"""Classes to represent physical systems, and their numerical representations."""

class physicalSystem(object):
	"""My subclasses are abstract data types for physical systems.  They store physical parameters, and construct exact moments of the system's dynamics."""

	pass


class physicalState(object):
	"""I store a representation of a system, and its context.  The latter includes times and instances of stochastic processes.  I know how to compute derivatives of this representation, and moments."""

	pass


class stateEnsemble(object):
	"""I store a representation of a weighted ensemble of states."""
	
	def __init__(self, system, size):
		"""Subclasses should provide methods to initialise the representations for a well known state.  Integrators can assign self.noise directly."""
		self.system = system
		self.size = size
		self.time = 0.
		self.representations = None
		self.weights = ones((size,))
		
	def advanced(self, step, state = None):
		if state is None: state = self
		final = copy(self)
		final.time += step
		noise = self.noise.derivative(self.time, step)
		final.representations = self.representations + state.derivative(noise)
		final.weights = self.weights*(1 + state.weight_log_derivative(noise))
		return final
