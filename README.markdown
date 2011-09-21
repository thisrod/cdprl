The point of this is explained in [the paper](http://arxiv.org/abs/quant-ph/0404052).

Review requests
---------------

* There must be a better way to write Simulator.__init__
* Please suggest extra Greens functions to test
* TestDelta and TestDerivative aren't nearly thorough enough
* Please confirm the assumption 〈H〉 = -t∑<sub>〈ij〉σ</sub> n<sub>ijσ</sub> + U∑<sub>j</sub> n<sub>jj↑</sub> n<sub>jj↓</sub> - μ ∑<sub>jσ</sub>n<sub>jjσ</sub>

Issues
------

Where should the noise be scaled by repulsion?

Coding conventions
------------------

<table>
<tr><th>Paper<th>Program
<tr><td><i>U</i><td><tt>repulsion
<tr><td><i>t</i><td><tt>hopping
<tr><td>μ<td><tt>chemical_potential
<tr><td><i>n</i><td><tt>normal_greens
</table>


The n matrices for spin up and spin down are stored in a single array N.  The spin down elements go in N[0,:,:], spin up in N[1,:,:].  Thus the opposite spin is given by 1-spin.

Design notes
-----

Integration is carried out by four classes.  Three of them, <tt>Integrator</tt>, <tt>Noise</tt>, and <tt>Moments</tt>, do the integration.  A forth class represents the system of interest, and is different for every integration.  Let's call it <tt>Physics</tt>.

<tt>Integrator</tt> is a method object, that integrates the SDEs.  It
* stores numerical parameters, most notably the timestep,
* adds up the increments of the system state at each timestep,
* passes moments to the <tt>Record</tt> at the times it requests.
Subclasses implement particular algorithms, by the method <tt>increment</tt> which
* computes the increment of the state over a specified timestep.

<tt>Record</tt> averages moments over trajectories.  It
* tells what times to record moments
* records the moments of a labelled trajectory at a given time
* interpolates moments at times between those recorded
* computes a weighted average of moments over the recorded trajectories

<tt>Noise</tt> generates Wiener processes.  It
* generates an independent process for every trajectory label and integer index
* computes the value of each process at a given time
* computes the derivative of each process over any timestep

<tt>Physics</tt> is the object that knows what's going on.  It
* remembers physical parameters
* constructs initial states
* tells which noise processes are required to compute the derivative of a state
* computes the derivative of a state, given the noise
* computes the moments to be recorded for a state.

Currently, <tt>Integrator</tt> associates <tt>Physics</tt> and <tt>Noise</tt>, and passes arrays of numbers between them.  Things would be simpler if this association was direct, and <tt>Integrator</tt> was ignorant of <tt>Noise</tt>.  This would require the <tt>derivative</tt> method to take labels.