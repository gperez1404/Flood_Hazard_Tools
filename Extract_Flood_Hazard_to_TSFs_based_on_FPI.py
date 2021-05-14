"""
Created on Mon Apr 19 18:32:50 2021

@author: uqgpere2 : Gabriel Perez Murillo UQ-SMI 
@author: g.perezmurillo@uq.edu.au

This script  extract the max Hazard value for different simulations
based on excel files with the FPI value 


Outputs:
    
    HAZARD_TSFs_SHPs -> multiple point shapefiles with the hazrd value for each TSF
    HAZARD_TSFs_TABLES -> multiple excel files witht eh hazard value for each TSF

"""
#*   This script is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU General Public License as published by  *
#*   the Free Software Foundation; either version 2 of the License, or     *
#*   any later version.                                   *

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#                                                                       WARNING
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# This was written under python 2 (ArcGIS 10.8)

# This script imports acrpy (you need ARCGIS license)

# YOU need to run : Generate_Flood_Exposure_Index_for_a_list_of_simulations.py


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
current_working_directory=r'C:\00-C-GPM_INFO\04-C-RDM\04-C-02-Python\04-C-02-03-TSFs-Hazard'    

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

# Folder name with exposure shape-files
Output_folder_TSFs_hazard_shps= r'HAZARD_TSFs_SHPs'

# Folder name with exposure tables
Output_folder_TSFs_hazard_tables= r'HAZARD_TSFs_TABLES'

# Folder Names for paper results
Output_folder_file_name = "RESULTS_PAPER_SWIFT"    

# FOLDER PATHS-----------------------------------------------------------------


#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#                                                                       Outputs
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #

# Path to files shapes:
OutPath_files= os.path.join(current_working_directory,Output_files_folder_name)

# Path to raster results:
OutPath_rasters= os.path.join(current_working_directory,Output_rasters_folder_name)

# Path to shapefile results:
OutPath_shapes= os.path.join(current_working_directory,Output_shapes_folder_name)

# Path to output shps:
OutPath_TSFs_hazard_shps= os.path.join(OutPath_shapes,Output_folder_TSFs_hazard_shps)

# Path to output files:
OutPath_TSFs_hazard_files= os.path.join(OutPath_files,Output_folder_TSFs_hazard_tables)

#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#                                                                        Inputs
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #

# Path to input files:
Inputpath_files= os.path.join(current_working_directory,Input_files_folder_name)

# Path to input shapes:
Inputpath_shapes= os.path.join(current_working_directory,Input_shapes_folder_name)

# Path to input rasters:
Inputpath_rasters= os.path.join(current_working_directory,Input_rasters_folder_name)

# RESULTS FOLDERS -------------------------------------------------------------

# Results:
OutPath_results_files= os.path.join(OutPath_files,Output_folder_file_name)

OutPath_results_shps= os.path.join(OutPath_shapes,Output_folder_file_name)

OutPath_results_rasters= os.path.join(OutPath_rasters,Output_folder_file_name)


# FILE NAMES-------------------------------------------------------------------

#input_file_name=r'list-of-files-to-extract-hazard-according-to-FPI.xls'
input_file_name=r'list-of-files-to-extract-hazard-according-to-FPI-for-SWIFT-paper.xls'

# This is the shapefile with TSFs polygons: 
TSFs_polygons_shape= r'TSFs_polygons.shp'

# This is the shapefile with the polygons' centroids:
TSFs_polygon_centroids_shape = r'TSFs_polygons_centroids.shp'

# This is the list with shapefile names  of the buffer polygons 

list_of_buffer_files= [r'TSFs_bff15m.shp',r'TSFs_bff30m.shp',r'TSFs_bff60m.shp']


# FILE PATHS-------------------------------------------------------------------

list_inputs_file_path = os.path.join(Inputpath_files,input_file_name)

TSFs_polygons_filepath = os.path.join(Inputpath_shapes,TSFs_polygons_shape)

TSFs_polygon_centroids_filepath = os.path.join(Inputpath_shapes,TSFs_polygon_centroids_shape)


def create_path(list_of_files,i):
    path=os.path.join(Inputpath_shapes,list_of_files[i])
    return(path)
    
list_buffer_polygons_filepath=list(map(lambda i:create_path(list_of_buffer_files, i), range(0, len(list_of_buffer_files))))


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

###############################################################################
#%% ^  ^  ^  ^  ^  ^  ^  DEFINITION OF FILE  LOCATIONS ^  ^  ^  ^  ^  ^  ^  ^  ^
###############################################################################


###############################################################################
#%%                        DEFINITION INPUT ARGUMENTS
###############################################################################

list_of_buffer_distances=[15,30,60]

number_of_buffer_rings=len(list_of_buffer_distances)

# Here you create a list of names for each buffer

def create_col_name(list_of_buffer_distances,i):
    name='buff_' + str(list_of_buffer_distances[i])+'m'
    return(name)
    
list_buffer_names=list(map(lambda i:create_col_name(list_of_buffer_distances, i), range(0, len(list_of_buffer_distances))))

###############################################################################
#%% ^  ^  ^  ^  ^  ^  ^   DEFINITION INPUT ARGUMENTS  ^  ^  ^  ^  ^  ^  ^  
###############################################################################

###############################################################################
#                                                             Nested functions:
#______________________________________________________________________________
#%%

# This function executes the Zonal Statistics tool from ArcGIS and creates a
# raster file with the desired statistics

def Zonal_Stats_to_extract_raster_to_polygons(polygons_filepath,raster_filepath,result_raster_filepath):
    
    mask_raster = r'C:\00-C-GPM_INFO\04-C-RDM\04-C-02-Python\04-C-02-03-TSFs-Exposure\05-Inputs-rasters\TSFs_polygons_rasterized.tif'
    arcpy.env.extent = mask_raster
    arcpy.env.mask = mask_raster

    ext = arcpy.Describe(mask_raster).extent
    #extent area in [km^2]
    area_inskm = (ext.width * ext.height)/1000000
    
    #get the cellsize:
    pixelsize = float( arcpy.GetRasterProperties_management (mask_raster, "CELLSIZEX").getOutput(0) )
    cellarea = pixelsize ** 2
    # define cell size and extension for raster calculator
    arcpy.env.cellSize = pixelsize

    #Option 1:
    # use zonal statisticis as raster
    # here you use the FUNCTION zonal statistics from arcgis to create 
    # a raster with the maximum flood height  for each TSFs polygon
    
    raster_stats= arcpy.sa.ZonalStatistics(polygons_filepath, "IDs_paper",raster_filepath,"MAXIMUM","DATA")
    raster_stats.save(result_raster_filepath)
    
#-----------------------------------------------------------------------------

# This function executes the extract to points tool from ArcGIS and then 
# creates a pandas df with the attribute table of extracted values
    
# This fucntion deletes all the temp files   
    
def return_df_with_raster_values_extracted_to_points(shp_points_filepath,raster_filepath):
    
    
    result_shp_filepath= os.path.join(OutPath_shapes,r'temp_extracted_points.shp')
    
    # Here you extract the  raster value for each polygon to its associated point:
    # Point extraction:
    arcpy.sa.ExtractValuesToPoints(shp_points_filepath,raster_filepath,result_shp_filepath,"INTERPOLATE","VALUE_ONLY")
    
    # Here you repalce NAN values ( -9999.99 ) to 0
    field_to_modify = ['RASTERVALU']

    with arcpy.da.UpdateCursor(result_shp_filepath, field_to_modify) as cursor:
      for row in cursor:
          if row[0] <0: # this is a simple conditional assuming the column is float()
              row[0] = 0
          cursor.updateRow(row)
    
    arr = arcpy.da.TableToNumPyArray(result_shp_filepath, ('IDs_paper', 'RASTERVALU'))

    df = pd.DataFrame(arr)
    # Here youd elet the Temp file
    arcpy.Delete_management(result_shp_filepath)
    return(df)
    
#%%
#______________________________________________________________________________
#                                                          End Nested functions
###############################################################################
  

###############################################################################
#%%                                                            Hazard  analysis
###############################################################################

# Here you load the table with the list of rasters
# Warning: MAKE SURE THE FILE LOCATIONS HAVE THE PYTHON NOTATION '\\' or '\' instead of '/' (R)

df_file_list=pd.read_excel(list_inputs_file_path)

number_of_simulations=len(df_file_list.simulation_ID)

list_of_IDs=df_file_list['simulation_ID'].tolist()

# In this loop you calculate the FPI value for each simulation 

time_before_execution = time.time()

#
###
########
########### Main Loop 

# In this loop you extract the maximum hazard for each simulation

for x in range(0,number_of_simulations,1):

    print('.............................................................')
    print('Extracting Flood Hazard to TSFs for simulation: ' + str(df_file_list.simulation_ID[x]))
    print('Simulation # '+str(x+1)+ ' out of '+ str(number_of_simulations))    
    
    base_name_result_files=str(df_file_list.simulation_ID[x])
    TSF_id=r'TSF_id'
    
    # here you load the max Hazard raster for the current simulation

    hazard_raster_filepath=str(df_file_list.file_path_max_hazard_raster[x])
    hazard_raster_name=str(df_file_list.Hazard_file_name[x])
    
    hazard_raster=os.path.join(hazard_raster_filepath,hazard_raster_name)
    

    # here you load the FPI file for the current simulation
    FPI_file_name=str(df_file_list.FPI_file[x])
    FPI_folder_path=str(df_file_list.FPI_table_file_path[x])
    
    FPI_path=os.path.join(FPI_folder_path,FPI_file_name)
    
    df_FPI=pd.read_excel(FPI_path)

    number_of_polygons=len(df_FPI[TSF_id])

    # Here you extract the max Flood hazard value according to FPI

    print('Extracting Hazard to TSFs....')
    
    # here you create the file path to all th buffer polygons
    shp_buffer_1=list_buffer_polygons_filepath[0]
    shp_buffer_2=list_buffer_polygons_filepath[1]
    shp_buffer_3=list_buffer_polygons_filepath[2]
    
    ZE_raster_buffer_1=os.path.join(OutPath_rasters,r'temp_raster_ZE_buff1_stats.tif')
    ZE_raster_buffer_2=os.path.join(OutPath_rasters,r'temp_raster_ZE_buff2_stats.tif')
    ZE_raster_buffer_3=os.path.join(OutPath_rasters,r'temp_raster_ZE_buff3_stats.tif')
    
    Zonal_Stats_to_extract_raster_to_polygons(shp_buffer_1,hazard_raster,ZE_raster_buffer_1)
    Zonal_Stats_to_extract_raster_to_polygons(shp_buffer_2,hazard_raster,ZE_raster_buffer_2)
    Zonal_Stats_to_extract_raster_to_polygons(shp_buffer_3,hazard_raster,ZE_raster_buffer_3)
    
    # here you generate the dfs with max Flood Hazard for all the possible buffers
    
    df_buffer_1=return_df_with_raster_values_extracted_to_points(TSFs_polygon_centroids_filepath,ZE_raster_buffer_1)
    df_buffer_2=return_df_with_raster_values_extracted_to_points(TSFs_polygon_centroids_filepath,ZE_raster_buffer_2)
    df_buffer_3=return_df_with_raster_values_extracted_to_points(TSFs_polygon_centroids_filepath,ZE_raster_buffer_3)
    
    # Here you delete all teh temp files
    arcpy.Delete_management(ZE_raster_buffer_1)
    arcpy.Delete_management(ZE_raster_buffer_2)
    arcpy.Delete_management(ZE_raster_buffer_3)
    print('dfs with max hazard values created successfully')
    
    # in this loop you select the right Hazad according to the FPI value
    
    list_TSFs_IDs= df_FPI.TSF_id.tolist()
    max_Hazard_values={}
    
    for TSF in range(0,number_of_polygons,1):

        FPI= df_FPI.FPI[TSF]
        current_TSF_ID= str(df_FPI[TSF_id][TSF])

        if (FPI == 0) :
            HAZARD=0
        elif (FPI == 0.33):
            row=df_buffer_3.loc[df_buffer_3['IDs_paper'] == current_TSF_ID]
            row.columns = ['TSF_id', 'Hazard']
            HAZARD= round(float(row['Hazard']),3)
        elif (FPI == 0.66):   
            row= df_buffer_2.loc[df_buffer_2['IDs_paper'] == current_TSF_ID]
            row.columns = ['TSF_id', 'Hazard']
            HAZARD= round(float(row['Hazard']),3)
        elif (FPI >= 1):
            row= df_buffer_1.loc[df_buffer_1['IDs_paper'] == current_TSF_ID]
            row.columns = ['TSF_id', 'Hazard']
            HAZARD= round(float(row['Hazard']),3)
        # here you save the max Hazard value of the current TSF
        max_Hazard_values[TSF]=HAZARD

    print('max Hazard values extracted to TSFs polygons successfully !')
        
    #-------------------------------------------------------------------------
    # Here you create a copy of the shp with TSFs points to save the max Hazard value
    
    output_name=  r'max_Hazard_values_' +base_name_result_files + r'.shp'
    output_HZ_shp_path=os.path.join(OutPath_TSFs_hazard_shps,output_name)
    
    # Set local variables
    in_data =  TSFs_polygon_centroids_filepath
    out_data = output_HZ_shp_path

    # Execute Copy
    arcpy.Copy_management(in_data, out_data)
    
    # Here you delete unnecessary fields from the attribute table
    dropFields = ["OBJECTID"]
    
    arcpy.DeleteField_management(output_HZ_shp_path, dropFields)
    
    # Here you Add a new field with the Hazard value to the shp file
        
    fieldName = 'max_HZ'
    field_type= "FLOAT"
    fieldPrecision = 6 # DIGITS INCLUDING DECIMAL POSITIONS
    field_scale=3      # NUMBER OF DECIMAL POSITIONS
    fieldAlias = "Haz"
    
    arcpy.AddField_management(output_HZ_shp_path,
                              field_name=fieldName,
                              field_type=field_type,
                              field_precision=fieldPrecision,
                              field_scale=field_scale,
                              field_alias=fieldAlias,
                              field_is_nullable="NON_NULLABLE")
    

    # here you populate the field with the list of Hazard values
    
    field_to_modify = [fieldName]
    Alloc_index=0
    with arcpy.da.UpdateCursor(output_HZ_shp_path, field_to_modify) as cursor:
      for row in cursor:
          row[0]=max_Hazard_values[Alloc_index]
          Alloc_index=Alloc_index+1
          cursor.updateRow(row)
          
    
    # second copy
    output_shp_path=os.path.join(OutPath_results_shps,output_name)
    arcpy.Copy_management(output_HZ_shp_path, output_shp_path)
    
    
    #-------------------------------------------------------------------------
    # here you create an excel file with the hazard values:
    
    # first you covnert the dict into a list 
    list_max_Hazard_values=[]
    
    for key, value in max_Hazard_values.iteritems():
        temp = value
        list_max_Hazard_values.append(temp)

    df_values= pd.DataFrame({'TSF_id': list_TSFs_IDs,'max_Hazard':list_max_Hazard_values})

    output_name=  base_name_result_files + r'_max_Hazard.xlsx'
    output_filepath=os.path.join(OutPath_TSFs_hazard_files,output_name)
    writer = ExcelWriter(output_filepath)
    df_values.to_excel(writer,'Sheet1')
    writer.save()
    
    #second copy:
    output_filepath=os.path.join(OutPath_results_files,output_name)
    writer = ExcelWriter(output_filepath)
    df_values.to_excel(writer,'Sheet1')
    writer.save()
    #--------------------------------------------------------------------------

    print(r'Hazard values extracted successfully !!')
    elapsed_time = (time.time() - time_before_execution) 
    print('Execution time: ' + str(round(elapsed_time/3600)) + ' hours ' + str(round(elapsed_time/60)%60)+ ' minutes ' + str(round(elapsed_time%60))+' seconds')
    print('...................................................')
########### Main Loop 
########
###
#
    
#%%    
