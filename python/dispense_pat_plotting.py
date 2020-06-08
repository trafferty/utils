import argparse
import numpy as np
from matplotlib import pyplot as plt

def plot_pattern(pat_file, rows, cols):
    pat = np.fromfile(pat_file, dtype='bool').reshape(rows,cols)

    plt.figure(figsize = (200,60))
    plt.imshow(pat, cmap='gray')
    plt.show()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Dispense Pattern Plotter')
    parser.add_argument('-r', '--rows', type=int, default=1352, help='Data Rows', required=False)
    parser.add_argument('-c', '--cols', type=int, default=856,  help='Data Cols', required=False)
    parser.add_argument('pattern_file')
    args = parser.parse_args()

    plot_pattern(args.pattern_file, args.rows, args.cols)