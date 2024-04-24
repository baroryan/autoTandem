#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 08:59:11 2024

@author: bar
"""

import autoTandemSimulation as autoTandem
import argparse
from pint import UnitRegistry
import os
#%%
def create_range_validator(min_value=None, max_value=None):
    def validate_range(value):
        try:
            fvalue = float(value)
        except ValueError:
            raise argparse.ArgumentTypeError(f"{value} is not a valid float")
        
        if min_value is not None and fvalue < min_value:
            raise argparse.ArgumentTypeError(f"Value must be greater than or equal to {min_value}")
        
        if max_value is not None and fvalue > max_value:
            raise argparse.ArgumentTypeError(f"Value must be less than or equal to {max_value}")
        
        return fvalue
    return validate_range
#%%
if __name__ == "__main__":
   
    ureg=UnitRegistry()
    
    parser = argparse.ArgumentParser(description="Process input file for bp3 like tandem simulation")
    parser.add_argument("--dipAngle", type=create_range_validator(0,90), help="Enter a dip angle value between 0 and 90 [deg]",required=True)
    parser.add_argument("--slipRate", type=create_range_validator(0,200), help="Enter slip rate between 0 and 200 [cm/yr]",required=True)
    parser.add_argument("--H0", type=create_range_validator(0,100), help="Enter depth range for the shallowest [km]",required=True)
    parser.add_argument("--H1", type=create_range_validator(0,100), help="Enter depth range for the middle section [km] ",required=True)
    parser.add_argument("--H2", type=create_range_validator(0,100), help="Enter depth range for the deepest section [km]",required=True)
    parser.add_argument("--depthVarying"  ,help="Check true or false if lame parameters change with depth [true/false]",default=True)
    parser.add_argument("--path",type=str,  help="set a path where everything will run",required=True)
    parser.add_argument("--endTime",type=create_range_validator(0,None) , help="Set number of years to run simlation [yr]",default=1000)
    parser.add_argument("--Ls", type=create_range_validator(0.02,10), help="Max mesh size along surface[km] - larger vaule coraser mesh",default=0.6)
    parser.add_argument("--Lf", type=create_range_validator(0.02,10), help="Max mesh size along fault[km] - larger vaule coraser mesh",default=0.6)
    parser.add_argument("--gf_dir",type=str , help="Set a green function dir- if not set will not use gf",default=None)
    parser.add_argument("--dr",type=create_range_validator(0,10),  help="plot every dr along the fault [km]",default=2)
    args = parser.parse_args()
    
    if not os.path.exists(args.path):
        os.makedirs(args.path)
    
    
    ## converstion to tandem units
    slipRate=ureg.Quantity(args.slipRate, ureg.cm/ureg.year)
    args.slipRate=slipRate.to(ureg.meters/ureg.sec).magnitude
    
    endTime=ureg.Quantity(args.endTime, ureg.year)
    args.endTime=endTime.to( ureg.sec).magnitude
    
    
    dictArgs=vars(args)
    
    model=autoTandem.bp3(**dictArgs)
    
    model.WriteFiles()
