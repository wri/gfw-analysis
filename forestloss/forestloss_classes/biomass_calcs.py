import arcpy

def calcbiomass(merged_dir, filename):
    arcpy.env.workspace = merged_dir
    area = arcpy.ListTables("*" + filename + "_forest_loss")[0]
    biomass = arcpy.ListTables("*" + filename + "_biomass")[0]

    arcpy.AddField_management(biomass, "L", "DOUBLE")
    arcpy.CalculateField_management(biomass, "L", "!SUM!", "PYTHON_9.3", "")
    arcpy.DeleteField_management(biomass, "SUM")


    arcpy.AddField_management(biomass, "uID", "TEXT")
    arcpy.CalculateField_management(biomass, "uID", """!ID!+"_"+str( !Value!)""", "PYTHON_9.3", "")

    arcpy.AddField_management(area, "uID", "TEXT")
    arcpy.CalculateField_management(area, "uID", """!ID!+"_"+str( !Value!)""", "PYTHON_9.3", "")

    arcpy.JoinField_management(area, "uID", biomass, "uID", ["L"])

    arcpy.AddField_management(area, "Emis_mtc02", "DOUBLE")

    arcpy.CalculateField_management(area, "Emis_mtc02",
                                    "((!SUM!/10000)/!COUNT! * (!L!/1000000))*.5*3.67",
                                    "PYTHON_9.3", "")
def avgbiomass(merged_dir, filename):
    # average the min/max biomass tables
    arcpy.env.workspace = merged_dir
    area = arcpy.ListTables("*" + filename + "_forest_loss")[0]
    max = arcpy.ListTables("*" + filename + "_biomass_max")[0]
    min = arcpy.ListTables("*" + filename + "_biomass_min")[0]

    arcpy.AddField_management(max, "L", "DOUBLE")
    arcpy.CalculateField_management(max, "L", "!SUM!", "PYTHON_9.3", "")
    arcpy.DeleteField_management(max, "SUM")

    arcpy.AddField_management(max, "uID", "TEXT")
    arcpy.CalculateField_management(max, "uID", """!ID!+"_"+str( !Value!)""", "PYTHON_9.3", "")

    arcpy.AddField_management(min, "S", "DOUBLE")
    arcpy.CalculateField_management(min, "S", "!SUM!", "PYTHON_9.3", "")
    arcpy.DeleteField_management(min, "SUM")

    arcpy.AddField_management(min, "uID", "TEXT")
    arcpy.CalculateField_management(min, "uID", """!ID!+"_"+str( !Value!)""", "PYTHON_9.3", "")

    arcpy.AddField_management(area, "uID", "TEXT")
    arcpy.CalculateField_management(area, "uID", """!ID!+"_"+str( !Value!)""", "PYTHON_9.3", "")

    arcpy.JoinField_management(area, "uID", max, "uID", ["L"])
    arcpy.JoinField_management(area, "uID", min, "uID", ["S"])
    arcpy.AddField_management(area, "Emis_mtc02", "DOUBLE")
    # arcpy.AddField_management(area,"emissions_TgBiomass","DOUBLE")
    # arcpy.CalculateField_management(area, "emissions_TgBiomass",
    #                                 "((!SUM!/10000)/!COUNT! * (!L!/1000000)+ (!SUM!/10000)/!COUNT! * ( !S!/1000000)/2)", "PYTHON_9.3", "")
    arcpy.CalculateField_management(area, "Emis_mtc02",
                                    "((!SUM!/10000)/!COUNT! * (!L!/1000000)+ (!SUM!/10000)/!COUNT! * ( !S!/1000000)/2)*.5*3.67",
                                    "PYTHON_9.3", "")


def biomass30m_calcs(merged_dir, filename):
    arcpy.env.workspace = merged_dir
    area30 = arcpy.ListTables("*" + filename + "_biomassweight")[0]
    biomass30 = arcpy.ListTables("*" + filename + "_biomass30m")[0]
    arcpy.AddField_management(biomass30, "MgBiomass", "DOUBLE")
    arcpy.CalculateField_management(biomass30, "MgBiomass", "!SUM!", "PYTHON_9.3", "")
    arcpy.DeleteField_management(biomass30, "SUM")

    arcpy.AddField_management(biomass30, "uID", "TEXT")
    arcpy.CalculateField_management(biomass30, "uID", """!ID!+"_"+str( !Value!)""", "PYTHON_9.3", "")

    arcpy.AddField_management(area30, "uID", "TEXT")
    arcpy.CalculateField_management(area30, "uID", """!ID!+"_"+str( !Value!)""", "PYTHON_9.3", "")

    arcpy.JoinField_management(area30, "uID", biomass30, "uID", ["MgBiomass"])
    arcpy.AddField_management(area30, "MgBiomassPerHa", "DOUBLE")
    arcpy.AddMessage("calculating MgBiomassPerHa")
    arcpy.CalculateField_management(area30, "MgBiomassPerHa", "!MgBiomass!/(!SUM!/10000)", "PYTHON_9.3", "")

    fields_to_delete = ("Value", "COUNT", "AREA")
    for f in fields_to_delete:
        arcpy.DeleteField_management(area30, f)
    arcpy.Delete_management(biomass30)