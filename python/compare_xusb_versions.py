#!/usr/bin/env python
import xmltodict
import argparse

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
    parser.add_argument('-o','--old', help='Old (previously saved) XUSB.XML file', required=True)
    parser.add_argument('-n','--new', help='New (current) XUSB.XML. Defaults to /c/Xaar/XUSB.XML)', required=False, default="/c/Xaar/XUSB.XML")
    args = vars(parser.parse_args())

    print args
    d1 = convert(args['old'])
    d2 = convert(args['new'])

    diffXUSB(d1, d2)
