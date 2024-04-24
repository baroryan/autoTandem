#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 14:54:17 2024

@author: bar
"""
import numpy as np

#%%

def format_xy_vectors_to_string(x, y):
    if len(x) != len(y):
        raise ValueError("x and y vectors must have the same length.")
    
    # Start the string with "probes = [ \n"
    formatted_string = "probes = [ \n"
    for i, (x_val, y_val) in enumerate(zip(x, y)):
        name = f"dp{str(i).zfill(3)}"
        entry = f'    {{ name = "{name}", x = [{x_val}, {y_val}] }},\n'
        formatted_string += entry
    
    # Remove the last comma and newline, then close the string with "]"
    formatted_string = formatted_string.rstrip(',\n') + "\n]"
    
    return formatted_string


def ComputePointsForPlanarFaultBasedOnDepth(dip,dy=0.5,ymin=0,ymax=20.1):
    y=np.arange(ymin,ymax,dy).astype(dtype=np.float64)
    x=y/np.tan(np.deg2rad(dip))
    
    return format_xy_vectors_to_string(x,-1*y)


def ComputePointsForPlanarFaultBasedOnDistanceAlongFault(dip,dy=0.5,ymin=0,ymax=20.1):
    y=np.arange(ymin,ymax,dy).astype(dtype=np.float64)
    y=y*np.sin(np.deg2rad(dip))
    x=y/np.tan(np.deg2rad(dip))
    
    if len(x) != len(y):
        
        raise ValueError("len of x and y for probing the fault are not of the same length! WHY ?! ")
    
    return format_xy_vectors_to_string(x,-1*y)
    