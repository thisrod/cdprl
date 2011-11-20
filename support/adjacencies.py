# Generate pairs of adjacent points in a grid of arbitrary dimensions.
#
# resp, 2011-10-05

from namespace import *

def adjacencies(dimensions):
	"""Yield pairs of adjacent sites in the given grid"""
	for p in sites(dimensions):
		for i in range(len(dimensions)):
			x = list(p)
			x[i] = x[i] + 1
			if x[i] < dimensions[i]:
				yield p, tuple(x)
				yield tuple(x), p
			
def sites(dimensions):
	"""Yield indices of sites in a grid of size dimensions"""
	axes = [xrange(n) for n in dimensions]
	return cartesian_product(*axes)
	
	
### Tests	
	
class SitesTest(TestCase):
	def testOne(self):
		self.assertEqual([x for x in sites([1])], [(0,)])
		self.assertEqual([x for x in sites([3])], [(0,), (1,), (2,)])
		self.assertEqual([x for x in sites([1000])], [(n,) for n in range(1000)])
		
	def testTwo(self):
		self.assertEqual(set(sites([2,3])), set([(0, 1), (1, 2), (0, 0), (1, 1), (1, 0), (0, 2)]))

		
class AdjacenciesTest(TestCase):
	def testTwo(self):
		self.assertEqual(len(set(adjacencies([2,3]))), 14)
		self.assertTrue(((1, 1), (1, 2)) in adjacencies([2,3]))

if __name__ == '__main__':
	run_tests()
