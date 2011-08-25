.TL
Design notes for Monte-Carlo simulation objects
.AU
Rodney E. S. Polkinghorne
.AI
Swinburne University of Technology

.PP
This code integrates stochastic differential equations.  It is split into three classes.

.PP
The 
.CW Simulation
class encapsulates the physics.  It has three main responsibilities.  Firstly, to remember the physical parameters of the system being simulated.  Secondly, the 
.CW deriviative
method computes the time derivative of a state, given noise derivatives.  (The state can be of arbitrary type—an array, tuple, or its own class.)  Finally, the 
.CW moments
method reduces a state to the results that need to be recorded.

.PP
Note that 
.CW Simulation
is given the stochastic derivatives from elsewhere.  There are two subtleties to this.  Firstly, the method 
.CW noise_required
tells elsewhere how many independent processes are required to compute the derivative of a given state.  Secondly, the derivatives given to 
.CW Simulation
are scaled by the timestep, but not by physical parameters.

.PP
The 
.CW Integrator
class is pretty straightforward.  It asks
.CW Simulator
for an initial state, adds up the derivatives returned from 
.CW Simulator.derivative ,
and passes the results to its
.CW Recorder
at the right intervals.

.PP
Finally, the 
.CW Recorder
class tells the 
.CW Integrator
when to record moments, receives the moments, and averages them over trajectories.  The moments will usually come in pairs, one either side of the requested time.  The 
.CW Recorder
is responsible for interpolating between them.

.PP
The interface to 
.CW Recorder
is a hybrid of function and dictionary.  Getting and setting items stores and retrieves data.  Calling the 
.CW Recorder
with a time, and possibly a series of
.CW run_labels ,
interpolates a value of the moments for each run at that time, and returns an average over any labels that haven't been specified.  The moments need to be 
.CW ndarray s,
not
.CW list s
or
.CW tuple s,
so that the averaging operations can access elemental addition and division.

