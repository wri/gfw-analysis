
import arcpy
import os

def dirs(maindir):
    scratch_gdb = os.path.join(maindir, "scratch.gdb")
    if not os.path.exists(scratch_gdb):
        arcpy.CreateFileGDB_management(maindir, "scratch.gdb")
    arcpy.env.scratchWorkspace = scratch_gdb
    error_text_file = os.path.join(maindir, 'errors.txt')
    outdir = os.path.join(maindir, "temp.gdb")
    if not os.path.exists(outdir):
        arcpy.CreateFileGDB_management(maindir, "temp.gdb")
    merged_dir = os.path.join(maindir, "final.gdb")
    if not os.path.exists(merged_dir):
        arcpy.CreateFileGDB_management(maindir, "final.gdb")
    return scratch_gdb,outdir,merged_dir
