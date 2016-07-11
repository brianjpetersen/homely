# standard libraries
pass
# third party libraries
from qtpy import QtGui, QtCore, QtWidgets
import numpy
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# first party libraries
pass


class QImageCanvas(FigureCanvas):

    def __init__(self, a, *args, **kwargs):
        figure = self.figure = Figure(frameon=True)
        super(QImageCanvas, self).__init__(figure)
        figure.patch.set_alpha(0.0)

        #self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        #self.updateGeometry()

        axis = self.axis = figure.add_subplot(111)
        axis.get_xaxis().set_visible(False)
        axis.get_yaxis().set_visible(False)
        #super(QImageCanvas, self).__init__(figure)
        self.a = a
        self.image = self.imshow(a, *args, **kwargs)
        figure.tight_layout()

    def imshow(self, a, *args, **kwargs):
        self.get_renderer().clear()
        self.axis.clear()
        self.image = self.axis.imshow(a, *args, **kwargs)
        self.draw()
        return self.image

    def contourf(self, a, *args, **kwargs):
        self.get_renderer().clear()
        self.axis.clear()
        self.image = self.axis.contourf(a, *args, **kwargs)
        self.draw()

    def set_clim(self, cmin, cmax):
        self.image.set_clim(cmin, cmax)
        self.draw()

    def save(self, *args, **kwargs):
        self.figure.savefig(*args, **kwargs)
