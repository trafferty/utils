#from PyQt4.QtCore import *
#from PyQt4.QtGui import *
from PySide.QtCore import *
from PySide.QtGui import *

from numpy import nan
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class LinePlot(FigureCanvas):
    def __init__(self, parent):

        self.figure = Figure()
        super(LinePlot, self).__init__(self.figure)
        self.setParent(parent)
       
        self.axes = self.figure.add_axes([0.1, 0.1, .9, .8])
        self.axes.clear()
        self.axes.grid()

        [self.line_plt] = self.axes.plot([])
        self.draw()


class LinePlotWidget(QWidget):

    def __init__(self, parent=None, title=None):
        super(LinePlotWidget, self).__init__(parent)

        if title:
            self.setWindowTitle(title)
            
        self._layout = QHBoxLayout(self)
        self._line_plot = LinePlot(self)

        self._layout.addWidget(self._line_plot)

    def set_data(self, data):
        self._line_plot.line_plt.set_data(*data)
        self._line_plot.axes.relim()
        self._line_plot.axes.autoscale_view()
        self._line_plot.axes.draw_artist(self._line_plot.line_plt)
        self._line_plot.draw()
        
    @property
    def ylim(self):
        return self.ylim

    @ylim.setter
    def ylim(self, ylim):
		self._line_plot.axes.set_ylim(*ylim)

    @property
    def xlim(self):
        return self.xlim

    @xlim.setter
    def xlim(self, xlim):
		self._line_plot.axes.set_xlim(*xlim)

    @property
    def xticks(self):
        return self.xticks

    @xticks.setter
    def xticks(self, xticks):
		self._line_plot.axes.set_xticks(xticks)

    @property
    def xlabel(self):
        return self.xlabel

    @xlabel.setter
    def xlabel(self, xlabel):
		self._line_plot.axes.set_xlabel(xlabel)

    @property
    def ylabel(self):
        return self.ylabel

    @ylabel.setter
    def ylabel(self, ylabel):
		self._line_plot.axes.set_ylabel(ylabel)

    @property
    def title(self):
        return self.title

    @title.setter
    def title(self, title):
		self._line_plot.axes.set_title(title)

    def annotate(self, str, coords):
        self._line_plot.axes.annotate(str, coords,  xycoords='axes fraction')
        self._line_plot.draw()


