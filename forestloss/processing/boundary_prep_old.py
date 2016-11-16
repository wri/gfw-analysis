import arcpy
import os
import directories as d
import column_calcs as c
def boundary_prep(dataset,column_name,summarize_by,directory):
    outdir = d.dirs(directory)
    filename = os.path.basename(dataset).split(".")[0]
    adm0 = r'C:\Users\samantha.gibbes\Documents\gis\admin_boundaries\gadm27_levels.gdb\adm0'
    adm1 = r'C:\Users\samantha.gibbes\Documents\gis\admin_boundaries\gadm27_levels.gdb\adm1'
    adm2 = r'C:\Users\samantha.gibbes\Documents\gis\admin_boundaries\gadm27_levels.gdb\adm2'
    admin_level = summarize_by
    print admin_level
    # set up the files and field calculations to use
    if summarize_by != "choose my own file": # run admin level boundary prep
        admin_column_name, column_calc, area_type, admin_file = c.dict(admin_level, adm0, adm1, adm2,column_name)
    else: # get user's file and column name
        column_calc = """str( !"""+column_name+"""!)+"___"+str( !"""+summarize_by_columnname+"""!)"""
        admin_file = summarize_file
    shapefile = os.path.join(outdir,filename+"_intersect")
    arcpy.Intersect_analysis([dataset,admin_file],shapefile)
    arcpy.AddField_management(shapefile, "FC_NAME", "TEXT", "", "", 50)

    exp = "!"+admin_column_name+"!"
    arcpy.AddMessage(exp)
    arcpy.AddMessage(shapefile)
    arcpy.CalculateField_management(shapefile, "FC_NAME",column_calc , "PYTHON_9.3")

    return shapefile,admin_column_name

