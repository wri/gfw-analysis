import os
def analysisinfo(maindir, shapefile, filename, column_name, threshold, forest_loss, carbon_emissions,
    tree_cover_extent, biomass_weight, summarize_by, summarize_file, summarize_by_columnname, mosaic_location):
    analysisinfo = os.path.join(maindir, "analysisinfo.txt")
    if os.path.exists(analysisinfo):
        os.remove(analysisinfo)
    text = open(analysisinfo, 'w')
    text.write("shapefile: {}".format(shapefile)
               + "\nfile name: {}".format(filename)
               + "\ncolumn name: {}".format(column_name)
               + "\nmosaic location: {}".format(mosaic_location)
               + "\nthreshold: {}".format(threshold)
               + "\nforest loss: {}".format(forest_loss)
               + "\ncarbon emissions: {}".format(carbon_emissions)
               + "\ntree cover extent: {}".format(tree_cover_extent)
               + "\nbiomass weight: {}".format(biomass_weight)
               + "\nsummarize by: {}".format(summarize_by)
               + "\nsummarize file: {}".format(summarize_file)
               + "\nsummarize by column name: {}".format(summarize_by_columnname))
    text.close()