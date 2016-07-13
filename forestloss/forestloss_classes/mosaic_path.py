import os
def mosaic_path(loss_tcd_function,mosaic_location,path):
    newfunction = os.path.join(path, 'loss_tcd2.rft.xml')
    if os.path.exists(newfunction):
        os.remove(newfunction)
    mosaic1replace = "<PathName>"+mosaic_location
    mosaic2replace = "Value xsi:type='xs:string'>"+mosaic_location
    with open(loss_tcd_function) as infile, open(
            newfunction, 'w') as outfile:
        count = 0
        for line in infile:
            for i in line.split('<'):
                count += 1
                if count == 48:
                    i = i.replace(i, mosaic1replace)
                    outfile.write(i)
                if count == 61:
                    i = i.replace(i,mosaic2replace)
                    outfile.write("<"+i)
                else:
                    if i != mosaic1replace:
                        if count ==1:
                            outfile.write(i)
                        else:
                            outfile.write("<"+i)

# path = os.path.dirname(os.path.abspath(__file__))
# mosaic_path(r'C:\Users\samantha.gibbes\Documents\GitHub\sams_files\loss_tcd.rft.xml',r'C:\Users\samantha.gibbes\Documents\gis\sample_tiles\mosaics2.gdb',path)