#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 15:35:32 2024

@author: bar
"""

import pandas as pd
import xarray as xr
import numpy as np
import glob
import matplotlib.pyplot as plt
#%%
def load_csv_extract_x_position(file_path):
    """
    Reads the first line of a CSV file to extract the position of 'x',
    then loads the rest of the CSV file into a pandas DataFrame, skipping the first line.

    Parameters:
    - file_path: str, path to the CSV file.

    Returns:
    - x_position: list of floats, the extracted position of 'x'.
    - df: pandas DataFrame, the loaded CSV data excluding the first line.
    """
    
    # Open the file and read the first line
    with open(file_path, 'r') as file:
        first_line = file.readline().strip()
    
    # Extract the position of 'x' using a regular expression
    #match = re.search(r'x = \[([-\d.e]+), ([-\d.e]+)\]', first_line)
    #if match:
    #    x_position = [float(match.group(1)), float(match.group(2))]
    #else:
    #    x_position = None
    #    print("x position not found in the first line.")
    position=first_line.split(']')[0].split('[')[-1].split(',')
    
    
    x=float(position[0])
    y=float(position[1])
     
    if len(position)==2:
        xyz=np.array([x,y])
    elif len(position)==3:
        z=float(position[2])
        xyz=np.array([x,y,z])
    else:
        raise ("problem with extracting position data from csv file header")
    
    # Load the rest of the CSV file into a pandas DataFrame, skipping the first line
    df = pd.read_csv(file_path, skiprows=1)
    
    return xyz, df
#%%

def pandas_to_xarray(df, x_coord,z_coord, y_coord=None):
    """
    Reads a CSV file with a 'time' column and multiple data columns, and converts it into an xarray Dataset.
    
    Parameters:
    - filepath: str, path to the CSV file.
    - x_coord: float, x coordinate of the location.
    - y_coord: float, y coordinate of the location.
    
    Returns:
    - ds: xarray Dataset containing the data from the CSV file.
    """

    
    # Ensure 'time' column is a datetime type
    #df['time'] = pd.to_datetime(df['time'])
    
    # Initialize an empty list to store the DataArrays
    data_arrays = []
    
    # Iterate over the columns in the DataFrame, skipping the 'time' column
    for column in df.columns[1:]:  # Assuming the first column is 'time'
        # Create a DataArray for the current column
        if y_coord is None:
            da = xr.DataArray(df[column].values, dims=['Time'], 
                        coords={'Time': df['Time'],
                                'x': x_coord,
                                'z': z_coord},
                        name=column)
        else:
            da = xr.DataArray(df[column].values, dims=['Time'], 
                        coords={'Time': df['Time'],
                                'x': x_coord,
                                'z': z_coord,'y':y_coord},
                        name=column)
        data_arrays.append(da)
    
    # Combine the DataArrays into a single Dataset
    ds = xr.merge(data_arrays)
    return ds
#%%
def ReturnDataSets(path,pattern="fltst_*"):
    
    """ get csv file for each site and turns them into xarray datarray """
    
    files=sorted(glob.glob(path+pattern))
    ds=[]
    for file in files:
        position,df=load_csv_extract_x_position(file)
        if len(position)==2:
            ds.append(pandas_to_xarray(df,position[0],position[1]))
        else:
            ds.append(pandas_to_xarray(df,position[0],position[1],position[2]))
            
    return ds

#%%
def PlotSlipFrequnelty(slip,time,frequency,z,plotAttributes=None,ax=None,coseismic=False):
    if ax is None:
        fig,ax=plt.subplots()
        
    i=0
    while i<(len(time)-1):
        
        if coseismic is True:
            if time[i+1]-time[i]>1:
                i+=1
                continue
        j=i+1
        while (time[j]-time[i]<frequency) & (j<len(time)-1):
            j+=1
            
        ax.plot(slip[:,j],z,**plotAttributes)
        i=j+1


    