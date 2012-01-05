# Tests of the class Record

from unittest import TestCase, main as run_tests
from integration import *


class TestAccessing(TestCase):

	def setUp(self):
		self.specimen = Record(timestep = 1)
		
	def testEmpty(self):
		self.assertFalse(3 in self.specimen)
		
	def testAdding(self):
		self.specimen[3] = 7
		self.assertTrue(3 in self.specimen)
		self.assertEqual(self.specimen[3], (1.0, 7))
		
	def testAddingWithRunLabel(self):
		self.specimen[3, 'run'] = 7
		self.assertTrue((3, 'run') in self.specimen)
		self.assertEqual(self.specimen[3, 'run'], (1.0, 7))
		

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
		self.assertEqual(self.specimen(0), 7)
		
	def testInterpolation(self):
		self.specimen[-0.1] = 7
		self.specimen[0.1] = 7
		self.assertTrue(self.specimen(0) == 7)
		
		
class TestWeighted(TestCase):

	def setUp(self):
		self.specimen = Record(timestep = 1)
		self.specimen[0, 'run1'] = (0.5, 7)
		
	def testMean(self):
		self.assertTrue(self.specimen(0) == 7)
		
	def testZeroWeight(self):
		self.specimen[0, 'run2'] = (0, 1000)
		self.assertTrue(self.specimen(0) == 7)
		
	def testBetween(self):
		self.specimen[0, 'run2'] = (0.5, 13)
		self.assertTrue(self.specimen(0) > 7)
		self.assertTrue(self.specimen(0) < 13)
		
		


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
			
	
# Regression tests for internal functions		
		
class TestMarshalling(TestCase):
	
	def setUp(self):
		self.specimen = Record(timestep = 1)
		
	def testKey(self):
		self.assertEqual(self.specimen.demux_key(2), (2.0, ()))
		self.assertEqual(self.specimen.demux_key((2, 'run1', 3)), (2.0, ('run1', 3)))
		
	def testValue(self):
		self.assertEqual(self.specimen.demux_value(2), (1.0, 2))
		self.assertEqual(self.specimen.demux_value((0.5, 2)), (0.5, 2))
	


if __name__ == '__main__':
	run_tests()
