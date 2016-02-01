__author__ = 'sgibbes'
import arcpy, os
def boundary_prep(fc,outdir,analysis_boundary,column_name,admin_file,grid,column_calc):
    arcpy.env.overwriteOutput = "TRUE"
    fname = os.path.basename(fc).split(".")[0]
    # check coordinat system
    desc = arcpy.Describe(fc)
    sr = desc.spatialReference
    coords = sr.Name
    if not coords == "GCS_WGS_1984":
        arcpy.AddMessage("projecting feature")
        out_coor_system="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
        arcpy.Project_management(fc,os.path.join(outdir,fname+"_proj.shp"),out_coor_system)
        fc = os.path.join(outdir,fname+"_proj.shp")
    intersect = os.path.join(outdir,fname+"_intersect.shp")
    if analysis_boundary == "land use boundary":
        arcpy.Dissolve_management(fc,"in_memory/dissolve")
        arcpy.AddMessage("intersecting feature, land use boundary")
        arcpy.Intersect_analysis(["in_memory/dissolve",admin_file],"in_memory/intersect")
        arcpy.Intersect_analysis(["in_memory/intersect",grid],intersect)
        arcpy.AddField_management(intersect,column_name,"TEXT","","",15)
        arcpy.CalculateField_management(intersect, column_name,column_calc ,"PYTHON_9.3")
    if analysis_boundary == "country level":
        arcpy.AddMessage("intersecting feature, country boundary")
        arcpy.Intersect_analysis([fc,grid],intersect)
        arcpy.AddField_management(intersect,column_name,"TEXT","","",15)
        arcpy.CalculateField_management(intersect, column_name,column_calc ,"PYTHON_9.3")
    return intersect
