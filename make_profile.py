import cProfile
from fermi_tests import *

moments = Record(timestep = 1)
noise = DiscreteNoise(timestep = 0.01)
system = figure_1_system()
integrator = SemiImplicitIntegrator(system, noise, timestep = 0.01)
cProfile.run('integrate_labels(integrator, system.initial(0.5), 3.1, moments, range(10))', 'profile.out')
