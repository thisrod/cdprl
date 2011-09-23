# Tests of Python's subprocess module, to help me understand it.

from unittest import TestCase, main as run_tests
from subprocess import Popen, PIPE
from shlex import split

class EchoTest(TestCase):
	
	def setUp(self):
		self.command = ["echo", "foo", "bar", "blow"]
		
	def testPipe(self):
		child = Popen(self.command, stdout = PIPE)
		self.assertEqual(child.communicate(), ("foo bar blow\n", None))

		
class CatTest(TestCase):
	
	def setUp(self):
		self.command = "cat"
		
	def testBasic(self):
		child = Popen(self.command)
		
	def testPipe(self):
		child = Popen(self.command, stdin = PIPE, stdout = PIPE)
		self.assertEqual(child.communicate("foo bar blow"), ("foo bar blow", None))
		
	def testCD(self):
		child = Popen(self.command, cwd="/tmp")
		child = Popen(self.command, cwd="../cdprl")
		

		
class ScilabTest(TestCase):
	
	def setUp(self):
		self.command = split("scilab -nogui -nb -e")
		
	def testBasic(self):
		child = Popen(self.command + ["quit"])
		
	def testNumber(self):
		child = Popen(self.command + ["disp(1+1); quit"], stdout = PIPE)
		self.assertEqual(float(child.communicate()[0]), 2)
		
	def testArray(self):
		child = Popen(self.command + ["disp([1,2]); quit"], stdout = PIPE)
		output = child.communicate()[0]
		self.assertEqual([float(s) for s in split(output)], [1, 2])
		
	def testFunction(self):
		script = "function y=f(x),y = x**2,endfunction; disp(f(3)); quit"
		child = Popen(self.command + [script], stdout = PIPE)
		self.assertEqual(float(child.communicate()[0]), 9)
	
		
class MatlabTest(TestCase):
	
	def setUp(self):
		self.command = split("matlab -maci -nojvm -nosplash -r")
		
	def testAmountBullshit(self):
		child = Popen(self.command + ["quit"], stdout = PIPE)
		self.assertEqual(len(child.communicate()[0]), 334)
		
	def testNumber(self):
		child = Popen(self.command + ["disp(1+1); quit"], stdout = PIPE)
		output = child.communicate()[0][334:]
		self.assertEqual(float(output), 2)
		
	def testArray(self):
		child = Popen(self.command + ["disp([1,2]); quit"], stdout = PIPE)
		output = child.communicate()[0][334:]
		self.assertEqual([float(s) for s in split(output)], [1, 2])
		
	

if __name__ == '__main__':
	run_tests()
