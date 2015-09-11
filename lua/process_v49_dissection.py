fname = '/media/sf_data/v49_64Bins.csv'

with open(fname) as f:
    lines = f.readlines()
f.close()
print "Read in %d lines" % (len(lines))

for line in lines:
    if len(line) > 1:
        fout.write(line)
fout.close()
