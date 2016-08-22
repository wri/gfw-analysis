import arcpy
arcpy.CheckOutExtension("Spatial")
import datetime

def calc_area(geom, tcd):
    '''
    Calculate loss area for a specific geometry and tree cover desity threashold
    :param geom: arcpy.geometry
    :param tcd: short
    :return: dict
    '''

    #Make mosaic layer from loss year, using predefined processing template for TCD
    in_mosaic_dataset = r"C:\Users\Thomas.Maschler\Documents\GFW\speedtest.gdb\lossyear"
    arcpy.MakeMosaicLayer_management (in_mosaic_dataset, "annual_loss", processing_template="tcd_{}".format(tcd))
    #arcpy.MakeMosaicLayer_management (in_mosaic_dataset, "annual_loss", processing_template="8bit")

    #Make mosaic layer from area raster, making sure it is served out as long int
    in_mosaic_dataset = r"C:\Users\Thomas.Maschler\Documents\GFW\speedtest.gdb\area"
    arcpy.MakeMosaicLayer_management (in_mosaic_dataset, "area", processing_template="times1000")

    pixel_size = 0.00025
    arcpy.env.extent = geom.extent
    #arcpy.env.mask = geom
    arcpy.CopyFeatures_management(geom, "in_memory/mask")
    arcpy.env.mask = "in_memory/mask"

    arcpy.env.overwriteOutput = True
    arcpy.gp.TabulateArea_sa("area", "Value", "annual_loss", "Value", "in_memory/area_pivot", pixel_size)

    fields = arcpy.ListFields("in_memory/area_pivot", field_type="Double")

    cur = arcpy.SearchCursor("in_memory/area_pivot")
    out = dict()
    for row in cur:
        area = (row.getValue("VALUE")/1000)
        for field in fields:
            field_area = row.getValue(field.name) * 1/(pixel_size*pixel_size) * area
            if field.name in out.keys():
                out[field.name] += field_area
            else:
                out[field.name] = field_area



    return out

print "start"
fc = r"C:\Users\Thomas.Maschler\Downloads\CIRAD\test.shp"
for row in arcpy.da.SearchCursor(fc, ["SHAPE@"]):
    start = datetime.datetime.now()
    print calc_area(row[0], 30)
    print datetime.datetime.now() - start
