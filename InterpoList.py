"""
	InterpoList module (c) Gaz Davidson December 2009.
	Modified by Rodney Polkinghorne, 2011

	This is a simple interpolated list type useful for graphing, you
	can set values at any index and it will linearly interpolate between
	the missing ones.

	License:
	   Use for any purpose under one condition: I am not to blame for anything.
"""

from bisect import bisect, bisect_left
from math import fabs
import string
from collections import MutableMapping, Callable
from unittest import TestCase, main as run_tests

class InterpoList(MutableMapping, Callable):
	"""
		A list type which automatically does linear interpolation.
		
	"""
	def __init__(self, data = {}):
		""" constructor """
		self.points = {}
		for x in data:
			self[x] = data[x]
			
	# self.points stores the known points.  subscript operations convert it to a dict, and interpolation to a sorted list of (abscissa, ordinate) pairs.
		
	def be_table(self):
		self.sampling = None
		
	def be_sorted(self):
		self.sampling = self.points.keys()
		self.sampling.sort()
		
	def series(self, i):
		"""return the ith sample point."""
		return (self.sampling[i], self.points[self.sampling[i]])
		
	def points_around(self, x):
		"""if x was sampled, return it.  otherwise, return the sampled abscissae either side x."""
		self.be_sorted()
		abscissa = float(x)
		if self.extrapolation(abscissa):
			raise IndexError("Extrapolation is not supported")
		i = bisect_left(self.sampling, abscissa)
		if self.sampling[i] == abscissa:
			return [self.series(i)]
		else:
			return [self.series(i-1), self.series(i)]
		
	
	def ordinate(self, abscissa, neighbours):
		"""return the ordinate at abscissa of the line through neighbours.  beware rounding near known points."""
		
		(preabs, preord), (postabs, postord) =  neighbours
		return (preord*(postabs-abscissa) + postord*(abscissa-preabs)) / (postabs-preabs)
		
	def extrapolation(self, abscissa):
		""" Is abscissa outside the domain of my data? """
		self.be_sorted()
		return self.sampling[0] > abscissa or self.sampling[-1] < abscissa

	def __call__(self, x):
		""" Returns the value interpolated for a given abscissa """
		neighbours = self.points_around(x)
		if len(neighbours) is 1:
			return neighbours[0][1]
		else:
			return self.ordinate(x, neighbours)
			
	def derivative(self, x):
		""" Returns the derivative of the interpolated function at a given abscissa.  doesn't try hard at sampled points"""
		neighbours = self.points_around(x)
		if len(neighbours) is 1:
			return 0
		else:
			(preabs, preord), (postabs, postord) =  neighbours
			return (postord - preord) / (postabs - preabs)
		
					
	def __setitem__(self, key, value):
		""" adds a new keypoint or replaces a current one """
		self.be_table()
		self.points[float(key)] = float(value)
			
	def __getitem__(self, key):
		""" Answers the value stored for key, if there is one """
		self.be_table()
		return self.points[float(key)]

	def __delitem__(self, key):
		""" Deletes a given keypoint """
		self.be_table()
		del self.points[float(key)]

	def __len__(self):
		""" Returns the range of the indices """
		if len(self.points) > 0:
			return fabs(self.points[-1].index - self.points[0].index)
		else:
			return 0.0

	def __repr__(self):
		""" Formal description of the object """
		# Dump the contents into a dict style string
		self.be_sorted()
		lst = string.join([string.join( (str(x), str(self.points[x]) ), ":") for x in self.sampling], ",")
		# spit the whole thing out
		return "%s(data={%s})" % (type(self).__name__, lst)

	def __iter__(self):
		""" Returns an iterator which can traverse the list """
		return self.points.__iter__()
		
		
# Simple regression tests

class TestAccessing(TestCase):

	def setUp(self):
		self.empty = InterpoList()
		self.mapping = InterpoList(data = {0: 7})
		self.triangle = InterpoList(data = {-1.3: 10, 0: 0, 1:5.2})
		
	def testAdding(self):
		self.empty[0] = 3
		self.assertTrue(0 in self.empty)
		self.assertTrue(self.empty[0] == 3)
		
	def testInitialization(self):
		self.assertTrue(0 in self.mapping)
		self.assertTrue(self.mapping[0] == 7)
		
	def testDeletion(self):
		del self.mapping[0]
		self.assertFalse(0 in self.mapping)
		
	def testNegativeKey(self):
		self.mapping[-1] = 0
		self.assertEqual(self.mapping[-1], 0)
		self.assertEqual(self.mapping(-1), 0)
		self.assertEqual(self.mapping(-0.5), 3.5)
		
	def testNegativeValue(self):
		self.mapping[1] = -7
		self.assertEqual(self.mapping[1], -7)
		self.assertEqual(self.mapping(1), -7)
		self.assertEqual(self.mapping(0.5), 0)
		
	def testLogic(self):
		self.assertEqual(self.triangle.points_around(-1.3), [(-1.3, 10)])
		self.assertEqual(self.triangle.points_around(-1), [(-1.3, 10), (0, 0)])
		self.assertEqual(self.triangle.points_around(0.5), [(0, 0), (1, 5.2)])
		self.assertEqual(self.triangle.points_around(1), [(1, 5.2)])
		


class TestPrinting(TestCase):

	def testEmpty(self):
		self.assertEqual(''.join([c for c in `InterpoList()` if not c.isspace()]), 'InterpoList(data={})')
		
	def testOne(self):
		self.assertEqual(''.join([c for c in `InterpoList(data={0:7})` if not c.isspace()]), 'InterpoList(data={0.0:7.0})')

		
class TestSingleton(TestCase):

	def setUp(self):
		self.specimen = InterpoList(data = {0:7})
		
	def testInterpolate(self):
		self.assertEqual(self.specimen(0), 7)
		

class TestNumerics(TestCase):
	
	def setUp(self):
		self.mapping = InterpoList(data = {-1:-1, 0:0, 1:7})
		
	def testNearPoint(self):
		""" Interpolated values near zero are correct to 1% """
		epsilon = 1e-30
		plus = self.mapping(epsilon)/epsilon
		zero = self.mapping(0)
		minus = -self.mapping(-epsilon)/epsilon
		self.assertTrue(0.99 < minus/1)
		self.assertTrue(minus/1 < 1.01)
		self.assertTrue(-epsilon < zero)
		self.assertTrue(zero < epsilon)
		self.assertTrue(0.99 < plus/7)
		self.assertTrue(plus/7 < 1.01)
		

class TestReversion(TestCase):
	
	def setUp(self):
		self.mapping = InterpoList(data = {-1:-1, 0:7, 1:1})
		
	def testRevert(self):
		""" Interpolated values revert when a point is deleted """
		del self.mapping[0]
		self.assertTrue(-1e-10 < self.mapping(0))
		self.assertTrue(self.mapping(0) < 1e-10)
		
		
class TestDerivative(TestCase):
	def setUp(self):
		self.mapping = InterpoList(data = {-1:0, 0:7, 1:0})
		
	def testValues(self):
		self.assertEqual(self.mapping.derivative(-0.5), 7)
		self.assertEqual(self.mapping.derivative(0.5), -7)
		

if __name__ == '__main__':
	run_tests()
