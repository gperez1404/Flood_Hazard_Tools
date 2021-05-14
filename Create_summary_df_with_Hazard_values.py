# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 12:16:52 2020

@author: uqgpere2

# This script loads individual files with max Flood Hazard values to create 
  a single df with all the Hazard values for different simulations as columns 
  
  This outoput can be loaded by R to make analysis and plots 
  

"""
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#                                                                       WARNING
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# YOU need to run the script :
#      Extract_Flood_Hazard_to_TSFs_based_on_FPI.py

# This was written under python 2

# This scrtip imports acrpy (you need ARCGIS license)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#                                                                       WARNING
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


###############################################################################
 #%%                       PACKAGES YOU NEED TO LOAD
###############################################################################

# These are the packages you need to load files
import os
import sys
import string
import math
import traceback
import glob
import arcpy
from arcpy.sa import *
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import pandas as pd
from pandas import ExcelWriter

# Allow output to overwrite...
arcpy.env.overwriteOutput = True

# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

###############################################################################
#%%  ^  ^  ^  ^  ^  ^  ^   PACKAGES YOU NEED TO LOAD       ^  ^  ^  ^  ^  ^  ^ 
###############################################################################

###############################################################################
#%%                       DEFINITION OF FILE LOCATIONS
###############################################################################

# Path of the main folder for the simulations
current_working_directory= r'C:\00-C-GPM_INFO\04-C-RDM\04-C-02-Python\04-C-02-03-TSFs-Hazard'
# FOLDER NAMES INPUTS ---------------------------------------------------------

# Folder name with inputs files
Input_files_folder_name= r'04-Inputs-files'

# Folder name with input rasters
Input_rasters_folder_name= r'05-Inputs-rasters'

# Folder name with input shapefiles
Input_shapes_folder_name= r'06-Inputs-shapes'


# FOLDER NAMES OUTPUTS ---------------------------------------------------------

# the output files folder
Output_files_folder_name= r'07-Results-files'

# Folder name with output shapefiles
Output_rasters_folder_name= r'08-Results-rasters'

# Folder name with output rasters
Output_shapes_folder_name= r'09-Results-shapes'

# Folder name  to save the FPI summary file 
HZ_folder_name=r'HAZARD_TSFs_TABLES'

#folder for paper results:
Output_folder_file_name=r'RESULTS_PAPER_SWIFT'

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

results_path=os.path.join(OutPath_files,HZ_folder_name)

# RESULTS FOLDERS -------------------------------------------------------------

# Results:
OutPath_results_files= os.path.join(OutPath_files,Output_folder_file_name)

OutPath_results_shps= os.path.join(OutPath_shapes,Output_folder_file_name)

OutPath_results_rasters= os.path.join(OutPath_rasters,Output_folder_file_name)


# FILE NAMES-------------------------------------------------------------------

# Excel  file with the list of simulations

#list_of_simulations= r'00-list-of-files-to-generate-Hazard-summary.xls'
list_of_simulations=r'00-list-of-files-to-generate-Hazard-summary-for-SWIFT-paper.xls'

# FILE PATHS-------------------------------------------------------------------

# Here you create a path to the table with the list of rasters
simulations_list_file_path=os.path.join(Inputpath_files,list_of_simulations)


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
#%%                                                                 FPI summary
###############################################################################

# Here you load the table with the list of simulations

# Warning: MAKE SURE THE FILE LOCATIONS HAVE THE PYTHON NOTATION '\\' or '\' instead of '/' (R)

df_file_list=pd.read_excel(simulations_list_file_path)

number_of_simulations=len(df_file_list.simulation_ID)

list_of_IDs=df_file_list['simulation_ID'].tolist()

#------------------------------------------------------------------------------
# Here you initialize the sumamry df:
df_summary_HZ  = pd.DataFrame()

# here you add the first columns to summary df:

file_path_first_file =  df_file_list['folder_path_HZ_files'][0]
file_name_first_file =  df_file_list['Name_HZ_files'][0]

first_file= os.path.join(file_path_first_file,file_name_first_file)

df_first_sim=pd.read_excel(first_file)

df1= df_first_sim[['TSF_id']]
df2= df_first_sim[['max_Hazard','TSF_id']]

df_summary_HZ= pd.merge(left=df1, right=df2, left_on='TSF_id', right_on='TSF_id')

# Here you rename the Hazard column with the name of the simulation
df_summary_HZ = df_summary_HZ.rename(columns={'max_Hazard': list_of_IDs[0] })

#%%
#
##
###
########
########### Main Loop 

# In this loop you convert the remaining excel files into  pandas dfs 

for x in range(1,number_of_simulations,1):
    
    print('........................................')
    print('Adding column for: '+ str(df_file_list.simulation_ID[x]))
    
    # here you load the excel file:
    file_path =  df_file_list['folder_path_HZ_files'][x]

    file_name = df_file_list['Name_HZ_files'][x]
    
    excel_file_path= os.path.join(file_path,file_name)
        
    # here you load the excel file as df
    df = pd.read_excel(excel_file_path)
    
    # Here you extract the hazard values 
    df_values = df[['max_Hazard','TSF_id']]
    
    # here you add the last column to the summary E
    df_summary_HZ= pd.merge(left=df_summary_HZ, right=df_values, left_on='TSF_id', right_on='TSF_id')
    
    # Here you rename the column  
    df_summary_HZ = df_summary_HZ.rename(columns={'max_Hazard': list_of_IDs[x] })

    print('Column Added successfully !!')
    print('........................................')
    
########### Main Loop 
########
###
##
#
#%%
    
# S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S
#                                                   Save results to Excel files
# S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S-S

output_name=  r'summary_max_Hazard_TSFs.xlsx'
output_filepath=os.path.join(results_path,output_name)
writer = ExcelWriter(output_filepath)
df_summary_HZ.to_excel(writer,'Sheet1')
writer.save()
    
#second copy:
output_filepath=os.path.join(OutPath_results_files,output_name)
writer = ExcelWriter(output_filepath)
df_summary_HZ.to_excel(writer,'Sheet1')
writer.save()
