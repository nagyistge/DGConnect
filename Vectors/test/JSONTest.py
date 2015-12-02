__author__ = 'mtrotter'

import unittest
from VectorsQuery import VectorQuery

class ProcessJSONTest(unittest.TestCase):
    def testGlobalSourcesJson(self):
        json_string = """\
        {"data":[{"name":"OSM","count":374842982},{"name":"GDELT","count":11839504},{"name":"Gazeteer","count":11332448},{"name":"HGIS","count":2837808},{"name":"Flickr - Gnip","count":411595},{"name":"Instagram - Gnip","count":333118},{"name":"Vector REST API","count":213521},{"name":"SETD","count":137353},{"name":"DG Car Counting","count":123918},{"name":"IIP-SA-Raster","count":89475},{"name":"Tomnod","count":69339},{"name":"ACLED","count":31802},{"name":"Anthrometer","count":19548},{"name":"VK - Gnip","count":15295},{"name":"GBD","count":6035},{"name":"MASS Service","count":15},{"name":"Tom Ruegger","count":3},{"name":"Test","count":2},{"name":"GoPro mounted on an eagle","count":1},{"name":"Mermaid","count":1}],"shards":1290}
                """
        query = VectorQuery(None, None, None, None)
        data = query.process_json_data(json_string)
        self.assertTrue(len(data) == 20)

        self.assertTrue('ACLED' in data)
        self.assertEquals(31802, data['ACLED'])

        self.assertTrue('Anthrometer' in data)
        self.assertEquals(19548, data['Anthrometer'])

        self.assertTrue('DG Car Counting' in data)
        self.assertEquals(123918, data['DG Car Counting'])

        self.assertTrue('Flickr - Gnip' in data)
        self.assertEquals(411595, data['Flickr - Gnip'])

        self.assertTrue('GBD' in data)
        self.assertEquals(6035, data['GBD'])

        self.assertTrue('GDELT' in data)
        self.assertEquals(11839504, data['GDELT'])

        self.assertTrue('Gazeteer' in data)
        self.assertEquals(11332448, data['Gazeteer'])

        self.assertTrue('GoPro mounted on an eagle' in data)
        self.assertEquals(1, data['GoPro mounted on an eagle'])

        self.assertTrue('HGIS' in data)
        self.assertEquals(2837808, data['HGIS'])

        self.assertTrue('IIP-SA-Raster' in data)
        self.assertEquals(89475, data['IIP-SA-Raster'])

        self.assertTrue('Instagram - Gnip' in data)
        self.assertEquals(333118, data['Instagram - Gnip'])

        self.assertTrue('MASS Service' in data)
        self.assertEquals(15, data['MASS Service'])

        self.assertTrue('OSM' in data)
        self.assertEquals(374842982, data['OSM'])

        self.assertTrue('SETD' in data)
        self.assertEquals(137353, data['SETD'])

        self.assertTrue('Test' in data)
        self.assertEquals(2, data['Test'])

        self.assertTrue('Tom Ruegger' in data)
        self.assertEquals(3, data['Tom Ruegger'])

        self.assertTrue('Tomnod' in data)
        self.assertEquals(69339, data['Tomnod'])

        self.assertTrue('VK - Gnip' in data)
        self.assertEquals(15295, data['VK - Gnip'])

        self.assertTrue('Vector REST API' in data)
        self.assertEquals(213521, data['Vector REST API'])

    def processGlobalOSMJson(self):
        json = """\
        {"data":[{"name":"Polygon","count":181368511},{"name":"PolyLine","count":98384903},{"name":"Point","count":95391003}],"shards":1295}
                """
        query = VectorQuery(None, None, None, None)
        data = query.process_json_data(json)

        self.assertTrue(len(data) == 3)

        self.assertTrue("Polygon" in data)
        self.assertEquals(181368511, data["Polygon"])

        self.assertTrue("PolyLine" in data)
        self.assertEquals(98384903, data["PolyLine"])

        self.assertTrue("Point" in data)
        self.assertEquals(95391003, data["Point"])

    def processGlobalGBDPolygonJson(self):
        json = """\
        {"data":[{"name":"LV3B","count":6016},{"name":"UNKNOWN","count":19}],"shards":1295}
                """

        query = VectorQuery(None, None, None, None)
        data = query.process_json_data(json)

        self.assertTrue(len(data) == 2)

        self.assertTrue("LV3B" in data)
        self.assertEquals(6016, data["LV3B"])

        self.assertTrue("UNKNOWN" in data)
        self.assertEquals(19, data["UNKNOWN"])