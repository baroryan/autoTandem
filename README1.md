# BP3 Input File and Mesh Generator

This package is designed to generate input files and meshes for the BP3 (thrust/normal planar fault) scenario based on user-provided parameters such as slip rate, dip angle, rate-and-state friction parameters, and more. After generating the mesh, the package runs Tandem and plots the slip and velocity results.

### Features

- **High-Resolution Mesh Generation**: The mesh is generated with high resolution along the velocity-weakening part of the fault. The mesh size decreases linearly as a function of distance from this section of the fault and the deformation front.
- **Customizable Input Parameters**: Easily configure simulation parameters, including fault geometry, slip rates, and material properties.

### Usage

Run the package by calling `callMeToRunTandem.py` with the following arguments:

```bash
python callMeToRunTandem.py --argument_name value


Arguments
--dipAngle DIPANGLE
Enter a dip angle value between 0 and 90 degrees [deg].

--slipRate SLIPRATE
Enter a slip rate between -200 and 200 cm/year.

--H0 H0
a-b rate and state shallowest depth range [km].

--H1 H1
a-b rate and state middle depth range [km].

--H2 H2
a-b rate and state deepest depth range [km].

--endTime ENDTIME
Simulation runtime [years].

--path PATH
Path where the package will run.

--depthVarying DEPTHVARYING
Specify if Lame parameters change with depth [true/false].

--Ls LS
Minimum mesh size along the surface [km] - larger values result in a coarser mesh.

--Lf LF
Minimum mesh size along the fault [km] - larger values result in a coarser mesh.

--Dc Dc
Uniform Dc along the fault [m].

--normalStress NORMALSTRESS
Uniform normal stress along the domain [MPa].

--rigidity RIGIDITY
Uniform rigidity along the domain [GPa].

--dr DR
Distance between fault probe stations [km].

--tandembin TANDEMBIN
Tandem binary path - default is tandem.

--gmshbin GMSHBIN
Gmsh binary path - default is gmsh.

Dependencies
Ensure the following are installed before running the package:

Tandem and Gmsh binaries
Python environment with the following packages:
xarray
numpy
pint
matplotlib
pandas
