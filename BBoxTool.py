__author__ = 'Michael Trotter <michael.trotter@digitalglobe.com>'

from qgis.gui import *
from qgis.core import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class BBoxTool(QgsMapToolEmitPoint):
    def __init__(self, canvas, dlg):
        QgsMapToolEmitPoint.__init__(self, canvas)
        self.canvas = canvas
        self.rubber_band = QgsRubberBand(self.canvas, QGis.Polygon)
        self.rubber_band.setColor(QColor(250, 0, 0, 100))
        self.rubber_band.setWidth(1)
        self.reset()
        self.start_point = None
        self.end_point = None
        self.is_emitting = False
        self.wgs_84 = QgsCoordinateReferenceSystem(4326)
        self.ui = dlg.ui

    def reset(self):
        self.start_point = self.end_point = None
        self.is_emitting = False
        self.rubber_band.reset()

    def canvasPressEvent(self, mouse_event):
        self.start_point = self.toMapCoordinates(mouse_event.pos())
        self.end_point = self.start_point
        self.is_emitting = True
        self.show_rect(self.start_point, self.end_point)

    def canvasReleaseEvent(self, mouse_event):
        self.is_emitting = False
        r = self.rectangle()
        if r is not None:
            upper_left = self.transform_point_to_wgs_84(r.xMinimum(), r.yMaximum())
            lower_right = self.transform_point_to_wgs_84(r.xMaximum(), r.yMinimum())

            self.ui.set_top_text(str(upper_left.y()))
            self.ui.set_left_text(str(upper_left.x()))
            self.ui.set_right_text(str(lower_right.x()))
            self.ui.set_bottom_text(str(lower_right.y()))
        self.reset()

    def canvasMoveEvent(self, mouse_event):
        if not self.is_emitting:
            return
        self.end_point = self.toMapCoordinates(mouse_event.pos())
        self.show_rect(self.start_point, self.end_point)

    def show_rect(self, start_point, end_point):
        self.rubber_band.reset(QGis.Polygon)
        # don't bother when rectangle == point
        if start_point.x() == end_point.x() or start_point.y() == end_point.y():
            return

        point_1 = QgsPoint(start_point.x(), start_point.y())
        point_2 = QgsPoint(start_point.x(), end_point.y())
        point_3 = QgsPoint(end_point.x(), end_point.y())
        point_4 = QgsPoint(end_point.x(), start_point.y())

        self.rubber_band.addPoint(point_1, False)
        self.rubber_band.addPoint(point_2, False)
        self.rubber_band.addPoint(point_3, False)
        self.rubber_band.addPoint(point_4, True)
        self.rubber_band.show()

    def rectangle(self):
        # don't generate an empty rectangle
        if self.start_point is None or self.end_point is None:
            return None
        # or if rectangle == a point/line
        elif self.start_point.x() == self.end_point.x() or self.start_point.y() == self.end_point.y():
            return None
        return QgsRectangle(self.start_point, self.end_point)

    def transform_point_to_wgs_84(self, x, y):
        point = QgsPoint(x, y)
        src_crs = self.canvas.mapRenderer().destinationCrs()
        # only transform points if necessary
        if src_crs.toWkt() != self.wgs_84.toWkt():
            x_form = QgsCoordinateTransform(src_crs, self.wgs_84)
            return x_form.transform(point)
        return point