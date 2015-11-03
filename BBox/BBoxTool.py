__author__ = 'Michael Trotter <michael.trotter@digitalglobe.com>'

from qgis.gui import *
from qgis.core import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from ..Settings import SettingsOps


VALIDATION_LAT_LOWER = -90.0
VALIDATION_LAT_UPPER = 90.0
VALIDATION_LONG_LOWER = -180.0
VALIDATION_LONG_UPPER = 180.0

VALIDATION_AOI_DIFF = 10


class BBoxTool(QgsMapToolEmitPoint):
    """
    Tool to draw rectangles on a map and update the Ui_DGConnect GUI
    """

    new_top = pyqtSignal(str)
    new_bottom = pyqtSignal(str)
    new_left = pyqtSignal(str)
    new_right = pyqtSignal(str)
    released = pyqtSignal(str, str, str, str)

    def __init__(self, iface):
        """
        Constructor
        :param iface: QGIS Interface
        :return: BBoxTool
        """
        QgsMapToolEmitPoint.__init__(self, iface.mapCanvas())
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
        # slots for the text fields
        self.top = None
        self.bottom = None
        self.left = None
        self.right = None
        
    def validate_bbox(self, errors):
        """
        Validates the boundary box fields (top, left, right, bottom)
        :param errors: The list of errors occurred thus far
        :return: None
        """
        return validate_bbox_fields(left=self.left, right=self.right, top=self.top, bottom=self.bottom, errors=errors)

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
        self.released.emit(self.top, self.bottom, self.left, self.right)
        self.iface.mapCanvas().unsetMapTool(self)

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
        src_crs = self.canvas.mapSettings().destinationCrs()
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
        dest_crs = self.canvas.mapSettings().destinationCrs()
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
        if not validate_bbox_fields(self.left, self.right, self.top, self.bottom, []):
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
        if SettingsOps.validate_is_float(new_top) and (self.top is None or float(self.top) != float(new_top)):
            self.top = new_top
            self.draw_new_rect()

    @pyqtSlot(str)
    def on_bottom(self, new_bottom):
        """
        Slot for the new bottom coordinate
        :param new_bottom: The new bottom coordinate
        :return: None
        """
        if SettingsOps.validate_is_float(new_bottom) and (self.bottom is None or float(self.bottom) != float(new_bottom)):
            self.bottom = new_bottom
            self.draw_new_rect()

    @pyqtSlot(str)
    def on_left(self, new_left):
        """
        Slot for the new left coordinate
        :param new_left: The new left coordinate
        :return: None
        """
        if SettingsOps.validate_is_float(new_left) and (self.left is None or float(self.left) != float(new_left)):
            self.left = new_left
            self.draw_new_rect()

    @pyqtSlot(str)
    def on_right(self, new_right):
        """
        Slot for the new right coordinate
        :param new_right: The new right coordinate
        :return: None
        """
        if SettingsOps.validate_is_float(new_right) and (self.right is None or float(self.right) != float(new_right)):
            self.right = new_right
            self.draw_new_rect()


def validate_bbox_fields(left, right, top, bottom, errors):
    """
    Validates the boundary box fields (top, left, right, bottom)
    :param left: The left value of the box
    :param right: The right value of the box
    :param top: The top value of the box
    :param bottom: The bottom value of the box
    :param errors: THe list of error occurred thus far
    :return: True if there are no errors; False otherwise
    """
    is_left_valid = validate_bbox_field(left, "Left", VALIDATION_LONG_LOWER, VALIDATION_LONG_UPPER, errors)
    is_right_valid = validate_bbox_field(right, "Right", VALIDATION_LONG_LOWER, VALIDATION_LONG_UPPER, errors)
    is_top_valid = validate_bbox_field(top, "Top", VALIDATION_LAT_LOWER, VALIDATION_LAT_UPPER, errors)
    is_bottom_valid = validate_bbox_field(bottom, "Bottom", VALIDATION_LAT_LOWER, VALIDATION_LAT_UPPER, errors)

    is_valid = is_left_valid and is_right_valid and is_top_valid and is_bottom_valid

    left_float = float(left)
    right_float = float(right)
    bottom_float = float(bottom)
    top_float = float(top)
    # check that right > left
    if is_left_valid and is_right_valid and left_float > right_float:
        errors.append("Provided left (%s) is greater than right (%s)" % (left, right))
        is_valid = False
    elif abs(right_float - left_float) > VALIDATION_AOI_DIFF:
        errors.append("Provided left (%s) is greater than 10 degrees away from right (%s)" % (left, right))
        is_valid = False

    if is_top_valid and is_bottom_valid and bottom_float > top_float:
        errors.append("Provided bottom (%s) is greater than top (%s)" % (bottom, top))
        is_valid = False
    elif abs(top_float - bottom_float) > VALIDATION_AOI_DIFF:
        errors.append("Provided top (%s) is greater than 10 degrees away from bottom (%s)" % (top, bottom))
        is_valid = False

    return is_valid

def validate_bbox_field(field_value, field_name, lower_bound, upper_bound, errors):
    """
    Performs value validation on a given box field
    :param field_value: The text value of the field
    :param field_name: The name of the field
    :param lower_bound: The lower bound of values for the field
    :param upper_bound: The upper bound of values for the field
    :param errors: List of errors that have occurred so far
    :return: True if there are no errors; False otherwise
    """
    is_field_valid = True
    if field_value is None or len(field_value) <= 0:
        is_field_valid = False
        errors.append("No %s provided." % field_name)
    else:
        # try parsing field value
        try:
            float_value = float(field_value)
            if float_value < lower_bound:
                is_field_valid = False
                errors.append("Provided %s (%s) is below threshold of %s."  % (field_name, field_value, lower_bound))
            elif float_value > upper_bound:
                is_field_valid = False
                errors.append("Provided %s (%s) is above threshold of %s." % (field_name, field_value, upper_bound))
        except ValueError, e:
            is_field_valid = False
            errors.append("Provided %s (%s) is not a number" % (field_name, field_value))
    return is_field_valid
