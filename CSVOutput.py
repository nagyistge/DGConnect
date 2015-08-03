__author__ = 'Michael Trotter <michael.trotter@digitalglobe.com>'

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
        return "Serial Number,Top,Right,Bottom,Left,Polygon,Num GBD (Age <= 1 Days Old)," \
               "Num GBD (1 < Age <= 3 Days Old),Num GBD (3 < Age <= 7 Days Old)," \
               "Num GBD (7 < Age <= 30 Days Old), Num GBD (30 < Age <= 60 Days Old)"


