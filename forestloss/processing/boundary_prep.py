import os

import arcpy

from processing import column_calcs as columncalcs


def boundary_prep(input_shapefile,summarize_by,adm0,adm1,adm2,maindir,filename,summarize_by_columnname,summarize_file):
    # arcpy.AddField_management(input_shapefile, "FC_NAME", "TEXT", "", "", 50)
    admin_level = summarize_by
    if summarize_by != "choose my own file": # run admin level boundary prep
        admin_column_name, column_calc, area_type, admin_file = columncalcs.dict(admin_level, adm0, adm1, adm2, "FC_NAME")
    else: # get user's file and column name
        admin_column_name = "feature_ID" # created this name- generatic
        # column_calc = """str( !""" + column_name + """!)+"___"+str( !""" + summarize_by_columnname + """!)"""
        column_calc = """str(!FC_NAME!)+"___"+str( !"""+summarize_by_columnname+"""!)"""
        admin_file = summarize_file
    shapefile = os.path.join(maindir,filename+"_intersect.shp")
    arcpy.Intersect_analysis([input_shapefile,admin_file],shapefile)
    arcpy.AddField_management(shapefile, admin_column_name, "TEXT", "", "", 50)

    arcpy.CalculateField_management(shapefile, admin_column_name, column_calc, "PYTHON_9.3")
    arcpy.CalculateField_management(shapefile, "FC_NAME", "!"+admin_column_name+"!", "PYTHON_9.3")
    return shapefile,admin_column_name