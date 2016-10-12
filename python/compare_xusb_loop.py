#!/usr/bin/env python
import xmltodict
import argparse
import time

def convert(xml_file, xml_attribs=True):
    with open(xml_file) as f:
        d = xmltodict.parse(f, xml_attribs=xml_attribs)
        return d

def diffXUSB(d1, d2):
    print(" *** Section: %s" % ('XUSB'))
    for k1 in d1['XUSB'].keys():
        print(" ****** Section: %s" % (k1))
        for k2 in d1['XUSB'][k1].keys():
            try:
                v1 = d1['XUSB'][k1][k2]['@value']
                v2 = d2['XUSB'][k1][k2]['@value']
                if v1 != v2:
                    print("      %s: %s -> %s" % (k2, v1, v2))
            except KeyError as err:
                print("      !! Key not found in new: {0}".format(err))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compares old XUSB.XML file to latest')
    parser.add_argument('xusb_xml_path', help='Path to XUSB.XML. Defaults to /c/Xaar/XUSB.XML)', default="/c/Xaar/XUSB.XML")
    args = vars(parser.parse_args())
    xusb_xml_path = args['xusb_xml_path']

    base_dict = convert(xusb_xml_path)
    refresh_ts = time.localtime()

    print("Starting loop, with base data read from %s" % xusb_xml_path)
    while True:
        cmd = raw_input(">>> ")
        cmd = cmd.strip().lower()
        if cmd == 'refresh':
            print("\nRefreshing data from base file: %s" % xusb_xml_path)
            base_dict = convert(xusb_xml_path)
            refresh_ts = time.localtime()

        elif cmd == 'compare':
            current_dict = convert(xusb_xml_path)
            diffXUSB(base_dict, current_dict)

        elif cmd == 'status':
            print("\nPath of base file: %s" % xusb_xml_path)
            print("Timestamp of last refresh: %s" % (time.strftime("[%Y_%d_%m (%a) - %H:%M:%S]", refresh_ts)))

        elif cmd == '?' or cmd == 'help':
            print("\nCommands:\n")
            print("\trefresh:      refresh base data from %s" % xusb_xml_path)
            print("\tcompare:      compare current XUSB.XML to base data")
            print("\tstatus:       status including xusb_xml_path")
            print("\thelp:         this help")
            print("\tquit:         quit program\n")

        elif cmd == 'q' or cmd == 'quit':
            break
