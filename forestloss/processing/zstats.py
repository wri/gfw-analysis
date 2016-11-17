import arcpy
arcpy.CheckOutExtension("Spatial")
import os
import subprocess

def zonal_stats_mask(snapraster,fc_geo,scratch_gdb,maindir,shapefile,column_name2,outdir):
    arcpy.env.snapRaster = snapraster
    arcpy.env.scratchWorkspace = scratch_gdb

    extent = fc_geo.extent
    envextent = arcpy.Extent(extent.XMin, extent.YMin, extent.XMax, extent.YMax)
    arcpy.env.extent = envextent
    layer = os.path.join(maindir, "shapefile")
    arcpy.MakeFeatureLayer_management(shapefile, layer)
    exp = """"FC_NAME" = '{}'""".format(column_name2)
    arcpy.AddMessage("selecting by attribute")
    arcpy.SelectLayerByAttribute_management(layer, "NEW_SELECTION", exp)
    arcpy.AddMessage("converting layer to feature class")
    arcpy.FeatureClassToFeatureClass_conversion(layer, outdir, column_name2)
    mask = os.path.join(outdir, column_name2)
    # mask = os.path.join(outdir, column_name2 + ".shp")
    return mask, envextent

def zonal_stats(zone_raster, value_raster, filename, calculation, snapraster, mask, maindir, outdir, column_name2,
                orig_fcname, envextent):
    arcpy.AddMessage(           "zonal stats")
    arcpy.env.scratchWorkspace = maindir
    arcpy.env.snapRaster = snapraster
    arcpy.env.mask = mask
    arcpy.env.extent = envextent

    z_stats_tbl = os.path.join(outdir, column_name2 + "_" + filename + "_" + calculation)

    zstats_cmd = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zstats_cmd.py')

    cmd = ["C:\Python27\ArcGIS10.3\python.exe", zstats_cmd,
           '-v', value_raster, '-z', zone_raster, '-m', mask, '-t', z_stats_tbl]

    # silence error message
    FNULL = open(os.devnull, 'w')
    try:

        subprocess.check_call(cmd, stdout=FNULL, stderr=subprocess.STDOUT)

        arcpy.AddField_management(z_stats_tbl, "ID", "TEXT")
        arcpy.CalculateField_management(z_stats_tbl, "ID", "'" + str(orig_fcname) + "'", "PYTHON_9.3")

        arcpy.AddMessage("adding field")
        arcpy.AddField_management(z_stats_tbl, "uID", "TEXT")
        arcpy.CalculateField_management(z_stats_tbl, "uID", """!ID!+"_"+str( !Value!)""", "PYTHON_9.3", "")

        arcpy.AddField_management(z_stats_tbl, "sum_field", "TEXT")
        admin_name = column_name2.split("_")[0]
        arcpy.CalculateField_management(z_stats_tbl, "sum_field", "'" + admin_name + "'", "PYTHON_9.3", "")

    except:

        arcpy.AddMessage('failed: mostly likely because raster doesnt cover feature')

    arcpy.env.workspace = maindir
    rasters = arcpy.ListRasters()
    for r in rasters:
        arcpy.Delete_management(r)