from unittest import TestCase, main as run_tests
from numpy import array
from weightings import *


class AccessTest(TestCase):

	def setUp(self):
		self.one = Weighting(7.0, 0.5)
		self.many = Weighting(array([1, 2, 3]), weight = 0.7)
	
	def testValues(self):
		self.assertEqual(self.one.mean, 7.0)
		self.assertEqual(self.many.mean, array([1, 2, 3]))
		
	def testWeights(self):
		self.assertEqual(self.one.weight, 0.5)
		self.assertEqual(self.many.weight, 0.7)
		

class ArithmeticTest(TestCase):

	def setUp(self):
		self.first = Weighting(0.3, 0.7)
		self.other = Weighting(3, 7)
		
	def testPlus(self):
		"""Addition is elemental"""
		self.assertEqual(self.first + self.other, Weighting(3.3, 7.7))
		
	def testTimes(self):
		"""Scalar multiplication"""
		self.assertEqual(7*self.first, self.first*7)
		self.assertEqual(7*self.first, Weighting(2.7, 4.9))
		
	def testDivide(self):
		"""Scalar division"""
		self.assertEqual(self.first/2, Weighting(0.15, 0.35))
		
		
class AverageTest(TestCase):
	
	def setUp(self):
		self.this = Weighting(0.4, 0.7)
		self.that = Weighting(0.4, 2.5)
		self.other = Weighting(0.1, 1.4)
		
	
	def testSame(self):
		self.assertEqual(self.this.combine(self.that).value, 0.4)
		self.assertEqual(self.this.combine(self.that).weight, 0.7+2.5)
		
	def testDifferent(self):
		self.assertEqual(self.this.combine(self.other).value, 0.2)
		self.assertEqual(self.this.combine(self.that).weight, 0.7+1.4)
		

if __name__ == '__main__':
	run_tests()
