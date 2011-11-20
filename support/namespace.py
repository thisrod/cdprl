"""
Import external classes and procedures used throughout cdprl, under the project's standard names.
"""

from numpy import array, zeros, tensordot, identity as unit, logical_or, allclose
from numpy.random import randn as normal_deviates
from math import fabs, sqrt, copysign

from operator import mul
from itertools import product as cartesian_product
from unittest import TestCase, main as run_tests
