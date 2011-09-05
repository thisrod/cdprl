## Tests of the prng

class TestNoise(TestCase):

	"noise(n, dt)*dt is a n*n matrix with Wiener increments on the diagonal, and zeros elsewhere." 

	def setUp(self):
		self.sites = 10
		
	def testShape(self):
		self.assertEqual(noise(self.sites, 1).shape, (self.sites,))
			
	def testDiagonal(self):
		self.assertTrue(is_diagonal(noise(self.sites, 1)))
	
	def testIndependentElements(self):
		samples = noise(self.sites, 1).diagonal()
		self.assertEqual(len(set(samples)), self.sites)
		
	def testOrderMagnitude(self):
		"The mean square noise probably has the same order of magnitude as the timestep.  (Try again if it doesn't)"
		for step in 1, 0.1, 1e-5:
			samples = noise(self.sites, step).diagonal()
			variance = (step*samples).var()
			self.assertTrue(step/3 < variance and variance < 3*step)

if __name__ == '__main__':
    run_tests()
