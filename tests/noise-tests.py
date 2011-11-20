from unittest import TestCase, main as run_tests
from functions import *

## Tests of the prng

class TestSingleProcess(TestCase):

	def setUp(self):
		self.source = DiscreteNoise(0.1)
		
	def testType(self):
		self.assertTrue(type(self.source[0](0.5,0.2)) is float)
			
	def testIndependentElements(self):
		samples = [self.source[0](0.1*t, 0.1) for t in range(20)]
		self.assertEqual(len(set(samples)), 20)
		
	def testIndependentProcesses(self):
		first = [self.source[0](0.1*t, 0.1) for t in range(20)]
		second = [self.source[1](0.1*t, 0.1) for t in range(20)]
		self.assertEqual(len(set(first+second)), 40)
		
		
	def testOrderMagnitude(self):
		"The mean square noise probably has the same order of magnitude as the timestep.  (Try again if it doesn't)"
		for step in 10, 1, 0.1:
			samples = array([self.source[0](step*t, step) for t in range(20)])
			variance = (step*samples).var()
			self.assertTrue(step/3 < variance and variance < 3*step)

if __name__ == '__main__':
    run_tests()
