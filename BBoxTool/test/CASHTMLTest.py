import unittest
from CASHTMLParser import CASFormHTMLParser

class CASHTMLTest(unittest.TestCase):
    def test_parse(self):
        html_data = """

    <style>
        .error {
            padding: 15px;
            margin-bottom: 20px;
            border: 1px solid transparent;
            border-radius: 4px;
            color: #a94442;
            background-color: #f2dede;
            border-color: #ebccd1;
            width: 300px;
            margin: 10px auto;
            text-align: center;
        }

        .msg {
            padding: 15px;
            margin-bottom: 20px;
            border: 1px solid transparent;
            border-radius: 4px;
            color: #31708f;
            background-color: #d9edf7;
            border-color: #bce8f1;
            width: 300px;
            margin: 10px auto;
            text-align: center;
        }

        body {
            background: #fefefe;
            color: #fefefe;
            font-family: Arial, Helvetica, sans-serif;
        }

        .logo-container {
            text-align: left;
            width: 100%;
        }
        .dg-logo {
            height: 50px;
            width: 150px;
        }
        .title-container {
            font-size: 3.5em;
            text-align: center;
        }
        .login-container{
            height:70%;
            width:300px;
            margin: auto;
            background-color:#004671;
            padding:30px;
        }
        .login-box {
            width: 275px;
            margin-top:40px;
            margin: 10px auto;
            background: #004671;
            text-align: right;

        }

        .input-value {
            margin: 10px auto;
        }
        .green-stripe {
            width:100%;
            height:200px;
            background-color:#709900;
        }

    </style>


<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">








<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
	<head>
	    <title>CAS &#8211; Central Authentication Service</title>


        <link type="text/css" rel="stylesheet" href="/cas/css/cas.css;jsessionid=xtMJ2IicJdAKg1yZuTa3C-Qv.node1" />
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
	    <link rel="icon" href="/cas/favicon.ico;jsessionid=xtMJ2IicJdAKg1yZuTa3C-Qv.node1" type="image/x-icon" />
	</head>
	<body id="cas" class="fl-theme-iphone">
    <div class="flc-screenNavigator-view-container">
        <div class="fl-screenNavigator-view">
            <div class="logo-container">
                <img class="dg-logo" src="/cas/images/logo_dg.png;jsessionid=xtMJ2IicJdAKg1yZuTa3C-Qv.node1" />
            </div>
            <br/>
            <br/>
            <br/>
            <br/>
            <div class="title-container">
                    <span style="font-size: 35px; color:#709900; ">Insight Explorer</span>
            </div>
            <br/>
            <br/>
            <div id="content" class="fl-screenNavigator-scroll-container">



  <div class="box fl-panel" id="login">
			<form id="fm1" class="fm-v clearfix" action="/cas/login?service=https%3A%2F%2Fiipbeta.digitalglobe.com%2Finsight-vector%2Fj_spring_cas_security_check" method="post">

                <!-- Congratulations on bringing CAS online!  The default authentication handler authenticates where usernames equal passwords: go ahead, try it out. -->
                    <h2>Enter your Username and Password</h2>
                    <div class="row fl-controls-left">
                        <label for="username" class="fl-label"><span class="accesskey">U</span>sername:</label>




						<input id="username" name="username" class="required" tabindex="1" accesskey="u" type="text" value="" size="25" autocomplete="false"/>

                    </div>
                    <div class="row fl-controls-left">
                        <label for="password" class="fl-label"><span class="accesskey">P</span>assword:</label>


						<input id="password" name="password" class="required" tabindex="2" accesskey="p" type="password" value="" size="25" autocomplete="off"/>
                    </div>
                    <div class="row check">
                        <input id="warn" name="warn" value="true" tabindex="3" accesskey="w" type="checkbox" />
                        <label for="warn"><span class="accesskey">W</span>arn me before logging me into other sites.</label>
                    </div>
                    <div class="row btn-row">
						<input type="hidden" name="lt" value="LT-703-0uXsfis9g7qYcXvaz0fPSNUJpxaPYc" />
						<input type="hidden" name="execution" value="e1s1" />
						<input type="hidden" name="_eventId" value="submit" />

                        <input class="btn-submit" name="submit" accesskey="l" value="LOGIN" tabindex="4" type="submit" />
                        <input class="btn-reset" name="reset" accesskey="c" value="CLEAR" tabindex="5" type="reset" />
                    </div>
            </form>
    </div>"""
        parser = CASFormHTMLParser()
        parser.feed(html_data)
        # test lt data in hidden data
        self.assertTrue('lt' in parser.hidden_data)
        self.assertEqual(parser.hidden_data['lt'], 'LT-703-0uXsfis9g7qYcXvaz0fPSNUJpxaPYc')
        # test execution
        self.assertTrue('execution' in parser.hidden_data)
        self.assertEqual(parser.hidden_data['execution'], 'e1s1')
        # test _eventId
        self.assertTrue('_eventId' in parser.hidden_data)
        self.assertEqual(parser.hidden_data['_eventId'], 'submit')
        # test action
        self.assertIsNotNone(parser.action)
        self.assertEqual(parser.action, '/cas/login?service=https%3A%2F%2Fiipbeta.digitalglobe.com%2Finsight-vector%2Fj_spring_cas_security_check')