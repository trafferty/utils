import os, sys
import glob
import argparse
import time
from datetime import date
from dateutil.relativedelta import relativedelta

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DIF Image Cleanup using folder list')
    parser.add_argument('wildcard_spec', default = "DispenserOpt*.png", help='Wildcard spec used to find files')
    args = parser.parse_args()

    folder_list = [
        "/media/DIF_DATA/images/DOE_2023-01-17_16.13.50",
        "/media/DIF_DATA/images/DOE_2023-01-19_14.23.02",
        "/media/DIF_DATA/images/DOE_2023-01-19_14.43.25",
        "/media/DIF_DATA/images/DOE_2023-01-19_14.47.20",
        "/media/DIF_DATA/images/DOE_2023-01-19_15.56.06",
        "/media/DIF_DATA/images/DOE_2023-01-20_12.29.30",
        "/media/DIF_DATA/images/DOE_2023-01-20_12.46.25",
        "/media/DIF_DATA/images/DOE_2023-01-20_13.02.23",
        "/media/DIF_DATA/images/DOE_2023-01-20_13.18.23",
        "/media/DIF_DATA/images/DOE_2023-01-20_13.32.29",
        "/media/DIF_DATA/images/DOE_2023-01-20_13.49.12",
        "/media/DIF_DATA/images/DOE_2023-01-20_14.02.34",
        "/media/DIF_DATA/images/DOE_2023-01-20_14.15.53",
        "/media/DIF_DATA/images/DOE_2023-01-20_14.29.31",
        "/media/DIF_DATA/images/DOE_2023-01-24_10.00.51",
        "/media/DIF_DATA/images/DOE_2023-01-24_10.09.48",
        "/media/DIF_DATA/images/DOE_2023-01-24_10.18.41",
        "/media/DIF_DATA/images/DOE_2023-01-24_10.27.52",
        "/media/DIF_DATA/images/DOE_2023-01-24_10.37.22",
        "/media/DIF_DATA/images/DOE_2023-01-24_10.46.15",
        "/media/DIF_DATA/images/DOE_2023-01-24_10.56.22",
        "/media/DIF_DATA/images/DOE_2023-01-24_12.38.51",
        "/media/DIF_DATA/images/DOE_2023-01-24_14.23.15",
        "/media/DIF_DATA/images/DOE_2023-01-24_14.45.57",
        "/media/DIF_DATA/images/DOE_2023-01-24_15.22.32",
        "/media/DIF_DATA/images/DOE_2023-01-24_15.32.50",
        "/media/DIF_DATA/images/DOE_2023-01-24_15.45.21",
        "/media/DIF_DATA/images/DOE_2023-01-24_15.54.49",
        "/media/DIF_DATA/images/DOE_2023-01-24_16.06.03",
        "/media/DIF_DATA/images/DOE_2023-01-24_16.16.06",
        "/media/DIF_DATA/images/DOE_2023-01-24_16.28.49",
        "/media/DIF_DATA/images/DOE_2023-01-24_17.14.37",
        "/media/DIF_DATA/images/DOE_2023-01-24_20.35.35",
        "/media/DIF_DATA/images/DOE_2023-01-25_10.54.11",
        "/media/DIF_DATA/images/DOE_2023-01-25_11.05.42",
        "/media/DIF_DATA/images/DOE_2023-01-25_11.19.49",
        "/media/DIF_DATA/images/DOE_2023-01-25_11.29.50",
        "/media/DIF_DATA/images/DOE_2023-01-25_11.40.46",
        "/media/DIF_DATA/images/DOE_2023-01-25_11.50.41",
        "/media/DIF_DATA/images/DOE_2023-01-25_12.13.17",
        "/media/DIF_DATA/images/DOE_2023-01-25_12.23.11",
        "/media/DIF_DATA/images/DOE_2023-01-25_12.42.56",
        "/media/DIF_DATA/images/DOE_2023-01-25_12.53.14",
        "/media/DIF_DATA/images/DOE_2023-01-25_13.06.20",
        "/media/DIF_DATA/images/DOE_2023-01-25_16.33.29",
        "/media/DIF_DATA/images/DOE_2023-01-26_09.40.01",
        "/media/DIF_DATA/images/DOE_2023-01-26_09.42.33",
        "/media/DIF_DATA/images/DOE_2023-01-27_10.07.56",
        "/media/DIF_DATA/images/DOE_2023-02-03_10.31.17",
        "/media/DIF_DATA/images/DOE_2023-02-09_14.54.04",
        "/media/DIF_DATA/images/DOE_2023-02-10_13.07.27",
        "/media/DIF_DATA/images/DOE_2023-02-10_14.12.55",
        "/media/DIF_DATA/images/DOE_2023-02-16_20.21.24",
        "/media/DIF_DATA/images/DOE_2023-02-17_08.31.47",
        "/media/DIF_DATA/images/DOE_2023-03-01_11.57.35",
        "/media/DIF_DATA/images/DOE_2023-03-01_15.54.14",
        "/media/DIF_DATA/images/DOE_2023-03-01_16.44.06",
        "/media/DIF_DATA/images/DOE_2023-03-02_16.32.15",
        "/media/DIF_DATA/images/DOE_2023-03-02_16.39.57",
        "/media/DIF_DATA/images/DOE_2023-03-02_16.47.14",
        "/media/DIF_DATA/images/DOE_2023-03-02_16.56.16",
        "/media/DIF_DATA/images/DOE_2023-03-02_20.47.29",
        "/media/DIF_DATA/images/DOE_2023-03-03_15.21.01",
        "/media/DIF_DATA/images/DOE_2023-03-03_20.19.49",
        "/media/DIF_DATA/images/DOE_2023-03-06_15.27.20",
        "/media/DIF_DATA/images/DOE_2023-03-06_15.48.43",
        "/media/DIF_DATA/images/DOE_2023-03-06_15.55.19",
        "/media/DIF_DATA/images/DOE_2023-04-06_16.07.41",
        "/media/DIF_DATA/images/DOE_2023-04-06_16.11.11"
    ]

    for folder in folder_list:
        print("-----------------------------------------------------------------------------")
        print("Searching " + folder + " with wildcard spec: %s (this could take a while)" % (args.wildcard_spec))
        glob_spec = "%s/%s" % (folder, args.wildcard_spec)
        image_file_paths = glob.glob(glob_spec)

        if len(image_file_paths) == 0:
            print("No image files found with glob_spec: %s" % (glob_spec))
        else:
            print("Found %d image files" % (len(image_file_paths)))

        cnt = 0
        for file_path in image_file_paths:
            p = os.path.split(file_path)
            _dir = p[0].split('/')[-1]
            file_name = p[1]
            print("Deleting file: %s/%s" %(_dir, file_name))            
            os.remove(file_path)
            cnt += 1
        print("Deleted %d image files." % (cnt))

