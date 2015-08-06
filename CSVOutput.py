__author__ = 'Michael Trotter <michael.trotter@digitalglobe.com>'

from datetime import datetime, timedelta

from GBDQuery import GBDOrderParams
from InsightCloudQuery import InsightCloudParams

from PyQt4.QtGui import QProgressDialog, QMessageBox

INCREMENTAL_INTERVAL = 1.0

class CSVOutput:
    serial_no_counter = 1

    def __init__(self, top, right, bottom, left, polygon):
        self.serial_no = CSVOutput.serial_no_counter
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

def generate_csv(left, top, right, bottom, gbd_query, insightcloud_query, csv_filename, days_to_query=60):
    csv_file = open(csv_filename, 'w')
    # write the header
    csv_file.write(CSVOutput.get_csv_header())
    csv_file.write("\n")

    # dates
    now = datetime.now()
    end_date = now
    begin_date = now - timedelta(days=days_to_query)

    current_x = left
    current_y = bottom

    # throw up a progress dialog
    min_progress = 0
    max_progress = right * top - left*bottom
    current_progress = min_progress

    progress_dialog = QProgressDialog("Building up CSV file", "Abort", int(min_progress), int(max_progress), None)
    progress_dialog.setValue(int(current_progress))

    for next_x in drange(left + INCREMENTAL_INTERVAL, right, INCREMENTAL_INTERVAL):
        if progress_dialog.wasCanceled():
            break
        for next_y in drange(bottom + INCREMENTAL_INTERVAL, top, INCREMENTAL_INTERVAL):
            gbd_params = GBDOrderParams(top=next_y, bottom=current_y, left=current_x, right=next_x,
                                        time_begin=begin_date, time_end=end_date)

            csv_element = CSVOutput(top=next_y, right=next_x, bottom=current_y, left=current_x,
                                    polygon=gbd_params.polygon)

            gbd_query.do_aoi_search(gbd_params, csv_element)

            insightcloud_params = InsightCloudParams(top=next_y, bottom=current_y, left=current_x, right=next_x,
                                                     time_begin=begin_date, time_end=end_date)
            insightcloud_query.query_osm(insightcloud_params, csv_element)
            insightcloud_query.query_twitter(insightcloud_params, csv_element)
            insightcloud_query.query_rss(insightcloud_params, csv_element)

            csv_file.write(str(csv_element))
            csv_file.write("\n")

            # update progress bar
            current_progress += INCREMENTAL_INTERVAL
            progress_dialog.setValue(int(current_progress))
            if progress_dialog.wasCanceled():
                break

            current_y = next_y
        current_y = bottom
        current_x = next_x

    csv_file.close()

    message = QMessageBox()
    message.information(None, "CSV Write Complete", "CSV output to " + csv_filename + " is complete")
