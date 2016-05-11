#!/usr/bin/env python

'''

  see http://docs.python.org/2/howto/argparse.html

'''

import sys
import argparse

def parse_drink_ids(present_drink_ids, order_file):
    drink_ids = present_drink_ids.split(',')
    for idx, drink_id in enumerate(drink_ids):
        print "present_drink_id(%d): %s" % (idx, drink_id.strip())

def build_drink_order(drinks_file, order_file, need_lid):
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This is just a test program to test out the argparse module')
    if False:
        parser.add_argument('-d', '--drinks_file', type=str, default="", help='JSON file listing the drinks in the order')
        parser.add_argument('-p', '--present_drink_ids', type=str, default="", help='Drink ID(s) of drink you want to present. multi-drinkIDs should be comma separated')
        parser.add_argument('-o', '--order_file', type=str, help='Output order file', required=True)
        parser.add_argument('--lids', dest='need_lid', action='store_true')
        parser.add_argument('--no-lids', dest='need_lid', action='store_false')
        parser.set_defaults(need_lid=True)
        args = parser.parse_args()

        if len(args.drinks_file):
            build_drink_order(args.drinks_file, args.order_file, args.need_lid)
        elif len(args.present_drink_ids):
            parse_drink_ids(args.present_drink_ids, args.order_file)

    #### Positional Args:
    else:
        parser.add_argument("echo")
        args = parser.parse_args()
        print args.echo
###############
# from canserver2:
    p = OptionParser()
    p.add_option("-p","--port", type="int",action="store",dest="port",
                 help="set udp port to PORT", metavar="PORT", default=6590)
    p.add_option("-f", "--file", dest="filename",default="candata",
                 help="write output to FILE", metavar="FILE")
    p.add_option("-v", "--version", default=False, action="store_true", 
                 dest="printversion", help="Print Version and exit")
    p.add_option("-q", "--quiet",
                 action="store_false", dest="verbose", default=True,
                 help="don't print status messages to stdout")
    p.add_option("-s", "--statusfile", dest="sfilename", default="canstatus.log",
                 help="status file", metavar="SFILE")
    p.add_option("-i", "--ip", dest="host",type="string",default="localhost",
                 help="host ip address dotted decimal")
    p.add_option("-l", "--logfile", dest="logfilename",
                 help="log file")
                
    (options,args) = p.parse_args()
