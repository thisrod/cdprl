# Functions to generate Wiener processes and their derivatives

# Issue: the current RNG has a cycle length of 2^32.  This might be improved by indirection, but it isn't clear how to do so.  Block TEA might be the simplest solution.

# TEA cypher, from < http://stackoverflow.com/questions/2588364/python-tea-implementation >

from ctypes import *
from scipy.special import erfinv
from InterpoList import InterpoList as Interpolation
from math import floor, ceil as ceiling, sqrt, log
from itertools import islice

## For now, we simulate a Brownian Bridge process from time 0 to 1.  A Wiener process can be recovered by adding a random slope.

## Return the sequence of interpolations, that contribute to the process at time t.

def W(n, t):
	return sum([f(t) for f in take(n, triangle_sequence(t, 0))])
	
cached_seed = None
triangle_cache = {}

def triangle_sequence(t, seed):
	# cache the interpolations for the next call, to optimise the common case of sequential values
	global triangle_cache
	if seed == cached_seed:
		old_cache, triangle_cache = triangle_cache, {}
	else:
		old_cache, triangle_cache = {}, {}
	n = 0
	while True:
		sequence = int(2**n*(1+t))	# index of random number for this interval
		if sequence in old_cache:
			triangle_cache[sequence] = old_cache[sequence]
		else:
			start = int(2**n*t)/2.0**n
			end = int(2**n*t+1)/2.0**n
			if (t == 1): start, end = 1-2**(-n),  1
			mid = 0.5*(start+end)
			triangle_cache[sequence] = \
				Interpolation(data = {start: 0, end: 0, mid: 0.5*normal_deviate([seed, sequence])/sqrt(2**n)})
		yield triangle_cache[sequence]
		n = n+1

def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))
    
def interval(max, samples):
 	return [float(max * i)/samples for i in range(samples+1)]

## A random access RNG, from gputea.pdf

# v is a list of two numbers
def normal_deviate(v):
    return erfinv(2*uniform_deviate(v)-1)
    
def uniform_deviate(v):
    x=encipher(v, key)
    return (2**32*x[0]+x[1])/float(2**64)

key = [0xA341316C, 0xC8013EA4, 0xAD90777D, 0x7E95761E]

def encipher(v, k):
    y=c_uint32(v[0]);
    z=c_uint32(v[1]);
    sum=c_uint32(0);
    delta=0x9E3779B9;
    n=8
    w=[0,0]

    while(n>0):
        sum.value += delta
        y.value += ( z.value << 4 ) + k[0] ^ z.value + sum.value ^ ( z.value >> 5 ) + k[1]
        z.value += ( y.value << 4 ) + k[2] ^ y.value + sum.value ^ ( y.value >> 5 ) + k[3]
        n -= 1

    w[0]=y.value
    w[1]=z.value
    return w
    

backbone = Interpolation(data = {0:0, 1:normal_deviate([-1,0])})
backbone_extent = 0

def extend_backbone(t):
	global backbone, backbone_extent
	# Python bogosity - "lexical scope", "free variable" and "closure" are big, scary words
	while (2**backbone_extent < t):
		backbone[2**(backbone_extent + 1)] \
			= backbone[2**backbone_extent] \
				+ normal_deviate([-1, backbone_extent + 1]) * sqrt(2**backbone_extent)
		backbone_extent += 1
	
def bridge(n, t):
	if (t == 0):
		seed = 0
	else:
		seed = int(max(0, ceiling(log(t)/log(2))))
	if (t < 1):
		scaled_t = t
	else: 
		scaled_t = (t - 2**(seed-1)) / 2**(seed-1)
	return sum([f(scaled_t) for f in take(n, triangle_sequence(scaled_t, seed))])

def wiener(n, t):
	extend_backbone(t)
	return backbone(t) + bridge(n,t)