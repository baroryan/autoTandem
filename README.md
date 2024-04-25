This simple package creates the input file and mesh for BP3 (thrust/normal planar fault) based on user input such as slip rate, dip angle, a-b parameters, and others. It eventually runs Tandem and plots slip and velocity results.




The package is run by calling callMeToRunTandem.py and accepts several arguments using the format --argument_name value and

  --dipAngle DIPANGLE   Enter a dip angle value between 0 and 90 [deg]
  --slipRate SLIPRATE   Enter slip rate between -200 and 200 [cm/yr]
  --H0 H0               a,b rate and state shallowest depth range [km]
  --H1 H1               a,b rate and state middle depth range [km]
  --H2 H2               a,b rate and state deepest depth range [km]
 --endTime ENDTIME     simulation ran time [years]
  --path PATH           path where package will run
  --depthVarying DEPTHVARYING
                        Check true or false if lame parameters change with depth [true/false]
  --Ls LS               Min mesh size along surface[km] - larger value coarser mesh
  --Lf LF               Min mesh size along fault[km] - larger value coarser mesh
  --gf_dir GF_DIR       Set a green function dir - if not set, will not use gf
  --dr DR               plot every dr along the fault [km]
  --tandembin TANDEMBIN
                        tandem binary path - default is tandem
  --gmshbin GMSHBIN     gmsh binary path - default is gmsh


  The package assumes that tandem and gmsh are already installed, and it needs a Python environment with xarray,numpy,pint, matplotlib, and pandas installed
