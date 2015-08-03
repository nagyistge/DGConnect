# -*- coding: utf-8 -*-
__author__ = 'mtrotter'

import unittest
import InsightCloudQuery
import CSVOutput

class JSONOSMTest(unittest.TestCase):
    def test_osm_json_parse(self):
        osm_str = """{
   "data":[
      {
         "name":"Road",
         "count":343346
      },
      {
         "name":"Building",
         "count":72252
      },
      {
         "name":"Uncategorized",
         "count":52873
      },
      {
         "name":"Tower",
         "count":34276
      },
      {
         "name":"Residential",
         "count":21875
      },
      {
         "name":"Apartments",
         "count":15057
      },
      {
         "name":"Village",
         "count":13225
      },
      {
         "name":"Pedestrian",
         "count":8461
      },
      {
         "name":"Place Of Worship",
         "count":7149
      },
      {
         "name":"Pole",
         "count":4567
      },
      {
         "name":"Stream",
         "count":4057
      },
      {
         "name":"Industrial",
         "count":2946
      },
      {
         "name":"School",
         "count":2751
      },
      {
         "name":"Boundary (Administrative)",
         "count":2662
      },
      {
         "name":"Rail",
         "count":2626
      },
      {
         "name":"Barrier (Wall)",
         "count":2568
      },
      {
         "name":"House",
         "count":2457
      },
      {
         "name":"Park",
         "count":2212
      },
      {
         "name":"Parking",
         "count":2146
      },
      {
         "name":"Cemetery",
         "count":2043
      },
      {
         "name":"Orchard",
         "count":2029
      },
      {
         "name":"Peak",
         "count":2027
      },
      {
         "name":"Suburb",
         "count":1965
      },
      {
         "name":"Water",
         "count":1815
      },
      {
         "name":"Farmland",
         "count":1734
      },
      {
         "name":"Tree",
         "count":1643
      },
      {
         "name":"Meadow",
         "count":1597
      },
      {
         "name":"Fuel",
         "count":1550
      },
      {
         "name":"Wood",
         "count":1533
      },
      {
         "name":"Pitch",
         "count":1422
      },
      {
         "name":"Forest",
         "count":1373
      },
      {
         "name":"River",
         "count":1334
      },
      {
         "name":"Line",
         "count":1300
      },
      {
         "name":"Locality",
         "count":1259
      },
      {
         "name":"Grass",
         "count":1234
      },
      {
         "name":"Hamlet",
         "count":1079
      },
      {
         "name":"Ditch",
         "count":1017
      },
      {
         "name":"Mast",
         "count":1009
      },
      {
         "name":"Bus Stop",
         "count":967
      },
      {
         "name":"Restaurant",
         "count":937
      },
      {
         "name":"Swimming Pool",
         "count":931
      },
      {
         "name":"Traffic Signals",
         "count":906
      },
      {
         "name":"Barrier (Fence)",
         "count":864
      },
      {
         "name":"Quarry",
         "count":804
      },
      {
         "name":"Neighbourhood",
         "count":747
      },
      {
         "name":"Cliff",
         "count":724
      },
      {
         "name":"Farm",
         "count":692
      },
      {
         "name":"Location",
         "count":675
      },
      {
         "name":"Level Crossing",
         "count":665
      },
      {
         "name":"Barrier (Gate)",
         "count":590
      },
      {
         "name":"Barrier (Hedge)",
         "count":528
      },
      {
         "name":"Dam",
         "count":519
      },
      {
         "name":"Scrub",
         "count":513
      },
      {
         "name":"Conservation",
         "count":482
      },
      {
         "name":"Switch",
         "count":482
      },
      {
         "name":"University",
         "count":470
      },
      {
         "name":"Crossing",
         "count":430
      },
      {
         "name":"Transportation - Uncategorized",
         "count":430
      },
      {
         "name":"Coastline",
         "count":416
      },
      {
         "name":"Hospital",
         "count":415
      },
      {
         "name":"Commercial",
         "count":397
      },
      {
         "name":"Mound",
         "count":388
      },
      {
         "name":"Cafe",
         "count":384
      },
      {
         "name":"Pharmacy",
         "count":372
      },
      {
         "name":"Shelter",
         "count":371
      },
      {
         "name":"Aeroway (Taxiway)",
         "count":367
      },
      {
         "name":"Military",
         "count":359
      },
      {
         "name":"Public Building",
         "count":349
      },
      {
         "name":"Canal",
         "count":342
      },
      {
         "name":"Minor Line",
         "count":316
      },
      {
         "name":"Bench",
         "count":300
      },
      {
         "name":"Station",
         "count":300
      },
      {
         "name":"Tree Row",
         "count":300
      },
      {
         "name":"Garden",
         "count":286
      },
      {
         "name":"Bank",
         "count":276
      },
      {
         "name":"Aeroway (Helipad)",
         "count":275
      },
      {
         "name":"Substation",
         "count":275
      },
      {
         "name":"Landfill",
         "count":269
      },
      {
         "name":"Roof",
         "count":261
      },
      {
         "name":"Town",
         "count":258
      },
      {
         "name":"Turning Circle",
         "count":256
      },
      {
         "name":"Reservoir",
         "count":254
      },
      {
         "name":"Wetland",
         "count":229
      },
      {
         "name":"Historic (Ruins)",
         "count":223
      },
      {
         "name":"Playground",
         "count":223
      },
      {
         "name":"Greenhouse",
         "count":221
      },
      {
         "name":"Pipeline",
         "count":210
      },
      {
         "name":"Drinking Water",
         "count":208
      },
      {
         "name":"Riverbank",
         "count":207
      },
      {
         "name":"Motorway Junction",
         "count":205
      },
      {
         "name":"Drain",
         "count":187
      },
      {
         "name":"Village Green",
         "count":181
      },
      {
         "name":"Buffer Stop",
         "count":173
      },
      {
         "name":"Fast Food",
         "count":173
      },
      {
         "name":"Generator",
         "count":169
      },
      {
         "name":"Vineyard",
         "count":167
      },
      {
         "name":"Spring",
         "count":151
      },
      {
         "name":"Farmyard",
         "count":146
      },
      {
         "name":"Historic (Archaeological Site)",
         "count":143
      },
      {
         "name":"Beach",
         "count":141
      },
      {
         "name":"Construction",
         "count":138
      },
      {
         "name":"Basin",
         "count":131
      },
      {
         "name":"Toilets",
         "count":129
      },
      {
         "name":"Stadium",
         "count":127
      },
      {
         "name":"Water Tower",
         "count":125
      },
      {
         "name":"Pier",
         "count":119
      },
      {
         "name":"Fountain",
         "count":118
      },
      {
         "name":"Hut",
         "count":113
      },
      {
         "name":"Public",
         "count":111
      },
      {
         "name":"Atm",
         "count":105
      },
      {
         "name":"Sports Centre",
         "count":104
      },
      {
         "name":"Pub",
         "count":100
      },
      {
         "name":"Waste Basket",
         "count":98
      },
      {
         "name":"Townhall",
         "count":97
      },
      {
         "name":"Marketplace",
         "count":96
      },
      {
         "name":"Bus Station",
         "count":94
      },
      {
         "name":"Mini Roundabout",
         "count":94
      },
      {
         "name":"Barrier (Lift Gate)",
         "count":91
      },
      {
         "name":"Police",
         "count":90
      },
      {
         "name":"Weir",
         "count":90
      },
      {
         "name":"Tram Stop",
         "count":88
      },
      {
         "name":"Dormitory",
         "count":86
      },
      {
         "name":"Grave Yard",
         "count":85
      },
      {
         "name":"Taxi",
         "count":83
      },
      {
         "name":"Halt",
         "count":82
      },
      {
         "name":"Historic (Castle)",
         "count":82
      },
      {
         "name":"Office",
         "count":82
      },
      {
         "name":"Bar",
         "count":81
      },
      {
         "name":"Barrier (Retaining Wall)",
         "count":81
      },
      {
         "name":"Mosque",
         "count":81
      },
      {
         "name":"Post Office",
         "count":80
      },
      {
         "name":"Historic (Monument)",
         "count":79
      },
      {
         "name":"Stop",
         "count":79
      },
      {
         "name":"Aeroway (Apron)",
         "count":67
      },
      {
         "name":"Barrier (Toll Booth)",
         "count":62
      },
      {
         "name":"Tram",
         "count":62
      },
      {
         "name":"Garage",
         "count":60
      },
      {
         "name":"Transformer",
         "count":59
      },
      {
         "name":"Barrier (Ditch)",
         "count":55
      },
      {
         "name":"Monitoring Station",
         "count":55
      },
      {
         "name":"Retail",
         "count":54
      },
      {
         "name":"Boundary (Postal Code)",
         "count":52
      },
      {
         "name":"Historic (Memorial)",
         "count":51
      },
      {
         "name":"Car Rental",
         "count":50
      },
      {
         "name":"Aeroway (Runway)",
         "count":49
      },
      {
         "name":"Post Box",
         "count":48
      },
      {
         "name":"Telephone",
         "count":48
      },
      {
         "name":"Embassy",
         "count":44
      },
      {
         "name":"Hangar",
         "count":44
      },
      {
         "name":"Kindergarten",
         "count":43
      },
      {
         "name":"Barrier (City Wall)",
         "count":42
      },
      {
         "name":"Subway",
         "count":42
      },
      {
         "name":"Aeroway (Aerodrome)",
         "count":40
      },
      {
         "name":"Prison",
         "count":40
      },
      {
         "name":"Theatre",
         "count":40
      },
      {
         "name":"Subway Entrance",
         "count":39
      },
      {
         "name":"Track",
         "count":39
      },
      {
         "name":"Light Rail",
         "count":38
      },
      {
         "name":"Barrier (Block)",
         "count":37
      },
      {
         "name":"Fire Station",
         "count":37
      },
      {
         "name":"Library",
         "count":37
      },
      {
         "name":"Aeroway (Hangar)",
         "count":36
      },
      {
         "name":"Breakwater",
         "count":36
      },
      {
         "name":"City",
         "count":36
      },
      {
         "name":"Parking Space",
         "count":36
      },
      {
         "name":"Wadi",
         "count":35
      },
      {
         "name":"Waste Disposal",
         "count":35
      },
      {
         "name":"Chimney",
         "count":33
      },
      {
         "name":"College",
         "count":33
      },
      {
         "name":"Greenfield",
         "count":33
      },
      {
         "name":"Bicycle Rental",
         "count":32
      },
      {
         "name":"Car Wash",
         "count":32
      },
      {
         "name":"Wastewater Plant",
         "count":32
      },
      {
         "name":"Fuel Storage Tank",
         "count":31
      },
      {
         "name":"Barrier (Bollard)",
         "count":30
      },
      {
         "name":"Platform",
         "count":29
      },
      {
         "name":"Church",
         "count":28
      },
      {
         "name":"Tell",
         "count":28
      },
      {
         "name":"Train Station",
         "count":28
      },
      {
         "name":"Barrier (Wire Fence)",
         "count":27
      },
      {
         "name":"Reservoir Covered",
         "count":27
      },
      {
         "name":"Barrier (Entrance)",
         "count":26
      },
      {
         "name":"Barrier (Kerb)",
         "count":26
      },
      {
         "name":"Courthouse",
         "count":26
      },
      {
         "name":"Entrance",
         "count":26
      },
      {
         "name":"State",
         "count":26
      },
      {
         "name":"Isolated Dwelling",
         "count":25
      },
      {
         "name":"Recycling",
         "count":25
      },
      {
         "name":"Cinema",
         "count":24
      },
      {
         "name":"Railway",
         "count":24
      },
      {
         "name":"Disused",
         "count":23
      },
      {
         "name":"Abandoned",
         "count":22
      },
      {
         "name":"Aeroway (Parking Position)",
         "count":22
      },
      {
         "name":"Cave Entrance",
         "count":22
      },
      {
         "name":"Collapsed",
         "count":21
      },
      {
         "name":"Marina",
         "count":21
      },
      {
         "name":"Vending Machine",
         "count":21
      },
      {
         "name":"Island",
         "count":20
      },
      {
         "name":"Waterfall",
         "count":20
      },
      {
         "name":"Ground Text",
         "count":19
      },
      {
         "name":"Recreation Ground",
         "count":18
      },
      {
         "name":"Storage Tank",
         "count":18
      },
      {
         "name":"Sub Station",
         "count":18
      },
      {
         "name":"Boundary (Bing Highres)",
         "count":17
      },
      {
         "name":"Ford",
         "count":17
      },
      {
         "name":"Street Lamp",
         "count":17
      },
      {
         "name":"Grassland",
         "count":16
      },
      {
         "name":"Speed Camera",
         "count":16
      },
      {
         "name":"Aeroway (Gate)",
         "count":15
      },
      {
         "name":"Brownfield",
         "count":15
      },
      {
         "name":"Bbq",
         "count":14
      },
      {
         "name":"Doctors",
         "count":14
      },
      {
         "name":"Hotel",
         "count":14
      },
      {
         "name":"Terrace",
         "count":14
      },
      {
         "name":"Warehouse",
         "count":14
      },
      {
         "name":"Barrier (Border Control)",
         "count":13
      },
      {
         "name":"Boundary (Military)",
         "count":13
      },
      {
         "name":"Historic (Wayside Shrine)",
         "count":13
      },
      {
         "name":"Cabin",
         "count":12
      },
      {
         "name":"Islet",
         "count":12
      },
      {
         "name":"Manufacture",
         "count":12
      },
      {
         "name":"Nature Reserve",
         "count":12
      },
      {
         "name":"Nightclub",
         "count":12
      },
      {
         "name":"Veterinary",
         "count":12
      },
      {
         "name":"Works",
         "count":12
      },
      {
         "name":"Bare Rock",
         "count":11
      },
      {
         "name":"Bicycle Parking",
         "count":11
      },
      {
         "name":"Dentist",
         "count":11
      },
      {
         "name":"Portal",
         "count":11
      },
      {
         "name":"Volcano",
         "count":11
      },
      {
         "name":"Clinic",
         "count":10
      },
      {
         "name":"Gasometer",
         "count":10
      },
      {
         "name":"Route (Ferry)",
         "count":10
      },
      {
         "name":"Turntable",
         "count":10
      },
      {
         "name":"Arts Centre",
         "count":9
      },
      {
         "name":"Barrier (Stile)",
         "count":9
      },
      {
         "name":"Flagpole",
         "count":9
      },
      {
         "name":"Garages",
         "count":9
      },
      {
         "name":"Greenhouse Horticulture",
         "count":9
      },
      {
         "name":"Ground Flag",
         "count":9
      },
      {
         "name":"Ridge",
         "count":9
      },
      {
         "name":"Silo",
         "count":9
      },
      {
         "name":"Sport (Soccer)",
         "count":9
      },
      {
         "name":"Windmill",
         "count":9
      },
      {
         "name":"Give Way",
         "count":8
      },
      {
         "name":"Reforestation",
         "count":8
      },
      {
         "name":"Sport",
         "count":8
      },
      {
         "name":"Barrier (Chain)",
         "count":7
      },
      {
         "name":"Boundary (Protected Area)",
         "count":7
      },
      {
         "name":"Bunker",
         "count":7
      },
      {
         "name":"Bureau De Change",
         "count":7
      },
      {
         "name":"Communications Tower",
         "count":7
      },
      {
         "name":"Heath",
         "count":7
      },
      {
         "name":"Kiln",
         "count":7
      },
      {
         "name":"Pond",
         "count":7
      },
      {
         "name":"Scree",
         "count":7
      },
      {
         "name":"Shingle",
         "count":7
      },
      {
         "name":"Allotments",
         "count":6
      },
      {
         "name":"Aqueduct",
         "count":6
      },
      {
         "name":"Barrier (Cattle Grid)",
         "count":6
      },
      {
         "name":"Barrier (Guard Rail)",
         "count":6
      },
      {
         "name":"Bay",
         "count":6
      },
      {
         "name":"Dive Centre",
         "count":6
      },
      {
         "name":"Ferry Terminal",
         "count":6
      },
      {
         "name":"Ice Cream",
         "count":6
      },
      {
         "name":"Lighthouse",
         "count":6
      },
      {
         "name":"Supermarket",
         "count":6
      },
      {
         "name":"Aeroway (Terminal)",
         "count":5
      },
      {
         "name":"Cable",
         "count":5
      },
      {
         "name":"Dune",
         "count":5
      },
      {
         "name":"Golf Course",
         "count":5
      },
      {
         "name":"Historic (Aqueduct)",
         "count":5
      },
      {
         "name":"No",
         "count":5
      },
      {
         "name":"Parking Entrance",
         "count":5
      },
      {
         "name":"Pumpıng Rig",
         "count":5
      },
      {
         "name":"Salt Pond",
         "count":5
      },
      {
         "name":"Satelite Dish",
         "count":5
      },
      {
         "name":"Shop",
         "count":5
      },
      {
         "name":"Shower",
         "count":5
      },
      {
         "name":"Social Facility",
         "count":5
      },
      {
         "name":"Sport (Basketball)",
         "count":5
      },
      {
         "name":"Sport (Equestrian)",
         "count":5
      },
      {
         "name":"Sport (Multi)",
         "count":5
      },
      {
         "name":"Sport (Swimming)",
         "count":5
      },
      {
         "name":"Sport (Tennis)",
         "count":5
      },
      {
         "name":"Tramstop",
         "count":5
      },
      {
         "name":"Waterway",
         "count":5
      },
      {
         "name":"Boundary (Political)",
         "count":4
      },
      {
         "name":"Bridge",
         "count":4
      },
      {
         "name":"Cargo",
         "count":4
      },
      {
         "name":"Club",
         "count":4
      },
      {
         "name":"Coastline-x",
         "count":4
      },
      {
         "name":"Community Centre",
         "count":4
      },
      {
         "name":"Detached",
         "count":4
      },
      {
         "name":"Groyne",
         "count":4
      },
      {
         "name":"Hamam",
         "count":4
      },
      {
         "name":"Historic (Cannon)",
         "count":4
      },
      {
         "name":"Hot Spring",
         "count":4
      },
      {
         "name":"Monastery",
         "count":4
      },
      {
         "name":"Region",
         "count":4
      },
      {
         "name":"Shed",
         "count":4
      },
      {
         "name":"Shoal",
         "count":4
      },
      {
         "name":"Slipway",
         "count":4
      },
      {
         "name":"Steps",
         "count":4
      },
      {
         "name":"Survey Point",
         "count":4
      },
      {
         "name":"Water Park",
         "count":4
      },
      {
         "name":"Water Well",
         "count":4
      },
      {
         "name":"Watermill",
         "count":4
      },
      {
         "name":"Amenity",
         "count":3
      },
      {
         "name":"Barrier",
         "count":3
      },
      {
         "name":"Barrier (Cycle Barrier)",
         "count":3
      },
      {
         "name":"Boundary (Maritime)",
         "count":3
      },
      {
         "name":"Boundary (National Park)",
         "count":3
      },
      {
         "name":"Caldera",
         "count":3
      },
      {
         "name":"Cape",
         "count":3
      },
      {
         "name":"Childcare",
         "count":3
      },
      {
         "name":"Clock",
         "count":3
      },
      {
         "name":"Common",
         "count":3
      },
      {
         "name":"Country",
         "count":3
      },
      {
         "name":"Dock",
         "count":3
      },
      {
         "name":"Dyke",
         "count":3
      },
      {
         "name":"Historic (Aircraft)",
         "count":3
      },
      {
         "name":"Horse Riding",
         "count":3
      },
      {
         "name":"Incline Steep",
         "count":3
      },
      {
         "name":"Picnic Table",
         "count":3
      },
      {
         "name":"Place",
         "count":3
      },
      {
         "name":"Retirement Home",
         "count":3
      },
      {
         "name":"Ruins",
         "count":3
      },
      {
         "name":"Services",
         "count":3
      },
      {
         "name":"Spa",
         "count":3
      },
      {
         "name":"Sport (10pin)",
         "count":3
      },
      {
         "name":"Sport (Paragliding)",
         "count":3
      },
      {
         "name":"Sport (Volleyball)",
         "count":3
      },
      {
         "name":"Telephone Exchange",
         "count":3
      },
      {
         "name":"Winery",
         "count":3
      },
      {
         "name":"Agriculture",
         "count":2
      },
      {
         "name":"Animal Shelter",
         "count":2
      },
      {
         "name":"Barn",
         "count":2
      },
      {
         "name":"Barrier (Full-height Turnstile)",
         "count":2
      },
      {
         "name":"Barrier (Spikes)",
         "count":2
      },
      {
         "name":"Barrier (Turnstile)",
         "count":2
      },
      {
         "name":"Canopy",
         "count":2
      },
      {
         "name":"Chapel",
         "count":2
      },
      {
         "name":"Civic",
         "count":2
      },
      {
         "name":"Communications Transponder",
         "count":2
      },
      {
         "name":"Crossover",
         "count":2
      },
      {
         "name":"Customs",
         "count":2
      },
      {
         "name":"Diving Center",
         "count":2
      },
      {
         "name":"Firepit",
         "count":2
      },
      {
         "name":"Fishing",
         "count":2
      },
      {
         "name":"Food Court",
         "count":2
      },
      {
         "name":"Government",
         "count":2
      },
      {
         "name":"Governmental",
         "count":2
      },
      {
         "name":"Historic (Battlefield)",
         "count":2
      },
      {
         "name":"Historic (Wayside Cross)",
         "count":2
      },
      {
         "name":"Import",
         "count":2
      },
      {
         "name":"Internet Cafe",
         "count":2
      },
      {
         "name":"Landuse",
         "count":2
      },
      {
         "name":"Railway Crossing",
         "count":2
      },
      {
         "name":"Reef",
         "count":2
      },
      {
         "name":"Religious",
         "count":2
      },
      {
         "name":"Rest Area",
         "count":2
      },
      {
         "name":"Sand",
         "count":2
      },
      {
         "name":"Sport (Football)",
         "count":2
      },
      {
         "name":"Sport (Motor)",
         "count":2
      },
      {
         "name":"Sport (Skating)",
         "count":2
      },
      {
         "name":"Stable",
         "count":2
      },
      {
         "name":"T",
         "count":2
      },
      {
         "name":"Trees",
         "count":2
      },
      {
         "name":"Unclassified",
         "count":2
      },
      {
         "name":"Water Works",
         "count":2
      },
      {
         "name":"Yield",
         "count":2
      },
      {
         "name":"112 Acil Çağrı Merkezi",
         "count":1
      },
      {
         "name":"Aeroway (Taxilane)",
         "count":1
      },
      {
         "name":"Antenna",
         "count":1
      },
      {
         "name":"Barrier (Fenced Wall)",
         "count":1
      },
      {
         "name":"Barrier (Rock)",
         "count":1
      },
      {
         "name":"Bicycle Rental;bıcycle Repair",
         "count":1
      },
      {
         "name":"Bird Hide",
         "count":1
      },
      {
         "name":"Boat Sharing",
         "count":1
      },
      {
         "name":"Boundary (Census)",
         "count":1
      },
      {
         "name":"Boundary (Hires)",
         "count":1
      },
      {
         "name":"Boundary (Imagery)",
         "count":1
      },
      {
         "name":"Boundary (Yahoo! Aerial Imagery)",
         "count":1
      },
      {
         "name":"Brook",
         "count":1
      },
      {
         "name":"Business",
         "count":1
      },
      {
         "name":"Car Wash;bicycle Rental",
         "count":1
      },
      {
         "name":"City Wall",
         "count":1
      },
      {
         "name":"Community Center",
         "count":1
      },
      {
         "name":"Crane",
         "count":1
      },
      {
         "name":"Cutline",
         "count":1
      },
      {
         "name":"Dain",
         "count":1
      },
      {
         "name":"Diving School",
         "count":1
      },
      {
         "name":"Driving School",
         "count":1
      },
      {
         "name":"Electronics Shop",
         "count":1
      },
      {
         "name":"Elevator",
         "count":1
      },
      {
         "name":"Emergency Phone",
         "count":1
      },
      {
         "name":"Factory",
         "count":1
      },
      {
         "name":"Faculty",
         "count":1
      },
      {
         "name":"Farm Auxiliary",
         "count":1
      },
      {
         "name":"Fell",
         "count":1
      },
      {
         "name":"Fitness Centre",
         "count":1
      },
      {
         "name":"Floodplain",
         "count":1
      },
      {
         "name":"Fruit",
         "count":1
      },
      {
         "name":"Geoglyph",
         "count":1
      },
      {
         "name":"Glacier",
         "count":1
      },
      {
         "name":"Goverment",
         "count":1
      },
      {
         "name":"Gym",
         "count":1
      },
      {
         "name":"Gölyazı Apt.",
         "count":1
      },
      {
         "name":"Halkapınar Ilkokulu",
         "count":1
      },
      {
         "name":"Harbour",
         "count":1
      },
      {
         "name":"Highway",
         "count":1
      },
      {
         "name":"Historic (Boundary Stone)",
         "count":1
      },
      {
         "name":"Historic (Bridge)",
         "count":1
      },
      {
         "name":"Historic (Church)",
         "count":1
      },
      {
         "name":"Historic (Milestone)",
         "count":1
      },
      {
         "name":"Historic (Monastery)",
         "count":1
      },
      {
         "name":"Historic (Old Building)",
         "count":1
      },
      {
         "name":"Historic (Ship)",
         "count":1
      },
      {
         "name":"Historic (Statue)",
         "count":1
      },
      {
         "name":"Hopital",
         "count":1
      },
      {
         "name":"Hunting Stand",
         "count":1
      },
      {
         "name":"Kamu Binası",
         "count":1
      },
      {
         "name":"King's Leisure Centre",
         "count":1
      },
      {
         "name":"Köy",
         "count":1
      },
      {
         "name":"Lake",
         "count":1
      },
      {
         "name":"Lifeboat Station",
         "count":1
      },
      {
         "name":"M",
         "count":1
      },
      {
         "name":"Man Made",
         "count":1
      },
      {
         "name":"Mill",
         "count":1
      },
      {
         "name":"Moor",
         "count":1
      },
      {
         "name":"Mountain",
         "count":1
      },
      {
         "name":"Mud",
         "count":1
      },
      {
         "name":"Municipality Offices",
         "count":1
      },
      {
         "name":"Museum",
         "count":1
      },
      {
         "name":"Müze",
         "count":1
      },
      {
         "name":"Oil Tank",
         "count":1
      },
      {
         "name":"Outdoor Seating",
         "count":1
      },
      {
         "name":"Patisserie",
         "count":1
      },
      {
         "name":"Pit",
         "count":1
      },
      {
         "name":"Plain",
         "count":1
      },
      {
         "name":"Plots For Sale",
         "count":1
      },
      {
         "name":"Post",
         "count":1
      },
      {
         "name":"Power",
         "count":1
      },
      {
         "name":"Proving Ground",
         "count":1
      },
      {
         "name":"Pumping Rig",
         "count":1
      },
      {
         "name":"Pumping Station",
         "count":1
      },
      {
         "name":"Radar",
         "count":1
      },
      {
         "name":"Sauna",
         "count":1
      },
      {
         "name":"Sinkhole",
         "count":1
      },
      {
         "name":"Social Space",
         "count":1
      },
      {
         "name":"Sport (9pin)",
         "count":1
      },
      {
         "name":"Sport (Athletics)",
         "count":1
      },
      {
         "name":"Sport (Baseball)",
         "count":1
      },
      {
         "name":"Sport (Climbing)",
         "count":1
      },
      {
         "name":"Sport (Gymnastics)",
         "count":1
      },
      {
         "name":"Sport (Horse Racing)",
         "count":1
      },
      {
         "name":"Sport (Karting)",
         "count":1
      },
      {
         "name":"Sport (Paintball)",
         "count":1
      },
      {
         "name":"Sport (Scuba Diving)",
         "count":1
      },
      {
         "name":"Square",
         "count":1
      },
      {
         "name":"Suburb;village",
         "count":1
      },
      {
         "name":"Sveltos Hotel",
         "count":1
      },
      {
         "name":"Tank",
         "count":1
      },
      {
         "name":"Theater",
         "count":1
      },
      {
         "name":"Traffic Island",
         "count":1
      },
      {
         "name":"Tv Station",
         "count":1
      },
      {
         "name":"Valley",
         "count":1
      },
      {
         "name":"Vehicle Inspection",
         "count":1
      },
      {
         "name":"Water Tank",
         "count":1
      },
      {
         "name":"Water Wheel",
         "count":1
      },
      {
         "name":"Watering Place",
         "count":1
      },
      {
         "name":"Watersports",
         "count":1
      },
      {
         "name":"Weighbridge",
         "count":1
      },
      {
         "name":"Winter Sports",
         "count":1
      },
      {
         "name":"Ş. Mustafa Kurtuluş Ilkokulu",
         "count":1
      }
   ],
   "shards":1270
}"""
        csv_element = CSVOutput.CSVOutput(left=32.3964, right=37.2633, bottom=34.7208, top=46.631, polygon=None)
        osm_query = InsightCloudQuery.InsightCloudQuery(None, None)
        osm_query.process_osm_data(osm_str, csv_element)
        self.assertEqual(csv_element.num_osm, 657759)