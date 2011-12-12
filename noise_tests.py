from namespace import *
from dynamics import *

## Tests of the prng

class SourceTest(TestCase):

	def setUp(self):
		self.source = numpyNoise()
	

class TestShape(TestCase):
		
	def testShape(self):
		self.assertEqual(numpyNoise()[0:1,0:2](1,0.1).shape, (1,2))
		self.assertEqual(numpyNoise()[0:1,0:2](1,0.0).shape, (1,2))

class TestSingleProcess(SourceTest):
		
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
			
			
class TestTwice(SourceTest):

	def testSame(self):
		"Generating the same noise twice in a row gives the same answer.  This is important for semi-implicit integration to converge."
		first = self.source[0:5](0.5,0.2)
		second = self.source[0:5](0.5,0.2)
		self.assertTrue((first==second).all())
		
	def testScaled(self):
		first = self.source[0:5](0.5,0.1)
		second = self.source[0:5](0.5,0.2)
		self.assertTrue(allclose(first*sqrt(2), second))
			
class TestSpecialCases(SourceTest):
		
	def testEmptyInterval(self):
		"Zero times a Wiener derivative over a zero-length interval is zero."
		
		self.assertEqual(0.* self.source[0:1](0.5,0.)[0], 0.)
	
			

if __name__ == '__main__':
    run_tests()
