from namespace import *
from dynamics import *

## Tests of the prng

class TestShape(TestCase):
		
	def testShape(self):
		self.assertEqual(numpyNoise()[0:1,0:2](1,0.1).shape, (1,2))

class TestSingleProcess(TestCase):

	def setUp(self):
		self.source = numpyNoise()
		
	def testType(self):
		self.assertTrue(isinstance(self.source[0:1](0.5,0.2)[0], float))
			
	def testIndependentElements(self):
		samples = [self.source[0:1](0.1*t, 0.1)[0] for t in range(20)]
		self.assertEqual(len(set(samples)), 20)
		
	def testIndependentProcesses(self):
		first = [self.source[0:1](0.1*t, 0.1)[0] for t in range(20)]
		second = [self.source[1:2](0.1*t, 0.1)[0] for t in range(20)]
		self.assertEqual(len(set(first+second)), 40)
		
		
	def testOrderMagnitude(self):
		"The mean square noise probably has the same order of magnitude as the timestep.  (Try again if it doesn't)"
		for step in 10, 1, 0.1:
			samples = array([self.source[0:1](step*t, step)[0] for t in range(20)])
			variance = (step*samples).var()
			self.assertTrue(step/3 < variance and variance < 3*step)

if __name__ == '__main__':
    run_tests()
