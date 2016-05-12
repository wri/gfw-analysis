__author__ = 'sgibbes'
import os
import arcpy
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = "TRUE"

glad_mosaic = r'D:\Users\sgibbes\glad_alerts\weighted_alerts\mosaic.gdb\peru'
remapfunction = r'D:\Users\sgibbes\GitHub\gfw-analysis\remapfunction_glad.rft.xml'
important_places_grid =r'D:\Users\sgibbes\glad_alerts\weighted_alerts\fishnet_10km_peru.shp'
remaptable = r'D:\Users\sgibbes\glad_alerts\weighted_alerts\julian_days_remap52.dbf'
outdir = r'D:\Users\sgibbes\glad_alerts\weighted_alerts\peru\outdir.gdb'
final_dir = r'D:\Users\sgibbes\glad_alerts\weighted_alerts\peru\final.gdb'

def remapmosaic(weekcolumn,remaptable,remapfunction):
    arcpy.AddMessage("removing potential existing function from mosaic")
    # remove potential existing function
    arcpy.EditRasterFunction_management(glad_mosaic, "EDIT_MOSAIC_DATASET",
    "REMOVE", remapfunction)

    # copying remap values from week column into the "output" column for remap table

    arcpy.AddMessage("updating remap table column")
    rows = arcpy.UpdateCursor(remaptable)
    for row in rows:
        output = row.getValue(weekcolumn)
        row.week = output
        rows.updateRow(row)
    del rows
    arcpy.EditRasterFunction_management(
     glad_mosaic, "EDIT_MOSAIC_DATASET",
     "INSERT", remapfunction)

for week_num in range(1,53):
    weekcolumn = "week" + str(week_num)
    print weekcolumn
    remapmosaic(weekcolumn,remaptable,remapfunction)
    z_stats_tbl = os.path.join(outdir, weekcolumn)
    print z_stats_tbl
    if arcpy.Exists(z_stats_tbl):
        print "already exists"
    else:
        print "running zonal stats"
        arcpy.gp.ZonalStatisticsAsTable_sa(important_places_grid, "FID_1", glad_mosaic, z_stats_tbl, "DATA", "SUM")
        print "adding week column to table"
        arcpy.AddField_management(z_stats_tbl, "weeknumber", "TEXT")
        arcpy.CalculateField_management(z_stats_tbl, "weeknumber", "'" + weekcolumn + "'", "PYTHON_9.3")

# merge tables
print "merging week tables"
arcpy.env.workspace = outdir
table_list = arcpy.ListTables()
print table_list
final_merge_table = os.path.join(final_dir, "glad_alerts")
arcpy.Merge_management(table_list, final_merge_table)


pivottable = os.path.join(final_dir, "glad_alerts_pivot")
print "creating pivot table"
arcpy.management.PivotTable(final_merge_table, "FID_1", "weeknumber", "SUM", pivottable)

