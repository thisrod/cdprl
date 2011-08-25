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
from unittest import TestCase, main as run_tests

class InterpoList(object):
    """
        A list type which automatically does linear interpolation.
        For example:
            >>> a = InterpoList()
            >>> a[0]   = 0
            >>> a[100] = 200
            >>> a[200] = 0
            >>> a[50]
            100.0
            >>> a[125]
            150.0
    """
    def __init__(self, data = {}):
        """ constructor """
        self.items = data.items()
        self.items.sort()
        
    def ordinate(self, findex, i):
        """ Return the ordinate at findex of the line through self[i-1] and self[i] """
        preindex, prevalue =  self.items[i-1]
        postindex, postvalue = self.items[i]
        return (prevalue*(postindex-findex) + postvalue*(findex-preindex)) / (postindex-preindex)
        
    def extrapolation(self, findex):
    	""" Is findex outside the domain of my data? """
    	return self.items[0][0] > findex or self.items[-1][0] < findex

    def __call__(self, index):
        """ Returns the value interpolated for a given index """
        # create a dummy item for searching
        findex = float(index)
        if self.extrapolation(findex):
            raise IndexError("Extrapolation is not supported")
        item   = (findex, 0)
        # find the position where it would be inserted
        i = bisect(self.items, item)

        if self.items[i-1].index == findex:
            # exact
            assert False	# this can't happen: index is a method
            return self.items[i-1].value
        else:
            return self.ordinate(findex, i)
                    
    def __getitem__(self, key):
    	""" Finds the value at a data point """
    	return self.items[key]

    def __setitem__(self, key, value):
        """ adds a new keypoint or replaces a current one """
        # create a new list item
        fkey = float(key)
        item = (fkey, value)
        # find the insertion point
        i = bisect_left(self.items, item)
        
        # replace existing value?
        if i < len(self.items) and self.items[i].index == fkey:
            self.items[i] = item
        else:
            # insert it
            self.items.insert(i, item)


    def __delitem__(self, key):
        """ Deletes a given keypoint """
        fkey = float(key)
        item = (fkey, 0)
        i = bisect_left(self.items, item)

        # convert IndexError to KeyError
        try:
            if self.items[i][0] == fkey:
                del self.items[i]
            else:
                raise KeyError("Key not found")
        except IndexError:
            raise KeyError("Key not found")

    def __len__(self):
        """ Returns the range of the indices """
        if len(self.items) > 0:
            return fabs(self.items[-1].index - self.items[0].index)
        else:
            return 0.0

    def __repr__(self):
        """ Formal description of the object """
        # Dump the contents into a dict style string
        lst = string.join([string.join( (str(i[0]), str(i[1]) ), ":") for i in self.items], ",")
        # spit the whole thing out
        return "%s(data={%s})" % (type(self).__name__, lst)

    def __iter__(self):
        """ Returns an iterator which can traverse the list """
        return self.items.__iter__()
        
        
# Simple regression test

class TestRegression(TestCase):
	
	def setUp(self):
		self.mapping = InterpoList(data = {-1:-1, 0:0, 1:7})
		
	def testRegression(self):
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
		

if __name__ == '__main__':
    run_tests()
