import arcpy


def jointable(maintable, table_to_join, outfiledlist):

    if maintable == table_to_join:
        arcpy.AddMessage('passing on {}'.format(table_to_join))
        pass

    else:
        arcpy.AddMessage("joining {} to {}".format(maintable, table_to_join))
        arcpy.JoinField_management(table_to_join, "uID", maintable, "uID", outfiledlist)


def fieldslist(table, filename):
    if table == filename+"_emissions":

        fieldlist = "emissions_tcl_area_m2"

    elif table == filename+"_biomassweight":
        fieldlist = "MgBiomass;MgBiomassPerHa"

    elif table == filename+"_tree_cover_extent" or table == filename+"_forest_loss" :
        fieldlist  = "emissions_tcl_area_m2"

    else:
        arcpy.AddMessage("not found")
        arcpy.AddMessage("{}, {}".format(table, filename))
    return fieldlist


def main(merged_dir, filename):

    arcpy.env.workspace = merged_dir

    table_list = arcpy.ListTables(filename + "*")

    maintable = table_list[0]

    for table in table_list:

        fields = fieldslist(table,filename)
        arcpy.AddMessage(fields)
        jointable(maintable, table, fields)