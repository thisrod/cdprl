# Tests of the class Record

from unittest import TestCase, main as run_tests
from functions import *


class TestIdentical(TestCase):

	"The average of identical data is the datum."

	def setUp(self):
		self.specimen = Record(timestep = 1)
		
	def testOneSample(self):
		self.specimen[0] = 7
		self.assertTrue(self.specimen(0) == 7)
		
	def testThreeSamples(self):
		self.specimen[0, 'run1'] = 7
		self.specimen[0, 'run2'] = 7
		self.specimen[0, 'run3'] = 7
		self.assertTrue(self.specimen(0) == 7)
		
	def testConstant(self):
		self.specimen[-1] = 7
		self.specimen[1] = 7
		self.assertTrue(self.specimen(0) == 7)
		
	def testInterpolation(self):
		self.specimen[-0.1] = 7
		self.specimen[0.1] = 7
		self.assertTrue(self.specimen(0) == 7)
		
		
class TestWeighted(TestCase):

	def setUp(self):
		self.specimen = Record(timestep = 1)
		self.specimen[0, 'run1'] = (0.5, 7)
		self.specimen[0, 'run2'] = (1.5, 13)


class TestTiming(TestCase):
	
	def setUp(self):
		self.specimen = Record(timestep = 1)
		
	def testAfter(self):
		for t in 1e-3, 1, 1000:
			self.assertTrue(self.specimen.after(t) > t)
			
	def testRange(self):
		"Forgive me father, I have compared floating point values for equality.  What does Python call closeTo?" 
		for t in 1e-3, 1, 1000:
			self.assertTrue(self.specimen.after(t) <= t+1)
	
		
		


if __name__ == '__main__':
	run_tests()
