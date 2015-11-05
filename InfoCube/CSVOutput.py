from multiprocessing import Lock

__author__ = 'Michael Trotter <michael.trotter@digitalglobe.com>'

from datetime import datetime, timedelta

from InfoCubeGBDQuery import GBDOrderParams
from InfoCubeInsightCloudQuery import InsightCloudParams

from PyQt4.QtGui import QProgressDialog
from PyQt4.QtCore import QThreadPool, QRunnable, QObject, pyqtSlot, pyqtSignal

from InfoCubeGBDQuery import GBDQuery
from InfoCubeInsightCloudQuery import InsightCloudQuery

import os

import logging as log

INCREMENTAL_INTERVAL = 1.0

ARG_TOP = "top"
ARG_RIGHT = "right"
ARG_BOTTOM = "bottom"
ARG_LEFT = "left"

ARG_CSV_FILENAME = "csv_filename"

ARG_USERNAME = "username"
ARG_PASSWORD = "password"

ARG_DAYS_TO_QUERY = "days_to_query"

class CSVOutput:
    serial_no_counter = 1

    def __init__(self, top, right, bottom, left, polygon, vector_header_dict, serial_no=None):

        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left
        self.polygon = polygon
        # gbd stats
        self.num_gbd_1_day = 0
        self.num_gbd_3_day = 0
        self.num_gbd_7_day = 0
        self.num_gbd_30_day = 0
        self.num_gbd_60_day = 0
        # vector stats
        self.vector_dict = {}
        self.vector_header_dict = vector_header_dict
        # increment counter
        if serial_no:
            self.serial_no = serial_no
        else:
            self.serial_no = CSVOutput.serial_no_counter
            CSVOutput.serial_no_counter += 1

    def __str__(self):
        text = "%s, %s, %s, %s, %s, \"%s\", %s, %s, %s, %s, %s," % (self.serial_no, self.top, self.right,
                                                                               self.bottom, self.left, self.polygon,
                                                                               self.num_gbd_1_day, self.num_gbd_3_day,
                                                                               self.num_gbd_7_day, self.num_gbd_30_day,
                                                                               self.num_gbd_60_day)
        for term in self.vector_header_dict:
            text = text + str(self.vector_dict.get(term) or "0") + ","
        text = text[:-1]
        return text

    @classmethod
    def get_csv_header(cls):
        return "S No,Top,Right,Bottom,Left,Polygon,GBD 1 Day,GBD 3 Days,GBD 7 Days," \
               "GBD 30 Days,GBD 60 Days,"


def drange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step

class CSVGeneratorObject(QObject):
    message_complete = pyqtSignal(str)

    def __init__(self, generator, QObject_parent=None):
        QObject.__init__(self, QObject_parent)
        self.generator = generator

    @pyqtSlot(object)
    def callback(self, csv_element):
        log.info("Received: " + str(csv_element))
        if csv_element:
            self.generator.csv_elements.append(csv_element)
            self.generator.current_progress += INCREMENTAL_INTERVAL
            if self.generator.progress_dialog:
                self.generator.progress_dialog.setValue((int(self.generator.current_progress)))
        thread_count = 0
        with self.generator.lock:
            thread_count = self.generator.pool.activeThreadCount()
        if self.generator.finished_submissions and thread_count == 0:
            self.generator.on_completion()



class CSVGenerator:

    def __init__(self, left, top, right, bottom, csv_filename, username, password, client_id, client_secret, days_to_query=60):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
        self.csv_filename = csv_filename
        self.days_to_query = days_to_query
        self.begin_date = None
        self.end_date = None

        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret

        # throw up a progress dialog
        min_progress = 0.0
        max_progress = ((self.right - self.left) / INCREMENTAL_INTERVAL) * \
                       ((self.top - self.bottom) / INCREMENTAL_INTERVAL)
        self.current_progress = min_progress

        self.progress_dialog = QProgressDialog("Building up CSV file", "Abort", int(min_progress), int(max_progress),
                                               None)
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setWindowTitle("CSV Output")
        self.progress_dialog.setLabelText("Building up CSV file")
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.setValue(0)
        self.progress_dialog.show()

        self.csv_elements = []

        self.csv_generator_object = CSVGeneratorObject(self)
        
        self.vector_header_dict = {}

        self.pool = QThreadPool()

        self.finished_submissions = False

        self.lock = Lock()

    def generate_csv(self):
        # dates
        now = datetime.now()
        self.end_date = now
        self.begin_date = now - timedelta(days=self.days_to_query)

        current_x = self.left
        current_y = self.bottom

        serial_no = 1
        
        # get header dict
        insightcloud_query = InsightCloudQuery(username=self.username, password=self.password, client_id=self.client_id, client_secret=self.client_secret)
        insightcloud_query.log_in()
        insightcloud_params = InsightCloudParams(top=self.top, bottom=self.bottom, left=self.left, right=self.right, time_begin=self.begin_date, time_end=self.end_date)
        header_result = insightcloud_query.get_vector_result(insightcloud_params)
        self.vector_header_dict = insightcloud_query.get_vector_data(header_result)

        for next_x in drange(self.left + INCREMENTAL_INTERVAL, self.right, INCREMENTAL_INTERVAL):
            for next_y in drange(self.bottom + INCREMENTAL_INTERVAL, self.top, INCREMENTAL_INTERVAL):

                username = self.username
                password = self.password
                client_id = self.client_id
                client_secret = self.client_secret
                
                csv_runnable = CSVRunnable(username, password, client_id, client_secret,
                                           serial_no, next_y, current_x, next_x,
                                           current_y, self.begin_date, self.end_date, self.vector_header_dict)
                csv_runnable.csv_object.new_csv_element.connect(self.csv_generator_object.callback)
                self.pool.start(csv_runnable)

                serial_no += 1
                current_y = next_y

            current_y = self.bottom
            current_x = next_x

        self.finished_submissions = True

    def on_completion(self):
        self.csv_elements.sort(key=lambda element: element.serial_no)
        log.info("Sort complete")
        # write file
        csv_file = open(self.csv_filename, 'w')
        
        # write the header
        header = CSVOutput.get_csv_header()
        if self.vector_header_dict:
            for term in self.vector_header_dict:
                header = header + str(term) + ","
        header = header[:-1]
        csv_file.write(header)
        csv_file.write("\n")

        for csv_element in self.csv_elements:
            csv_file.write(str(csv_element))
            csv_file.write("\n")

        csv_file.close()
        log.info("Write complete")

        if self.progress_dialog:
            self.progress_dialog.close()

        self.csv_generator_object.message_complete.emit(self.csv_filename)


class CSVObject(QObject):
    new_csv_element = pyqtSignal(object)

    def __init__(self, QObject_parent=None):
        QObject.__init__(self, QObject_parent)


class CSVRunnable(QRunnable):
    def __init__(self, client_id, client_secret, username, password,
                 serial_no, top, left, right, bottom, time_begin, time_end, vector_header_dict):
        QRunnable.__init__(self)
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
        self.serial_no = serial_no
        self.top = top
        self.left = left
        self.right = right
        self.bottom = bottom
        self.time_begin = time_begin
        self.time_end = time_end
        self.vector_header_dict = vector_header_dict
        self.csv_object = CSVObject()
        
    def run(self):
        gbd_params = GBDOrderParams(top=self.top, bottom=self.bottom, left=self.left, right=self.right,
                                    time_begin=self.time_begin, time_end=self.time_end)
        insightcloud_params = InsightCloudParams(top=self.top, bottom=self.bottom, left=self.left, right=self.right,
                                                 time_begin=self.time_begin, time_end=self.time_end)
        csv_element = CSVOutput(serial_no=self.serial_no, top=self.top, left=self.left, right=self.right,
                                bottom=self.bottom, polygon=gbd_params.polygon, vector_header_dict=self.vector_header_dict)

        gbd_query = GBDQuery(username=self.username, password=self.password, client_id=self.client_id, client_secret=self.client_secret)
        log.info("Starting GBD Query with params: " + str(gbd_params.__dict__))
        gbd_query.log_in()

        # build insightcloud query
        insightcloud_query = InsightCloudQuery(username=self.username, password=self.password, client_id=self.client_id, client_secret=self.client_secret)
        log.info("Starting InsightCloud queries with params: " + str(insightcloud_params.__dict__))
        insightcloud_query.log_in()
    
        gbd_query.do_aoi_search(gbd_params, csv_element)
        log.info("GBD Query complete for args: " + str(gbd_params.__dict__))
        insightcloud_query.query_vector(insightcloud_params, csv_element)
        log.info("Vector Query complete for args: " + str(insightcloud_params.__dict__))

        self.csv_object.new_csv_element.emit(csv_element)

