"""
Import external classes and procedures used throughout cdprl, under the project's standard names.
"""

from numpy import ndarray, array, zeros, zeros_like, ones, tensordot, identity as unit, logical_or, allclose, empty as empty_array, append, average, exp
from numpy.random import normal as normal_deviates
from math import fabs, sqrt, copysign

from operator import mul
from copy import copy
from itertools import product as cartesian_product
from unittest import TestCase, main as run_tests
