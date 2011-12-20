from namespace import *
from dynamics import record


class TestTimes(TestCase):
	
	def setUp(self):
		self.it = record(3.1, [])
		
	def testTypes(self):
		"Times are floats."
		for method in "nearest", "next", "after":
			self.assertTrue(returns_float(self.it, method))


def returns_float(object, method):
	return isinstance(getattr(object, method)(5), float)

if __name__ == '__main__':
    run_tests()
