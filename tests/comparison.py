# Compare my results to Laura's

from unittest import TestCase, main as run_tests
from subprocess import Popen, PIPE
from shlex import split
from fermi_hubbard import Simulator
from math import sqrt

class DeltaTest(TestCase):
	
	def setUp(self):
		self.command = split("matlab -maci -nojvm -nosplash -r")
		self.system = Simulator(repulsion = 1, chemical_potential = 0.5, hopping = 2, timestep = 0.1)
		self.state = self.system.initial()
		
	def testImport(self):
		s = self.system
		script = "Delta_M(%f, %f, %f, %f, 2, 1, %f, %s, %s); quit" % (s.hopping, s.repulsion, s.repulsion/abs(s.repulsion), s.chemical_potential, sqrt(s.timestep), mform(self.state.cdr[0,:,:]), mform(self.state.cdr[1,:,:]))
		child = Popen(self.command + [script], cwd="../laura")
		
		
def mform(xs):
	return str(xs.tolist())
	

if __name__ == '__main__':
	run_tests()
