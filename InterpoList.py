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
		self.points = dict(self.points)
		
	def be_sorted(self):
		if type(self.points) is dict:
			self.points = self.points.items()
			self.points.sort()
		
	def ordinate(self, abscissa, i):
		"""return the ordinate at abscissa of the line through points i-1 and i.  this only makes sense if the sorted list representation is in use.  beware rounding near known points."""
		
		preabs, preord =  self.points[i-1]
		postabs, postord = self.points[i]
		return (preord*(postabs-abscissa) + postord*(abscissa-preabs)) / (postabs-preabs)
		
	def extrapolation(self, abscissa):
		""" Is abscissa outside the domain of my data? """
		self.be_sorted()
		return self.points[0][0] > abscissa or self.points[-1][0] < abscissa

	def __call__(self, x):
		""" Returns the value interpolated for a given abscissa """
		self.be_sorted()
		abscissa = float(x)
		if self.extrapolation(abscissa):
			raise IndexError("Extrapolation is not supported")
		sampling = [p[0] for p in self.points]
		i = bisect_left(sampling, abscissa)
		# this test is needed in case i == 0
		if sampling[i] == abscissa:
			return self.points[i][1]
		else:
			return self.ordinate(abscissa, i)
					
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
		lst = string.join([string.join( (str(i[0]), str(i[1]) ), ":") for i in self.points], ",")
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
		

if __name__ == '__main__':
	run_tests()
