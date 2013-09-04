SHARPy
======

Simulation of High-Aspect-Ratio Planes in Python (SHARPy).

Nonlinear and dynamically linearized models of very flexible aircraft dynamics for design, analysis, and control law synthesis.

To run: clone this git repository onto your local machine at location [SharPyProjectDir].
Edit the file [SharPyProjectDir]/src/Main/SharPySettings so that SharPyProjectDir = [SharPyProjectDir]. Run some python unittests, which can be found in the test/ directory. Note: The BeamLib shared library, BeamLib.so, is compiled automatically by tests in the PyBeam package. However, the UVLMLib.so library must be compiled manually at present; to do this import the UVLMLib project in eclipse (with the C/C++ SDK installed) by navigating to 'File->Import->General->Existing Projects into Workspace' and set [SharPyProjectDir]/UVLMLib as the root directory. The boost and Eigen C++ libraries are required, and the project must be reconfigured to reflect the locations of these libraries and other differences on your system.
