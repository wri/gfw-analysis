import argparse
import arcpy


# check out spatial analyst extension
arcpy.CheckOutExtension("Spatial")

# always overwrite outputs
arcpy.env.overwriteOutput = "TRUE"

# parse arguments sent from main script
parser = argparse.ArgumentParser(description='Helper command line script to run z stats')

parser.add_argument('--value_raster', '-v', required=True)
parser.add_argument('--zone_raster', '-z', required=True)
parser.add_argument('--z_stats_tbl', '-t', required=True)
parser.add_argument('--mask', '-m', required=True)

args = parser.parse_args()

# set workspace to in_memory, zonal stats outputs rasters, this will clean them up
arcpy.env.workspace = "in_memory"

print " "*10+"zonal stats"

# set processing extent to contextual data extent

arcpy.env.extent = args.mask

# only run zonal stats within this polygon
arcpy.env.mask = args.mask

# set snapraster to area mosaic, it is globally consistent 27m res
arcpy.env.snapRaster = args.value_raster

# run zonal stats
arcpy.gp.ZonalStatisticsAsTable_sa(args.zone_raster, "VALUE", args.value_raster, args.z_stats_tbl, "DATA", "SUM")

# cleanup memory
arcpy.env.workspace = "in_memory"
datasets = arcpy.ListDatasets()

for dataset in datasets:
    arcpy.Delete_management(dataset)