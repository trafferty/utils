import os, sys
import glob
import argparse
import time
from datetime import date
from dateutil.relativedelta import relativedelta

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DIF Image Cleanup')
    parser.add_argument('path_to_images', default = "/media/DIF_DATA/images", help='Path to top level image folder')
    parser.add_argument('days_old_threshold', default = 30, help='Threshold age, in days, images must be to be deleted')
    parser.add_argument('wildcard_spec', default = "DispenserOpt*.png", help='Wildcard spec used to find files')
    args = parser.parse_args()

    print("Searching for image files with wildcard spec: %s (this could take a while)" % (args.wildcard_spec))
    glob_spec = "%s/**/%s" % (args.path_to_images, args.wildcard_spec)
    image_file_paths = glob.glob(glob_spec)

    if len(image_file_paths) == 0:
        print("No image files found with glob_spec: %s" % (glob_spec))
        sys.exit(1)
    else:
        print("Found %d image files" % (len(image_file_paths)))

    dt_threshold = date.today() + relativedelta(days = -1 * int(args.days_old_threshold))
    ts_threshold = time.mktime(dt_threshold.timetuple())
    print("Deleting all PNGs that are older than %s (%f)" % (dt_threshold.ctime(), ts_threshold))

    if input("Continue? [y]/n: ").lower() == 'n':
        sys.exit()

    cnt = 0
    for file_path in image_file_paths:
        ts = os.stat(file_path).st_mtime
        if ts < ts_threshold:
            p = os.path.split(file_path)
            _dir = p[0].split('/')[-1]
            file_name = p[1]
            print("Deleting file: %s/%s (%f)" %(_dir, file_name ,ts))            
            os.remove(file_path)
            cnt += 1
    print("Deleted %d image files." % (cnt))

