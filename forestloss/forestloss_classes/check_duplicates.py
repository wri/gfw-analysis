import arcpy
from itertools import groupby

def check_dups(dataset,column):
    fclist = []
    with arcpy.da.SearchCursor(dataset, ("Shape@", column)) as cursor:
        for row in cursor:
            fc_geo = row[0]
            fc_name = row[1]
            if not fc_name in fclist:
                fclist.append(fc_name)
            else:
                raise Exception("you have duplicates in your chosen field name, please choose a different one")

