import arcpy


def jointable(maintable, table_to_join, outfiledlist):

    if maintable == table_to_join:

        pass

    else:
        arcpy.AddMessage("joining {} to {}".format(maintable, table_to_join))
        arcpy.AddMessage("{}".format(outfiledlist))
        arcpy.JoinField_management(maintable, "uID", table_to_join, "uID", outfiledlist)


def fieldslist(table, filename):


    if table == filename+"_emissions":
        fieldlist = "emissions_tcl_area_m2"

    elif table == filename+"_biomassweight":
        fieldlist = "MgBiomass;MgBiomassPerHa"


    elif table == filename+"_tree_cover_extent":
        fieldlist  = "tree_cover_extent_tcl_area_m2"
    elif table == filename + "_forest_loss":
        fieldlist = "forest_loss_tcl_area_m2"
    else:
        arcpy.AddMessage("not found")
        arcpy.AddMessage("{}, {}".format(table, filename))
    return fieldlist


def main(merged_dir, filename):

    arcpy.env.workspace = merged_dir

    table_list = arcpy.ListTables(filename + "*")
    arcpy.AddMessage(table_list)
    maintable = table_list[0]

    for table in table_list:

        fields = fieldslist(table,filename)
        arcpy.AddMessage(fields)
        jointable(maintable, table, fields)

# main(r'U:\sgibbes\test\final.gdb', "test3")