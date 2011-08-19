The point of this is explained in [the paper](http://arxiv.org/abs/quant-ph/0404052).

Review requests
---------------

* There must be a better way to write Simulator.__init__
* Please suggest extra data to test

Coding conventions
------------------

<table>
<tr><th>Paper<th>Program
<tr><td><i>U</i><td><tt>repulsion
<tr><td><i>t</i><td><tt>hopping
<tr><td>μ<td><tt>chemical_potential
</table>


The n matrices for spin up and spin down are stored in a single array N.  The spin down elements go in N[0,:,:], spin up in N[1,:,:].  Thus the opposite spin is given by 1-spin.