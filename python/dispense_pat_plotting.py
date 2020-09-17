import argparse
import numpy as np
import glob
from matplotlib import pyplot as plt


def get_row_start(file_idx, flip_heads, offset): 
    return((file_idx%2)^flip_heads)*offset

def get_bin(x, n): 
    return format(x, 'b').zfill(n)

def read_file_to_pat(pat_file, bits_per_col=8):

    dat = open(pat_file, 'rb').read()
    pat = np.zeros(len(dat)*bits_per_col)

    for idx, d in enumerate(dat):
        if d > 0:
            pat_offset = idx * bits_per_col
            bs = get_bin(d, bits_per_col)
            for idx2, b in enumerate(bs):
                if b is '1':
                    pat[pat_offset + idx2] = 1
    return pat

def plot_pattern_old(pat_file, rows, cols):
    pat = np.fromfile(pat_file, dtype='bool').reshape(rows,cols)

    #plt.figure(figsize = (200,60))
    plt.figure(figsize = (20,10))
    plt.imshow(pat, cmap='gray')
    plt.show()

def plot_pattern(pat_file, rows, cols):
    bits_per_col=8
    pat = read_file_to_pat(pat_file, bits_per_col)
    plt.figure(figsize = (10,4))
    plt.imshow(pat.reshape(rows,cols*bits_per_col), cmap='gray')
    plt.show()

def plot_pattern_multiXX(pat_file_list, rows, cols, num_heads, bits_per_col=8, flip_heads=False):
    max_passes = 2
    rows_per_head = rows * max_passes
    total_rows = rows_per_head * num_heads
    total_cols = cols * bits_per_col

    pat = np.zeros(total_rows*total_cols).reshape(total_rows, total_cols)   
    print("pattern shape: ", pat.shape)  

    for file_idx, pat_file in enumerate(sorted(pat_file_list)):
        print("  Processing swathe file: ", pat_file)  
        #swathe = open(pat_file, 'rb').read()
        swathe = np.fromfile(pat_file, dtype=np.int8)
        print("  swathe shape: ", swathe.shape) 

        if file_idx % 2 == 1:
            swathe = np.fliplr(swathe)

        row_start = get_row_start(file_idx, flip_heads, rows_per_head)
        print("  row_start: ", row_start) 

        for idx, val in enumerate(swathe):
            if val > 0:
                print(val)
                r = idx//cols
                c = idx - (r*cols)

                # adjust for head flip
                r += row_start
                # adjust for odd/even swathe
                r += file_idx%2

                bs = get_bin(val, bits_per_col)
                for idx2, b in enumerate(bs):
                    if b is '1':
                        c_sub = c + idx2
                        pat[r, c_sub] = 1
        print("  idx: ", idx) 
        print("---------------------------------------")


    plt.figure(figsize = (10,(4*num_heads)))
    plt.imshow(pat, cmap='gray')
    plt.show()


def plot_pattern_multi(pat_file_list, rows, cols, num_heads, bits_per_col=8, flip_heads=False):
    max_passes = 2
    rows_per_head = rows * max_passes
    total_rows = rows_per_head * num_heads
    total_cols = cols * bits_per_col

    pat = np.zeros(total_rows*total_cols).reshape(total_rows, total_cols)   
    print("pattern shape: ", pat.shape)  

    for file_idx, pat_file in enumerate(sorted(pat_file_list)):
        print("  Processing swathe file: ", pat_file)  
        #swathe = open(pat_file, 'rb').read()
        swathe = np.fromfile(pat_file, dtype=np.int8).reshape(rows,cols)
        print("  swathe shape: ", swathe.shape) 

        if file_idx % 2 == 0:
            swathe = np.fliplr(swathe)

        row_start = get_row_start(file_idx, flip_heads, rows_per_head)
        print("  row_start: ", row_start) 

        for row in range(rows):
            for col in range(cols):
                val = swathe[row,col]
                if val > 0:
                    print(val)
                    r = row
                    c = col

                    # adjust for head flip
                    r += row_start
                    # adjust for odd/even swathe
                    r += file_idx%2

                    bs = get_bin(val, bits_per_col)
                    for idx2, b in enumerate(bs):
                        if b is '1':
                            c_sub = c + idx2
                            pat[r, c_sub] = 1

        print("---------------------------------------")


    plt.figure(figsize = (10,(4*num_heads)))
    plt.imshow(pat, cmap='gray')
    plt.show()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Dispense Pattern Plotter')
    parser.add_argument('-r', '--rows', type=int, default=1352, help='Data Rows', required=False)
    parser.add_argument('-c', '--cols', type=int, default=856,  help='Data Cols', required=False)
    parser.add_argument('-n', '--num_heads', type=int, default=1,  help='num heads (assume side-by-side)', required=False)
    parser.add_argument('-b', '--bits_per_col', type=int, default=8,  help='bits per column (default=8)', required=False)
    parser.add_argument('-f', '--flip_heads', type=bool, default=False,  help='Flip heads? (default=False)', required=False)
    parser.add_argument('glob_spec')
    args = parser.parse_args()

    pat_file_list = glob.glob(args.glob_spec)
    print(f"Found %d files: " % (len(pat_file_list)))
    for idx, f in enumerate(pat_file_list):
        print(" [%d] %s" % (idx, f))

    if len(pat_file_list) == 1:
        plot_pattern(pat_file_list[0], args.rows, args.cols)
    else:
        plot_pattern_multi(pat_file_list, args.rows, args.cols, args.num_heads, args.bits_per_col, args.flip_heads)
