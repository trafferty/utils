from gi.repository import Gtk
import threading

class ImgAPO_GUI(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="imgAPO Control")

        self.eventCallbackList = []

        # self.start_btn = Gtk.Button(label="Start")
        # self.start_btn.connect("clicked", self.btnStart_clicked)
        # self.add(self.start_btn)
        # self.show_all()
        # self.connect("delete-event", Gtk.main_quit)  # connects quit button in app toolbar

        builder = Gtk.Builder()
        builder.add_from_file("imgAPO_GUI.glade")
        window = builder.get_object("main_window")

        handlers = {
            "gtk_main_quit"   : Gtk.main_quit,
            "btnStart_clicked": self.btnStart_clicked,
            "btnStop_clicked" : self.btnStop_clicked,
            "btnLoop_clicked" : self.btnLoop_clicked,
            "btnQuit_clicked" : Gtk.main_quit
        }
        builder.connect_signals(handlers)

        window.show_all()

        # worker = threading.Thread(target=self.run)
        # worker.setDaemon(1)
        # worker.start()

    def run(self):
        Gtk.main()
        print "Main loop quiting..."
        self.sendCallback( dict(event='quit') )

    def addCallback(self, callbackFuncion):
        self.eventCallbackList.append(callbackFuncion)
        print "callback added"
        callbackFuncion( dict(event='ack') )

    def sendCallback(self, cb_dict):
        for eventCallback in self.eventCallbackList:
            eventCallback(cb_dict)

    def btnStart_clicked(self, widget):
        self.sendCallback( dict(event='start') )

    def btnStop_clicked(self, widget):
        self.sendCallback( dict(event='stop') )

    def btnLoop_clicked(self, widget):
        self.sendCallback( dict(event='loop') )
