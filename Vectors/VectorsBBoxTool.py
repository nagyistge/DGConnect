

__author__ = 'Michael Trotter <michael.trotter@digitalglobe.com>'

from qgis.gui import *
from qgis.core import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from VectorsSettingsTool import VectorsSettingsTool
import VectorsProcessForm


class VectorsBBoxTool(QgsMapToolEmitPoint):
    """
    Tool to draw rectangles on a map and update the Ui_DGConnect GUI
    """

    new_top = pyqtSignal(str)
    new_bottom = pyqtSignal(str)
    new_left = pyqtSignal(str)
    new_right = pyqtSignal(str)

    def __init__(self, iface, bbox_ui):
        """
        Constructor
        :param iface: QGIS Interface
        :param bbox_ui: The Boundary Box GUI
        :return: BBoxTool
        """
        QgsMapToolEmitPoint.__init__(self, iface.mapCanvas())
        self.dialog_tool = None
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.rubber_band = QgsRubberBand(self.canvas, QGis.Polygon)
        self.rubber_band.setColor(QColor(250, 0, 0, 8))
        self.rubber_band.setBorderColor(QColor(250, 0, 0, 128))
        self.rubber_band.setWidth(3)
        self.reset()
        self.start_point = None
        self.end_point = None
        self.is_emitting = False
        self.wgs_84 = QgsCoordinateReferenceSystem(4326)
        self.bbox_ui = bbox_ui
        # slots for the text fields
        self.top = None
        self.bottom = None
        self.left = None
        self.right = None
        # connect the signals and slot
        self.new_top.connect(self.bbox_ui.on_new_top)
        self.new_bottom.connect(self.bbox_ui.on_new_bottom)
        self.new_left.connect(self.bbox_ui.on_new_left)
        self.new_right.connect(self.bbox_ui.on_new_right)
        # and vice versa
        self.bbox_ui.top.textChanged.connect(self.on_top)
        self.bbox_ui.bottom.textChanged.connect(self.on_bottom)
        self.bbox_ui.left.textChanged.connect(self.on_left)
        self.bbox_ui.right.textChanged.connect(self.on_right)
        # set up button
        self.bbox_ui.settings_button.clicked.connect(lambda: self.settings_button_clicked())
        self.bbox_ui.search_button.clicked.connect(lambda: self.search_button_clicked())

    def settings_button_clicked(self):
        """
        Validates and runs the settings UI if validation successful
        :return: None
        """
        # can't change settings during export
        if self.dialog_tool.is_exporting():
            self.iface.messageBar().pushMessage("Error", "Cannot alter settings while export is running.",
                                                level=QgsMessageBar.CRITICAL)
        else:
            VectorsSettingsTool(self.iface)

    def search_button_clicked(self):
        """
        Validates and runs the search if validation successful
        :return: None
        """
        # can't run search during export
        if self.dialog_tool.is_exporting():
            self.iface.messageBar().pushMessage("Error", "Cannot run search while export is running.",
                                                level=QgsMessageBar.CRITICAL)
        # can't run multiple search
        elif self.dialog_tool.is_searching():
            self.iface.messageBar().pushMessage("Error", "Cannot run a new search while a search is running.",
                                                level=QgsMessageBar.CRITICAL)
        else:
            VectorsProcessForm.search_clicked(self.bbox_ui, self.dialog_tool)

    def reset(self):
        """
        Resets the start and end points
        :return: None
        """
        self.start_point = self.end_point = None
        self.is_emitting = False
        self.rubber_band.reset()
        self.top = None
        self.bottom = None
        self.left = None
        self.right = None

    def canvasPressEvent(self, mouse_event):
        """
        Callback function for when the canvas is clicked; begins rendering the bbox
        :param mouse_event: The mouse event holding the cursor information
        :return: None
        """
        self.top = None
        self.bottom = None
        self.left = None
        self.right = None
        self.start_point = self.toMapCoordinates(mouse_event.pos())
        self.end_point = self.start_point
        self.is_emitting = True
        self.show_rect(self.start_point, self.end_point)

    def canvasReleaseEvent(self, mouse_event):
        """
        Callback function for when the mouse is release; ends rendering the bbox and updates the GUI
        :param mouse_event: The mouse event holding the cursor information
        :return: None
        """
        self.is_emitting = False
        # self.reset()

    def canvasMoveEvent(self, mouse_event):
        """
        Callback function for when the mouse is moved; updates the GUI rendering
        :param mouse_event: The mouse event holding cursor information
        :return: None
        """
        if not self.is_emitting:
            return
        self.end_point = self.toMapCoordinates(mouse_event.pos())
        self.show_rect(self.start_point, self.end_point)

    def show_rect(self, start_point, end_point):
        """
        Renders the rectangle on the canvas
        :param start_point: The start point of the rectangle
        :param end_point: The end point of the rectangle
        :return: None
        """
        self.rubber_band.reset(QGis.Polygon)
        # don't bother when rectangle == point
        if start_point.x() == end_point.x() or start_point.y() == end_point.y():
            return

        point_1 = QgsPoint(start_point.x(), start_point.y())
        point_2 = QgsPoint(start_point.x(), end_point.y())
        point_3 = QgsPoint(end_point.x(), end_point.y())
        point_4 = QgsPoint(end_point.x(), start_point.y())

        x_start_point = self.transform_point_to_wgs_84(start_point.x(), start_point.y())
        x_end_point = self.transform_point_to_wgs_84(end_point.x(), end_point.y())

        if x_start_point.y() > x_end_point.y():
            self.top = str(x_start_point.y())
            self.bottom = str(x_end_point.y())
        else:
            self.top = str(x_end_point.y())
            self.bottom = str(x_start_point.y())

        if x_start_point.x() > x_end_point.x():
            self.left = str(x_end_point.x())
            self.right = str(x_start_point.x())
        else:
            self.left = str(x_start_point.x())
            self.right = str(x_end_point.x())

        self.new_top.emit(self.top)
        self.new_bottom.emit(self.bottom)
        self.new_right.emit(self.right)
        self.new_left.emit(self.left)

        self.rubber_band.addPoint(point_1, False)
        self.rubber_band.addPoint(point_2, False)
        self.rubber_band.addPoint(point_3, False)
        self.rubber_band.addPoint(point_4, True)
        self.rubber_band.show()

    def rectangle(self):
        """
        Generates a QgsRectangle based off of the start and end points
        :return: A QgsRectangle if there's something actually there to draw (no lines/points)
        """
        # don't generate an empty rectangle
        if self.start_point is None or self.end_point is None:
            return None
        # or if rectangle == a point/line
        elif self.start_point.x() == self.end_point.x() or self.start_point.y() == self.end_point.y():
            return None
        rect = QgsRectangle(self.start_point, self.end_point)
        return rect

    def transform_point_to_wgs_84(self, x, y):
        """
        Transforms the current coordinates to WGS84
        :param x: The X coordinate (longitude)
        :param y: The Y coordinate (latitude)
        :return: A converted point in WGS84 form
        """
        point = QgsPoint(x, y)
        src_crs = self.canvas.mapRenderer().destinationCrs()
        # only transform points if necessary
        if src_crs.toWkt() != self.wgs_84.toWkt():
            x_form = QgsCoordinateTransform(src_crs, self.wgs_84)
            return x_form.transform(point)
        return point

    def transform_point_from_wgs_84(self, x, y):
        """
        Transforms the current coordinates from WGS84
        :param x: The X coordinate (longitude)
        :param y: The Y coordinate (latitude)
        :return: A converted point in WGS84 form
        """
        point = QgsPoint(x, y)
        dest_crs = self.canvas.mapRenderer().destinationCrs()
        # only transform points if necessary
        if dest_crs.toWkt() != self.wgs_84.toWkt():
            x_form = QgsCoordinateTransform(self.wgs_84, dest_crs)
            return x_form.transform(point)
        return point

    def draw_new_rect(self):
        """
        Redraws the rectangle when the coordinates are changed manually
        :return: None
        """
        # all points must be valid
        if not VectorsProcessForm.validate_bbox_fields(self.left, self.right, self.top, self.bottom, []):
            return
        # convert points from wgs84
        x_upper_left = self.transform_point_from_wgs_84(float(self.left), float(self.top))
        x_lower_right = self.transform_point_from_wgs_84(float(self.right), float(self.bottom))
        self.show_rect(x_upper_left, x_lower_right)

    @pyqtSlot(str)
    def on_top(self, new_top):
        """
        Slot for new top coordinates
        :param new_top: The new top coordinate
        :return: None
        """
        if VectorsProcessForm.validate_is_float(new_top) and (self.top is None or float(self.top) != float(new_top)):
            self.top = new_top
            self.draw_new_rect()

    @pyqtSlot(str)
    def on_bottom(self, new_bottom):
        """
        Slot for the new bottom coordinate
        :param new_bottom: The new bottom coordinate
        :return: None
        """
        if VectorsProcessForm.validate_is_float(new_bottom) and (self.bottom is None or float(self.bottom) != float(new_bottom)):
            self.bottom = new_bottom
            self.draw_new_rect()

    @pyqtSlot(str)
    def on_left(self, new_left):
        """
        Slot for the new left coordinate
        :param new_left: The new left coordinate
        :return: None
        """
        if VectorsProcessForm.validate_is_float(new_left) and (self.left is None or float(self.left) != float(new_left)):
            self.left = new_left
            self.draw_new_rect()

    @pyqtSlot(str)
    def on_right(self, new_right):
        """
        Slot for the new right coordinate
        :param new_right: The new right coordinate
        :return: None
        """
        if VectorsProcessForm.validate_is_float(new_right) and (self.right is None or float(self.right) != float(new_right)):
            self.right = new_right
            self.draw_new_rect()
