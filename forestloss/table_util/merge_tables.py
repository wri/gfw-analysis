import arcpy
import os


def merge_tables(outdir, option, filename, merged_dir, threshold):
    tcd_year_table = os.path.join(os.path.dirname(os.path.abspath(__file__)), "2001_2019_tcd_year_codes.dbf")
    arcpy.env.workspace = outdir
    table_list = arcpy.ListTables("*" + filename + "_" + option)
    if len(table_list) == 0:
        arcpy.AddMessage("no tables")
        table = False
    else:
        table = True
        final_merge_table = os.path.join(merged_dir, filename + "_" + option)

        if len(table_list) > 1:
            arcpy.Merge_management(table_list, final_merge_table)
        else:
            table = os.path.join(outdir,table_list[0])
            arcpy.Copy_management(table,final_merge_table)

        if option == "biomassweight" or option ==  "area only":
            dict =  {20:"no loss"}
        else:
            # delete rows where valye <15 and add Year field and update rows
            dict = {20:"no loss",21:"y2001",22:"y2002",23:"y2003",24:"y2004",25:"y2005",26:"y2006",27:"y2007",28:"y2008",29:"y2009",30:"y2010",31:"y2011",32:"y2012",33:"y2013",34:"y2014",35:"y2015",36:"y2016",37:"y2017",38:"y2018",39:"y2019",40:"y2020"}

        arcpy.AddField_management(final_merge_table, "Year", "TEXT", "", "" ,10)
        with arcpy.da.UpdateCursor(final_merge_table, ["Value", "Year"]) as cursor:
            for row in cursor:
                if row[0] < 20:
                    cursor.deleteRow()
                for v in range(20,40):
                    if row[0] == v:
                        row[1] = dict[v]
                        cursor.updateRow(row)
            del cursor

        # join tcd/year code table to output table and calculate clean year column
        arcpy.JoinField_management(final_merge_table, "Value", tcd_year_table, "f1", ["year","tcd"])

        arcpy.CalculateField_management(final_merge_table,"Year","!year_1!", "PYTHON_9.3", "")
        arcpy.DeleteField_management(final_merge_table, "year_1")
        if option == "forest_loss" or option == "carbon_emissions":
            with arcpy.da.UpdateCursor(final_merge_table, ["Year"]) as cursor:
                for row in cursor:
                    if row[0] == "0":
                        row[0]= "no loss"
                        cursor.updateRow(row)
                    if len(row[0]) == 1:
                        row[0] = "200" + row[0]
                        cursor.updateRow(row)
                    if len(row[0]) == 2:
                        row[0] = "20" + row[0]
                        cursor.updateRow(row)
                del cursor
        else:
            arcpy.DeleteField_management(final_merge_table, "Year")
        if threshold != "all":
            exp =  "> "+str(threshold)
            arcpy.CalculateField_management(final_merge_table, "tcd", '"'+exp+'"', "PYTHON_9.3", "")
        arcpy.AddField_management(final_merge_table,option+"_tcl_area_m2","DOUBLE")
        arcpy.CalculateField_management(final_merge_table,option+"_tcl_area_m2","!SUM!","PYTHON_9.3")
    return table