#!/usr/bin/env python
import xmltodict
import argparse
import time
import readline

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

class SimpleCompleter(object):
    def __init__(self, options):
        self.options = sorted(options)
        return

    def complete(self, text, state):
        response = None
        if state == 0:
            # This is the first time for this text, so build a match list.
            if text:
                self.matches = [s
                                for s in self.options
                                if s and s.startswith(text)]
            else:
                self.matches = self.options[:]

        # Return the state'th item from the match list,
        # if we have that many.
        try:
            response = self.matches[state]
        except IndexError:
            response = None
        return response

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compares old XUSB.XML file to latest')
    parser.add_argument('xusb_xml_path', help='Path to XUSB.XML. Defaults to /c/Xaar/XUSB.XML)', default="/c/Xaar/XUSB.XML")
    args = vars(parser.parse_args())
    xusb_xml_path = args['xusb_xml_path']

    base_dict = convert(xusb_xml_path)
    refresh_ts = time.localtime()

    # Register our completer function
    readline.set_completer(SimpleCompleter(['refresh', 'compare', 'status', 'help', 'quit']).complete)
    # Use the tab key for completion
    readline.parse_and_bind('tab: complete')

    print("Starting loop, with base data read from %s" % xusb_xml_path)
    while True:
        cmd = raw_input(">>> ")
        cmd = cmd.strip().lower()
        if cmd == 'refresh' or cmd == 'r':
            print("\nRefreshing data from base file: %s" % xusb_xml_path)
            base_dict = convert(xusb_xml_path)
            refresh_ts = time.localtime()

        elif cmd == 'compare' or cmd == 'c':
            current_dict = convert(xusb_xml_path)
            diffXUSB(base_dict, current_dict)
            print("-----------------------------------------")

        elif cmd == 'status' or cmd == 'st':
            print("\nPath of base file: %s" % xusb_xml_path)
            print("Timestamp of last refresh: %s" % (time.strftime("%Y_%d_%m (%a) - %H:%M:%S", refresh_ts)))

        elif cmd == '?' or cmd == 'help':
            print("\nCommands:\n")
            print("\trefresh:      refresh base data from %s" % xusb_xml_path)
            print("\tcompare:      compare current XUSB.XML to base data")
            print("\tstatus:       status including xusb_xml_path")
            print("\thelp:         this help")
            print("\tquit:         quit program\n")

        elif cmd == 'q' or cmd == 'quit':
            break
