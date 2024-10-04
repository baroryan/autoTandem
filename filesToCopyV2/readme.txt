Hey!

Thank you for using Tandem.

This gateway app automatically generates the input and mesh files needed to run a simple planar fault simulation
 along a dip angle chosen by the user, loosely based on the bp3-QD SEAS benchmark (Erickson et al., 2023).

The app first computes the mesh using Gmsh, leveraging the bp3.geo script to generate the
mesh file (bp3.msh) based on user input. You can find the command it used to generate the
mesh in outputs/meshGeneration.log.
Next, it calculates the physical properties for the domain based on your input. If you are familiar
with Lua (a simple scripting language), the app sets the parameters based on the functions and
properties defined in the bp3.lua file, specifically using the bp3_custom class and its functions.
Finally, the app configures bp3.toml according to your input, particularly setting the runtime
and fault probe positions (locations where Tandem records outputs along the fault). You will find the
data for these fault probes under outputs/fltst_*.

Once the app completes these tasks, it runs Tandem (Uphoff et al., 2023) using the command found in
outputs/tandemSimulation.log, and then plots the slip rate along the fault over time (outputs/slipVelFigure.pdf).

The Python code that orchestrates all of buliding this setup automatically based on user input can be
found on GitHub at:
https://github.com/baroryan/autoTandem.

If you are interested in running more complex scenarios, feel free to use the Tandem 2D/Tandem 3D apps,
which require you to upload a mesh file, TOML file, and Lua scripts.

For more documentation about Tandem, you can visit the GitHub page at:
https://github.com/TEAR-ERC/tandem
or the Tandem documentation at:
https://tandem.readthedocs.io/.

If you'd like to run Tandem on your laptop without compiling all the dependencies, you can use the
 UTM virtual machine for Mac M1/M2/M3 available here:
https://zenodo.org/records/12365886.

Good luck, and let us know if you need more help through our GitHub page.
