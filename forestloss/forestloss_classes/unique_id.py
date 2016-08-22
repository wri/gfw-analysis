import arcpy
import correct_rownames as cor

def unique_id(dataset,column):
    arcpy.AddField_management(dataset, "FC_NAME", "TEXT")
    exp = "name({})".format('!'+column+'!')
    # arcpy.CalculateField_management(in_table=dataset, field="FC_NAME", expression=exp,
    print "calculating fc_name"
    arcpy.CalculateField_management(in_table=dataset, field="FC_NAME", expression=exp, expression_type="PYTHON_9.3", code_block="""def name(fc):\n    try:\n        fc= fc.encode("utf-8", "ignore")\n        fc= unicode(fc,"ascii", "ignore")\n        if str(fc)[0].isdigit():\n            fc= "x"+str(fc)\n    except:\n        if str(fc)[0].isdigit():\n            fc= "x"+str(fc)\n    bad = [" ","-",'/', ':', '*', '?', '"', '<', '>', '|','.',"_"]\n    for char in bad:\n        fc= fc.replace(char,"_")\n    return fc""")