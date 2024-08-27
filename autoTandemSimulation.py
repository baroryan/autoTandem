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
    def __init__(self,dipAngle=10,slipRate=1e-9,H0=2,H1=8,H2=8,depthVarying=False,endTime=1500*3600*24*365.25,dr=2,path=".",Lf=0.6,Ls=0.6,gf_dir=None,**kwargs):
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
        self.LoadFilesToCopy()
        
    def LoadFilesToCopy(self):
        self.filesToCopy="/filesToCopy/"
        
    def WriteCommandStringToFile(self,command,filename):
        with open(filename, 'w') as file:
            file.write("Command using: \n")
            for item in command:
                file.write("%s\n" % item)
                
            file.write("######## Log starting below ####### \n ")
    def RunOSCommand(self,command,logfile):
        """ generic function to run os processes """
        
        with open(logfile, 'a') as f:
            # Start the process in the specified directory
            process = subprocess.Popen(command, stdout=f, stderr=subprocess.STDOUT, text=True, cwd=self.path)
            # Wait for the process to complete
            return_code = process.wait()
            
        return return_code
    
    def ReturnGmshCommand(self,gmshBin):
        
        command = [gmshBin,'-2','bp3.geo','-setnumber', 'dip', str(self.dipAngle),'-setnumber', 'Lf', str(self.Lf),'-setnumber', 'Ls', str(self.Ls)]
        return command
        
    def ComputeMesh(self,gmshBin,logfile='/meshGeneration.log'):
        """ compute the mesh based on paramters like dip angle and mesh size """
        
        logfile=self.path+"/outputs/"+logfile
        command=self.ReturnGmshCommand(gmshBin)
        self.WriteCommandStringToFile(command,logfile)
        return_code=self.RunOSCommand(command,logfile)
            
        if return_code == 0:
            print("Mesh generated successfully.")
            
        else:
            print(f"Generating Mesh failed with return code: {return_code}. Check mesh log file")
            raise ValueError("byebye")
        
    def PlotSlipMaxVel(self):
        """ plotting slip along fault and max vel """
        
        ds=readtandemoutput.ReturnDataSets(self.path+"/outputs/")
        ds = xr.concat(ds, dim=('z'))
        ds['years'] = ds['Time']/(3600*24*365.25)
        
        coseismic={'color':'blue','alpha':0.5,'linewidth':0.5}
        interseismic={'color':'red','alpha':0.5,'linewidth':0.5}
        
        fig,ax=plt.subplots(2,1,figsize=(10,10))
        readtandemoutput.PlotSlipFrequnelty(ds['slip0'].values, ds['Time'].values, 5, np.abs(ds['z'].values),plotAttributes=coseismic,ax=ax[0],coseismic=True)
        readtandemoutput.PlotSlipFrequnelty(ds['slip0'].values, ds['Time'].values, 3600*24*365.25*5, np.abs(ds['z'].values),plotAttributes=interseismic,ax=ax[0],coseismic=False)
        
        highest_velocity = ds['slip-rate0'].max(['z']).values
        ax[1].plot(ds['years'],np.log10(highest_velocity))
        
        ax[1].set_ylabel('Log10(max Vel[m/s]) ')
        ax[1].set_xlabel('Time [years] ')
        
        ax[0].set_ylabel('Depth[km]')
        ax[0].set_xlabel('Slip [m]')
                   
        fig.savefig(self.path+"//outputs/slipMaxVel.pdf",dpi=300)
        
        
        
    def RunEQSimulation(self,tandemBinaryPath,logfile='/tandemSimulation.log',n=1):
        """ run tandem simultion with or without gf """
        
        logfile=self.path+"/outputs/"+logfile
        command = ['mpirun','-n',str(n),tandemBinaryPath, 'bp3.toml','--mode', 'QDGreen','--gf_checkpoint_prefix', self.gf_dir, '--petsc', '-ts_monitor', '-options_file', 'rk45.cfg', '-options_file', 'lu_mumps.cfg']
        
        if self.gf_dir is None:
            command = ['mpirun','-n',str(n),tandemBinaryPath, 'bp3.toml','--mode', 'QD', '--petsc', '-ts_monitor', '-options_file', 'rk45.cfg', '-options_file', 'lu_mumps.cfg']
            
        self.WriteCommandStringToFile(command,logfile)
        
        return_code=self.RunOSCommand(command,logfile)
            
        if return_code == 0:
            print("EQ simulation finished successfully.")
            
        else:
            print(f"EQ simulation failed with return code: {return_code}. Check  log file")
            raise ValueError("byebye")
        
        
    def WriteFiles(self):
        """ this function copies and and write toml,lua ,geo and cfg params files """
        
        shutil.copy(self.homeDir+self.filesToCopy+"bp3.lua",self.path+"/bp3.lua")
        shutil.copy(self.homeDir+self.filesToCopy+"bp3.geo",self.path+"/bp3.geo")
        shutil.copy(self.homeDir+self.filesToCopy+"lu_mumps.cfg",self.path+"/lu_mumps.cfg")
        shutil.copy(self.homeDir+self.filesToCopy+"rk45.cfg",self.path+"/rk45.cfg")
        luaFotter="\n -- adding user choice \n" + self.LuaFooter()
        toml=self.TomlHeader()+self.TomlBody()+self.TomlFotter() # gathering strings for toml file

        
        with open(self.path+'/bp3.toml', 'w') as file:
            file.writelines(toml)
            
        with open(self.path+'/bp3.lua', 'a') as file:
            file.writelines(luaFotter)

        
    def TomlHeader(self):
        """ adds run time as a first line to the toml file """
        
        return f"final_time = {self.endTime}"
    
    
    def ComputeRmax(self):
        return (1.1*(self.H0+self.H1+self.H2))/np.sin(np.deg2rad(self.dipAngle))
    
    def TomlFotter(self):
        """ this function compute where to add sites along the fault for plotting """
        
        Rmax=self.ComputeRmax()
        #print(Rmax)
        string=generateTomlFile.ComputePointsForPlanarFaultBasedOnDistanceAlongFault(self.dipAngle,dy=self.dr,ymin=0,ymax=Rmax)
        
        return string
    def LuaFooter(self):
        """ this function add one line of code to the Lua file to based on dipAngle,slipRate and a-b params """
        
        
        if self.depthVarying is False:
            depthVarying='false'
        else:
            depthVarying='true'
            
        output_line = f"bp3_custom = BP3.new{{dip={self.dipAngle}, Vp={self.slipRate}, inelastic=false, ratioWidthX=2, widthY=5, amp=0.1, depthVarying={depthVarying}, H0={self.H0}, H={self.H1}, h={self.H2}}}"

        return output_line
    
    def TomlBody(self):
        """ adding some lines to toml file """
        
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
 
    

#%%
class bp3_uniform(bp3):
    def __init__(self,dipAngle=10,slipRate=1e-9,H0=2,H1=8,H2=8,endTime=1500*3600*24*365.25,dr=2,path=".",Lf=0.6,Ls=0.6,gf_dir=None,Dc=0.02,normalStress=50,rigidity=30e9,**kwargs):
        """ get dipAngle in deg
    slip rate in m/s
    H0,H,h in km 
    endTime in second 
    Dc in meter 
    and normalStress in MPa"""
    
        self.dipAngle=dipAngle
        self.slipRate=slipRate
        self.H0=H0
        self.H1=H1
        self.H2=H2
        self.endTime=endTime
        self.dr=1
        self.path=path
        self.Lf=Lf
        self.Ls=Ls
        self.gf_dir=gf_dir
        self.homeDir = os.path.dirname(__file__)
        self.Dc=Dc
        self.normalStress=normalStress
        self.rigidity=rigidity
        self.LoadFilesToCopy()
        
    def LoadFilesToCopy(self):
        self.filesToCopy="/filesToCopyV2/"
    def LuaFooter(self):
        """ this function add one line of code to the Lua file to based on dipAngle,slipRate and a-b params """
        
        
            
        output_line = f"bp3_custom = BP3.new{{dip={self.dipAngle}, Vp={self.slipRate},  H0={self.H0}, H={self.H1}, h={self.H2},normalStress={self.normalStress},Dc={self.Dc},rigidity={self.rigidity}}}"

        return output_line
    
    def ReturnGmshCommand(self,gmshBin):
        
        command = [gmshBin,'-2','bp3.geo','-setnumber', 'dip', str(self.dipAngle),'-setnumber', 'Lf', str(self.Lf),'-setnumber', 'Ls', str(self.Ls),'-setnumber','vwMinDepth',str(self.H0),'-setnumber','vwMaxDepth',str(self.H1+self.H0),
                   '-setnumber','depthfaultEnds',str((self.H0+self.H1+self.H2*1.1))]
        return command
    
    def ComputeRmax(self):
        return ((self.H0+self.H1+self.H2*1.1))/np.sin(np.deg2rad(self.dipAngle))
    




