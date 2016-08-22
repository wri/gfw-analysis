import arcpy

def jointable(maintable,jointable,outfiledlist):
    if maintable == jointable:
        pass
    else:
        arcpy.AddMessage("joining {} to {}".format(maintable,jointable))
        arcpy.JoinField_management(maintable, "uID", jointable, "uID",outfiledlist )

def fieldslist(table,filename):
    if table == filename+"_biomassweight":
        fieldlist = "MgBiomass;MgBiomassPerHa"
    if table == filename+"_tree_cover_extent" or table == filename+"_forest_loss" :
        fieldlist  = "SUM"
    return fieldlist

def main(merged_dir,filename):
    arcpy.env.workspace = merged_dir

    area = arcpy.ListTables("*" + filename + "*")
    maintable = area[0]

    for table in area:
        print table
        if table == filename+"_biomass_max" or table == filename+"_biomass_min" or table == filename + "_biomass":
            pass
        else:
            fields = fieldslist(table,filename)
            print table
            print fields
            jointable(maintable,table,fields)