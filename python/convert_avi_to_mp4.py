#!/usr/bin/env python
import argparse
import signal
import glob
import os
import ffmpy

class convert_avi_to_mp4(file_list):

def main():
    done = False
    def sigint_handler(signal, frame):
        global done
        print( "\nShutting down...")
        done = True
    signal.signal(signal.SIGINT, sigint_handler)


  files = glob.glob(args.path, recursive=True)

  if len(files) > 0:



if __name__ == '__main__':
  main()