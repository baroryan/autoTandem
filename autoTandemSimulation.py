#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 15:35:32 2024

@author: bar
"""




import generateTomlFile 
import numpy as np
import shutil
import subprocess
import glob
import readtandemoutput
import xarray as xr
import matplotlib.pyplot as plt
import os
#%%

class bp3:
    def __init__(self,dipAngle=10,slipRate=1e-9,H0=2,H1=8,H2=8,depthVarying=False,endTime=1500*3600*24*365,dr=2,path=".",Lf=0.6,Ls=0.6,gf_dir=None):
        """ get dipAngle in deg
    slip rate in m/s
    H0,H,h in km 
    endTime in second """
    
        self.dipAngle=dipAngle
        self.slipRate=slipRate
        self.H0=H0
        self.H1=H1
        self.H2=H2
        self.depthVarying=depthVarying
        self.endTime=endTime
        self.dr=1
        self.path=path
        self.Lf=Lf
        self.Ls=Ls
        self.gf_dir=gf_dir
        self.homeDir = os.path.dirname(__file__)
        
        
    def RunOSCommand(self,command,logfile):

        with open(logfile, 'w') as f:
            # Start the process in the specified directory
            process = subprocess.Popen(command, stdout=f, stderr=subprocess.STDOUT, text=True, cwd=self.path)
            # Wait for the process to complete
            return_code = process.wait()
            
        return return_code
        
    def ComputeMesh(self,gmshBin,logfile='/meshGeneration.log'):
        logfile=self.path+"/outputs/"+logfile
        command = [gmshBin,'-2','bp3.geo','-setnumber', 'dip', str(self.dipAngle),'-setnumber', 'Lf', str(self.Lf),'-setnumber', 'Ls', str(self.Ls)]
        return_code=self.RunOSCommand(command,logfile)
            
        if return_code == 0:
            print("Mesh generated successfully.")
            
        else:
            print(f"Generating Mesh failed with return code: {return_code}. Check mesh log file")
            raise ValueError("byebye")
        
    def PlotSlipMaxVel(self):
        
        ds=readtandemoutput.ReturnDataSets(self.path)
        ds = xr.concat(ds, dim=('z'))
        ds['years'] = ds['Time']/(3600*24*365.25)
        
        coseismic={'color':'blue','alpha':0.5,'linewidth':0.5}
        interseismic={'color':'red','alpha':0.5,'linewidth':0.5}
        
        fig,ax=plt.subplots(2,1)
        readtandemoutput.PlotSlipFrequnelty(ds['slip0'].values, ds['Time'].values, 5, np.abs(ds['z'].values),plotAttributes=coseismic,ax=ax[0],coseismic=True)
        readtandemoutput.PlotSlipFrequnelty(ds['slip0'].values, ds['Time'].values, 3600*24*365*5, np.abs(ds['z'].values),plotAttributes=interseismic,ax=ax[0],coseismic=False)
        highest_velocity = ds['slip-rate0'].max(['z']).values
        ax[1].plot(ds['years'],np.log10(highest_velocity))
                   
        fig.savefig(self.path+"slipMaxVel.pdf",dpi=300)
        
        
        
    def RunEQSimulation(self,tandemBinaryPath,logfile='/tandemSimulation.log'):
        logfile=self.path+"/outputs/"+logfile
        command = [tandemBinaryPath, 'bp3.toml','--mode', 'QDGreen','--gf_checkpoint_prefix', 'gf/', '--petsc', '-ts_monitor', '-options_file', 'rk45.cfg', '-options_file', 'lu_mumps.cf']
        
        if self.gf_dir is None:
            command=command[:2] + command[6:]
            
        return_code=self.RunOSCommand(command,logfile)
            
        if return_code == 0:
            print("Earth simulations finished successfully.")
            
        else:
            print(f"EQ simulations failed with return code: {return_code}. Check mesh log file")
            raise ValueError("byebye")
        
        
    def WriteFiles(self):
        
        shutil.copy(self.homeDir+"/filesToCopy/bp3.lua",self.path+"/bp3.lua")
        shutil.copy(self.homeDir+"/filesToCopy/bp3.geo",self.path+"/bp3.geo")
        shutil.copy(self.homeDir+"/filesToCopy/lu_mumps.cfg",self.path+"/lu_mumps.cfg")
        shutil.copy(self.homeDir+"/filesToCopy/rk45.cfg",self.path+"/rk45.cfg")
        luaFotter="\n -- adding user choice \n" + self.LuaFooter()
        toml=self.TomlHeader()+self.TomlBody()+self.TomlFotter()

        
        with open(self.path+'/bp3.toml', 'w') as file:
            file.writelines(toml)
            
        with open(self.path+'/bp3.lua', 'a') as file:
            file.writelines(luaFotter)

        
    def TomlHeader(self):
        return f"final_time = {self.endTime}"
    
    def TomlFotter(self):
        Rmax=(1.2*(self.H0+self.H1+self.H2))/np.sin(np.deg2rad(self.dipAngle))
        #print(Rmax)
        string=generateTomlFile.ComputePointsForPlanarFaultBasedOnDistanceAlongFault(self.dipAngle,dy=self.dr,ymin=0,ymax=Rmax)
        
        return string
    def LuaFooter(self):
        if self.depthVarying is False:
            depthVarying='false'
        else:
            depthVarying='true'
            
        output_line = f"bp3_custom = BP3.new{{dip={self.dipAngle}, Vp={self.slipRate}, inelastic=false, ratioWidthX=2, widthY=5, amp=0.1, depthVarying={depthVarying}, H0={self.H0}, H={self.H1}, h={self.H2}}}"

        return output_line
    
    def TomlBody(self):
        string="""
mesh_file = "bp3.msh"
lib = "bp3.lua"
scenario = "bp3_custom"
mode = "QD"
type = "elasticity"
ref_normal = [1, 0]
boundary_linear = true

[fault_probe_output]
prefix = "outputs/fltst_"
t_max = 9460800 
"""

        return string
 
    






