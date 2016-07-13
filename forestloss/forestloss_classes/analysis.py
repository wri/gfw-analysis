import zstats as zstats
import arcpy
from arcpy.sa import *

def forest_loss_function(hansenareamosaic,fc_geo,scratch_gdb,maindir,shapefile,column_name2,outdir,lossyr,filename,orig_fcname):
    mask = zstats.zonal_stats_mask(hansenareamosaic, fc_geo, scratch_gdb, maindir, shapefile, column_name2, outdir)
    zstats.zonal_stats(lossyr, hansenareamosaic, filename, "forest_loss", hansenareamosaic, mask, scratch_gdb, outdir,
                       column_name2, orig_fcname)


def new_carbon_emissions_function(hansenareamosaic,biomassmosaic,fc_geo,scratch_gdb,maindir,shapefile,column_name2,outdir,lossyr,filename,orig_fcname):
    mask = zstats.zonal_stats_mask(hansenareamosaic, fc_geo, scratch_gdb, maindir, shapefile, column_name2, outdir)
    zstats.zonal_stats(lossyr, hansenareamosaic, filename, "forest_loss", hansenareamosaic, mask, scratch_gdb, outdir,
                       column_name2, orig_fcname)
    zstats.zonal_stats(lossyr, biomassmosaic, filename, "biomass", hansenareamosaic, mask, scratch_gdb, outdir,
                       column_name2, orig_fcname)



def carbon_emissions_function(hansenareamosaic,biomassmosaic,fc_geo,scratch_gdb,maindir,shapefile,column_name2,outdir,lossyr,filename,orig_fcname):
    mask = zstats.zonal_stats_mask(hansenareamosaic, fc_geo, scratch_gdb, maindir, shapefile, column_name2, outdir)
    zstats.zonal_stats(lossyr, hansenareamosaic, filename, "forest_loss", hansenareamosaic, mask, scratch_gdb, outdir,
                       column_name2, orig_fcname)
    zstats.zonal_stats(lossyr, biomassmosaic, filename, "biomass_max", hansenareamosaic, mask, scratch_gdb, outdir,
                       column_name2, orig_fcname)
    zstats.zonal_stats(lossyr, biomassmosaic, filename, "biomass_min", hansenareamosaic, mask, scratch_gdb, outdir,
                       column_name2, orig_fcname)


def carbon_emissions_resample_function(hansenareamosaic,biomassmosaic,fc_geo,scratch_gdb,maindir,shapefile,column_name2,outdir,lossyr,filename,orig_fcname):
    mask = zstats.zonal_stats_mask(hansenareamosaic, fc_geo, scratch_gdb, maindir, shapefile, column_name2, outdir)
    zstats.zonal_stats(lossyr, hansenareamosaic, filename, "forest_loss", hansenareamosaic, mask, scratch_gdb, outdir,
                       column_name2, orig_fcname)
    zstats.zonal_stats(lossyr, biomassmosaic, filename, "biomass", hansenareamosaic, mask, scratch_gdb, outdir,
                       column_name2, orig_fcname)


def biomass_weight_function(hansenareamosaic30m,biomassmosaic,fc_geo,tcdmosaic30m,filename,scratch_gdb,outdir,column_name2,orig_fcname):
    arcpy.env.snapRaster = hansenareamosaic30m
    arcpy.env.cellSize = "MAXOF"
    arcpy.AddMessage("extracting for biomass weight")
    arcpy.AddMessage("extracting by mask")
    outextractbymask = ExtractByMask(biomassmosaic, fc_geo)
    area_extract = ExtractByMask(hansenareamosaic30m, fc_geo)
    outPlus = outextractbymask * (Raster(hansenareamosaic30m) / 10000)
    nodata = arcpy.GetRasterProperties_management(outPlus, "ALLNODATA")
    nodata2 = nodata.getOutput(0)
    if nodata2 == "1":
        arcpy.AddMessage("passing")
    nodata3 = arcpy.GetRasterProperties_management(area_extract, "ALLNODATA")
    nodata4 = nodata3.getOutput(0)
    if nodata4 == "1":
        arcpy.AddMessage("passing")
    zstats.zonal_stats_nomask(tcdmosaic30m, area_extract, filename, "biomassweight", hansenareamosaic30m, scratch_gdb,
                              outdir,
                              column_name2, orig_fcname)
    zstats.zonal_stats_nomask(tcdmosaic30m, outPlus, filename, "biomass30m", hansenareamosaic30m, scratch_gdb, outdir,
                              column_name2, orig_fcname)


def tree_cover_extent_function(hansenareamosaic,fc_geo,scratch_gdb,maindir,shapefile,column_name2,outdir,tcdmosaic,filename,orig_fcname):
    mask = zstats.zonal_stats_mask(hansenareamosaic, fc_geo, scratch_gdb, maindir, shapefile, column_name2, outdir)
    zstats.zonal_stats(tcdmosaic, hansenareamosaic, filename, "tree_cover_extent", hansenareamosaic, mask, scratch_gdb,
                       outdir, column_name2, orig_fcname)