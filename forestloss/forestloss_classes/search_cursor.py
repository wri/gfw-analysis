import arcpy
import datetime


def search_cursor():
    with arcpy.da.SearchCursor(shapefile, ("Shape@", "FC_NAME", column_name)) as cursor:
        feature_count = 0
        for row in cursor:
            fctime = datetime.datetime.now()
            feature_count += 1
            arcpy.AddMessage("processing feature {} out of {}".format(feature_count, total_features))
            fc_geo = row[0]
            column_name2 = row[1]
            orig_fcname = row[2]
            # removed the overwrite option for now
            if forest_loss == "true" and carbon_emissions == "false":
                option_list.append("forest_loss")
                lossyr = os.path.join(mosaic_location, 'loss')
                tcdmosaic = os.path.join(mosaic_location, 'tcd')
                hansenareamosaic = os.path.join(mosaic_location, 'area')
                analysis.forest_loss_function(hansenareamosaic, fc_geo, scratch_gdb, maindir, shapefile, column_name2,
                                              outdir, lossyr, filename, orig_fcname)

            if tree_cover_extent == "true":
                option_list.append("tree_cover_extent")
                hansenareamosaic = os.path.join(mosaic_location, 'area')
                tcdmosaic = os.path.join(mosaic_location, 'tcd')
                analysis.tree_cover_extent_function(hansenareamosaic, fc_geo, scratch_gdb, maindir, shapefile,
                                                    column_name2, outdir, tcdmosaic, filename, orig_fcname)

            if carbon_emissions == "true":
                option_list.append("emissions")
                lossyr = os.path.join(mosaic_location, 'loss')
                hansenareamosaic = os.path.join(mosaic_location, 'area')
                emissions_mosaic = os.path.join(mosaic_location, 'emissions')
                analysis.carbon_emissions_function(hansenareamosaic, emissions_mosaic, fc_geo,
                                                   scratch_gdb, maindir, shapefile, column_name2,
                                                   outdir, lossyr, filename, orig_fcname)

                # if biomass_weight == "true":
                #     option_list.append("biomassweight")
                #     biomassmosaic = os.path.join(mosaic_location, 'biomass')
                #     analysis.biomass_weight_function(hansenareamosaic30m,biomassmosaic,fc_geo,tcdmosaic30m,filename,scratch_gdb,outdir,column_name2,orig_fcname)
                #

            arcpy.AddMessage("     " + str(datetime.datetime.now() - fctime))

        del cursor