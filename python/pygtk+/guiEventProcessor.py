import time
import urllib2

class MyException(Exception):
    pass

class GUIEventProcessor(object):
    """ Generic GUI Event Processor object """

    def __init__(self, log_file, data_log_uri_base):
        self.log_file = log_file
        self.data_log_uri_base = data_log_uri_base

    def eventCB(self, event):
        self.doLog('Default handler for event: %s' % (event))

    def doLog(self, log_msg):
        msg = "%s: %s" % (time.strftime("[%Y_%d_%m (%a) - %H:%M:%S]", time.localtime()), log_msg)
        print msg
        if len(self.log_file) > 0: 
            f = open(self.log_file, 'a')
            f.write(msg + '\n')
            f.close()

    def dataLog(self, data):
        if len(self.data_log_uri_base) > 0: 
            try:
                rep = urllib2.urlopen("%s%s" % (self.data_log_uri_base, data)).read()
                self.doLog("Logging data: %s. reply: %s" % ( data, rep))
            except:
                self.doLog("Error connecting to data logger; skipping post")
