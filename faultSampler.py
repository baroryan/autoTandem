#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 09:58:46 2024

@author: bar
"""
import numpy as np
import matplotlib.pyplot as plt
import pointsInSidePoly
import pandas as pd
#%%
class powerLawSampler:
    def __init__(self, n, a, b):
        self.n = n
        self.a = a
        self.b = b
    
    def draw(self, size=1000):
        # Generate uniform random numbers U between 0 and 1
        U = np.random.uniform(0, 1, size)
        
        # Compute the random draws based on the inverse CDF
        r = (U * (self.b**(1-self.n) - self.a**(1-self.n)) + self.a**(1-self.n))**(1/(1-self.n))
        
        return r
    
    def plot_histogram(self, size=1000, bins=30,ax=None):
        if ax is None:
            fig,ax=plt.subplots()
        random_draws = self.draw(size)
        
        # Plot the histogram of the random draws
        ax.figure(figsize=(8, 6))
        ax.hist(random_draws, bins=bins, density=True, edgecolor='black')
        ax.title('Histogram of Random Draws from Power-Law Distribution');ax.xlabel('r');ax.ylabel('Density')
        
#%%
        
class polygonSampler:
    def __init__(self, x_points, y_points):
        if len(x_points) != len(y_points):
            raise ValueError("x_points and y_points must have the same length.")
        
        # Store the polygon as a 2D array of points
        self.polygon = np.column_stack((x_points, y_points))

    def draw(self, size=1000):
        min_x, min_y = np.min(self.polygon, axis=0)
        max_x, max_y = np.max(self.polygon, axis=0)
        points = []

        while len(points) < size:
            random_points = np.column_stack((
                np.random.uniform(min_x, max_x, size),
                np.random.uniform(min_y, max_y, size)
            ))
            inside=self.CheckIfPointIsInsidePolygon(random_points)
            # Check if the points are inside the polygon
            
            points.extend(random_points[inside])

        return np.array(points[:size])
    def CheckIfPointIsInsidePolygon(self,points):
        return pointsInSidePoly.CheckIfPointsAreInsidePolygon(points, self.polygon)
    
    def ReturnPloygonPoints(self):
        return self.polygon[:,0],self.polygon[:,1]

    def plot_polygon_with_points(self, size=1000,ax=None):
        if ax is None:
            fig,ax=plt.subplots()
            
        points = self.draw(size)

        ax.figure(figsize=(8, 6))
        x, y = self.ReturnPloygonPoints()
        ax.plot(x, y, 'k-', label='Polygon')
        ax.scatter(points[:, 0], points[:, 1], color='red', s=10, label='Random Points');ax.xlabel('X');ax.ylabel('Y');ax.title('Random Points Inside Polygon')
        

#%%
class rectangleSampler:
    def __init__(self, x_min, x_max, y_min, y_max):
        if x_min >= x_max or y_min >= y_max:
            raise ValueError("x_min must be less than x_max and y_min must be less than y_max.")
        
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

    def draw(self, size=1000):
        # Generate random x and y coordinates within the rectangle
        x_points = np.random.uniform(self.x_min, self.x_max, size)
        y_points = np.random.uniform(self.y_min, self.y_max, size)
        
        return np.column_stack((x_points, y_points))

    def plot_rectangle_with_points(self, size=1000,ax=None):
        if ax is None:
            fig,ax=plt.subplots()
        points = self.draw(size)

        ax.figure(figsize=(8, 6))
        ax.scatter(points[:, 0], points[:, 1], color='blue', s=10, label='Random Points')
        ax.plot([self.x_min, self.x_max, self.x_max, self.x_min, self.x_min],
                 [self.y_min, self.y_min, self.y_max, self.y_max, self.y_min], 'k-', label='Rectangle')
        ax.xlabel('X');ax.ylabel('Y');ax.title('Random Points Inside Rectangle')
        
#%%
class angleSample:
    def __init__(self, dip, std):
        self.dip = dip
        self.std = std

    def draw(self, size=1000):
        # Generate random choices between dip and 180 - dip
        choices = np.array([self.dip, 180 - self.dip])
        base_angles = np.random.choice(choices, size=size, p=[0.5, 0.5])
        
        # Add noise from a normal distribution with the given standard deviation
        noise = np.random.normal(0, self.std, size=size)
        noisy_angles = base_angles + noise
        
        return noisy_angles   
    
    
#%%
class planarfaultSampler:
    def __init__(self,positionSampler,angleSampler,lengthSampler):
        self.positionSampler=positionSampler
        self.angleSampler=angleSampler
        self.lengthSampler=lengthSampler
        
        
    def draw(self,size=1000):
        
        count=0
        faults_list=[]
        while count<size:
            middleFaultPoint=self.positionSampler.draw(size)
            dipAngle=self.angleSampler.draw(size)
            faultLengthAlongDip=self.lengthSampler.draw(size)
            
            shallowPoints=self.ComputeEndPointAlongTheFault(dipAngle,middleFaultPoint,-faultLengthAlongDip/2)
            deepPoints=self.ComputeEndPointAlongTheFault(dipAngle,middleFaultPoint,faultLengthAlongDip/2)
            
            maskShallow=self.positionSampler.CheckIfPointIsInsidePolygon(shallowPoints)
            maskDeep=self.positionSampler.CheckIfPointIsInsidePolygon(deepPoints)
            
            
            maskIntersection = maskShallow & maskDeep
            
            fault_df = pd.DataFrame({'shallowX': shallowPoints[maskIntersection][:, 0],'shallowZ': shallowPoints[maskIntersection][:, 1],'deepX': deepPoints[maskIntersection][:, 0],'deepZ': deepPoints[maskIntersection][:, 1]})
            count+=len(fault_df)
            faults_list.append(fault_df)
            
        faults=pd.concat(faults_list, ignore_index=True)
        return faults.loc[0:size] 
        
        
        
    def ComputeEndPointAlongTheFault(length,dipAngle,startPoint):
        dipAngleRad=np.deg2rad(dipAngle)
        direction_vector = np.array([np.cos(dipAngleRad), np.sin(dipAngleRad)])
        endPoint=startPoint+length*direction_vector
        return endPoint
    
    
    def plot_faults(self, size=1000,ax=None):
        if ax is None:
            fig,ax=plt.subplots()
        
        faults=self.draws(size)
        for _, row in faults.iterrows():
            ax.plot([row['shallowX'], row['deepX']], [row['shallowZ'], row['deepZ']], 'r-')
        
        ax.scatter(faults['shallowX'], faults['shallowZ'], color='blue', label='Shallow Points')
        ax.scatter(faults['deepX'], faults['deepZ'], color='green', label='Deep Points')
        
        ax.xlabel('X');ax.ylabel('Z');ax.title('Faults Visualization')
        x,y=self.positionSampler.ReturnPloygonPoints()
        ax.plot(x,y,label='bounding polygon')
        

        
        
        
        
        
 
