__author__ = 'Michael Trotter <michael.trotter@digitalglobe.com>'

from datetime import datetime, timedelta

from GBDQuery import GBDOrderParams
from InsightCloudQuery import InsightCloudParams

from PyQt4.QtGui import QProgressDialog, QMessageBox, QApplication

import sys
import getopt

from GBDQuery import GBDQuery
from InsightCloudQuery import InsightCloudQuery

from multiprocessing import Pool

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

USAGE = "CSVOutput.py --" + ARG_TOP + " <" + ARG_TOP + "> --" + ARG_RIGHT + " <" + ARG_RIGHT + "> --" + ARG_BOTTOM +\
        " <" + ARG_BOTTOM + "> --" + ARG_LEFT + " <" + ARG_LEFT +"> --" + ARG_CSV_FILENAME + " <" + ARG_CSV_FILENAME +\
        "> --" + ARG_GBD_API_KEY + " <" + ARG_GBD_API_KEY + "> --" + ARG_GBD_USERNAME + " <" + ARG_GBD_USERNAME + \
        "> --" + ARG_GBD_PASSWORD + " <" + ARG_GBD_PASSWORD +"> --" + ARG_INSIGHTCLOUD_USERNAME + \
        " <" + ARG_INSIGHTCLOUD_USERNAME +"> --" + ARG_INSIGHTCLOUD_PASSWORD + " <" + ARG_INSIGHTCLOUD_PASSWORD +"> " \
        "--" + ARG_DAYS_TO_QUERY + " <" + ARG_DAYS_TO_QUERY + ">"

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


class CSVGenerator(QApplication):

    def __init__(self, left, top, right, bottom, csv_filename, gbd_api_key, gbd_username,
                 gbd_password, insightcloud_username, insightcloud_password, days_to_query=60):
        QApplication.__init__(self, [])
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
        max_progress = ((self.right - self.left) * (self.top - self.bottom)) / INCREMENTAL_INTERVAL
        self.current_progress = min_progress

        self.progress_dialog = QProgressDialog("Building up CSV file", "Abort", int(min_progress), int(max_progress),
                                               None)
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setWindowTitle("CSV Output")
        self.progress_dialog.setLabelText("Building up CSV file")
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.setModal(True)
        self.progress_dialog.setValue(int(self.current_progress))
        self.progress_dialog.forceShow()
        # hack to force it to render
        self.progress_dialog.setValue(int(self.current_progress))

        self.csv_elements = []

        self.pool = Pool()

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

                gbd_api_key = self.gbd_api_key
                gbd_username = self.gbd_username
                gbd_password = self.gbd_password

                insightcloud_username = self.insightcloud_username
                insightcloud_password = self.insightcloud_password

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

        # write file
        csv_file = open(self.csv_filename, 'w')
        # write the header
        csv_file.write(CSVOutput.get_csv_header())
        csv_file.write("\n")

        for csv_element in self.csv_elements:
            csv_file.write(str(csv_element))
            csv_file.write("\n")

        csv_file.close()

        # remove lock
        os.remove(self.csv_lock_filename)

        self.progress_dialog.close()
        message = QMessageBox()
        message.setModal(True)
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

def main(argv):
    '''
    Debug settings

    import sys
    sys.path.insert(1, '/home/mtrotter/pycharm-debug.egg')
    import pydevd
    pydevd.settrace('localhost', port=53100, stdoutToServer=True, stderrToServer=True)
    '''

    left = None
    right = None
    top = None
    bottom = None

    csv_filename = None

    gbd_api_key = None
    gbd_username = None
    gbd_password = None

    insightcloud_username = None
    insightcloud_password = None

    days_to_query = None

    try:
        opts, args = getopt.getopt(argv, "h", [ARG_LEFT + "=", ARG_RIGHT + "=", ARG_TOP + "=",
                                               ARG_BOTTOM + "=", ARG_CSV_FILENAME + "=", ARG_GBD_API_KEY + "=",
                                               ARG_GBD_USERNAME + "=", ARG_GBD_PASSWORD + "=",
                                               ARG_INSIGHTCLOUD_USERNAME + "=", ARG_INSIGHTCLOUD_PASSWORD + "=",
                                               ARG_DAYS_TO_QUERY + "="])
    except getopt.GetoptError, e:
        print("Received error: " + str(e))
        print(USAGE)
        sys.exit(2)

    for o, a in opts:
        if o == '-h':
            print(USAGE)
            sys.exit(0)
        elif o == "--" + ARG_LEFT:
            left = float(a)
        elif o == "--" + ARG_RIGHT:
            right = float(a)
        elif o == "--" + ARG_BOTTOM:
            bottom = float(a)
        elif o == "--" + ARG_TOP:
            top = float(a)
        elif o == "--" + ARG_CSV_FILENAME:
            csv_filename = a
        elif o == "--" + ARG_GBD_API_KEY:
            gbd_api_key = a
        elif o == "--" + ARG_GBD_USERNAME:
            gbd_username = a
        elif o == "--" + ARG_GBD_PASSWORD:
            gbd_password = a
        elif o == "--" + ARG_INSIGHTCLOUD_USERNAME:
            insightcloud_username = a
        elif o == "--" + ARG_INSIGHTCLOUD_PASSWORD:
            insightcloud_password = a
        elif o == "--" + ARG_DAYS_TO_QUERY:
            days_to_query = int(a)

    generator = CSVGenerator(left=left, top=top, right=right, bottom=bottom, csv_filename=csv_filename,
                             gbd_api_key=gbd_api_key, gbd_username=gbd_username, gbd_password=gbd_password,
                             insightcloud_username=insightcloud_username, insightcloud_password=insightcloud_password,
                             days_to_query=days_to_query)
    generator.generate_csv()

if __name__ == '__main__':
    main(sys.argv[1:])
