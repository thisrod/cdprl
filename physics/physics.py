"""Classes to represent physical systems, and their numerical representations."""

class physicalSystem(object):
	"""My subclasses are abstract data types for physical systems.  They store physical parameters, and construct exact moments of the system's dynamics."""

	pass


class physicalState(object):
	"""I store a representation of a system, and its context.  The latter includes times and instances of stochastic processes.  I know how to compute derivatives of this representation, and moments."""

	pass


class stateEnsemble(object):
	"""I store a representation of a weighted ensemble of states."""

	def increment(self, step):
		"An object that can be added to me to obtain a state step in the future."
		
	def __add__(self, other):
		assert self.system == other.system
		result = copy(self)
		result.time += other.time
		result.representations += other.representations
		result.weights += other.weights
		return result