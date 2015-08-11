__author__ = 'Michael Trotter <michael.trotter@digitalglobe.com>'

from datetime import datetime, timedelta

from GBDQuery import GBDOrderParams
from InsightCloudQuery import InsightCloudParams

from PyQt4.QtGui import QProgressDialog, QMessageBox
from PyQt4.QtCore import Qt, QObject, pyqtSlot



from GBDQuery import GBDQuery
from InsightCloudQuery import InsightCloudQuery

from multiprocessing import Pool

import logging as log

INCREMENTAL_INTERVAL = 1.0

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


class CSVGenerator(QObject):
    @pyqtSlot()
    def on_canceled(self):
        self.pool.terminate()

    def __init__(self, left, top, right, bottom, csv_filename, ui, days_to_query=60, qparent=None):
        QObject.__init__(self, qparent)
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
        self.csv_filename = csv_filename
        self.ui = ui
        self.days_to_query = days_to_query
        # throw up a progress dialog
        min_progress = 0
        max_progress = ((self.right - self.left) * (self.top - self.bottom)) / INCREMENTAL_INTERVAL
        self.current_progress = min_progress

        self.progress_dialog = QProgressDialog("Building up CSV file", "Abort", int(min_progress), int(max_progress),
                                               None)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setValue(int(self.current_progress))
        self.progress_dialog.show()
        self.progress_dialog.canceled.connect(self.on_canceled)

        self.csv_elements = []

        self.pool = Pool(processes=100)

    def generate_csv(self):
        # dates
        now = datetime.now()
        end_date = now
        begin_date = now - timedelta(days=self.days_to_query)

        current_x = self.left
        current_y = self.bottom

        results = []

        serial_no = 1

        for next_x in drange(self.left + INCREMENTAL_INTERVAL, self.right, INCREMENTAL_INTERVAL):
            for next_y in drange(self.bottom + INCREMENTAL_INTERVAL, self.top, INCREMENTAL_INTERVAL):

                gbd_api_key = self.ui.gbd_api_key.text()
                gbd_username = self.ui.gbd_username.text()
                gbd_password = self.ui.gbd_password.text()

                insightcloud_username = self.ui.insightcloud_username.text()
                insightcloud_password = self.ui.insightcloud_password.text()

                result = self.pool.apply_async(run, (gbd_api_key, gbd_username, gbd_password, insightcloud_username,
                                                insightcloud_password, serial_no, next_y, current_x, next_x,
                                                current_y, begin_date, end_date), callback=self.callback)
                results.append(result)

                serial_no += 1
                current_y = next_y

            current_y = self.bottom
            current_x = next_x

        for result in results:
            result.wait()

        self.csv_elements.sort(key=lambda element: element.serial_no)

        csv_file = open(self.csv_filename, 'w')
        # write the header
        csv_file.write(CSVOutput.get_csv_header())
        csv_file.write("\n")

        for csv_element in self.csv_elements:
            csv_file.write(str(csv_element))
            csv_file.write("\n")

        csv_file.close()
        self.progress_dialog.close()
        message = QMessageBox()
        message.information(None, "CSV Write Complete", "CSV output to " + self.csv_filename + " is complete")

    def callback(self, csv_element):
        log.info("Received: " + str(csv_element))
        if csv_element:
            self.csv_elements.append(csv_element)
            self.current_progress += INCREMENTAL_INTERVAL
            self.progress_dialog.setValue((int(self.current_progress)))

def run(auth_token, gbd_username, gbd_password, insightcloud_username, insightcloud_password,
        serial_no, top, left, right, bottom, time_begin, time_end):
    gbd_params = GBDOrderParams(top=top, bottom=bottom, left=left, right=right,
                                time_begin=time_begin, time_end=time_end)
    insightcloud_params = InsightCloudParams(top=top, bottom=bottom, left=left, right=right,
                                             time_begin=time_begin, time_end=time_end)
    csv_element = CSVOutput(serial_no=serial_no, top=top, left=left, right=right, bottom=bottom,
                            polygon=gbd_params.polygon)

    gbd_query = GBDQuery(auth_token=auth_token, username=gbd_username,
                         password=gbd_password)
    gbd_query.log_in()
    gbd_query.hit_test_endpoint()

    # build insightcloud query
    insightcloud_query = InsightCloudQuery(username=insightcloud_username,
                                           password=insightcloud_password)
    insightcloud_query.log_into_monocle_3()

    gbd_query.do_aoi_search(gbd_params, csv_element)
    insightcloud_query.query_osm(insightcloud_params, csv_element)
    insightcloud_query.query_twitter(insightcloud_params, csv_element)
    insightcloud_query.query_rss(insightcloud_params, csv_element)

    return csv_element

