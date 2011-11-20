# Matrices with multipart indices

from namespace import *
from adjacencies import *

class ndmat:
	def __init__(self, array_like):
		self.elements = array(array_like)
		
	def __array__(self):
		return self.elements
		
	def __eq__(self, other):
		return (self.elements == other.elements).all()

	def __mul__(self, other):
		"""Shapes go as [i, j, ..., n, m, ...] * [n, m, ..., p, q, ...] = [i, j, ..., p, q, ...]"""
		
		if isinstance(other, ndmat):
			n = len(self.elements.shape)
			return ndmat(tensordot(self.elements, other.elements, (range(n/2, n), range(n/2))))
		else:
			return self.elements * other
		
	# There follows a bunch of boilerplate to proxy for elements,
	# because Smalltalk 80 is still in the future of Python 2011.
	
	def __rmul__(self, other): 
		return other * self.elements
	
	def __add__(self, other):
		return ndmat(self.elements + other.elements)
			
	def __sub__(self, other):
		return ndmat(self.elements - other.elements)

	def __getitem__(self, indices):
		return self.elements[indices]

	def __setitem__(self, indices, value):
		self.elements[indices] = value
		
		
		
# Tests

class AccessTest(TestCase):
	def setUp(self):
		self.A = ndmat(zeros([2,3]))
		
	def testGet(self):
		self.assertEqual(self.A[1,1], 0)
		
	def testSet(self):
		self.A[1,1] = 7
		self.assertEqual(self.A[1,1], 7)
		
	def testTuple(self):
		i = (0,1)
		self.A[i] = 13
		self.assertEqual(self.A[i], 13)

class IdentityTest(TestCase):
	def setUp(self):
		A = zeros([2,3,2,3])
		for i in sites([2,3]):
			A[2*i] = 1
		self.I = ndmat(A)
		self.X = ndmat(array(range(2*3*2*3)).reshape([2,3,2,3]))
		
	def testMul(self):
		self.assertEqual(self.I*self.X, self.X)
		self.assertEqual(self.X*self.I, self.X)
	
if __name__ == '__main__':
	run_tests()
