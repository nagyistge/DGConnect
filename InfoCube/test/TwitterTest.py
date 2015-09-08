# -*- coding: utf-8 -*-
__author__ = 'Michael Trotter <michael.trotter@digitalglobe.com>'

import unittest
from CSVOutput import CSVOutput
from InfoCubeInsightCloudQuery import InsightCloudQuery

class JSONTwitterTest(unittest.TestCase):
    def test_parse_twitter_json(self):
        json_data = r"""{
   "took":22137,
   "timed_out":false,
   "_shards":{
      "total":3350,
      "successful":3350,
      "failed":0
   },
   "hits":{
      "total":1541190,
      "max_score":1.0,
      "hits":[
         {
            "_index":"orbit-2015-02-04",
            "_type":"tweet",
            "_id":"562967110952169472",
            "_score":1.0,
            "_source":{
               "text":"Brian Chaffin \u2022 C \u2022 6-2 \u2022 285 \u2022 Harrisburg, N.C. \u2022 Charlotte Christian\nFirst official Stanford football signee.",
               "screenName":"rickeymer",
               "loc_hash":"9q8ysbphnskdtf4nvp7j",
               "retweets":null,
               "gnipLanguage":"en",
               "friendsCount":654,
               "actorDescription":"On a mission to become Zen Master.",
               "followersCount":230,
               "negativeSentiment":0.05968315554023689,
               "favoritesCount":0,
               "positiveSentiment":0.940316844459763,
               "process_version":"20140909T120800Z",
               "twitterCountryCode":"US",
               "twitterLanguage":null,
               "device":"Twitter for iPhone",
               "created":"2015-02-04T13:33:13.000Z",
               "geo":{
                  "lat":37.705788,
                  "lon":-122.476674
               },
               "actorDisplayName":"Rick Eymer",
               "listedCount":5,
               "exactGeo":"true",
               "verb":"post",
               "countryCode":"United States",
               "statusesCount":1954,
               "id":"562967110952169472",
               "actorLanguages":[
                  "en"
               ],
               "actorId":"123056175",
               "placeGeoType":"Polygon"
            }
         },
         {
            "_index":"orbit-2015-02-04",
            "_type":"tweet",
            "_id":"562968745447268354",
            "_score":1.0,
            "_source":{
               "text":"Rain's good luck for weddings..another #WorldSeries perhaps? RT@R8ders_4life rain Sat on @SFGiantsFans Fest? @abc7kristensze @MikeNiccoABC7",
               "screenName":"LeylaGulenABC7",
               "loc_hash":"9q8yvguy4btqnrbdjr9j",
               "retweets":null,
               "gnipLanguage":"en",
               "friendsCount":646,
               "actorDescription":"Weekday morning traffic reporter and feature reporter for ABC7 News in San Francisco. Facebook: https:\/\/www.facebook.com\/LeylaGulenABC7",
               "followersCount":3279,
               "negativeSentiment":0.24136288806488154,
               "favoritesCount":0,
               "positiveSentiment":0.7586371119351184,
               "userMentions":[
                  "520513452:Nelson Cheng",
                  "8521542:San Francisco Giants",
                  "33907531:Kristen Sze",
                  "258857757:Mike Nicco"
               ],
               "process_version":"20140909T120800Z",
               "twitterCountryCode":"US",
               "twitterLanguage":null,
               "device":"Twitter Web Client",
               "created":"2015-02-04T13:39:43.000Z",
               "geo":{
                  "lat":37.7706565,
                  "lon":-122.4359785
               },
               "actorDisplayName":"Leyla Gulen",
               "listedCount":110,
               "exactGeo":"false",
               "verb":"post",
               "countryCode":"United States",
               "statusesCount":8434,
               "id":"562968745447268354",
               "actorLanguages":[
                  "en"
               ],
               "hashtags":[
                  "WorldSeries"
               ],
               "actorId":"1301668658",
               "placeGeoType":"Polygon"
            }
         },
         {
            "_index":"orbit-2015-02-04",
            "_type":"tweet",
            "_id":"562983858787082243",
            "_score":1.0,
            "_source":{
               "text":"@CarnegieMellon to get new research center on self driving cars in partnership with uber. http:\/\/t.co\/TibZ9A14OT",
               "screenName":"geoffhendrey",
               "loc_hash":"9q8ytpupkv44vucg3u24",
               "retweets":null,
               "gnipLanguage":"en",
               "friendsCount":328,
               "actorDescription":"Splunker, founder http:\/\/www.meetup.com\/Real-time-Big-Data\/, Carnegie Mellon, San Francisco",
               "followersCount":203,
               "negativeSentiment":0.22847969141073096,
               "favoritesCount":0,
               "positiveSentiment":0.7715203085892691,
               "userMentions":[
                  "17631078:Carnegie Mellon"
               ],
               "process_version":"20140909T120800Z",
               "twitterCountryCode":"US",
               "twitterLanguage":null,
               "device":"Twitter for iPhone",
               "created":"2015-02-04T14:39:46.000Z",
               "geo":{
                  "lat":37.748922,
                  "lon":-122.469886
               },
               "actorDisplayName":"Geoffrey Hendrey",
               "listedCount":24,
               "exactGeo":"true",
               "verb":"post",
               "countryCode":"United States",
               "statusesCount":665,
               "id":"562983858787082243",
               "actorLanguages":[
                  "en"
               ],
               "actorId":"58553047",
               "placeGeoType":"Polygon"
            }
         },
         {
            "_index":"orbit-2015-02-04",
            "_type":"tweet",
            "_id":"562984139620904961",
            "_score":1.0,
            "_source":{
               "text":"Now Hiring: Reg Client Associate (FP) - SAN FRANCISCO, CA | Bank of America: CA - San Francisco | http:\/\/t.co\/Ii2iXA7efQ #jobs",
               "screenName":"lgbtcareerlink_",
               "loc_hash":"9q8znbcm25b00xk904ms",
               "retweets":null,
               "gnipLanguage":"en",
               "friendsCount":128,
               "actorDescription":"Diversity-friendly employers and jobs for the LGBT workforce across the nation from Out & Equal Workplace Advocates",
               "followersCount":807,
               "negativeSentiment":0.1451865452421416,
               "favoritesCount":0,
               "positiveSentiment":0.8548134547578584,
               "process_version":"20140909T120800Z",
               "twitterCountryCode":"US",
               "twitterLanguage":null,
               "device":"CareerCenter",
               "created":"2015-02-04T14:40:53.000Z",
               "geo":{
                  "lat":37.79801,
                  "lon":-122.396965
               },
               "actorDisplayName":"Stephen Huey",
               "listedCount":54,
               "exactGeo":"true",
               "verb":"post",
               "countryCode":"United States",
               "statusesCount":277055,
               "id":"562984139620904961",
               "actorLanguages":[
                  "en"
               ],
               "hashtags":[
                  "jobs"
               ],
               "actorId":"15519381",
               "placeGeoType":"Polygon"
            }
         },
         {
            "_index":"orbit-2015-02-04",
            "_type":"tweet",
            "_id":"562981817134104578",
            "_score":1.0,
            "_source":{
               "text":"@rcooley123 \n\nNo big anti war movement? Because no one is being drafted.",
               "screenName":"russmorgan1958",
               "loc_hash":"9q8yyh9qs3ruvkmxmdeq",
               "retweets":null,
               "gnipLanguage":"en",
               "friendsCount":404,
               "actorDescription":"Happily married since 2008 to my hon, Anthony. Originally from Northern Virginia. I've lived in San Francisco for just about all of my adult life.",
               "followersCount":123,
               "negativeSentiment":0.2743683939431398,
               "favoritesCount":0,
               "positiveSentiment":0.7256316060568602,
               "userMentions":[
                  "172867574:Rick Cooley"
               ],
               "process_version":"20140909T120800Z",
               "twitterCountryCode":"US",
               "twitterLanguage":null,
               "device":"Twitter for iPad",
               "created":"2015-02-04T14:31:39.000Z",
               "geo":{
                  "lat":37.774866,
                  "lon":-122.429731
               },
               "actorDisplayName":"Russ Morgan",
               "listedCount":2,
               "exactGeo":"true",
               "verb":"post",
               "countryCode":"United States",
               "statusesCount":1105,
               "id":"562981817134104578",
               "actorLanguages":[
                  "en"
               ],
               "actorId":"2892519259",
               "placeGeoType":"Polygon"
            }
         },
         {
            "_index":"orbit-2015-02-04",
            "_type":"tweet",
            "_id":"562984386371801090",
            "_score":1.0,
            "_source":{
               "text":"@JamesSemaj1220 Fox news is never fair and balanced either...and Mike can take his book and shove it God guns grits and gravy is out dated",
               "screenName":"MillsBambi",
               "loc_hash":"9q8yvguy4btqnrbdjr9j",
               "retweets":null,
               "gnipLanguage":"en",
               "friendsCount":743,
               "actorDescription":"*smiles* Tryin to live on the upbeat",
               "followersCount":426,
               "negativeSentiment":0.054492212986706326,
               "favoritesCount":0,
               "positiveSentiment":0.9455077870132937,
               "userMentions":[
                  "17600254:JamesSemaJ1220"
               ],
               "process_version":"20140909T120800Z",
               "twitterCountryCode":"US",
               "twitterLanguage":null,
               "device":"Twitter Web Client",
               "created":"2015-02-04T14:41:52.000Z",
               "geo":{
                  "lat":37.7706565,
                  "lon":-122.4359785
               },
               "actorDisplayName":"Robyn",
               "listedCount":3,
               "exactGeo":"false",
               "verb":"post",
               "countryCode":"United States",
               "statusesCount":10710,
               "id":"562984386371801090",
               "actorLanguages":[
                  "en"
               ],
               "actorId":"2814005132",
               "placeGeoType":"Polygon"
            }
         },
         {
            "_index":"orbit-2015-02-04",
            "_type":"tweet",
            "_id":"562984683924094976",
            "_score":1.0,
            "_source":{
               "text":"@kerfluffer narrowing their loss and stating that the hack will not affect their profits",
               "screenName":"rodolfor",
               "loc_hash":"9q8zn1m08hcdgu0zfgzd",
               "retweets":null,
               "gnipLanguage":"en",
               "friendsCount":872,
               "actorDescription":"Now, I am CEO at @Storybricks, the destroyer of worlds. Excited about AI, MMORPGs, Security and DUNE. NSFW.",
               "followersCount":1637,
               "negativeSentiment":0.6414114561269884,
               "favoritesCount":0,
               "positiveSentiment":0.35858854387301153,
               "userMentions":[
                  "6424072:Michael Slavitch "
               ],
               "process_version":"20140909T120800Z",
               "twitterCountryCode":"US",
               "twitterLanguage":null,
               "device":"Twitter for iPhone",
               "created":"2015-02-04T14:43:03.000Z",
               "geo":{
                  "lat":37.799947,
                  "lon":-122.424772
               },
               "actorDisplayName":"Rodolfo Rosini",
               "listedCount":114,
               "exactGeo":"true",
               "verb":"post",
               "countryCode":"United States",
               "statusesCount":44185,
               "id":"562984683924094976",
               "actorLanguages":[
                  "en"
               ],
               "actorId":"16690663",
               "placeGeoType":"Polygon"
            }
         },
         {
            "_index":"orbit-2015-02-04",
            "_type":"tweet",
            "_id":"562984943002062849",
            "_score":1.0,
            "_source":{
               "text":"S.F. hotel group's '50 Shades of Women' is inspired by erotic novels http:\/\/t.co\/NwYFaO2v3z",
               "screenName":"SanFranciscoCP",
               "loc_hash":"9q8yyqu5ywused116xxr",
               "retweets":null,
               "gnipLanguage":"en",
               "friendsCount":8,
               "actorDescription":"Latest news from San Francisco. Updates are frequent. For local news addicts.",
               "followersCount":2917,
               "negativeSentiment":0.0952227746447489,
               "favoritesCount":0,
               "positiveSentiment":0.9047772253552511,
               "process_version":"20140909T120800Z",
               "twitterCountryCode":"US",
               "twitterLanguage":null,
               "device":"dlvr.it",
               "created":"2015-02-04T14:44:04.000Z",
               "geo":{
                  "lat":37.786783,
                  "lon":-122.414876
               },
               "actorDisplayName":"San Francisco Press",
               "listedCount":146,
               "exactGeo":"true",
               "verb":"post",
               "countryCode":"United States",
               "statusesCount":185743,
               "id":"562984943002062849",
               "actorLanguages":[
                  "en"
               ],
               "actorId":"60452453",
               "placeGeoType":"Polygon"
            }
         },
         {
            "_index":"orbit-2015-02-04",
            "_type":"tweet",
            "_id":"562985027441799168",
            "_score":1.0,
            "_source":{
               "text":"@theresaanna @mkramer you ladies are the sweetest. Can't wait until you join the team - as my fellow Chaco sporter. :)",
               "screenName":"jmealbrecht",
               "loc_hash":"9q8yyk8zf4s55ntgq0cs",
               "retweets":null,
               "gnipLanguage":"en",
               "friendsCount":139,
               "actorDescription":"Ops Team @18F. People Watcher. Wellness Captain. & Your Average Spontaneous Dancer.",
               "followersCount":105,
               "negativeSentiment":0.00361266075828408,
               "favoritesCount":0,
               "positiveSentiment":0.9963873392417159,
               "userMentions":[
                  "7439182:Theresa Summa",
                  "10232022:Melody Joy Kramer"
               ],
               "process_version":"20140909T120800Z",
               "twitterCountryCode":"US",
               "twitterLanguage":null,
               "device":"Twitter for iPhone",
               "created":"2015-02-04T14:44:24.000Z",
               "geo":{
                  "lat":37.775087,
                  "lon":-122.419533
               },
               "actorDisplayName":"Jamie Albrecht",
               "listedCount":4,
               "exactGeo":"true",
               "verb":"post",
               "countryCode":"United States",
               "statusesCount":95,
               "id":"562985027441799168",
               "actorLanguages":[
                  "en"
               ],
               "actorId":"2159441905",
               "placeGeoType":"Polygon"
            }
         },
         {
            "_index":"orbit-2015-02-04",
            "_type":"tweet",
            "_id":"562985127538872322",
            "_score":1.0,
            "_source":{
               "text":"Thx Warren! RT @dustormagic: Great AAP talk by tweet master Scott Traylor @360KID @AmericanPublish http:\/\/t.co\/g8ZUI7IaM9",
               "screenName":"360KID",
               "loc_hash":"9q8yvguy4btqnrbdjr9j",
               "retweets":null,
               "gnipLanguage":"en",
               "friendsCount":1383,
               "actorDescription":"Entrepreneur, business advisor, research evangelist, former computer science professor, data junkie, kidtech product creator, blogger & vlogger",
               "followersCount":3971,
               "negativeSentiment":0.01728948973010511,
               "favoritesCount":0,
               "positiveSentiment":0.9827105102698949,
               "userMentions":[
                  "34953322:Dust or Magic",
                  "16308661:Scott Traylor",
                  "17395999:Assn Am. Publishers"
               ],
               "process_version":"20140909T120800Z",
               "twitterCountryCode":"US",
               "twitterLanguage":null,
               "device":"Twitter Web Client",
               "created":"2015-02-04T14:44:48.000Z",
               "geo":{
                  "lat":37.7706565,
                  "lon":-122.4359785
               },
               "actorDisplayName":"Scott Traylor",
               "listedCount":250,
               "exactGeo":"false",
               "verb":"post",
               "countryCode":"United States",
               "statusesCount":6193,
               "id":"562985127538872322",
               "actorLanguages":[
                  "en"
               ],
               "actorId":"16308661",
               "placeGeoType":"Polygon"
            }
         },
         {
            "_index":"orbit-2015-02-04",
            "_type":"tweet",
            "_id":"562970809489457155",
            "_score":1.0,
            "_source":{
               "text":"2\/4 That dream though \u2764\ufe0f\ud83d\udc94",
               "screenName":"_jehanspiration",
               "loc_hash":"9q8yyqh7c35fgk23svwg",
               "retweets":null,
               "gnipLanguage":"en",
               "friendsCount":20,
               "actorDescription":"My Twitter, my diary, my life.",
               "followersCount":7,
               "negativeSentiment":0.5265891561530753,
               "favoritesCount":0,
               "positiveSentiment":0.4734108438469245,
               "process_version":"20140909T120800Z",
               "twitterCountryCode":"US",
               "twitterLanguage":null,
               "device":"Twitter for iPhone",
               "created":"2015-02-04T13:47:55.000Z",
               "geo":{
                  "lat":37.782632,
                  "lon":-122.414759
               },
               "actorDisplayName":"Jehan Recaulla",
               "listedCount":0,
               "exactGeo":"true",
               "verb":"post",
               "countryCode":"United States",
               "statusesCount":35,
               "id":"562970809489457155",
               "actorLanguages":[
                  "en"
               ],
               "actorId":"545301537",
               "placeGeoType":"Polygon"
            }
         },
         {
            "_index":"orbit-2015-02-04",
            "_type":"tweet",
            "_id":"562972873493856256",
            "_score":1.0,
            "_source":{
               "text":"Up To Speed: Yahoo picks unit to bundle with Alibaba stake in spinoff (Video) http:\/\/t.co\/hxwcsxk3lI",
               "screenName":"SanFranciscoCP",
               "loc_hash":"9q8yyqu5ywused116xxr",
               "retweets":null,
               "gnipLanguage":"en",
               "friendsCount":8,
               "actorDescription":"Latest news from San Francisco. Updates are frequent. For local news addicts.",
               "followersCount":2917,
               "negativeSentiment":0.11075202354539959,
               "favoritesCount":0,
               "positiveSentiment":0.8892479764546005,
               "process_version":"20140909T120800Z",
               "twitterCountryCode":"US",
               "twitterLanguage":null,
               "device":"dlvr.it",
               "created":"2015-02-04T13:56:07.000Z",
               "geo":{
                  "lat":37.786783,
                  "lon":-122.414876
               },
               "actorDisplayName":"San Francisco Press",
               "listedCount":146,
               "exactGeo":"true",
               "verb":"post",
               "countryCode":"United States",
               "statusesCount":185741,
               "id":"562972873493856256",
               "actorLanguages":[
                  "en"
               ],
               "actorId":"60452453",
               "placeGeoType":"Polygon"
            }
         },
         {
            "_index":"orbit-2015-02-04",
            "_type":"tweet",
            "_id":"562972991718703104",
            "_score":1.0,
            "_source":{
               "text":"@SonLaHostiaTu El putasuna",
               "screenName":"ErmismoRmFc",
               "loc_hash":"9q8yvguy4btqnrbdjr9j",
               "retweets":null,
               "gnipLanguage":"es",
               "friendsCount":521,
               "actorDescription":"Jugador CS:GO ||Steam \u2192Ermismo || #Dubstep #DrumbBass #Trap #Zomboy #FeedMe #KnifeParty #DubElements #TheProdigy #DaftPunk #TeamGallagher || Meredith\u2665. 24.03\u2665",
               "followersCount":4428,
               "negativeSentiment":0.7348233632744603,
               "favoritesCount":0,
               "positiveSentiment":0.2651766367255397,
               "userMentions":[
                  "2330473128:ElJardinerDeTarrasa"
               ],
               "process_version":"20140909T120800Z",
               "twitterCountryCode":"US",
               "twitterLanguage":null,
               "device":"Twitter Web Client",
               "created":"2015-02-04T13:56:35.000Z",
               "geo":{
                  "lat":37.7706565,
                  "lon":-122.4359785
               },
               "actorDisplayName":"\u00a0\u00a0\u00a0\u00a0\u00a0#TeamGallagher\u21af",
               "listedCount":9,
               "exactGeo":"false",
               "verb":"post",
               "countryCode":"United States",
               "statusesCount":21792,
               "id":"562972991718703104",
               "actorLanguages":[
                  "es"
               ],
               "actorId":"234396275",
               "placeGeoType":"Polygon"
            }
         },
         {
            "_index":"orbit-2015-02-04",
            "_type":"tweet",
            "_id":"563004744810373120",
            "_score":1.0,
            "_source":{
               "text":"So much snow everywhere except here :O",
               "screenName":"elisamari94",
               "loc_hash":"9q8yut18qedn28eq1xvy",
               "retweets":null,
               "gnipLanguage":"en",
               "friendsCount":93,
               "actorDescription":"Currently living in San Francisco, university in Madrid and my heart in Tokyo.",
               "followersCount":106,
               "negativeSentiment":0.1778395203618781,
               "favoritesCount":0,
               "positiveSentiment":0.822160479638122,
               "process_version":"20140909T120800Z",
               "twitterCountryCode":"US",
               "twitterLanguage":null,
               "device":"Twitter for iPhone",
               "created":"2015-02-04T16:02:45.000Z",
               "geo":{
                  "lat":37.776552,
                  "lon":-122.495217
               },
               "actorDisplayName":"Elisa Gallego",
               "listedCount":3,
               "exactGeo":"true",
               "verb":"post",
               "countryCode":"United States",
               "statusesCount":3873,
               "id":"563004744810373120",
               "actorLanguages":[
                  "en"
               ],
               "actorId":"160167277",
               "placeGeoType":"Polygon"
            }
         },
         {
            "_index":"orbit-2015-02-04",
            "_type":"tweet",
            "_id":"563005577434243073",
            "_score":1.0,
            "_source":{
               "text":"Yaaaay more testing",
               "screenName":"sammmlui104",
               "loc_hash":"9q8yutk4rymh54g7n6hy",
               "retweets":null,
               "gnipLanguage":"en",
               "friendsCount":128,
               "actorDescription":"sc:sammmlui104",
               "followersCount":135,
               "negativeSentiment":0.2501416770308098,
               "favoritesCount":0,
               "positiveSentiment":0.7498583229691902,
               "process_version":"20140909T120800Z",
               "twitterCountryCode":"US",
               "twitterLanguage":null,
               "device":"Twitter for iPhone",
               "created":"2015-02-04T16:06:04.000Z",
               "geo":{
                  "lat":37.778283,
                  "lon":-122.491726
               },
               "actorDisplayName":"fire trucker",
               "listedCount":2,
               "exactGeo":"true",
               "verb":"post",
               "countryCode":"United States",
               "statusesCount":658,
               "id":"563005577434243073",
               "actorLanguages":[
                  "en"
               ],
               "actorId":"232435241",
               "placeGeoType":"Polygon"
            }
         },
         {
            "_index":"orbit-2015-02-04",
            "_type":"tweet",
            "_id":"563005938752561152",
            "_score":1.0,
            "_source":{
               "text":"@VMwarePEX @GilShneorson thanking all our excellent partners. Great time was had by all last night. http:\/\/t.co\/qGdrOTIAeo",
               "screenName":"karleboy",
               "loc_hash":"9q8yyweyth82m4utb142",
               "retweets":null,
               "gnipLanguage":"en",
               "friendsCount":125,
               "actorDescription":"Born Dublin Ireland. Licensed Attorney at Law in Massachusetts USA. Marketing Manager @ EMC.  Mixing records and djing quality house music is my passion.",
               "followersCount":159,
               "negativeSentiment":0.019833212125691436,
               "favoritesCount":0,
               "media_urls":[
                  "http:\/\/pbs.twimg.com\/media\/B9Ay6VEIQAAc_0C.jpg"
               ],
               "positiveSentiment":0.9801667878743086,
               "userMentions":[
                  "20472833:VMware Partner Exch.",
                  "602336452:Gil "
               ],
               "process_version":"20140909T120800Z",
               "twitterCountryCode":"US",
               "twitterLanguage":null,
               "device":"Twitter for iPhone",
               "created":"2015-02-04T16:07:30.000Z",
               "geo":{
                  "lat":37.785869,
                  "lon":-122.404303
               },
               "actorDisplayName":"Karl",
               "listedCount":8,
               "exactGeo":"true",
               "verb":"post",
               "countryCode":"United States",
               "statusesCount":746,
               "id":"563005938752561152",
               "actorLanguages":[
                  "en"
               ],
               "actorId":"254240467",
               "placeGeoType":"Polygon"
            }
         },
         {
            "_index":"orbit-2015-02-04",
            "_type":"tweet",
            "_id":"563007131830743041",
            "_score":1.0,
            "_source":{
               "text":"@Dirk_Gently pretty sure mine is getting out of bed.",
               "screenName":"segiddins",
               "loc_hash":"9q8yyt241hb7xjges2sn",
               "retweets":null,
               "gnipLanguage":"en",
               "friendsCount":503,
               "actorDescription":"UChicago 2018. Realm. CocoaPods.",
               "followersCount":437,
               "negativeSentiment":0.1891119535125609,
               "favoritesCount":0,
               "positiveSentiment":0.8108880464874391,
               "userMentions":[
                  "15886726:Sam Marshall"
               ],
               "process_version":"20140909T120800Z",
               "twitterCountryCode":"US",
               "twitterLanguage":null,
               "device":"Tweetbot for i\u039fS",
               "created":"2015-02-04T16:12:15.000Z",
               "geo":{
                  "lat":37.77823196999999,
                  "lon":-122.40962442
               },
               "actorDisplayName":"Samuel E. Giddins",
               "listedCount":19,
               "exactGeo":"false",
               "verb":"post",
               "countryCode":"United States",
               "statusesCount":7511,
               "id":"563007131830743041",
               "actorLanguages":[
                  "en"
               ],
               "actorId":"73644377",
               "placeGeoType":"Polygon"
            }
         },
         {
            "_index":"orbit-2015-02-04",
            "_type":"tweet",
            "_id":"563007220821262337",
            "_score":1.0,
            "_source":{
               "text":"From that same album review: \"sumptuous mechanisms.\" Oy",
               "screenName":"TheRealWBTC",
               "loc_hash":"9q8yyx19pu2dtvtnjedt",
               "retweets":null,
               "gnipLanguage":"en",
               "friendsCount":510,
               "actorDescription":"Marconi plays the mamba \/ listen to the radio \/ Don't you remember? \/ http:\/\/webuiltthiscity.tumblr.com \/\/\/  Podcast: http:\/\/fortherecordpodcast.com",
               "followersCount":1812,
               "negativeSentiment":0.13622912872255843,
               "favoritesCount":0,
               "positiveSentiment":0.8637708712774416,
               "process_version":"20140909T120800Z",
               "twitterCountryCode":"US",
               "twitterLanguage":null,
               "device":"Tweetbot for i\u039fS",
               "created":"2015-02-04T16:12:36.000Z",
               "geo":{
                  "lat":37.787670495,
                  "lon":-122.40727452
               },
               "actorDisplayName":"We Built This City",
               "listedCount":111,
               "exactGeo":"false",
               "verb":"post",
               "countryCode":"United States",
               "statusesCount":13759,
               "id":"563007220821262337",
               "actorLanguages":[
                  "en"
               ],
               "actorId":"255630558",
               "placeGeoType":"Polygon"
            }
         },
         {
            "_index":"orbit-2015-02-04",
            "_type":"tweet",
            "_id":"563008315714973696",
            "_score":1.0,
            "_source":{
               "text":"@lruettimann where\u2019s my $100!? ;)",
               "screenName":"toddx",
               "loc_hash":"9q8yy6k1uvns3878x34x",
               "retweets":null,
               "gnipLanguage":"en",
               "friendsCount":515,
               "actorDescription":"Sarcastic, caffeinated existentialist in SF & the voice of Iced Tea & Sarcasm. #Hashtag Engineer. All opinions expressed are mine alone and truth.",
               "followersCount":976,
               "negativeSentiment":0.33169202567368294,
               "favoritesCount":0,
               "positiveSentiment":0.6683079743263171,
               "userMentions":[
                  "7099112:LFR"
               ],
               "process_version":"20140909T120800Z",
               "twitterCountryCode":"US",
               "twitterLanguage":null,
               "device":"Tweetbot for i\u039fS",
               "created":"2015-02-04T16:16:57.000Z",
               "geo":{
                  "lat":37.761711,
                  "lon":-122.41494850000001
               },
               "actorDisplayName":"Todd X.",
               "listedCount":47,
               "exactGeo":"false",
               "verb":"post",
               "countryCode":"United States",
               "statusesCount":28389,
               "id":"563008315714973696",
               "actorLanguages":[
                  "en"
               ],
               "actorId":"19077572",
               "placeGeoType":"Polygon"
            }
         },
         {
            "_index":"orbit-2015-02-04",
            "_type":"tweet",
            "_id":"563005426967793667",
            "_score":1.0,
            "_source":{
               "text":"@mikefreemanNFL Isn't that permissible if your pizza is delivered after 30 minutes? #DQwellLogic",
               "screenName":"NYC_Cowsheep",
               "loc_hash":"9q8yvguy4btqnrbdjr9j",
               "retweets":null,
               "gnipLanguage":"en",
               "friendsCount":1193,
               "actorDescription":"Die-hard Dallas Cowboys Fan since 1980. #CowboysNation Also, worshipping the King Of All Media since 1985. #HeyNow Living EVERY day like it's my last!",
               "followersCount":180,
               "negativeSentiment":0.2696299399634494,
               "favoritesCount":0,
               "positiveSentiment":0.7303700600365507,
               "userMentions":[
                  "19050461:mike freeman"
               ],
               "process_version":"20140909T120800Z",
               "twitterCountryCode":"US",
               "twitterLanguage":null,
               "device":"Twitter Web Client",
               "created":"2015-02-04T16:05:28.000Z",
               "geo":{
                  "lat":37.7706565,
                  "lon":-122.4359785
               },
               "actorDisplayName":"JP \u272d",
               "listedCount":5,
               "exactGeo":"false",
               "verb":"post",
               "countryCode":"United States",
               "statusesCount":8377,
               "id":"563005426967793667",
               "actorLanguages":[
                  "en"
               ],
               "hashtags":[
                  "DQwellLogic"
               ],
               "actorId":"31203558",
               "placeGeoType":"Polygon"
            }
         },
         {
            "_index":"orbit-2015-02-04",
            "_type":"tweet",
            "_id":"563006476596555778",
            "_score":1.0,
            "_source":{
               "text":"40% of Iowa Republicans believe that Beyonce's music is \"mental poison.\"",
               "screenName":"DwightKnell",
               "loc_hash":"9q8yyk3wkuuz7qsx6vw3",
               "retweets":null,
               "gnipLanguage":"en",
               "friendsCount":253,
               "actorDescription":null,
               "followersCount":128,
               "negativeSentiment":0.3091901433474098,
               "favoritesCount":0,
               "positiveSentiment":0.6908098566525901,
               "process_version":"20140909T120800Z",
               "twitterCountryCode":"US",
               "twitterLanguage":null,
               "device":"Twitter for iPhone",
               "created":"2015-02-04T16:09:38.000Z",
               "geo":{
                  "lat":37.773469,
                  "lon":-122.418384
               },
               "actorDisplayName":"Dwight Knell",
               "listedCount":2,
               "exactGeo":"true",
               "verb":"post",
               "countryCode":"United States",
               "statusesCount":2719,
               "id":"563006476596555778",
               "actorLanguages":[
                  "en"
               ],
               "actorId":"199436908",
               "placeGeoType":"Polygon"
            }
         },
         {
            "_index":"orbit-2015-02-04",
            "_type":"tweet",
            "_id":"563007306041131010",
            "_score":1.0,
            "_source":{
               "text":"Ta-da! Our newest Wellness Center and Massage Room are officially open for business at HQ! http:\/\/t.co\/1GDV67NmCJ",
               "screenName":"salesforcejobs",
               "loc_hash":"9q8zn26wbqfqptw9kkmh",
               "retweets":null,
               "gnipLanguage":"en",
               "friendsCount":2570,
               "actorDescription":"Follow us to learn more about careers and culture @salesforce. We're the world\u2019s #1 Most Innovative Company 4 years in a row!",
               "followersCount":19513,
               "negativeSentiment":0.0015975620542020561,
               "favoritesCount":0,
               "media_urls":[
                  "http:\/\/pbs.twimg.com\/media\/B9A0J0SIAAA667g.jpg"
               ],
               "positiveSentiment":0.998402437945798,
               "process_version":"20140909T120800Z",
               "twitterCountryCode":"US",
               "twitterLanguage":null,
               "device":"Twitter for iPhone",
               "created":"2015-02-04T16:12:56.000Z",
               "geo":{
                  "lat":37.795538,
                  "lon":-122.417207
               },
               "actorDisplayName":"Salesforce #dreamjob",
               "listedCount":449,
               "exactGeo":"true",
               "verb":"post",
               "countryCode":"United States",
               "statusesCount":3104,
               "id":"563007306041131010",
               "actorLanguages":[
                  "en"
               ],
               "actorId":"29833504",
               "placeGeoType":"Polygon"
            }
         },
         {
            "_index":"orbit-2015-02-04",
            "_type":"tweet",
            "_id":"563004420758466561",
            "_score":1.0,
            "_source":{
               "text":"Opened Street or Sidewalk Cleaning request via iphone at 1101 Ocean Ave http:\/\/t.co\/TGSNxxzc6K. Vacuum.",
               "screenName":"SF311Reports",
               "loc_hash":"9q8yt7rg13tbmgtsz54w",
               "retweets":null,
               "gnipLanguage":"en",
               "friendsCount":0,
               "actorDescription":"This is account is not monitored and is used to post service request update information. To communicate with SF311, please use our main account 'SF311'",
               "followersCount":6,
               "negativeSentiment":0.029913927914585706,
               "favoritesCount":0,
               "positiveSentiment":0.9700860720854143,
               "process_version":"20140909T120800Z",
               "twitterCountryCode":"US",
               "twitterLanguage":null,
               "device":"Spot Reporters Server",
               "created":"2015-02-04T16:01:28.000Z",
               "geo":{
                  "lat":37.723454,
                  "lon":-122.453895
               },
               "actorDisplayName":"SF311 Reports",
               "listedCount":0,
               "exactGeo":"true",
               "verb":"post",
               "countryCode":"United States",
               "statusesCount":141538,
               "id":"563004420758466561",
               "actorLanguages":[
                  "en"
               ],
               "actorId":"1589692776",
               "placeGeoType":"Polygon"
            }
         },
         {
            "_index":"orbit-2015-02-04",
            "_type":"tweet",
            "_id":"563006559509577729",
            "_score":1.0,
            "_source":{
               "text":"@seeson Have you picked up H1Z1 yet?",
               "screenName":"FemSteph",
               "loc_hash":"9q8yyjn68p5qhwng7jjk",
               "retweets":null,
               "gnipLanguage":"en",
               "friendsCount":542,
               "actorDescription":"I may or may not have an obsession with shoes, video games and mashed potatoes. I work in the vidya gamez.",
               "followersCount":4261,
               "negativeSentiment":0.030395179989584107,
               "favoritesCount":0,
               "positiveSentiment":0.9696048200104159,
               "userMentions":[
                  "17526132:seeson"
               ],
               "process_version":"20140909T120800Z",
               "twitterCountryCode":"US",
               "twitterLanguage":null,
               "device":"Twitter for iPhone",
               "created":"2015-02-04T16:09:58.000Z",
               "geo":{
                  "lat":37.776957,
                  "lon":-122.423053
               },
               "actorDisplayName":"FemSteph",
               "listedCount":112,
               "exactGeo":"true",
               "verb":"post",
               "countryCode":"United States",
               "statusesCount":6308,
               "id":"563006559509577729",
               "actorLanguages":[
                  "en"
               ],
               "actorId":"58714972",
               "placeGeoType":"Polygon"
            }
         },
         {
            "_index":"orbit-2015-02-04",
            "_type":"tweet",
            "_id":"563007387997843456",
            "_score":1.0,
            "_source":{
               "text":"@MurrayRGJ hopefully many more surprises to come! (In a good way of course).",
               "screenName":"NevadaSportsGuy",
               "loc_hash":"9q8yyymh68fhjnhjuet3",
               "retweets":null,
               "gnipLanguage":"en",
               "friendsCount":31,
               "actorDescription":"Sharing personal thoughts on the University of Nevada Wolfpack athletics.",
               "followersCount":9,
               "negativeSentiment":0.06443123548352578,
               "favoritesCount":0,
               "positiveSentiment":0.9355687645164742,
               "userMentions":[
                  "40287046:Chris Murray"
               ],
               "process_version":"20140909T120800Z",
               "twitterCountryCode":"US",
               "twitterLanguage":null,
               "device":"Twitter for iPhone",
               "created":"2015-02-04T16:13:16.000Z",
               "geo":{
                  "lat":37.78409,
                  "lon":-122.391705
               },
               "actorDisplayName":"NevadaSportsGuy",
               "listedCount":3,
               "exactGeo":"true",
               "verb":"post",
               "countryCode":"United States",
               "statusesCount":26,
               "id":"563007387997843456",
               "actorLanguages":[
                  "en"
               ],
               "actorId":"2958783410",
               "placeGeoType":"Polygon"
            }
         }
      ]
   }
}"""
        csv_element = CSVOutput(left=-112.509461, bottom=37.701051, right=37.815197, top=37.815197, polygon=None)
        query = InsightCloudQuery(None, None)
        query.process_twitter_data(json_data, csv_element)
        self.assertEqual(csv_element.num_twitter, 1541190)