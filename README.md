This simple package creates the input file and mesh for BP3 (thrust/normal planar fault) based on user input such as slip rate, dip angle, a-b parameters, and others. It eventually runs Tandem and plots slip and velocity results.
The mesh will be generated with high resolution along the velocity weakening part of the fault, with mesh size decreasing linearly as a function of distance from this section of the fault and the deformation front.



The package is run by calling callMeToRunTandem.py and accepts several arguments using the format --argument_name value :

    --dipAngle DIPANGLE   Enter a dip angle value between 0 and 90 [deg]

    --slipRate SLIPRATE   Enter slip rate between -200 and 200 [cm/yr]

    --H0 H0               a,b rate and state shallowest depth range [km]

    --H1 H1               a,b rate and state middle depth range [km]

    --H2 H2               a,b rate and state deepest depth range [km]

     --endTime ENDTIME     simulation ran time [years]

    --path PATH           path where package will run

    --depthVarying DEPTHVARYING Check true or false if lame parameters change with depth [true/false]

    --Ls LS               Min mesh size along surface[km] - larger value coarser mesh

    --Lf LF               Min mesh size along fault[km] - larger value coarser mesh

    --Dc Dc               Uniform Dc along the fault [m]

    --normalStress        Uniform normalStress along the domain [MPa]

    --rigidity            Uniform rigidity along the domain [GPa]

    --dr DR               distance between fault probe stations [km]

    --tandembin TANDEMBIN tandem binary path - default is tandem

    --gmshbin GMSHBIN     gmsh binary path - default is gmsh



  The package assumes that tandem and gmsh are already installed, and it needs a Python environment with xarray,numpy,pint, matplotlib, and pandas installed.
