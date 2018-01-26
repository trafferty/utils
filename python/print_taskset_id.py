#!/usr/bin/env python

import argparse
import taskset_ids as ts

if __name__ == "__main__":
    '''
    print_taskset_id.py 
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("taskset_id")
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true')
    parser.set_defaults(verbose=False)
    
    args = parser.parse_args()

    if args.taskset_id:
        print ts.stringifyTasksetID(int(args.taskset_id), args.verbose)
    else:
        parser.print_help()
        sys.exit(1)