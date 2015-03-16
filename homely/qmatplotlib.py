# standard libraries
pass
# third party libraries
from PyQt4 import QtGui, QtCore
import numpy
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
# first party libraries
pass

class QImageCanvas(FigureCanvas):

    def __init__(self, a, *args, **kwargs):
        figure = self.figure = Figure(frameon=True)
        figure.patch.set_alpha(0.0)
        self.axis = figure.add_subplot(111)
        self.axis.get_xaxis().set_visible(False)
        self.axis.get_yaxis().set_visible(False)
        figure.tight_layout()
        super(QImageCanvas, self).__init__(figure)
        self.imshow(a, *args, **kwargs)

    def imshow(self, a, *args, **kwargs):
        self.axis.imshow(a, *args, **kwargs)
        self.draw()