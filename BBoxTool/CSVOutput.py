from multiprocessing import Lock

__author__ = 'Michael Trotter <michael.trotter@digitalglobe.com>'

from datetime import datetime, timedelta

from GBDQuery import GBDOrderParams
from InsightCloudQuery import InsightCloudParams

from PyQt4.QtGui import QProgressDialog
from PyQt4.QtCore import QThreadPool, QRunnable, QObject, pyqtSlot, pyqtSignal

from GBDQuery import GBDQuery
from InsightCloudQuery import InsightCloudQuery

import os

import logging as log

INCREMENTAL_INTERVAL = 1.0

ARG_TOP = "top"
ARG_RIGHT = "right"
ARG_BOTTOM = "bottom"
ARG_LEFT = "left"

ARG_CSV_FILENAME = "csv_filename"

ARG_GBD_API_KEY = "gbd_api_key"
ARG_GBD_USERNAME = "gbd_username"
ARG_GBD_PASSWORD = "gbd_password"

ARG_INSIGHTCLOUD_USERNAME = "insightcloud_username"
ARG_INSIGHTCLOUD_PASSWORD = "insightcloud_password"

ARG_DAYS_TO_QUERY = "days_to_query"

LOCK_SUFFIX = ".lock"

class CSVOutput:
    serial_no_counter = 1

    def __init__(self, top, right, bottom, left, polygon, serial_no=None):

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
        # uvi stats
        self.num_osm = 0
        self.num_twitter = 0
        self.num_rss = 0
        # increment counter
        if serial_no:
            self.serial_no = serial_no
        else:
            self.serial_no = CSVOutput.serial_no_counter
            CSVOutput.serial_no_counter += 1

    def __str__(self):
        return "%s, %s, %s, %s, %s, \"%s\", %s, %s, %s, %s, %s, %s, %s, %s" % (self.serial_no, self.top, self.right,
                                                                               self.bottom, self.left, self.polygon,
                                                                               self.num_gbd_1_day, self.num_gbd_3_day,
                                                                               self.num_gbd_7_day, self.num_gbd_30_day,
                                                                               self.num_gbd_60_day,self.num_osm,
                                                                               self.num_twitter, self.num_rss)

    @classmethod
    def get_csv_header(cls):
        return "S No,Top,Right,Bottom,Left,Polygon,GBD 1 Day,GBD 3 Days,GBD 7 Days," \
               "GBD 30 Days,GBD 60 Days,OSM,Twitter,RSS"


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

    def __init__(self, left, top, right, bottom, csv_filename, gbd_api_key, gbd_username,
                 gbd_password, insightcloud_username, insightcloud_password, days_to_query=60):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
        self.csv_filename = csv_filename
        self.csv_lock_filename = csv_filename + LOCK_SUFFIX
        self.days_to_query = days_to_query

        self.gbd_api_key = gbd_api_key
        self.gbd_username = gbd_username
        self.gbd_password = gbd_password

        self.insightcloud_username = insightcloud_username
        self.insightcloud_password = insightcloud_password

        # create lock file
        open(self.csv_lock_filename, 'a').close()

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

        self.pool = QThreadPool()

        self.finished_submissions = False

        self.lock = Lock()

    def generate_csv(self):
        # dates
        now = datetime.now()
        end_date = now
        begin_date = now - timedelta(days=self.days_to_query)

        current_x = self.left
        current_y = self.bottom

        serial_no = 1

        for next_x in drange(self.left + INCREMENTAL_INTERVAL, self.right, INCREMENTAL_INTERVAL):
            for next_y in drange(self.bottom + INCREMENTAL_INTERVAL, self.top, INCREMENTAL_INTERVAL):

                gbd_api_key = self.gbd_api_key
                gbd_username = self.gbd_username
                gbd_password = self.gbd_password

                insightcloud_username = self.insightcloud_username
                insightcloud_password = self.insightcloud_password

                csv_runnable = CSVRunnable(gbd_api_key, gbd_username, gbd_password, insightcloud_username,
                                           insightcloud_password, serial_no, next_y, current_x, next_x,
                                           current_y, begin_date, end_date)
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
        csv_file.write(CSVOutput.get_csv_header())
        csv_file.write("\n")

        for csv_element in self.csv_elements:
            csv_file.write(str(csv_element))
            csv_file.write("\n")

        csv_file.close()
        log.info("Write complete")

        # remove lock
        if os.path.exists(self.csv_lock_filename):
            os.remove(self.csv_lock_filename)
        log.info("Removal of lock file complete")

        if self.progress_dialog:
            self.progress_dialog.close()

        self.csv_generator_object.message_complete.emit(self.csv_filename)


class CSVObject(QObject):
    new_csv_element = pyqtSignal(object)

    def __init__(self, QObject_parent=None):
        QObject.__init__(self, QObject_parent)


class CSVRunnable(QRunnable):
    def __init__(self, auth_token, gbd_username, gbd_password, insightcloud_username, insightcloud_password,
                 serial_no, top, left, right, bottom, time_begin, time_end):
        QRunnable.__init__(self)
        self.auth_token = auth_token
        self.gbd_username = gbd_username
        self.gbd_password = gbd_password
        self.insightcloud_username = insightcloud_username
        self.insightcloud_password = insightcloud_password
        self.serial_no = serial_no
        self.top = top
        self.left = left
        self.right = right
        self.bottom = bottom
        self.time_begin = time_begin
        self.time_end = time_end
        self.csv_object = CSVObject()
        
    def run(self):
        gbd_params = GBDOrderParams(top=self.top, bottom=self.bottom, left=self.left, right=self.right,
                                    time_begin=self.time_begin, time_end=self.time_end)
        insightcloud_params = InsightCloudParams(top=self.top, bottom=self.bottom, left=self.left, right=self.right,
                                                 time_begin=self.time_begin, time_end=self.time_end)
        csv_element = CSVOutput(serial_no=self.serial_no, top=self.top, left=self.left, right=self.right,
                                bottom=self.bottom,
                                polygon=gbd_params.polygon)

        gbd_query = GBDQuery(auth_token=self.auth_token, username=self.gbd_username,
                             password=self.gbd_password)
        log.info("Starting GBD Query with params: " + str(gbd_params.__dict__))
        gbd_query.log_in()
        gbd_query.hit_test_endpoint()

        # build insightcloud query
        insightcloud_query = InsightCloudQuery(username=self.insightcloud_username,
                                               password=self.insightcloud_password)
        log.info("Starting InsightCloud queries with params: " + str(insightcloud_params.__dict__))
        insightcloud_query.log_into_monocle_3()
    
        gbd_query.do_aoi_search(gbd_params, csv_element)
        log.info("GBD Query complete for args: " + str(gbd_params.__dict__))
        insightcloud_query.query_osm(insightcloud_params, csv_element)
        log.info("OSM Query complete for args: " + str(insightcloud_params.__dict__))
        insightcloud_query.query_twitter(insightcloud_params, csv_element)
        log.info("Twitter Query complete for args: " + str(insightcloud_params.__dict__))
        insightcloud_query.query_rss(insightcloud_params, csv_element)
        log.info("RSS Query complete for args: " + str(insightcloud_params.__dict__))

        self.csv_object.new_csv_element.emit(csv_element)

