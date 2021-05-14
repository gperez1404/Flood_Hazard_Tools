"""
Created on Mon Apr 19 18:32:50 2021

@author: uqgpere2 : Gabriel Perez Murillo UQ-SMI 
@author: g.perezmurillo@uq.edu.au

This script calculates the FEI  for different simulations as:

 FEI = FPI x Flood Hazard

Inputs:
    1. Excel files with FPI values  for different simulations
    2. Excel files with  Hazard values for different simulations
    2. Excel file with the location of the input files (1 & 2)
"""
#*   This script is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU General Public License as published by  *
#*   the Free Software Foundation; either version 2 of the License, or     *
#*   any later version.                                   *

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#                                                                       WARNING
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# This was written under python 2 (ArcGIS 10.8)

# This script imports acrpy (you need an ARCGIS license)

# YOU need to execute these scripts  previously:
#      
#      Generate_Flood_Proximity_Index_for_a_list_of_simulations.py        
#      Extract_Flood_Hazard_to_TSFs_based_on_FPI.py        
#      

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#                                                                       WARNING
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!



###############################################################################
#%%                    PACKAGES YOU NEED TO LOAD
###############################################################################

# These are the packages you need to load files

import sys
import string 
import os
import math
import traceback
import glob
import itertools

import openpyxl
from openpyxl import Workbook

import arcpy
from arcpy.sa import *

import time
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np

import pandas as pd
from pandas import ExcelWriter

# Allow output to overwrite...
arcpy.env.overwriteOutput = True

# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

###############################################################################
#%%                        PACKAGES YOU NEED TO LOAD
###############################################################################

###############################################################################
#%%                      DEFINITION OF FILE LOCATIONS
###############################################################################

# Path of the main folder for the simulations
current_working_directory=r'C:\00-C-GPM_INFO\04-C-RDM\04-C-02-Python\04-C-02-03-TSFs-Exposure'    

# INPUTS FOLDER NAMES----------------------------------------------------------

# Folder name with inputs files
Input_files_folder_name= r'04-Inputs-files'

# Folder name with input rasters
Input_rasters_folder_name= r'05-Inputs-rasters'

# Folder name with input shapefiles
Input_shapes_folder_name= r'06-Inputs-shapes'

# OUTPUT FOLDER NAMES----------------------------------------------------------

# the output files folder
Output_files_folder_name= r'07-Results-files'

# Folder name with output shapefiles
Output_rasters_folder_name= r'08-Results-rasters'

# Folder name with output rasters
Output_shapes_folder_name= r'09-Results-shapes'

# RESULTS FOLDER NAMES---------------------------------------------------------

# Folder name with exposure rasters
Output_folder_FEI_shps= r'FEI_SHPs'

# Folder name with exposure tables
Output_folder_FEI_tables= r'FEI_TABLES'

# Folder Names for intermediate results
Output_folder_file_name = "RESULTS_PAPER_SWIFT"                  

# FOLDER PATHS-----------------------------------------------------------------

#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#                                                                        Inputs
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #

# Path to input files:
Inputpath_files= os.path.join(current_working_directory,Input_files_folder_name)

# Path to input shapes:
Inputpath_shapes= os.path.join(current_working_directory,Input_shapes_folder_name)

# Path to input rasters:
Inputpath_rasters= os.path.join(current_working_directory,Input_rasters_folder_name)

#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#                                                                       Outputs
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #

# Path to files shapes:
OutPath_files= os.path.join(current_working_directory,Output_files_folder_name)

# Path to raster results:
OutPath_rasters= os.path.join(current_working_directory,Output_rasters_folder_name)

# Path to shapefile results:
OutPath_shapes= os.path.join(current_working_directory,Output_shapes_folder_name)



# RESULTS FOLDER -------------------------------------------------------------

# Path to output shps:
OutPath_FEI_shps= os.path.join(OutPath_shapes,Output_folder_FEI_shps)

# Path to output files:
OutPath_FEI_files= os.path.join(OutPath_files,Output_folder_FEI_tables)


# Results:
OutPath_results_files= os.path.join(OutPath_files,Output_folder_file_name)

OutPath_results_shps= os.path.join(OutPath_shapes,Output_folder_file_name)

OutPath_results_rasters= os.path.join(OutPath_rasters,Output_folder_file_name)

# FILE NAMES-------------------------------------------------------------------

# Excel file with the list of files to generate FEI
list_of_input_files= r'00-list-of-files-to-generate-FEI-SWIFT-paper.xls'

# This is the shapefile with TSFs polygons: 
TSFs_polygons_shape= r'TSFs_polygons.shp'

# This is the shapefile with the polygons' centroids:
TSFs_polygon_centroids_shape = r'TSFs_polygons_centroids.shp'

# FILE PATHS INPUTS------------------------------------------------------------

# Here you create a path to the table with the list of rasters
input_list_file_paths=os.path.join(Inputpath_files,list_of_input_files)

# Here you create a path to the input shapefiles:

TSFs_polygons_filepath = os.path.join(Inputpath_shapes,TSFs_polygons_shape)

TSFs_polygon_centroids_filepath = os.path.join(Inputpath_shapes,TSFs_polygon_centroids_shape)

###############################################################################
#%% ^  ^  ^  ^  ^  ^  ^  DEFINITION OF FILE  LOCATIONS ^  ^  ^  ^  ^  ^  ^  ^  ^
###############################################################################

###############################################################################
#%%                                                                FEI analysis
###############################################################################

# Here you load the table with the list of rasters
# Warning: MAKE SURE THE FILE LOCATIONS HAVE THE PYTHON NOTATION '\\' or '\' instead of '/' (R)

df_file_list=pd.read_excel(input_list_file_paths)

number_of_simulations=len(df_file_list.simulation_ID)

list_of_IDs=df_file_list['simulation_ID'].tolist()

# Here you create the output folders in case they don't exist:

if not os.path.exists(OutPath_FEI_shps):
    os.makedirs(OutPath_FEI_shps)
    print("Output folder for result shp files  didn't exist and was created")

if not os.path.exists(OutPath_FEI_files):
    os.makedirs(OutPath_FEI_files)
    print("Output folder result  tables didn't exist and was created")

# Here you create the output folders in case they don't exist:

if not os.path.exists(OutPath_results_files):
    os.makedirs(OutPath_results_files)
    print("Output folder for result  files  didn't exist and was created")

if not os.path.exists(OutPath_results_shps):
    os.makedirs(OutPath_results_shps)
    print("Output folder result  shps didn't exist and was created")

if not os.path.exists(OutPath_results_rasters):
    os.makedirs(OutPath_results_rasters)
    print("Output folder result rasters didn't exist and was created")


# In this loop you calculate the FEI value for each simulation 

time_before_execution = time.time()

#
###
########
########### Main Loop 

for x in range(0,number_of_simulations,1):

    print('...................................................')
    print(r'Calculating FEI for simulation # '+str(x+1) + r' out of ' + str(number_of_simulations)) 
    
    simulationID=str(df_file_list.simulation_ID[x])
    
    print(simulationID)
    
    FPI_filepath=str(df_file_list.folder_path_FPI_files[x])
    FPI_filename=str(df_file_list.Name_FPI_files[x])
    
    FPI_file=os.path.join(FPI_filepath,FPI_filename)
    
    df_FPI=pd.read_excel(FPI_file)
    
    HZ_filepath=str(df_file_list.folder_path_hazard_files[x])
    HZ_filename=str(df_file_list.Name_hazard_files[x])
    
    HZ_file=os.path.join(HZ_filepath,HZ_filename)

    df_HAZARD=pd.read_excel(HZ_file)
    
    col_TSFs_IDs=df_FPI['TSF_id']
    col_TSFs_IDs_2=df_HAZARD['TSF_id']
    
    # This tests help you confirm that the TSF row order is the sam in the two arrays
    test= np.where(col_TSFs_IDs==col_TSFs_IDs_2, 'all good', 'ERROR')
    # print(np.unique(test))
    
    FPI=df_FPI['FPI']
    HAZARD=df_HAZARD['max_Hazard']
    
    FEI=FPI*HAZARD
    
    #--------------------------------------------------------------------------
    # Here you create a dataframe to save an excel file with FEI values
    
    df_FEI_values= pd.DataFrame({'TSF_id': col_TSFs_IDs,
                                 'FPI':FPI,
                                 'Flood_Hazard':HAZARD,
                                 'FEI':FEI})
    
    
    output_name=  r'FEI_values_' +simulationID + r'.xlsx'
    output_filepath=os.path.join(OutPath_FEI_files,output_name)
    writer = ExcelWriter(output_filepath)
    df_FEI_values.to_excel(writer,'Sheet1')
    writer.save()
    
    #second copy:
    output_filepath=os.path.join(OutPath_results_files,output_name)
    writer = ExcelWriter(output_filepath)
    df_FEI_values.to_excel(writer,'Sheet1')
    writer.save()
    
    
    #--------------------------------------------------------------------------
    # Here you create a copy of the Shapefile with TSFs points
    
    output_name=  r'FEI_values_' +simulationID + r'.shp'
    output_FEI_shp_path=os.path.join(OutPath_FEI_shps,output_name)
    
    # Set local variables
    in_data =  TSFs_polygon_centroids_filepath
    out_data = output_FEI_shp_path

    # Execute Copy
    arcpy.Copy_management(in_data, out_data)
    
    # Here you delete fields fron the attribute table
    dropFields = ["OBJECTID"]
    
    # Here you add Fields to the attribute table
    arcpy.DeleteField_management(output_FEI_shp_path, dropFields)
    
    #--------------------------------------------------------------------------
    # Here you Add a new field with the FPI VALUES
        
    fieldName1 = "FPI"
    field_type1= "FLOAT"
    fieldPrecision1 = 6 # DIGITS INCLUDING DECIMAL POSITIONS
    field_scale1=2 # NUMBER OF DECIMAL POSITIONS
    fieldAlias1 = "FPI"
    
    arcpy.AddField_management(output_FEI_shp_path,
                              field_name=fieldName1,
                              field_type=field_type1,
                              field_precision=fieldPrecision1,
                              field_scale=field_scale1,
                              field_alias=fieldAlias1,
                              field_is_nullable="NON_NULLABLE")
    

    # here you populate the field with the list of FPI values
    
    field_to_modify = ['FPI']
    Alloc_index=0
    with arcpy.da.UpdateCursor(output_FEI_shp_path, field_to_modify) as cursor:
      for row in cursor:
          row[0]=FPI[Alloc_index]
          Alloc_index=Alloc_index+1
          cursor.updateRow(row)
              
    #--------------------------------------------------------------------------          
    # Here you Add a new field with the Hazard value to the shp file
        
    fieldName2 = "max_Haz"
    field_type2= "FLOAT"
    fieldPrecision2 = 6 # DIGITS INCLUDING DECIMAL POSITIONS
    field_scale2=3 # NUMBER OF DECIMAL POSITIONS
    fieldAlias2 = "HAZ"
    
    arcpy.AddField_management(output_FEI_shp_path,
                              field_name=fieldName2,
                              field_type=field_type2,
                              field_precision=fieldPrecision2,
                              field_scale=field_scale2,
                              field_alias=fieldAlias2,
                              field_is_nullable="NON_NULLABLE")
    

    # here you populate the field with the list of Hazard values
    
    field_to_modify = ['max_Haz']
    Alloc_index=0
    with arcpy.da.UpdateCursor(output_FEI_shp_path, field_to_modify) as cursor:
      for row in cursor:
          row[0]=HAZARD[Alloc_index]
          Alloc_index=Alloc_index+1
          cursor.updateRow(row)
    
    #--------------------------------------------------------------------------
    # Here you Add a new field with the FEI VALUES
        
    fieldName1 = "FEI"
    field_type1= "FLOAT"
    fieldPrecision1 = 6 # DIGITS INCLUDING DECIMAL POSITIONS
    field_scale1=2 # NUMBER OF DECIMAL POSITIONS
    fieldAlias1 = "FEI"
    
    arcpy.AddField_management(output_FEI_shp_path,
                              field_name=fieldName1,
                              field_type=field_type1,
                              field_precision=fieldPrecision1,
                              field_scale=field_scale1,
                              field_alias=fieldAlias1,
                              field_is_nullable="NON_NULLABLE")
    

    # here you populate the field with the list of FPI values
    
    field_to_modify = ['FEI']
    Alloc_index=0
    with arcpy.da.UpdateCursor(output_FEI_shp_path, field_to_modify) as cursor:
      for row in cursor:
          row[0]=FEI[Alloc_index]
          Alloc_index=Alloc_index+1
          cursor.updateRow(row)
    
    #--------------------------------------------------------------------------
    
    #second copy of Shapefile:
    output_shp_path=os.path.join(OutPath_results_shps,output_name)
    arcpy.Copy_management(output_FEI_shp_path, output_shp_path)
    
    print('FEI calculated successfully !!')
    elapsed_time = (time.time() - time_before_execution) 
    print('Execution time: ' + str(round(elapsed_time/3600)) + ' hours ' + str(round(elapsed_time/60)%60)+ ' minutes ' + str(round(elapsed_time%60))+' seconds')

########### Main Loop 
########
###
#

    
#%%    