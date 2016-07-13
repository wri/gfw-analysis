import arcpy
def correct_rownames(fc_name):
    fc_name = fc_name.encode("utf-8", "ignore")
    fc_name = unicode(fc_name, "ascii", "ignore")
    if str(fc_name)[0].isdigit():
        fc_name = "x" + str(fc_name)
    bad = [" ", "-", '/', ':', '*', '?', '"', '<', '>', '|', '.', "_"]
    for char in bad:
        fc_name = fc_name.replace(char, "_")
    return fc_name

# Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
# The following inputs are layers or table views: "test"
