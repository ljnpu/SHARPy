SHARPy
======

Simulation of High-Aspect-Ratio Planes in Python (SHARPy).

Nonlinear and dynamically linearized models of very flexible aircraft dynamics
for design, analysis, and control law synthesis.

Install
-------

Clone this git repository onto your local machine at location
[SharPyProjectDir].
Edit the file [SharPyProjectDir]/src/Main/SharPySettings.py so that

	SharPyProjectDir = [SharPyProjectDir]

Note: The BeamLib shared library, BeamLib.so, is compiled automatically by
unit tests in the PyBeam package.
However, the UVLMLib.so library must be compiled manually at present;
to do this import the UVLMLib project in eclipse (with the C/C++ SDK installed)
by navigating to 'File->Import->General->Existing Projects into Workspace',
and set [SharPyProjectDir]/UVLMLib as the root
directory.
Then build a Debug configuration of the project.

### Dependencies ###

* Python 3.2
* numpy (1.7.x+)
* scipy
* slycot (routines for preditive controller design)
* muAO-MPC (MPC controller design and C-code generation)
* Eigen (C++ libraries)
* Boost (C++ libraries)
* LAPACK (Fortran libraries)
* BLAS (Fortran libraries)

The fortran and C/C++ projects must be reconfigured to reflect the locations
of these libraries on your system.

Run
---

The first thing you should do is run some python unittests
which can be found in the test/ directory of PyAero, PyBeam and PyCoupled
solver scripts.


License
-------

SHARPy is distributed as open source software under a BSD license. Please check the license.txt file for details.


Acknowledgments
---------------

The development of SHARPy at Imperial College London has been supported by the Engineering and Physical Sciences Research Council [grant number EP/I014683/1].
