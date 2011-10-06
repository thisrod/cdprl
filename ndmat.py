# Matrices with multipart indices

from numpy import array, tensordot, zeros
from unittest import TestCase, main as run_tests
from adjacencies import *

class ndmat:
	def __init__(self, array_like):
		self.elements = array(array_like)
		
	def __eq__(self, other):
		return (self.elements == other.elements).all()
		
	def __add__(self, other):
		return ndmat(self.elements + other.elements)
			
	def __sub__(self, other):
		return ndmat(self.elements - other.elements)
		
	def __mul__(self, other):
		"""Shapes go as [i, j, ..., n, m, ...] * [n, m, ..., p, q, ...] = [i, j, ..., p, q, ...]"""
		
		n = len(self.elements.shape)
		return ndmat(tensordot(self.elements, other.elements, (range(n/2, n), range(n/2))))
		
		
# Tests

class TestIdentityTest(TestCase):
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
