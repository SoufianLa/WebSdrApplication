# -*-coding: utf-8 -*-
from __future__ import division
from twisted.internet import reactor, threads
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.enterprise import adbapi
from twisted.web.server import NOT_DONE_YET
from twisted.internet.task import deferLater
from twisted.internet import task
from twisted.web.static import File
from twisted.web import static, twcgi
from rtlsdr import *
from time import time
from time import *
import sqlite3
from pylab import *
import sys
from bottle import request
import cgi
from cgi import *
import string
import json
from twisted.python import log
import os
import socket
#import MySQLdb
form = cgi.FieldStorage()
filename = "toto"
dbpool = adbapi.ConnectionPool("sqlite3", filename, check_same_thread=False)
src_url = """<link href="scripts/bootstrap.min.css" rel="stylesheet" /><script type="text/javascript" src="scripts/jquery-1.11.2.min.js"></script><script type="text/javascript" src="scripts/bootstrap.min.js"></script><script type="text/javascript" src="scripts/angular.min.js"></script>"""
if os.name != "nt":
    import fcntl
    import struct

    def get_interface_ip(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s',ifname[:15]))[20:24])
def get_lan_ip():
    ip = socket.gethostbyname(socket.gethostname())
    if ip.startswith("127.") and os.name != "nt":
        interfaces = [
            "eth0",
            "eth1",
            "eth2",
            "wlan0",
            "wlan1",
            "wifi0",
            "ath0",
            "ath1",
            "ppp0",
            ]
        for ifname in interfaces:
            try:
                ip = get_interface_ip(ifname)
                break
            except IOError:
                pass
    return ip
############################################################################################################
#RETRIEVE ALL FREQUIENCIES FROM MONITOR TABLE 
############################################################################################################
class DatabasePage(Resource):
    isLeaf = True
    def render_POST(self, request):
        global password, username
        password = cgi.escape(request.args["password"][0])
        username = cgi.escape(request.args["username"][0])
        def _getresult(txn):
            txn.execute("SELECT f, ts, tp, value, id FROM alarms order by id desc")
            result1 = txn.fetchall()
            txn.execute("SELECT f, description, time, statut, highthreshold, lowthreshold  FROM monitor")
            result2 = txn.fetchall()
            txn.execute("SELECT f  FROM monitor where statut like 'ON' ")
            result3 = txn.fetchall()
            txn.execute("SELECT highthreshold, lowthreshold FROM monitor INNER JOIN alarms ON monitor.f = alarms.f order  by  alarms.id desc")
            result4 = txn.fetchall()
            txn.execute("SELECT user, password FROM credential")
            result5 = txn.fetchall()
            return result1, result2, result3, result4, result5 
        def getresult():
            return dbpool.runInteraction(_getresult)
        def onResult(data):
            global user, passpass
            frequency = list()
            descriptions = list()
            ti = list()
            st = list()
            highthreshold = list()
            lowthreshold = list()
            frequency_alarms = list()
            time_alarms = list()
            situation_alarms = list()
            value_alarms = list()
            frequency_ON = list()
            id_alarms = list()
            highthreshold_alarms = list()
            lowthreshold_alarms = list()
            user = list()
            passpass = list()
            for row in data[0]:
                frequency_alarms.append(row[0])
                time_alarms.append( row[1])
                situation_alarms.append( row[2])
                value_alarms.append( row[3])
                id_alarms.append( row[4])
            for row in data[1]:
                frequency.append( row[0] )
                descriptions.append( row[1] )
                ti.append( row[2] )
                st.append( row[3] )
                highthreshold.append( row[4] )
                lowthreshold.append( row[5] )
            for row in data[2]:
                frequency_ON.append( row[0] )
            for row in data[3]:
                highthreshold_alarms.append( row[0] )
                lowthreshold_alarms.append( row[1] )
            for row in data[4]:
                user.append( row[0] )
                passpass.append( row[1] )

            #frequency = json.dumps(frequency)
            frequency_ON = json.dumps(frequency_ON)
            table_frequencies = """<div class="panel panel-primary" id="delfrequencies" ><div class="panel-heading"><b>Frequencies : </b></div><div class="panel-body"><div class="table-responsive" id ="showfrequencies"><table class="table"><thead><tr class=""><th>frequency</th><th><center>Description</center></th><th><center>Time</center></th><th>Status</th><th><center>Lowthreshold</center></th><th><center>Highthreshold</center></th></tr></thead><tbody>"""
            del_frequencies ="""<div class="panel panel-primary" id="delfrequencies" ><div class="panel-heading"><b>Delete Frequency : </b></div><div class="panel-body"><form action="/del" method="GET" ><label>Frequency (MHz) :  </label><SELECT  class="form-control" name="form-field0" size="1" type="float" >"""
            change_ON_OFF = """<div class="panel panel-primary" id="changestate" ><div class="panel-heading"><b>Change the state (ON/OFF)</b></div><div class="panel-body"><form action="/change" method="GET"><label>Frequency :</label><SELECT  class="form-control" name="form-field0" size="1" type="float">"""
            show_graphs = """<div class="panel panel-primary" id="showgraphs" ><div class="panel-heading"><b>show graphs :</b></div><div class="panel-body"><form  action="/sg" method="GET"><label>Frequency :</label><SELECT class="form-control" name="form-field0" size="1" type="float">"""
            frequecy_html =""
            make_threshold = """<div class="panel panel-primary" id="make_threshold" ><div class="panel-heading"><b>Monitoring with alarms parameters:</b></div><div class="panel-body"><form action="/parameterswithalarms" method="GET"><label>Frequency (MHz) :</label><SELECT  class="form-control" name="form-field0" size="1" type="float" >"""
            for i in range(len(frequency)):
                table_frequencies += "<tr><td><b>" + str(frequency[i]) +" MHz </b></td><td><b><center>" +str(descriptions[i])+ "</center></b></td><td><b><center>" +str(ti[i])+ "</center></b></td><td><b>" + str(st[i]) + "</b></td><td><center><b>" + str(lowthreshold[i]) + "</b></center></td><td><center><b>" + str(highthreshold[i]) + "</b></center></td></tr>"
                frequecy_html += "<option>"+str(frequency[i])+"</option>"
            del_frequencies += frequecy_html
            change_ON_OFF += frequecy_html
            show_graphs += frequecy_html
            make_threshold += frequecy_html
            table_frequencies += "</tbody></table></div></div></div>"
            del_frequencies += """</SELECT><br><button  class="btn btn-primary" type="submit" value="delete Frequency" size="1" ><b>Delete Frequency</b></button></form></div></div>"""
            add_frequencies ="""<div class="panel panel-primary" id="addfrequencies"><div class="panel-heading"><b>Add Frequency</b></div><div class="panel-body"><form action="/add" method="GET"><label for="formGroupExampleInput">Frequency :</label><input type="float" class="form-control" name="form-field0"  placeholder="type the frequency in Mhz" ><label for="formGroupExampleInput">Description :</label><input type="string" class="form-control" placeholder="type the description" name="form-field1"   ><label>State : </label><select name = "form-field2" size = "1" class="form-control" ><option selected>Choose the state </option><option>ON</option><option>OFF</option></select><br><button class="btn btn-primary"><b>Add frequency </b></button></form></div></div>"""
            change_ON_OFF += """</SELECT><label> State : </label><select name = "form-field2" size = "1" class="form-control" ><option selected>Choose the state </option><option>ON</option><option>OFF</option></select><br><button class="btn btn-primary"><b> Change(ON/OFF) </b></button></form></div></div>"""
            show_graphs += """</SELECT><br><button class="btn btn-primary" type="submit" value="Show Graph" size="1"><b>Show Graph</b></button></form></div></div>"""
            make_threshold += """</select><label >Low Threshold (DB):</label><input type="float" class="form-control" placeholder="type the Low threshold" name="form-field1" ><label>High Threshold (DB) : </label><input type="float" class="form-control" placeholder="type the High threshold" name="form-field3" ><br><input type="submit" name="action" value="Make Thresholds" class="btn btn-primary" /><br><hr class="divider"><label>Duration (sec): </label><input type="float" class="form-control"  name="form-field4" placeholder="Type the duration before alarms in seconde"><br><input type="submit" name="action" value="Make the duration" class="btn btn-primary" /><hr class="divider"><input type="submit" name="action" value="Begin Surveillance" class="btn btn-primary" /></form></div></div>"""
            texto_html = """<table class="table"><thead><tr><th><center>Frequency</center></th><th><center>type</center></th><th><center>LowThreshold</center></th><th><center>HighThreshold</center></th><th><center>Power level(DB)</center></th><th><center>Time</center></th></tr></thead><tbody><tbody>"""
            Alarm_notif = """<ul class="dropdown-menu" id ="messages">"""
            for i in range(3):
                try:
                    if frequency_alarms[i]:
                        if situation_alarms[i].endswith("begining.."):
                            Alarm_notif += """<li class="list-group-item list-group-item-danger"><a href="#" >"""+str(frequency_alarms[i])+""" Mhz :"""+str(situation_alarms[i])+""" at """+str(time_alarms[i])+"""</a></li>"""
                        elif situation_alarms[i].startswith("Low Alarm finished"):
                            Alarm_notif += """<li class="list-group-item list-group-item-success"><a href="#" >"""+str(frequency_alarms[i])+""" Mhz :"""+str(situation_alarms[i])+""" at """+str(time_alarms[i])+"""</a></li>"""
                except IndexError:
                    Alarm_notif += ''
            if password in passpass and username in user:
                request.write("""<!DOCTYPE html>
                             <html>
                             <title> SDR Monitoring..</title>
                             <link rel="icon" type="image/png" href="scripts/logo_smallm.png">
                             <head><meta name="viewport" content="width=device-width, initial-scale=1">"""+str(src_url)+"""
                             <style>body {
                                    padding-top: 70px;
                                        }
                             .starter-template {
                                padding: 40px 15px;
                                text-align: center;
                             }</style>
                             <style>
                             #mycontent {
                                height: 100px;
                            }
                            .active a {
                                border: 2px solid black;
                            }
                            ul.nav-pills {
                              top: 207px;
                              position: fixed;
                            }
                             </style>
                             <script type="text/javascript" src="scripts/notifjs.js"></script>
                             <script>
                             function zeroNumber(){                                
                             if(document.getElementById('number').innerHTML==0){
                                document.getElementById('box').style.display="none";
                             }else{
                                document.getElementById('box').style.display="block";
                             }}
                             function RazNumber(){
                                document.getElementById('number').innerHTML=0;
                                zeroNumber();
                             }
                             function decreaseNumber(){
                                n = n-1;
                                document.getElementById('number').innerHTML=n;
                                zeroNumber();
                                  }
                             </script>
                             </head>
                             <style type="text/css">
                             #box{
                                width:25px;
                                height:20px;
                                background: red;
                                position: fixed;
                                left:729px;
                                top:0;
                                z-index: 9999;
                                border-radius: 10px;
                                color: white;
                             }
                             #number{
                                text-align: center;
                             }
                             .dropdown-menu {
                                max-height: 340px;
                                overflow-y: scroll;
                             }
                             .pull-left{
                                width:60px;
                                height:51px;
                                position: fixed;
                                left:0.25px;
                                top:1.75px;
                             }
                             #logout{

                                position: fixed;
                                left:1225px;
                                top:0;
                             }
                             </style>
                             </head>
                             <body onload=zeroNumber() data-spy="scroll" data-target="#sidebar" data-spy="affix" data-offset-top="28">
                             <nav class="navbar navbar-inverse navbar-fixed-top">
                             <a href="#" class="pull-left"><img src="scripts/logo_smallm.png" width="60" height="51" hspace="1" style=" margin-top: 1px; margin-buttum: 10px;"></a> 
                             <div class="container">
                             <div class="navbar-header">
                             <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                             <span class="sr-only">Toggle navigation</span>
                             <span class="icon-bar"></span>
                             <span class="icon-bar"></span>
                             <span class="icon-bar"></span>
                             </button>
                             <a class="navbar-brand" href="/sl">HACA SDR</a>
                             </div>
                             <div id="navbar" class="collapse navbar-collapse">              
                             <ul class="nav navbar-nav">
                             <li class="active"><a href="/db"><b>Surveillance</b></a></li>
                             <li class="dropdown"><a class="dropdown-toggle" data-toggle="dropdown" href="#"><b>Ploting and updating</b><span class="caret"></span></a><ul class="dropdown-menu"><li><a href="/form"><b>Band of frequencies</b></a></li><li role="presentation" class="divider"></li><li><a href="/parametersonefres"><b>One frequency</b></a></li></ul></li>
                             <li><a href="/hom" ><b>Recording history</b></a></li>
                             <li class="dropdown scrollable"><a class="dropdown-toggle" data-toggle="dropdown" onclick="RazNumber()"><b>Alarms</b><span class="caret"></span></a>"""+str(Alarm_notif)+"""<li><a href="/disall"><center>Display all</center></a></li></ul></li>
                             <li><a href="/somestatistics"><b>Statistics</b></a></li>
                             <li><a href="http://"""+str(get_lan_ip())+""":8001/streaming/" onclick="window.open('http://"""+str(get_lan_ip())+""":8001/streaming/', 'exemple', 'height=600, width=800, top=90, left=350, toolbar=no, menubar=no, location=yes, resizable=yes, scrollbars=yes, status=no'); return false;"><b>Real Time Streaming</b></a></li>
                             <li id="logout"><a href="/logout"><i class="glyphicon glyphicon-lock"></i> <b>Logout</b></a></li>
                             </ul>              
                             </div>
                             </div>
                             </nav>
                             <div id="box"><p id="number">0</p></div>
                             <div class="container">
                             <div class="page-header">
                             <h1>Parameters Concerning Surveillance :</h1>      
                             </div>
                            <nav class="col-sm-3" id="sidebar">
                              <ul class="nav nav-pills nav-stacked">
                                <li class="active"><a href="#showfrequencies">Show frequencies</a></li>
                                <li><a href="#addfrequencies">Add frequency</a></li>
                                <li><a href="#delfrequencies">Delete frequiency</a></li>
                                <li><a href="#changestate">Change State(ON/OFF)</a></li>
                                <li><a href="#showgraphs">Show graph</a></li>
                                <li class="dropdown">
                                <a class="dropdown-toggle" data-toggle="dropdown" href="#">Start Montoring <span class="caret"></span></a>
                                <ul class="dropdown-menu">
                                    <li><a href="#make_threshold">With Alarms</a></li>
                                    <li><a href="/ch">Without Alarms</a></li>                     
                                </ul>
                                </li>
                                <li><a href="/st">Stop Monitoring</a></li>
                              </ul>
                            </nav>
                            <div class="col-sm-9">
                             <br>
                             """+str(table_frequencies)+str(add_frequencies)+str(del_frequencies)+str(change_ON_OFF)+str(show_graphs)+str(make_threshold)+"""
                             
                             </div>
                             </div>
                             </div>
                             </div>
                             </body>
                             </html>""")
            else:
                request.write("""
                            <!DOCTYPE html>
                            <html>
                            <title> SDR Monitoring..</title>
                            <link rel="icon" type="image/png" href="scripts/logo_smallm.png">
                            <head>"""+str(src_url)+"""
                            <style>
                            body, html {
                                height: 100%;
                                background-repeat: no-repeat;
                                background-image: linear-gradient(rgb(104, 145, 162), rgb(12, 97, 33));
                            }

                            .card-container.card {
                                width: 350px;
                                padding: 40px 40px;
                            }

                            .btn {
                                font-weight: 700;
                                height: 36px;
                                -moz-user-select: none;
                                -webkit-user-select: none;
                                user-select: none;
                                cursor: default;
                            }
                            .card {
                                background-color: #F7F7F7;
                                /* just in case there no content*/
                                padding: 20px 25px 30px;
                                margin: 0 auto 25px;
                                margin-top: 50px;
                                /* shadows and rounded borders */
                                -moz-border-radius: 2px;
                                -webkit-border-radius: 2px;
                                border-radius: 2px;
                                -moz-box-shadow: 0px 2px 2px rgba(0, 0, 0, 0.3);
                                -webkit-box-shadow: 0px 2px 2px rgba(0, 0, 0, 0.3);
                                box-shadow: 0px 2px 2px rgba(0, 0, 0, 0.3);
                            }

                            .profile-img-card {
                                width: 96px;
                                height: 96px;
                                margin: 0 auto 10px;
                                display: block;
                                -moz-border-radius: 50%;
                                -webkit-border-radius: 50%;
                                border-radius: 50%;
                            }
                            .profile-name-card {
                                font-size: 16px;
                                font-weight: bold;
                                text-align: center;
                                margin: 10px 0 0;
                                min-height: 1em;
                            }
                            .reauth-email {
                                display: block;
                                color: #404040;
                                line-height: 2;
                                margin-bottom: 10px;
                                font-size: 14px;
                                text-align: center;
                                overflow: hidden;
                                text-overflow: ellipsis;
                                white-space: nowrap;
                                -moz-box-sizing: border-box;
                                -webkit-box-sizing: border-box;
                                box-sizing: border-box;
                            }
                            .form-signin #inputEmail,
                            .form-signin #inputPassword {
                                direction: ltr;
                                height: 44px;
                                font-size: 16px;
                            }
                            .form-signin input[type=email],
                            .form-signin input[type=password],
                            .form-signin input[type=text],
                            .form-signin button {
                                width: 100%;
                                display: block;
                                margin-bottom: 10px;
                                z-index: 1;
                                position: relative;
                                -moz-box-sizing: border-box;
                                -webkit-box-sizing: border-box;
                                box-sizing: border-box;
                            }
                            .form-signin .form-control:focus {
                                border-color: rgb(104, 145, 162);
                                outline: 0;
                                -webkit-box-shadow: inset 0 1px 1px rgba(0,0,0,.075),0 0 8px rgb(104, 145, 162);
                                box-shadow: inset 0 1px 1px rgba(0,0,0,.075),0 0 8px rgb(104, 145, 162);
                            }
                            .btn-signin {
                                /*background-color: #4d90fe; */
                                background-color: rgb(104, 145, 162);
                                /* background-color: linear-gradient(rgb(104, 145, 162), rgb(12, 97, 33));*/
                                padding: 0px;
                                font-weight: 700;
                                font-size: 14px;
                                height: 36px;
                                -moz-border-radius: 3px;
                                -webkit-border-radius: 3px;
                                border-radius: 3px;
                                border: none;
                                -o-transition: all 0.218s;
                                -moz-transition: all 0.218s;
                                -webkit-transition: all 0.218s;
                                transition: all 0.218s;
                            }

                            .btn-signin:hover,
                            .btn-signin:active,
                            .btn-signin:focus {
                                background-color: rgb(12, 97, 33);
                            }

                            .forgot-password {
                                color: rgb(104, 145, 162);
                            }

                            .forgot-password:hover,
                            .forgot-password:active,
                            .forgot-password:focus{
                                color: rgb(12, 97, 33);
                            }
                            </style>
                            <script type="text/javascript">
                            function supportsHTML5Storage() {
                                try {
                                    return 'localStorage' in window && window['localStorage'] !== null;
                                } catch (e) {
                                    return false;
                                }
                            }

                            /**
                             * Test data. This data will be safe by the web app
                             * in the first successful login of a auth user.
                             * To Test the scripts, delete the localstorage data
                             * and comment this call.
                             *
                             * @returns {boolean}
                             */
                            function testLocalStorageData() {
                                if(!supportsHTML5Storage()) { return false; }
                                localStorage.setItem("PROFILE_IMG_SRC", "//lh3.googleusercontent.com/-6V8xOA6M7BA/AAAAAAAAAAI/AAAAAAAAAAA/rzlHcD0KYwo/photo.jpg?sz=120" );
                                localStorage.setItem("PROFILE_NAME", "César Izquierdo Tello");
                                localStorage.setItem("PROFILE_REAUTH_EMAIL", "oneaccount@gmail.com");
                            }
                            </script>
                            <head>
                            <body>
                            <div class="container">
                            <div class="card card-container">
                                <!-- <img class="profile-img-card" src="scripts/logo_smallm.png" alt="" /> -->
                                <img id="profile-img" class="profile-img-card" src="//ssl.gstatic.com/accounts/ui/avatar_2x.png" />
                                <p id="profile-name" class="profile-name-card"></p>
                                <div class="alert alert-error">
                                <a class="close" data-dismiss="alert" href="#">Incorrect Username or Password!</a>
                                </div>
                                <form class="form-signin" action="/home" method="POST">
                                    <span id="reauth-email" class="reauth-email"></span>
                                    <input type="string" name="username" id="inputEmail" class="form-control" placeholder="UserName" required autofocus>
                                    <input type="password" name="password" id="inputPassword" class="form-control" placeholder="Password" required>
                                    <div id="remember" class="checkbox">
                                        <label>
                                            <input type="checkbox" value="remember-me"> Remember me
                                        </label>
                                    </div>
                                    <button class="btn btn-lg btn-primary btn-block btn-signin" type="submit">Sign in</button>
                                </form><!-- /form -->

                            </div><!-- /card-container -->
                        </div><!-- /container -->
                            </body>
                            </html>
                    """)
            request.finish()

        d= getresult()
        d.addCallback(onResult)

        return NOT_DONE_YET
class Home(Resource):
    isLeaf = False
    def render_GET(self, request):
        global password, username, user, passpass
        def _getresult(txn):
            txn.execute("SELECT f, ts, tp, value, id FROM alarms order by id desc")
            result1 = txn.fetchall()
            txn.execute("SELECT f, description, time, statut, highthreshold, lowthreshold  FROM monitor")
            result2 = txn.fetchall()
            txn.execute("SELECT f  FROM monitor where statut like 'ON' ")
            result3 = txn.fetchall()
            txn.execute("SELECT highthreshold, lowthreshold FROM monitor INNER JOIN alarms ON monitor.f = alarms.f order  by  alarms.id desc")
            result4 = txn.fetchall()
            return result1, result2, result3, result4
        def getresult():
            return dbpool.runInteraction(_getresult)
        def onResult(data):
            frequency = list()
            descriptions = list()
            ti = list()
            st = list()
            highthreshold = list()
            lowthreshold = list()
            frequency_alarms = list()
            time_alarms = list()
            situation_alarms = list()
            value_alarms = list()
            frequency_ON = list()
            id_alarms = list()
            highthreshold_alarms = list()
            lowthreshold_alarms = list()
            for row in data[0]:
                frequency_alarms.append(row[0])
                time_alarms.append( row[1])
                situation_alarms.append( row[2])
                value_alarms.append( row[3])
                id_alarms.append( row[4])
            for row in data[1]:
                frequency.append( row[0] )
                descriptions.append( row[1] )
                ti.append( row[2] )
                st.append( row[3] )
                highthreshold.append( row[4] )
                lowthreshold.append( row[5] )
            for row in data[2]:
                frequency_ON.append( row[0] )
            for row in data[3]:
                highthreshold_alarms.append( row[0] )
                lowthreshold_alarms.append( row[1] )
            #frequency = json.dumps(frequency)
            frequency_ON = json.dumps(frequency_ON)
            table_frequencies = """<div class="panel panel-primary" id="delfrequencies" ><div class="panel-heading"><b>Frequencies : </b></div><div class="panel-body"><div class="table-responsive" id ="showfrequencies"><table class="table"><thead><tr class=""><th>frequency</th><th><center>Description</center></th><th><center>Time</center></th><th>Status</th><th><center>Lowthreshold</center></th><th><center>Highthreshold</center></th></tr></thead><tbody>"""
            del_frequencies ="""<div class="panel panel-primary" id="delfrequencies" ><div class="panel-heading"><b>Delete Frequency : </b></div><div class="panel-body"><form action="/del" method="GET" ><label>Frequency (MHz) :  </label><SELECT  class="form-control" name="form-field0" size="1" type="float" >"""
            change_ON_OFF = """<div class="panel panel-primary" id="changestate" ><div class="panel-heading"><b>Change the state (ON/OFF)</b></div><div class="panel-body"><form action="/change" method="GET"><label>Frequency :</label><SELECT  class="form-control" name="form-field0" size="1" type="float">"""
            show_graphs = """<div class="panel panel-primary" id="showgraphs" ><div class="panel-heading"><b>show graphs :</b></div><div class="panel-body"><form  action="/sg" method="GET"><label>Frequency :</label><SELECT class="form-control" name="form-field0" size="1" type="float">"""
            frequecy_html =""
            make_threshold = """<div class="panel panel-primary" id="make_threshold" ><div class="panel-heading"><b>Monitoring with alarms parameters:</b></div><div class="panel-body"><form action="/parameterswithalarms" method="GET"><label>Frequency (MHz) :</label><SELECT  class="form-control" name="form-field0" size="1" type="float" >"""
            for i in range(len(frequency)):
                table_frequencies += "<tr><td><b>" + str(frequency[i]) +" MHz </b></td><td><b><center>" +str(descriptions[i])+ "</center></b></td><td><b><center>" +str(ti[i])+ "</center></b></td><td><b>" + str(st[i]) + "</b></td><td><center><b>" + str(lowthreshold[i]) + "</b></center></td><td><center><b>" + str(highthreshold[i]) + "</b></center></td></tr>"
                frequecy_html += "<option>"+str(frequency[i])+"</option>"
            del_frequencies += frequecy_html
            change_ON_OFF += frequecy_html
            show_graphs += frequecy_html
            make_threshold += frequecy_html
            table_frequencies += "</tbody></table></div></div></div>"
            del_frequencies += """</SELECT><br><button  class="btn btn-primary" type="submit" value="delete Frequency" size="1" ><b>Delete Frequency</b></button></form></div></div>"""
            add_frequencies ="""<div class="panel panel-primary" id="addfrequencies"><div class="panel-heading"><b>Add Frequency</b></div><div class="panel-body"><form action="/add" method="GET"><label for="formGroupExampleInput">Frequency :</label><input type="float" class="form-control" name="form-field0"  placeholder="type the frequency in Mhz" ><label for="formGroupExampleInput">Description :</label><input type="string" class="form-control" placeholder="type the description" name="form-field1"   ><label>State : </label><select name = "form-field2" size = "1" class="form-control" ><option selected>Choose the state </option><option>ON</option><option>OFF</option></select><br><button class="btn btn-primary"><b>Add frequency </b></button></form></div></div>"""
            change_ON_OFF += """</SELECT><label> State : </label><select name = "form-field2" size = "1" class="form-control" ><option selected>Choose the state </option><option>ON</option><option>OFF</option></select><br><button class="btn btn-primary"><b> Change(ON/OFF) </b></button></form></div></div>"""
            show_graphs += """</SELECT><br><button class="btn btn-primary" type="submit" value="Show Graph" size="1"><b>Show Graph</b></button></form></div></div>"""
            make_threshold += """</select><label >Low Threshold (DB):</label><input type="float" class="form-control" placeholder="type the Low threshold" name="form-field1" ><label>High Threshold (DB) : </label><input type="float" class="form-control" placeholder="type the High threshold" name="form-field3" ><br><input type="submit" name="action" value="Make Thresholds" class="btn btn-primary" /><br><hr class="divider"><label>Duration (sec): </label><input type="float" class="form-control"  name="form-field4" placeholder="Type the duration before alarms in seconde"><br><input type="submit" name="action" value="Make the duration" class="btn btn-primary" /><hr class="divider"><input type="submit" name="action" value="Begin Surveillance" class="btn btn-primary" /></form></div></div>"""
            texto_html = """<table class="table"><thead><tr><th><center>Frequency</center></th><th><center>type</center></th><th><center>LowThreshold</center></th><th><center>HighThreshold</center></th><th><center>Power level(DB)</center></th><th><center>Time</center></th></tr></thead><tbody><tbody>"""
            Alarm_notif = """<ul class="dropdown-menu" id ="messages">"""
            for i in range(3):
                try:
                    if frequency_alarms[i]:
                        if situation_alarms[i].endswith("begining.."):
                            Alarm_notif += """<li class="list-group-item list-group-item-danger"><a href="#" >"""+str(frequency_alarms[i])+""" Mhz :"""+str(situation_alarms[i])+""" at """+str(time_alarms[i])+"""</a></li>"""
                        elif situation_alarms[i].startswith("Low Alarm finished"):
                            Alarm_notif += """<li class="list-group-item list-group-item-success"><a href="#" >"""+str(frequency_alarms[i])+""" Mhz :"""+str(situation_alarms[i])+""" at """+str(time_alarms[i])+"""</a></li>"""
                except IndexError:
                    Alarm_notif += ''
            if password in passpass and username in user:
                request.write("""<!DOCTYPE html>
                             <html>
                             <title> SDR Monitoring..</title>
                             <link rel="icon" type="image/png" href="scripts/logo_smallm.png">
                             <head>"""+str(src_url)+"""
                             <style>body {
                                    padding-top: 70px;
                                        }
                             .starter-template {
                                padding: 40px 15px;
                                text-align: center;
                             }</style>
                             <style>
                             #mycontent {
                                height: 100px;
                            }
                            .active a {
                                border: 2px solid black;
                            }
                            ul.nav-pills {
                              top: 207px;
                              position: fixed;
                            }
                            #logout{
                            position: fixed;
                            left:1225px;
                            top:0;
                            }
                             </style>
                             <script type="text/javascript" src="scripts/notifjs.js"></script>
                             <script>
                             function zeroNumber(){                                
                             if(document.getElementById('number').innerHTML==0){
                                document.getElementById('box').style.display="none";
                             }else{
                                document.getElementById('box').style.display="block";
                             }}
                             function RazNumber(){
                                document.getElementById('number').innerHTML=0;
                                zeroNumber();
                             }
                             function decreaseNumber(){
                                n = n-1;
                                document.getElementById('number').innerHTML=n;
                                zeroNumber();
                                  }
                             </script>
                             </head>
                             <style type="text/css">
                             #box{
                                width:25px;
                                height:20px;
                                background: red;
                                position: fixed;
                                left:729px;
                                top:0;
                                z-index: 9999;
                                border-radius: 10px;
                                color: white;
                             }
                             #number{
                                text-align: center;
                             }
                             .dropdown-menu {
                                max-height: 340px;
                                overflow-y: scroll;
                             }
                             .pull-left{
                                width:60px;
                                height:51px;
                                position: fixed;
                                left:0.25px;
                                top:1.75px;
                             }
                             </style>
                             </head>
                             <body onload=zeroNumber() data-spy="scroll" data-target="#sidebar" data-spy="affix" data-offset-top="28">
                             <nav class="navbar navbar-inverse navbar-fixed-top">
                             <a href="#" class="pull-left"><img src="scripts/logo_smallm.png" width="60" height="51" hspace="1" style=" margin-top: 1px; margin-buttum: 10px;"></a> 
                             <div class="container">
                             <div class="navbar-header">
                             <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                             <span class="sr-only">Toggle navigation</span>
                             <span class="icon-bar"></span>
                             <span class="icon-bar"></span>
                             <span class="icon-bar"></span>
                             </button>
                             <a class="navbar-brand" href="/sl">HACA SDR</a>
                             </div>
                             <div id="navbar" class="collapse navbar-collapse">              
                             <ul class="nav navbar-nav">
                             <li class="active"><a href="/db"><b>Surveillance</b></a></li>
                             <li class="dropdown"><a class="dropdown-toggle" data-toggle="dropdown" href="#"><b>Ploting and updating</b><span class="caret"></span></a><ul class="dropdown-menu"><li><a href="/form"><b>Band of frequencies</b></a></li><li role="presentation" class="divider"></li><li><a href="/parametersonefres"><b>One frequency</b></a></li></ul></li>
                             <li><a href="/hom" ><b>Recording history</b></a></li>
                             <li class="dropdown scrollable"><a class="dropdown-toggle" data-toggle="dropdown" onclick="RazNumber()"><b>Alarms</b><span class="caret"></span></a>"""+str(Alarm_notif)+"""<li><a href="/disall"><center>Display all</center></a></li></ul></li>
                             <li><a href="/somestatistics"><b>Statistics</b></a></li>
                             <li><a href="http://"""+str(get_lan_ip())+""":8001/streaming/" onclick="window.open('http://"""+str(get_lan_ip())+""":8001/streaming/', 'exemple', 'height=600, width=800, top=90, left=350, toolbar=no, menubar=no, location=yes, resizable=yes, scrollbars=yes, status=no'); return false;"><b>Real Time Streaming</b></a></li>
                             <li id="logout"><a href="/logout"><i class="glyphicon glyphicon-lock"></i> <b>Logout</b></a></li>
                             </ul>              
                             </div>
                             </div>
                             </nav>
                             <div id="box"><p id="number">0</p></div>
                             <div class="container">
                             <div class="page-header">
                             <h1>Parameters Concerning Surveillance :</h1>      
                             </div>
                            <nav class="col-sm-3" id="sidebar">
                              <ul class="nav nav-pills nav-stacked">
                                <li class="active"><a href="#showfrequencies">Show frequencies</a></li>
                                <li><a href="#addfrequencies">Add frequency</a></li>
                                <li><a href="#delfrequencies">Delete frequiency</a></li>
                                <li><a href="#changestate">Change State(ON/OFF)</a></li>
                                <li><a href="#showgraphs">Show graph</a></li>
                                <li class="dropdown">
                                <a class="dropdown-toggle" data-toggle="dropdown" href="#">Start Montoring <span class="caret"></span></a>
                                <ul class="dropdown-menu">
                                    <li><a href="#make_threshold">With Alarms</a></li>
                                    <li><a href="/ch">Without Alarms</a></li>                     
                                </ul>
                                </li>
                                <li><a href="/st">Stop Monitoring</a></li>
                              </ul>
                            </nav>
                            <div class="col-sm-9">
                             <br>
                             """+str(table_frequencies)+str(add_frequencies)+str(del_frequencies)+str(change_ON_OFF)+str(show_graphs)+str(make_threshold)+"""
                             
                             </div>
                             </div>
                             </div>
                             </div>
                             </body>
                             </html>""")
            else:
                request.write("You have a problem with your crendential  !! Please try again with your authetification Interface ")
            request.finish()

        d= getresult()
        d.addCallback(onResult)

        return NOT_DONE_YET

############################################################################################################
#Insertion into table Monitor !!
############################################################################################################
class Add_frequ(Resource):

    isLeaf = True

    def render_GET(self, request):
        filename = "toto"
        conn = sqlite3.connect(filename)
        ti = ctime(int(time()))
        curs = conn.cursor()
        curs.execute("INSERT INTO monitor(f, description, time, statut) VALUES(?, ?, ?, ?)", (float(cgi.escape(request.args["form-field0"][0])), str(cgi.escape(request.args["form-field1"][0])), ti, str(cgi.escape(request.args["form-field2"][0])) ))
        conn.commit()
        conn.close()
        def getResult(self):
            return dbpool.runQuery("SELECT f, description, time FROM monitor")
 
        def onResult(data):
            frequency = list()
            descriptions = list()
            ti = list()
            for row in data:
                frequency.append( row[0] )
                descriptions.append( row[1].encode('utf-8') )
                ti.append( row[2].encode('utf-8') )
            longueur = len(frequency)
            request.write("""<!DOCTYPE html>
                                <html>
                                <head>
                                <link rel="icon" type="image/png" href="scripts/logo_smallm.png">
                                <link href="scripts/bootstrap.min.css" rel="stylesheet" /> 
                                <script type="text/javascript" src="scripts/jquery-1.11.2.min.js"></script>                          
                                <script type="text/javascript" src="scripts/bootstrap.min.js"></script>
                                <style>body {
                                padding-top: 50px;
                                }
                                .starter-template {
                                padding: 40px 15px;
                                text-align: center;
                                }
                                #logout{
                                position: fixed;
                                left:1225px;
                                top:0;
                                }
                                </style>
                                <script type="text/javascript" src="scripts/angular.min.js"></script>
                                </head>
                                <body>
                                <nav class="navbar navbar-inverse navbar-fixed-top">
                                <a href="#" class="pull-left"><img src="scripts/logo_smallm.png" width="60" height="51" hspace="1" style=" margin-top: 1px; margin-buttum: 10px;"></a> 
                                <div class="container">
                                <div class="navbar-header">
                                <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                                <span class="sr-only">Toggle navigation</span>
                                <span class="icon-bar"></span>
                                <span class="icon-bar"></span>
                                <span class="icon-bar"></span>
                                </button>
                                <a class="navbar-brand" href="/sl">HACA SDR</a>
                                </div>
                                <div id="navbar" class="collapse navbar-collapse"> 
                                <ul class="nav navbar-nav">
                                <li class="active"><a href="/db"><b>Surveillance</b></a></li>
                                <li class="dropdown"><a class="dropdown-toggle" data-toggle="dropdown" href="#"><b>Ploting and updating</b><span class="caret"></span></a><ul class="dropdown-menu"><li><a href="/form"><b>Band of frequencies</b></a></li><li role="presentation" class="divider"></li><li><a href="/parametersonefres"><b>One frequency</b></a></li></ul></li>
                                <li><a href="/hom" ><b>Recording history</b></a></li>
                                <li class="dropdown scrollable"><a class="dropdown-toggle" data-toggle="dropdown" onclick="RazNumber()"><b>Alarms</b><span class="caret"></span></a><ul class="dropdown-menu" id ="messages"><li><a href="/disall"><center>Display all</center></a></li></ul></li>
                                <li><a href="/somestatistics"><b>Statistics</b></a></li>
                                <li><a href="http://"""+str(get_lan_ip())+""":8001/streaming/" onclick="window.open('http://"""+str(get_lan_ip())+""":8001/streaming/', 'exemple', 'height=600, width=800, top=90, left=350, toolbar=no, menubar=no, location=yes, resizable=yes, scrollbars=yes, status=no'); return false;"><b>Real Time Streaming</b></a></li>
                                <li id="logout"><a href="/logout"><i class="glyphicon glyphicon-lock"></i> <b>Logout</b></a></li>
                                </ul>          
                                </div>
                                </div>
                                </nav>
                                <div class="container">
                                <br>
                                <br>
                                <div class="alert alert-success"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a><strong> Well done  !</strong> You successfully added this Frequency  """+str(cgi.escape(request.args["form-field0"][0]))+""" MHz</div>
                                </div>
                                </body>
                                </html>""")
            request.finish()
            return frequency
        d = getResult(self)
        d.addCallback(onResult)
        return NOT_DONE_YET
############################################################################################################
#delete frequency !!
############################################################################################################
class Del_frequ(Resource):
    isLeaf = True
    def render_GET(self, request):
        ff = float(cgi.escape(request.args["form-field0"][0]))
        filename = "toto"
        conn = sqlite3.connect(filename)
        ti = ctime(int(time()))
        curs = conn.cursor()
        curs.execute("delete from monitor where f= "+str(ff)+ "")
        conn.commit()
        print str(cgi.escape(request.args["form-field0"][0]))
        print ti
        conn.close()
        def getResult(self):
            return dbpool.runQuery("SELECT f, description, time FROM monitor")
 
        def onResult(data):
            frequency = list()
            descriptions = list()
            ti = list()
            for row in data:
                frequency.append( row[0] )
                descriptions.append( row[1].encode('utf-8') )
                ti.append( row[2].encode('utf-8') )
            longueur = len(frequency)
            request.write("""<!DOCTYPE html>
                                <html>
                                <head>
                                <link rel="icon" type="image/png" href="scripts/logo_smallm.png">
                                <link href="scripts/bootstrap.min.css" rel="stylesheet" /> 
                                <script type="text/javascript" src="scripts/jquery-1.11.2.min.js"></script>                          
                                <script type="text/javascript" src="scripts/bootstrap.min.js"></script>
                                <style>body {
                                padding-top: 50px;
                                }
                                .starter-template {
                                padding: 40px 15px;
                                text-align: center;
                                }
                                #logout{

                                position: fixed;
                                left:1225px;
                                top:0;
                                }
                                </style>
                                <script type="text/javascript" src="scripts/angular.min.js"></script>
                                </head>
                                <body>
                                <nav class="navbar navbar-inverse navbar-fixed-top">
                                <a href="#" class="pull-left"><img src="scripts/logo_smallm.png" width="60" height="51" hspace="1" style=" margin-top: 1px; margin-buttum: 10px;"></a> 
                                <div class="container">
                                <div class="navbar-header">
                                <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                                <span class="sr-only">Toggle navigation</span>
                                <span class="icon-bar"></span>
                                <span class="icon-bar"></span>
                                <span class="icon-bar"></span>
                                </button>
                                <a class="navbar-brand" href="/sl">HACA SDR</a>
                                </div>
                                <div id="navbar" class="collapse navbar-collapse"> 
                                <ul class="nav navbar-nav">
                                <li class="active"><a href="/db"><b>Surveillance</b></a></li>
                                <li class="dropdown"><a class="dropdown-toggle" data-toggle="dropdown" href="#"><b>Ploting and updating</b><span class="caret"></span></a><ul class="dropdown-menu"><li><a href="/form"><b>Band of frequencies</b></a></li><li role="presentation" class="divider"></li><li><a href="/parametersonefres"><b>One frequency</b></a></li></ul></li>
                                <li><a href="/hom" ><b>Recording history</b></a></li>
                                <li class="dropdown scrollable"><a class="dropdown-toggle" data-toggle="dropdown" onclick="RazNumber()"><b>Alarms</b><span class="caret"></span></a><ul class="dropdown-menu" id ="messages"><li><a href="/disall"><center>Display all</center></a></li></ul></li>
                                <li><a href="/somestatistics"><b>Statistics</b></a></li>
                                <li><a href="http://"""+str(get_lan_ip())+""":8001/streaming/" onclick="window.open('http://"""+str(get_lan_ip())+""":8001/streaming/', 'exemple', 'height=600, width=800, top=90, left=350, toolbar=no, menubar=no, location=yes, resizable=yes, scrollbars=yes, status=no'); return false;"><b>Real Time Streaming</b></a></li>
                                <li id="logout"><a href="/logout"><i class="glyphicon glyphicon-lock"></i> <b>Logout</b></a></li>
                                </ul>          
                                </div>
                                </div>
                                </nav>
                                <div class="container">
                                <br>
                                <br>
                                <div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a><strong> Well done  !</strong> You successfully added this Frequency  """+str(ff)+""" MHz</div>
                                </div>
                                </body>
                                </html>""")
            request.finish()
            return frequency

        d = getResult(self)
        d.addCallback(onResult)
        return NOT_DONE_YET       
############################################################################################################
#Formulaire
############################################################################################################
class Formulaire(Resource):
    #global fmi, fma, inc
    isLeaf = True
    def render_GET(self, request):
        def get_result(self):
            return dbpool.runQuery("SELECT f, ts, tp FROM alarms order by id desc")
        def on_result(data):
            frequency_alarms = list()
            time_alarms = list()
            situation_alarms = list()
            for row in data:
                frequency_alarms.append(row[0])
                time_alarms.append( row[1])
                situation_alarms.append( row[2])
            Alarm_notif = """<ul class="dropdown-menu" id ="messages">"""
            for i in range(3):
                try:
                    if frequency_alarms[i]:
                        if situation_alarms[i].endswith("begining.."):
                            Alarm_notif += """<li class="list-group-item list-group-item-danger"><a href="#" >"""+str(frequency_alarms[i])+""" Mhz :"""+str(situation_alarms[i])+""" at """+str(time_alarms[i])+"""</a></li>"""
                        elif situation_alarms[i].startswith("Low Alarm finished"):
                            Alarm_notif += """<li class="list-group-item list-group-item-success"><a href="#" >"""+str(frequency_alarms[i])+""" Mhz :"""+str(situation_alarms[i])+""" at """+str(time_alarms[i])+"""</a></li>"""
                except IndexError:
                    Alarm_notif += ''
            request.write("""
                            <!DOCTYPE html>
                            <html>
                            <head>"""+str(src_url)+"""
                            <style>body {
                                padding-top: 70px;
                                }
                            .starter-template {
                                padding: 40px 15px;
                                text-align: center;
                                }
                            #logout{
                            position: fixed;
                            left:1225px;
                            top:0;
                            }
                            </style>
                            <style>
                            #mycontent {
                                height: 100px;
                            }
                            .active a {
                                border: 2px solid black;
                            }
                            </style>
                            <script type="text/javascript" src="scripts/notifjs.js"></script>
                            <script>
                            function zeroNumber(){                                
                                if(document.getElementById('number').innerHTML==0){
                                    document.getElementById('box').style.display="none";
                                }else{
                                    document.getElementById('box').style.display="block";
                                }}
                            function RazNumber(){
                                document.getElementById('number').innerHTML=0;
                                zeroNumber();
                            }
                            function decreaseNumber(){
                                n = n-1;
                                document.getElementById('number').innerHTML=n;
                                zeroNumber();
                            }
                            </script>
                            <style type="text/css">
                            #box{
                                width:25px;
                                height:20px;
                                background: red;
                                position: fixed;
                                left:729px;
                                top:0;
                                z-index: 9999;
                                border-radius: 10px;
                                color: white;
                                }
                            #number{
                                text-align: center;
                            }
                            .dropdown-menu {
                                max-height: 340px;
                                overflow-y: scroll;
                            }
                            .pull-left{
                                width:60px;
                                height:51px;
                                position: fixed;
                                left:0.25px;
                                top:1.75px;
                            }
                            </style>
                            </head>
                            <body onload=zeroNumber() data-spy="scroll" data-target="#sidebar" data-spy="affix" data-offset-top="28">
                            <nav class="navbar navbar-inverse navbar-fixed-top">
                            <a href="#" class="pull-left"><img src="scripts/logo_smallm.png" width="60" height="51" hspace="1" style=" margin-top: 1px; margin-buttum: 10px;"></a> 
                            <div class="container">
                            <div class="navbar-header">
                            <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                            <span class="sr-only">Toggle navigation</span>
                            <span class="icon-bar"></span>
                            <span class="icon-bar"></span>
                            <span class="icon-bar"></span>
                            </button>
                            <a class="navbar-brand" href="/sl">HACA SDR</a>
                            </div>
                            <div id="navbar" class="collapse navbar-collapse">              
                            <ul class="nav navbar-nav">
                            <li><a href="/db"><b>Surveillance</b></a></li>
                            <li class="dropdown"><a class="dropdown-toggle" data-toggle="dropdown" href="#"><b>Ploting and updating</b><span class="caret"></span></a><ul class="dropdown-menu"><li><a href="/form"><b>Band of frequencies</b></a></li><li role="presentation" class="divider"></li><li><a href="/parametersonefres"><b>One frequency</b></a></li></ul></li>
                            <li><a href="/hom" ><b>Recording history</b></a></li>
                            <li class="dropdown scrollable"><a class="dropdown-toggle" data-toggle="dropdown" onclick="RazNumber()"><b>Alarms</b><span class="caret"></span></a>"""+str(Alarm_notif)+"""<li><a href="/disall"><center>Display all</center></a></li></ul></li>
                            <li><a href="/somestatistics"><b>statistics</b></a></li>
                            <li><a href="http://"""+str(get_lan_ip())+""":8001/streaming/" onclick="window.open('http://"""+str(get_lan_ip())+""":8001/streaming/', 'exemple', 'height=600, width=800, top=90, left=350, toolbar=no, menubar=no, location=yes, resizable=yes, scrollbars=yes, status=no'); return false;"><b>Real Time Streaming</b></a></li>
                            <li id="logout"><a href="/logout"><i class="glyphicon glyphicon-lock"></i> <b>Logout</b></a></li>
                            </ul>              
                            </div>
                            </div>
                            </nav>
                            <div id="box"><p id="number">0</p></div>
                            <div class="container">
                            <div class="page-header">
                            <h1>Real Time for a Band Frequencies :</h1>      
                            </div>
                            <div class="btn-group btn-group-justified">
                              <a href="#" class="btn btn-primary">  </a>
                              <a href="#" class="btn btn-primary">  </a>
                              <a href="#" class="btn btn-primary">  </a>
                            </div>
                            <br>
                            <div class="panel panel-primary">
                            <div class="panel-heading"><b>Monitor a band of frequencies :</b></div>
                            <div class="panel-body">
                            <form action="/up" method="GET">
                            <fieldset class="form-group">
                            <label for="formGroupExampleInput">Frequency Min</label>
                            <input type="float"  name="form-field0" class="form-control" id="formGroupExampleInput" placeholder="Type your Fmin in Mhz">
                            </fieldset>
                            <fieldset class="form-group">
                            <label for="formGroupExampleInput2">Frequency Max</label>
                            <input name="form-field1" type="float" class="form-control" id="formGroupExampleInput2" placeholder="Type your Fmax in Mhz">
                            </fieldset>
                            <fieldset class="form-group">
                            <label for="formGroupExampleInput2">Increment :</label>
                            <input type="float" name="form-field2" class="form-control" id="formGroupExampleInput2" placeholder="Type your increment">
                            </fieldset>
                            <button class="btn btn-primary" type="submit"><span class="glyphicon glyphicon-ok-sign"></span> Begin</button>
                            </form>
                            </div>
                            </div>
                            </div>
                            </body>
                            </html>
                            """)
            request.finish()
        d = get_result(self)
        d.addCallback(on_result)
        return NOT_DONE_YET
############################################################################################################
#Ploting without updating static graph
############################################################################################################
class Graph(Resource):
    isLeaf = True
    def render_GET(self, request):

        value = []
        frequences = []
        
        def graphe(fmin, fmax, inc):
            freq= fmin
            while(freq<=fmax):
                frequences.append(freq)
                sdr.fc=(freq*1000000)
                deci=0
                samples=sdr.read_samples(512*1024)
                deci=10*log10(var(samples))
                print 'wait ... frequency: ',freq
                value.append(deci)
                freq+=inc
            return value, frequences
            
        value, frequences = graphe(float(cgi.escape(request.args["form-field0"][0])), float(cgi.escape(request.args["form-field1"][0])), float(cgi.escape(request.args["form-field2"][0])))
        diff = float(cgi.escape(request.args["form-field1"][0]))-float(cgi.escape(request.args["form-field0"][0])) 
        return """
            <!DOCTYPE HTML>
            <html>
            <head>
            <script type="text/javascript" src="scripts/canvasjs.min.js">
            </script>
                <script type="text/javascript">
                var a="""+str(frequences)+""";
                var b="""+str(value)+""";
                window.onload = function () {
                    var dps = []; // dataPoints
                    var chart = new CanvasJS.Chart("chartContainer",{
                        animationEnabled: true,
                        zoomEnabled: true,
                        title :{
                            text: "Ploting Xfrequiencies(MHz) and Yvalue(DB) "
                        },
                        axisX: {                        
                        title: "Frequencies (MHz)"
                        },
                        axisY: {                        
                        title: "Value (DB)"
                        },
                        legend :{
                        verticalAlign: 'bottom',
                        horizontalAlign: "center"},    
                        data: [{
                            type: "spline",
                            dataPoints: dps 
                        }]
                    });
                    var dataLength = """+str(diff)+"""; // number of dataPoints visible at any point
                    var updateChart = function () {                       
                        for (var j = 0; j < a.length; j++) {                 
                            dps.push({
                                x: a[j],
                                y: b[j]
                            });  
                        };
                        chart.render();     
                    };
                    // generates first set of dataPoints
                    updateChart(dataLength); 
                    // update chart after specified time. 
                     
                }
                </script>
            </head>
            <body>
            <div id="chartContainer" style="height: 400px; width:100%;">
            </div>
            </body>
            </html>
               """
############################################################################################################
#change the state
############################################################################################################
class ChangeState(Resource):
    isLeaf = True
    def render_GET(self, request):
        filename = "toto"
        conn = sqlite3.connect(filename)
        ti = ctime(int(time()))
        curs = conn.cursor()
        curs.execute("update credential set control='without' where id=1 ")
        conn.commit()
        conn.close()
        def getResult(self):
            return dbpool.runQuery("SELECT f, description, time FROM monitor")
 
        def onResult(data):
            frequency = list()
            descriptions = list()
            ti = list()
            for row in data:
                frequency.append( row[0] )
                descriptions.append( row[1].encode('utf-8') )
                ti.append( row[2].encode('utf-8') )
            longueur = len(frequency)
            request.write("""<!DOCTYPE html>
                                <html>
                                <head>
                                """+str(src_url)+"""
                                <style>body {
                                              padding-top: 50px;
                                            }
                                            .starter-template {
                                              padding: 40px 15px;
                                              text-align: center;
                                            }
                                #logout{
                                position: fixed;
                                left:1225px;
                                top:0;
                                }
                                </style>
                                </head>
                                <body>
                                <nav class="navbar navbar-inverse navbar-fixed-top">
                                      <div class="container">
                                        <div class="navbar-header">
                                          <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                                            <span class="sr-only">Toggle navigation</span>
                                            <span class="icon-bar"></span>
                                            <span class="icon-bar"></span>
                                            <span class="icon-bar"></span>
                                          </button>
                                          <a class="navbar-brand" href="#">HACA SDR</a>
                                        </div>
                                        <div id="navbar" class="collapse navbar-collapse">              
                                         <ul class="nav navbar-nav">
                                         <li class="active"><a href="/db"><b>Surveillance</b></a></li>
                                         <li class="dropdown"><a class="dropdown-toggle" data-toggle="dropdown" href="#"><b>Ploting and updating</b><span class="caret"></span></a><ul class="dropdown-menu"><li><a href="/form"><b>Band of frequencies</b></a></li><li role="presentation" class="divider"></li><li><a href="/parametersonefres"><b>One frequency</b></a></li></ul></li>
                                         <li><a href="/hom" ><b>Recording history</b></a></li>
                                         <li class="dropdown scrollable"><a class="dropdown-toggle" data-toggle="dropdown" onclick="RazNumber()"><b>Alarms</b><span class="caret"></span></a><ul class="dropdown-menu" id ="messages"><li><a href="/disall"><center>Display all</center></a></li></ul></li>
                                         <li><a href="/somestatistics"><b>Statistics</b></a></li>
                                         <li><a href="http://"""+str(get_lan_ip())+""":8001/streaming/" onclick="window.open('http://"""+str(get_lan_ip())+""":8001/r720ZdlpCZfVdLqx1Gu4Fg/', 'exemple', 'height=600, width=800, top=90, left=350, toolbar=no, menubar=no, location=yes, resizable=yes, scrollbars=yes, status=no'); return false;"><b>Real Time Streaming</b></a></li>
                                         <li id="logout"><a href="/logout"><i class="glyphicon glyphicon-lock"></i> <b>Logout</b></a></li>
                                         </ul>
                                          
                                        </div><!--/.nav-collapse -->
                                      </div>
                                    </nav>
                                <div class="container">
                                <br>
                                <div class="alert alert-success"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a><strong>Well done!</strong> Your system is turning on (mode without alarms)...</div>
                                
                                </div>
                                </body>
                                </html>""")
            request.finish()
            return frequency

        d = getResult(self)
        d.addCallback(onResult)

 
        return NOT_DONE_YET
############################################################################################################
#Change state ON/OFF
############################################################################################################
class ChangeOnff(Resource):
    isLeaf = True
    def render_GET(self, request):
        filename = "toto"
        conn = sqlite3.connect(filename)
        ti = ctime(int(time()))
        curs = conn.cursor()
        curs.execute("update monitor set statut='"+str(cgi.escape(request.args["form-field2"][0]))+"' where f="+str(cgi.escape(request.args["form-field0"][0]))+" ")
        conn.commit()
        conn.close()
        def getResult(self):
            return dbpool.runQuery("SELECT f, description, time FROM monitor")
 
        def onResult(data):
            frequency = list()
            descriptions = list()
            ti = list()
            for row in data:
                frequency.append( row[0] )
                descriptions.append( row[1].encode('utf-8') )
                ti.append( row[2].encode('utf-8') )
            longueur = len(frequency)
            request.write("""<!DOCTYPE html>
                                <html>
                                <head>
                                """+str(src_url)+"""
                                <style>body {
                                              padding-top: 50px;
                                            }
                                            .starter-template {
                                              padding: 40px 15px;
                                              text-align: center;
                                            }
                                #logout{
                                position: fixed;
                                left:1225px;
                                top:0;
                                }
                                </style>
                                </head>
                                <body>
                                <nav class="navbar navbar-inverse navbar-fixed-top">
                                      <div class="container">
                                        <div class="navbar-header">
                                          <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                                            <span class="sr-only">Toggle navigation</span>
                                            <span class="icon-bar"></span>
                                            <span class="icon-bar"></span>
                                            <span class="icon-bar"></span>
                                          </button>
                                          <a class="navbar-brand" href="#">HACA SDR</a>
                                        </div>
                                        <div id="navbar" class="collapse navbar-collapse">
                                          
                                        <ul class="nav navbar-nav">
                                        <li class="active"><a href="/db"><b>Surveillance</b></a></li>
                                        <li class="dropdown"><a class="dropdown-toggle" data-toggle="dropdown" href="#"><b>Ploting and updating</b><span class="caret"></span></a><ul class="dropdown-menu"><li><a href="/form"><b>Band of frequencies</b></a></li><li role="presentation" class="divider"></li><li><a href="/parametersonefres"><b>One frequency</b></a></li></ul></li>
                                        <li><a href="/hom" ><b>Recording history</b></a></li>
                                        <li class="dropdown scrollable"><a class="dropdown-toggle" data-toggle="dropdown" onclick="RazNumber()"><b>Alarms</b><span class="caret"></span></a><ul class="dropdown-menu" id ="messages"><li><a href="/disall"><center>Display all</center></a></li></ul></li>
                                        <li><a href="/somestatistics"><b>Statistics</b></a></li>
                                        <li><a href="http://"""+str(get_lan_ip())+""":8001/streaming/" onclick="window.open('http://"""+str(get_lan_ip())+""":8001/streaming/', 'exemple', 'height=600, width=800, top=90, left=350, toolbar=no, menubar=no, location=yes, resizable=yes, scrollbars=yes, status=no'); return false;"><b>Real Time Streaming</b></a></li>
                                        <li id="logout"><a href="/logout"><i class="glyphicon glyphicon-lock"></i> <b>Logout</b></a></li>
                                        </ul>
                                          
                                        </div><!--/.nav-collapse -->
                                      </div>
                                    </nav>
                                <div class="container">
                                <br>
                                <div class="alert alert-success"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a><strong> Well done  !</strong> You successfully changed the state of frequency :"""+str(cgi.escape(request.args["form-field0"][0]))+""" MHz to """+str(cgi.escape(request.args["form-field2"][0]))+"""</div>
                                </div>
                                </body>
                                </html>""")
            request.finish()
            return frequency

        d = getResult(self)
        d.addCallback(onResult)

 
        return NOT_DONE_YET
############################################################################################################
#stop monitoring
############################################################################################################
class ChangeStateTostop(Resource):
    isLeaf = True
    def render_GET(self, request):
        filename = "toto"
        conn = sqlite3.connect(filename)
        ti = ctime(int(time()))
        curs = conn.cursor()
        curs.execute("update credential set control='stop' where id=1 ")
        conn.commit()
        conn.close()
        def getResult(self):
            return dbpool.runQuery("SELECT f, description, time FROM monitor")
 
        def onResult(data):
            frequency = list()
            descriptions = list()
            ti = list()
            for row in data:
                frequency.append( row[0] )
                descriptions.append( row[1].encode('utf-8') )
                ti.append( row[2].encode('utf-8') )
            longueur = len(frequency)
            request.write("""<!DOCTYPE html>
                                <html>
                                <head>
                                """+str(src_url)+"""
                                <style>body {
                                    padding-top: 50px;
                                    }
                                .starter-template {
                                padding: 40px 15px;
                                text-align: center;
                                }
                                #logout{
                                position: fixed;
                                left:1225px;
                                top:0;
                                }</style>
                                </head>
                                <body>
                                <nav class="navbar navbar-inverse navbar-fixed-top">
                                <div class="container">
                                <div class="navbar-header">
                                <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                                <span class="sr-only">Toggle navigation</span>
                                <span class="icon-bar"></span>
                                <span class="icon-bar"></span>
                                <span class="icon-bar"></span>
                                </button>
                                <a class="navbar-brand" href="#">HACA SDR</a>
                                </div>
                                <div id="navbar" class="collapse navbar-collapse">   
                                 <ul class="nav navbar-nav">
                                 <li class="active"><a href="/db"><b>Surveillance</b></a></li>
                                <li class="dropdown"><a class="dropdown-toggle" data-toggle="dropdown" href="#"><b>Ploting and updating</b><span class="caret"></span></a><ul class="dropdown-menu"><li><a href="/form"><b>Band of frequencies</b></a></li><li role="presentation" class="divider"></li><li><a href="/parametersonefres"><b>One frequency</b></a></li></ul></li>
                                <li><a href="/hom" ><b>Recording history</b></a></li>
                                <li class="dropdown scrollable"><a class="dropdown-toggle" data-toggle="dropdown" onclick="RazNumber()"><b>Alarms</b><span class="caret"></span></a><ul class="dropdown-menu" id ="messages"><li><a href="/disall"><center>Display all</center></a></li></ul></li>
                                <li><a href="/somestatistics"><b>Statistics</b></a></li>
                                <li><a href="http://"""+str(get_lan_ip())+""":8001/streaming/" onclick="window.open('http://"""+str(get_lan_ip())+""":8001/streaming/', 'exemple', 'height=600, width=800, top=90, left=350, toolbar=no, menubar=no, location=yes, resizable=yes, scrollbars=yes, status=no'); return false;"><b>Real Time Streaming</b></a></li>
                                <li id="logout"><a href="/logout"><i class="glyphicon glyphicon-lock"></i> <b>Logout</b></a></li>
                                </ul>
                                          
                                </div><!--/.nav-collapse -->
          
                                </div>
                                </div>
                                </nav>
                                <div class="container">
                                <br>
                                <br>
                                <div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a><strong> System has stoped !</strong> Your system is turning off ...</div>
                                </div>
                                </body>
                                </html>""")
            request.finish()
            return frequency

        d = getResult(self)
        d.addCallback(onResult)

 
        return NOT_DONE_YET
############################################################################################################
#shows graphs
############################################################################################################
class Show_gra(Resource):
    isLeaf = True

    def render_GET(self, request):
        frequency_alarms = list()
        time_alarms = list()
        situation_alarms = list()
        high = list()
        low = list()
        conn = sqlite3.connect(filename)
        curs = conn.cursor()
        curs.execute("SELECT f, ts, tp FROM alarms order by id desc")
        conn.commit()
        resul_notif = curs.fetchall()
        for row in resul_notif:
            frequency_alarms.append(row[0])
            time_alarms.append( row[1])
            situation_alarms.append( row[2])
        Alarm_notif = """<ul class="dropdown-menu" id ="messages">"""
        for i in range(3):
            try:
                if frequency_alarms[i]:
                    if situation_alarms[i].endswith("begining.."):
                        Alarm_notif += """<li class="list-group-item list-group-item-danger"><a href="#" >"""+str(frequency_alarms[i])+""" Mhz :"""+str(situation_alarms[i])+""" at """+str(time_alarms[i])+"""</a></li>"""
                    elif situation_alarms[i].startswith("Low Alarm finished"):
                        Alarm_notif += """<li class="list-group-item list-group-item-success"><a href="#" >"""+str(frequency_alarms[i])+""" Mhz :"""+str(situation_alarms[i])+""" at """+str(time_alarms[i])+"""</a></li>"""
            except IndexError:
                Alarm_notif += ''
        curs.execute("SELECT highthreshold, lowthreshold FROM monitor where f ="+str(float(cgi.escape(request.args["form-field0"][0]))))
        conn.commit()
        res_thresholds = curs.fetchall()
        for row in res_thresholds:
            high.append(row[0])
            low.append(row[1])
        def retrieve_freq_time(freq):
            return dbpool.runQuery("select deci, ts from measurement where f="+str(freq))
        def working(data):
            value_db = list()
            time = list()
            for row in data:
                value_db.append(row[0])
                time.append( (row[1]))
            if high[0]:
                high_thresholds = "startValue:"+str(high[0])+","
            else:
                high_thresholds = ""
            if low[0]:
                low_thresholds = "endValue:"+str(low[0])+","
            else:
                low_thresholds = ""
            thresholds_html = high_thresholds+low_thresholds
            request.write("""
            <!DOCTYPE HTML>
            <html>
            <head>
            """+str(src_url)+"""
            <script src="scripts/canvasjs.min.js"></script>
            <style>body {
                padding-top: 70px;
                }
            .starter-template {
                padding: 40px 15px;
                text-align: center;
            }
            #logout{
            position: fixed;
            left:1225px;
            top:0;
            }
            </style>
            <style>
                #mycontent {
                height: 100px;
                }
            .active a {
                border: 2px solid black;
            }
            ul.nav-pills {
                top: 207px;
                position: fixed;
            }
            </style>
            <script type="text/javascript" src="scripts/notifjs.js"></script>
            <script>
            function zeroNumber(){                                
            if(document.getElementById('number').innerHTML==0){
                document.getElementById('box').style.display="none";
            }else{
                document.getElementById('box').style.display="block";
            }}
            function RazNumber(){
                document.getElementById('number').innerHTML=0;
                zeroNumber();
             }
            function decreaseNumber(){
                n = n-1;
            document.getElementById('number').innerHTML=n;
            zeroNumber();
            }
            </script>
            </head>
            <style type="text/css">
            #box{
                width:25px;
                height:20px;
                background: red;
                position: fixed;
                left:729px;
                top:0;
                z-index: 9999;
                border-radius: 10px;
                color: white;
                }
            #number{
                text-align: center;
             }
            .dropdown-menu {
                max-height: 340px;
                overflow-y: scroll;
            }
            .pull-left{
                width:60px;
                height:51px;
                position: fixed;
                left:0.25px;
                top:1.75px;
            }
            </style>       
            <script type="text/javascript">
            var a="""+str(time)+""";
            var b="""+str(value_db)+""";
            var c="""+str(float(cgi.escape(request.args["form-field0"][0])))+""";
            var time_conv = [];
            for(var i=0; i<a.length; i++){
                time_conv[i] = new Date(a[i]*1000);
            }
            window.onload = function () {
            var dps = []; // dataPoints
            var chart = new CanvasJS.Chart("chartContainer",{
                animationEnabled: true,
                zoomEnabled: true,
            title :{
                text: "Ploting Xtime and YTime frequency : "+c+" Mhz "
            },
                    toolTip: {
            shared: true,
            contentFormatter: function (e) {
                var content = " ";
                for (var i = 0; i < e.entries.length; i++) {
                    content += e.entries[i].dataPoint.x + " " + "<strong>" + e.entries[i].dataPoint.y + "</strong>";
                    content += "<br/>";
                }
                return content;
            }
        },
            axisX: {                        
            title: "Time"
            },
            axisY: {                        
            title: "The Value (DB) "
            },
            legend :{
            verticalAlign: 'bottom',
            horizontalAlign: "center"},
            axisY:{
            stripLines:[
                {                
                """+str(thresholds_html)+"""               
                color:"#FF0000",
            }
            ],
            valueFormatString: "####"
            },    
            data: [{
                xValueType: "date",
                type: "line",
                color: "rgba(0, 100, 0, .6)",
                dataPoints: dps 
            }]
            });
            var dataLength = 55000; // number of dataPoints visible at any point
            var updateChart = function () {                       
            for (var j = 0; j < a.length; j++) {                 
                dps.push({
                    x: time_conv[j],
                    y: b[j]
            });  
            };
            chart.render();     
            };
            // generates first set of dataPoints
            updateChart(dataLength); 
            // update chart after specified time. 
                     
            }
            </script>
            </head>
            <body onload=zeroNumber() data-spy="scroll" data-target="#sidebar" data-spy="affix" data-offset-top="28">
            <nav class="navbar navbar-inverse navbar-fixed-top">
            <a href="#" class="pull-left"><img src="scripts/logo_smallm.png" width="60" height="51" hspace="1" style=" margin-top: 1px; margin-buttum: 10px;"></a> 
            <div class="container">
            <div class="navbar-header">
            <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            </button>
            <a class="navbar-brand" href="/sl">HACA SDR</a>
            </div>
            <div id="navbar" class="collapse navbar-collapse">              
            <ul class="nav navbar-nav">
            <li><a href="/db"><b>Surveillance</b></a></li>
            <li class="dropdown"><a class="dropdown-toggle" data-toggle="dropdown" href="#"><b>Ploting and updating</b><span class="caret"></span></a><ul class="dropdown-menu"><li><a href="/form"><b>Band of frequencies</b></a></li><li role="presentation" class="divider"></li><li><a href="/parametersonefres"><b>One frequency</b></a></li></ul></li>
            <li><a href="/hom" ><b>Recording history</b></a></li>
            <li class="dropdown scrollable"><a class="dropdown-toggle" data-toggle="dropdown" onclick="RazNumber()"><b>Alarms</b><span class="caret"></span></a>"""+str(Alarm_notif)+"""<li><a href="/disall"><center>Display all</center></a></li></ul></li>
            <li><a href="/somestatistics"><b>Statistics</b></a></li>
            <li><a href="http://"""+str(get_lan_ip())+""":8001/streaming/" onclick="window.open('http://"""+str(get_lan_ip())+""":8001/streaming/', 'exemple', 'height=600, width=800, top=90, left=350, toolbar=no, menubar=no, location=yes, resizable=yes, scrollbars=yes, status=no'); return false;"><b>Real Time Streaming</b></a></li>
            <li id="logout"><a href="/logout"><i class="glyphicon glyphicon-lock"></i> <b>Logout</b></a></li>
            </ul>              
                             
                                          
            </div><!--/.nav-collapse -->
            </div>
            </nav>

            <div id="chartContainer" style="height: 500px; width:100%;">
            </div>
            </body>
            </html>
        """)
            request.finish()
        d =  retrieve_freq_time(float(cgi.escape(request.args["form-field0"][0])))
        d.addCallback(working)
        return NOT_DONE_YET

############################################################################################################
#Send data with jsonp
############################################################################################################
class InfoServer(Resource):
    isLeaf = True
    fm=87
    fma=89
    inc=1

    def __init__(self):
        # throttle in seconds to check app for new data
        self.throttle = 1
        # define a list to store client requests
        self.delayed_requests = []
        # setup a loop to process delayed requests
        loopingCall = task.LoopingCall(self.processDelayedRequests)
        loopingCall.start(self.throttle, False)
        # initialize parent
        
        Resource.__init__(self)
    def render(self, request):
        """
        Handle a new request
        """
        # set the request content type
        request.setHeader('Content-Type', 'application/json')
        # set args
        args = request.args
       
        # set jsonp callback handler name if it exists
        if 'callback' in args:
            request.jsonpcallback =  args['callback'][0]
           
        # set lastupdate if it exists
        if 'lastupdate' in args:
            request.lastupdate =  args['lastupdate'][0]
        else:
            request.lastupdate = 0
        # if we have data now, send it
        data = self.getData(request)
        if len(data) > 0:
            return self.__format_response(request, 1, data)
           
        # otherwise, put it in the delayed request list
        self.delayed_requests.append(request)
        # tell the client we're not done yet
        return server.NOT_DONE_YET

       
    def getData(self, request):
        #from rtlsdr import *
        sdr = RtlSdr()
        sdr.gain = 50
        # init data
        data = {}
        vale = []
        frequences = []
        #sdr = RtlSdr()
        def graphe(fmin, fmax, inc):
            freq= fmin
            while(freq<=fmax):
                frequences.append(freq)
                sdr.fc=(freq*1000000)
                deci=0
                samples=sdr.read_samples(512*1024)
                deci=10*log10(var(samples))

                print ("wait ... frequency: "+str(freq)+ " /value :" +str(deci))
                vale.append(deci)
                freq+=inc
            return vale, frequences


        
        value, frequences = graphe(self.fm, self.fma, self.inc)
        d = len(vale)
        a = True


        #simulate the chance of new data being available or not
        #new_data_available = bool(random.getrandbits(1))
       
        # set some simulated data
        if a:
            # you can dynamically add any key/value pair here
            
                    data = {'messages':[
                            {
                                'freq':frequences,
                                'vale':vale
                            },
                        ]
                    }
           
        return data
       
    def processDelayedRequests(self):
        """
        Processes the delayed requests that did not have
        any data to return last time around.
        """       
        # run through delayed requests
        for request in self.delayed_requests:
            # attempt to get data again
            data = self.getData(request)
           
            # write response and remove request from list if data is found
            if len(data) > 0:
                try:
                    request.write(self.__format_response(request, 1, data))
                    request.finish()
                except:
                    # Connection was lost
                    print 'connection lost before complete.'
                finally:
                    # Remove request from list
                    self.delayed_requests.remove(request)
    def __format_response(self, request, status, data):
        """
        Format responses uniformly
        """
        # Set the response in a json format
        response = json.dumps({'data':data})
       
        # Format with callback format if this was a jsonp request
        if hasattr(request, 'jsonpcallback'):
            return request.jsonpcallback+'('+response+')'
        else:
            return response
############################################################################################################
class Updtaed(Resource):
    isLeaf = True
    def render_GET(self, request):
        InfoServer.fm = float(cgi.escape(request.args["form-field0"][0]))
        InfoServer.fma = float(cgi.escape(request.args["form-field1"][0]))
        InfoServer.inc = float(cgi.escape(request.args["form-field2"][0]))
        #ipp = request.getClientIP()
        #d =  request.getHost()
        #print d.getHost
        frequency_alarms = list()
        time_alarms = list()
        situation_alarms = list()
        def get_result(self):
            return dbpool.runQuery("SELECT f, ts, tp FROM alarms order by id desc")
        def on_result(data):
            for row in data:
                frequency_alarms.append(row[0])
                time_alarms.append( row[1])
                situation_alarms.append( row[2])
            Alarm_notif = """<ul class="dropdown-menu" id ="messages">"""
            for i in range(3):
                try:
                    if frequency_alarms[i]:
                        if situation_alarms[i].endswith("begining.."):
                            Alarm_notif += """<li class="list-group-item list-group-item-danger"><a href="#" >"""+str(frequency_alarms[i])+""" Mhz :"""+str(situation_alarms[i])+""" at """+str(time_alarms[i])+"""</a></li>"""
                        elif situation_alarms[i].startswith("Low Alarm finished"):
                            Alarm_notif += """<li class="list-group-item list-group-item-success"><a href="#" >"""+str(frequency_alarms[i])+""" Mhz :"""+str(situation_alarms[i])+""" at """+str(time_alarms[i])+"""</a></li>"""
                except IndexError:
                    Alarm_notif += ''
            request.write("""
                <!DOCTYPE HTML>
                <?xml version="1.0" encoding="UTF-8"?>
                <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
                      "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
                <html>
                <head>
                <title>Simulation of real time</title>
                """+str(src_url)+"""
                <style>body {
                    padding-top: 70px;
                    }
                .starter-template {
                    padding: 40px 15px;
                    text-align: center;
                }
                #logout{
                position: fixed;
                left:1225px;
                top:0;
                }
                </style>
                <style>
                #mycontent {
                    height: 100px;
                    }
                .active a {
                border: 2px solid black;
                        }
                ul.nav-pills {
                    top: 207px;
                    position: fixed;
                    }
                </style>
                <script type="text/javascript" src="scripts/notifjs.js"></script>
                <script>
                    function zeroNumber(){                                
                    if(document.getElementById('number').innerHTML==0){
                    document.getElementById('box').style.display="none";
                    }else{
                    document.getElementById('box').style.display="block";
                    }}
                function RazNumber(){
                    document.getElementById('number').innerHTML=0;
                    zeroNumber();
                }
                function decreaseNumber(){
                    n = n-1;
                    document.getElementById('number').innerHTML=n;
                    zeroNumber();
                }
                </script>
                </head>
                <style type="text/css">
                    #box{
                        width:25px;
                        height:20px;
                        background: red;
                        position: fixed;
                        left:729px;
                        top:0;
                        z-index: 9999;
                        border-radius: 10px;
                        color: white;
                        }
                    #number{
                        text-align: center;
                        }
                    .dropdown-menu {
                            max-height: 340px;
                            overflow-y: scroll;    
                    }
                    .pull-left{
                        width:60px;
                        height:51px;
                        position: fixed;
                        left:0.25px;
                        top:1.75px;
                    }
                </style>
                <script src="http://ajax.googleapis.com/ajax/libs/angularjs/1.4.8/angular.min.js"></script>
                <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
                <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.0/jquery.min.js"></script>
                <script type="text/javascript" src="scripts/upjs.js"></script>
                <script src="scripts/canvasjs.min.js"></script>
                </head>
                <body onload=zeroNumber() data-spy="scroll" data-target="#sidebar" data-spy="affix" data-offset-top="28">
                <nav class="navbar navbar-inverse navbar-fixed-top">
                <a href="#" class="pull-left"><img src="scripts/logo_smallm.png" width="60" height="51" hspace="1" style=" margin-top: 1px; margin-buttum: 10px;"></a> 
                <div class="container">
                <div class="navbar-header">
                <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                <span class="sr-only">Toggle navigation</span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
                </button>
                <a class="navbar-brand" href="/sl">HACA SDR</a>
                </div>
                <div id="navbar" class="collapse navbar-collapse">              
                <ul class="nav navbar-nav">
                <li class="active"><a href="/db"><b>Surveillance</b></a></li>
                <li class="dropdown"><a class="dropdown-toggle" data-toggle="dropdown" href="#"><b>Ploting and updating</b><span class="caret"></span></a><ul class="dropdown-menu"><li><a href="/form"><b>Band of frequencies</b></a></li><li role="presentation" class="divider"></li><li><a href="/parametersonefres"><b>One frequency</b></a></li></ul></li>
                <li><a href="/hom" ><b>Recording history</b></a></li>
                <li class="dropdown scrollable"><a class="dropdown-toggle" data-toggle="dropdown" onclick="RazNumber()"><b>Alarms</b><span class="caret"></span></a>"""+str(Alarm_notif)+"""<li><a href="/disall"><center>Display all</center></a></li></ul></li>
                <li><a href="/somestatistics"><b>Statistics</b></a></li>
                <li><a href="http://"""+str(get_lan_ip())+""":8001/streaming/" onclick="window.open('http://"""+str(get_lan_ip())+""":8001/streaming/', 'exemple', 'height=600, width=800, top=90, left=350, toolbar=no, menubar=no, location=yes, resizable=yes, scrollbars=yes, status=no'); return false;"><b>Real Time Streaming</b></a></li>
                <li id="logout"><a href="/out"><i class="glyphicon glyphicon-lock"></i> <b>Logout</b></a></li>
                </ul>              
                </div>
                </div>
                </nav>
                <div id="chartContainer" ></div>
                </body>
                </html>
                        """)
            request.finish()
        d= get_result(self)
        d.addCallback(on_result)

        return NOT_DONE_YET
class Slide(Resource):
    isLeaf = True
    def render_GET(self, request):
        return"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                    """+str(src_url)+"""
                    <style>body {
                                            padding-top: 80px;
                                            }
                                        .starter-template {
                                            padding: 40px 15px;
                                            text-align: center;
                                            }</style>
                    </head>
                    <body>
                    <nav class="navbar navbar-inverse navbar-fixed-top">
                    <div class="container">
                    <div class="navbar-header">
                    <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                    <span class="sr-only">Toggle navigation</span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                    </button>
                    <a class="navbar-brand" class="active" href="/sl">HACA SDR</a>
                    </div>
                    <div id="navbar" class="collapse navbar-collapse">
                                                              
                    <ul class="nav navbar-nav">
                    <li><a href="/db"><b>Surveillance</b></a></li>
                    <li><a href="/form"><b>Ploting and updating</b></a></li>
                    <li><a href="" onclick="window.open('/form', 'exemple', 'height=600, width=800, top=90, left=350, toolbar=no, menubar=no, location=yes, resizable=yes, scrollbars=yes, status=no'); return false;"><b>recording history</b></a></li>
                    <li><a href="#contact"><b>Alarms</b></a></li>
                    <li><a href="http://localhost:9800/r720ZdlpCZfVdLqx1Gu4Fg/" onclick="window.open('http://localhost:9800/r720ZdlpCZfVdLqx1Gu4Fg/', 'exemple', 'height=600, width=800, top=90, left=350, toolbar=no, menubar=no, location=yes, resizable=yes, scrollbars=yes, status=no'); return false;"><b>Real Time Streaming</b></a></li>
                    </ul>
                    </div><!--/.nav-collapse -->
                    </div></nav>
                    <div id="carousel-example-generic" class="carousel slide" data-ride="carousel">
                      <!-- Indicators -->
                      <ol class="carousel-indicators">
                        <li data-target="#carousel-example-generic" data-slide-to="0" class="active"></li>
                        <li data-target="#carousel-example-generic" data-slide-to="1"></li>
                        <li data-target="#carousel-example-generic" data-slide-to="2"></li>
                      </ol>

                      <!-- Wrapper for slides -->
                      <div class="carousel-inner" role="listbox">
                        <div class="item active">
                          <center><img src="/scripts/CONCEPTIONdb.png" alt="failed to load image"></image>
                          <div class="carousel-caption">
                            hello
                          </div>
                        </div>
                        <div class="item">
                          <center><img src="/scripts/CONCEPTIONdb.png" alt="failed to load image"></center>
                          <div class="carousel-caption">
                           kjhjkhjhj
                          </div>
                        </div>
                        k;jkn,n,n
                      </div>

                      <!-- Controls -->
                      <a class="left carousel-control" href="#carousel-example-generic" role="button" data-slide="prev">
                        <span class="glyphicon glyphicon-chevron-left" aria-hidden="true"></span>
                        <span class="sr-only">Previous</span>
                      </a>
                      <a class="right carousel-control" href="#carousel-example-generic" role="button" data-slide="next">
                        <span class="glyphicon glyphicon-chevron-right" aria-hidden="true"></span>
                        <span class="sr-only">Next</span>
                      </a>
                    </div>
                    </body>
                    </html>
                            """
############################################################################################################
#Alarms !!!
############################################################################################################
class InfoNotification(Resource):
    isLeaf = True
    def __init__(self):
        # throttle in seconds to check app for new data
        self.throttle = 2
        # define a list to store client requests
        self.delayed_requests = []
        # setup a loop to process delayed requests
        loopingCall = task.LoopingCall(self.processDelayedRequests)
        loopingCall.start(self.throttle, False)
        # initialize parent
        
        Resource.__init__(self)
    def render(self, request):
        """
        Handle a new request
        """
        # set the request content type
        request.setHeader('Content-Type', 'application/json')
        # set args
        args = request.args
       
        # set jsonp callback handler name if it exists
        if 'callback' in args:
            request.jsonpcallback =  args['callback'][0]
           
        # set lastupdate if it exists
        if 'lastupdate' in args:
            request.lastupdate =  args['lastupdate'][0]
        else:
            request.lastupdate = 0
        # if we have data now, send it
        data = self.getData(request)
        if len(data) > 0:
            return self.__format_response(request, 1, data)
        # otherwise, put it in the delayed request list
        self.delayed_requests.append(request)
        # tell the client we're not done yet
        return server.NOT_DONE_YET
    def getData(self, request):
        data = {}
        f = open("scripts/alarms.json","r")
        d =json.load(f)
        freq =  d["f"]
        val = d["value"]
        timestamp = d["ts"]
        situation = d["tp"]
        ide = d["id"]
        f.close()    
        data = {'messages':[{'f':freq,'value':val,'ts':timestamp,'tp':situation,'id':ide},]}
        return data
    def processDelayedRequests(self):
        """
        Processes the delayed requests that did not have
        any data to return last time around.
        """       
        # run through delayed requests
        for request in self.delayed_requests:
            # attempt to get data again
            data = self.getData(request)
           
            # write response and remove request from list if data is found
            if len(data) > 0:
                try:
                    request.write(self.__format_response(request, 1, data))
                    request.finish()
                except:
                    # Connection was lost
                    print 'connection lost before complete.'
                finally:
                    # Remove request from list
                    self.delayed_requests.remove(request)
    def __format_response(self, request, status, data):
        """
        Format responses uniformly
        """
        # Set the response in a json format
        response = json.dumps({'data':data})
       
        # Format with callback format if this was a jsonp request
        if hasattr(request, 'jsonpcallback'):
            return request.jsonpcallback+'('+response+')'
        else:
            return response
############################################################################################################
#Display_All_measures
############################################################################################################
class Allmesure(Resource):
    isLeaf = True
    def render_GET(self, request):
        def _getresult(txn):
            txn.execute("SELECT f, ts, tp, value, id, t_low, t_high FROM alarms order by id desc")
            result1 = txn.fetchall()
            return result1
        def getresult():
            return dbpool.runInteraction(_getresult)
        def onResult(data):
            frequency_alarms = list()
            time_alarms = list()
            situation_alarms = list()
            value_alarms = list()
            id_alarms = list()
            highthreshold_alarms = list()
            lowthreshold_alarms = list()
            if data:
                for row in data:
                    frequency_alarms.append(row[0])
                    time_alarms.append( row[1])
                    situation_alarms.append( row[2])
                    value_alarms.append( row[3])
                    id_alarms.append( row[4])
                    lowthreshold_alarms.append( row[5] ) 
                    highthreshold_alarms.append( row[6] )
            ID_html = """<div class="panel panel-primary"><div class="panel-heading">Delete some registrations :</div><div class="panel-body"><form class="form-inline" action="/delsomereg" method="GET"><label for="title">Id_Alarm : </label> <select class="form-control" name="id_alarm" >"""
            texto_html = """<table class="table"><thead><tr><th><center>ID_ Alarm</center></th><th><center>Frequency</center></th><th><center>type</center></th><th><center>LowThreshold</center></th><th><center>HighThreshold</center></th><th><center>Power level(DB)</center></th><th><center>Time</center></th></tr></thead><tbody><tbody>"""
            for tr in range(len(frequency_alarms)):
                if situation_alarms[tr].endswith("begining.."):
                    texto_html += """<tr class="danger"><td><center>"""+str(id_alarms[tr])+"""</center></td><td><center>"""+str(frequency_alarms[tr])+"""</center></td><td><center>"""+str(situation_alarms[tr])+"""</center></td><td><center>"""+str(highthreshold_alarms[tr])+"""</center></td><td><center>"""+str(lowthreshold_alarms[tr])+"""</center></td><td><center>"""+str(value_alarms[tr])+"""</center></td><td><center>"""+str(time_alarms[tr])+"""</center></td></tr>"""
                    ID_html += """<option class="danger">"""+str(id_alarms[tr])+"""</option>"""
                elif situation_alarms[tr].startswith("Low Alarm finished"):
                    texto_html += """<tr class="success"><td><center>"""+str(id_alarms[tr])+"""</center></td><td><center>"""+str(frequency_alarms[tr])+"""</center></td><td><center>"""+str(situation_alarms[tr])+"""</center></td><td><center>"""+str(highthreshold_alarms[tr])+"""</center></td><td><center>"""+str(lowthreshold_alarms[tr])+"""</center></td><td><center>"""+str(value_alarms[tr])+"""</center></td><td><center>"""+str(time_alarms[tr])+"""</center></td></tr>"""
                    ID_html += """<option class="success">"""+str(id_alarms[tr])+"""</option>"""
            texto_html += "</tbody></table>"
            Alarm_notif = """<ul class="dropdown-menu" id ="messages">"""
            ID_html +="""</select> <input type="submit" name="action" value="Remove" class="btn btn-primary" />   <input type="submit" name="action" value="Remove all" class="btn btn-primary" /></form></div>""" 
            for i in range(3):
                try:
                    if frequency_alarms[i]:
                        if situation_alarms[i].endswith("begining.."):
                            Alarm_notif += """<li class="list-group-item list-group-item-danger"><a href="#" >"""+str(frequency_alarms[i])+""" Mhz :"""+str(situation_alarms[i])+""" at """+str(time_alarms[i])+"""</a></li>"""
                        elif situation_alarms[i].startswith("Low Alarm finished"):
                            Alarm_notif += """<li class="list-group-item list-group-item-success"><a href="#" >"""+str(frequency_alarms[i])+""" Mhz :"""+str(situation_alarms[i])+""" at """+str(time_alarms[i])+"""</a></li>"""

                except IndexError:
                    Alarm_notif += ''

            request.write("""<!DOCTYPE html>
                                <html>
                                <title> SDR Monitoring..</title>
                                <link rel="icon" type="image/png" href="scripts/logo_smallm.png">
                                <head>
                                """+str(src_url)+"""
                                <script type="text/javascript" src="scripts/notifjs.js"></script>
                                <style>body {
                                              padding-top: 50px;
                                            }
                                            .starter-template {
                                              pa
                                              dding: 40px 15px;
                                              text-align: center;
                                            }
                                #logout{
                                position: fixed;
                                left:1225px;
                                top:0;
                                }
                                </style>
                                <script type="text/javascript" >
                                $(function(){
                                     $('li').hover(function(){
                                          $(this).addClass('highlight');
                                      }, function(){
                                          $(this).removeClass('highlight');
                                      });

                                      $('li').click(function(){
                                           $(this).addClass('highlight_stay');
                                      });
                                });
                                </script>
                                <style type="text/css">
                                .highlight, .highlight_stay{
                                color:red;
                                  }
                                </style>
                                <script>
                                function zeroNumber(){                                
                                    if(document.getElementById('number').innerHTML==0){
                                       document.getElementById('box').style.display="none";
                                    }else{
                                       document.getElementById('box').style.display="block";
                                   }}
                                function RazNumber(){
                                 document.getElementById('number').innerHTML=0;
                                 zeroNumber();
                                }
                                function decreaseNumber(){
                                n = n-1;
                                document.getElementById('number').innerHTML=n;
                                zeroNumber();
                                  }
                                </script>
                                </head>
                                <style type="text/css">
                                #box{
                                width:25px;
                                height:20px;
                                background: red;
                                position: fixed;
                                left:720px;
                                top:0;
                                z-index: 9999;
                                border-radius: 10px;
                                color: white;

                                }
                                #number{
                                   text-align: center;

                                }
                                .dropdown-menu {
                                max-height: 340px;
                                overflow-y: scroll;

                            }
                            .pull-left{
                                width:60px;
                                height:51px;
                                position: fixed;
                                left:0.25px;
                                top:1.75px;
                             }
                                </style>
                                <body onload=zeroNumber()>
                                <nav class="navbar navbar-inverse navbar-fixed-top">
                                <a href="#" class="pull-left"><img src="scripts/logo_smallm.png" width="60" height="51" hspace="1" style=" margin-top: 1px; margin-buttum: 10px;"></a> 
                                      <div class="container">
                                        <div class="navbar-header">
                                          <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                                            <span class="sr-only">Toggle navigation</span>
                                            <span class="icon-bar"></span>
                                            <span class="icon-bar"></span>
                                            <span class="icon-bar"></span>
                                          </button>
                                          <a class="navbar-brand" href="/sl">HACA SDR</a>
                                        </div>
                                        <div id="navbar" class="collapse navbar-collapse">
                                          
                                          <ul class="nav navbar-nav">
                                            <li><a href="/db"><b>Surveillance</b></a></li>
                                            <li><a href="/form"><b>Ploting and updating</b></a></li>
                                            <li><a href="/hom"><b>Recording history</b></a></li>
                                            <li class="dropdown scrollable"><a class="dropdown-toggle" data-toggle="dropdown" onclick="RazNumber()"><b>Alarms</b><span class="caret"></span></a>"""+str(Alarm_notif)+"""<li><a href="#"><center>Display all</center></a></li> </ul></li>
                                            <li><a href="/somestatistics"><b>Statistics</b></a></li>
                                            <li><a href="http://"""+str(get_lan_ip())+""":8001/streaming/" onclick="window.open('http://"""+str(get_lan_ip())+""":8001/streaming/', 'exemple', 'height=600, width=800, top=90, left=350, toolbar=no, menubar=no, location=yes, resizable=yes, scrollbars=yes, status=no'); return false;"><b>Real Time Streaming</b></a></li>
                                            <li id="logout"><a href="/out"><i class="glyphicon glyphicon-lock"></i> <b>Logout</b></a></li>
                                          </ul>
                                          
                                        </div><!--/.nav-collapse -->
                                      </div>
                                    </nav>
                                <div id="box"><p id="number">0</p></div>
                                <div class="container">
                                <br>
                                """+str(texto_html)+str(ID_html)+"""
                                </div>
                                </body>
                                </html>""")
            request.finish()

        d= getresult()
        d.addCallback(onResult)

        return NOT_DONE_YET

############################################################################################################
#Delete some registrations : 
############################################################################################################
class DeleteSomeRegistrations(Resource):
    isLeaf = True
    def render_GET(self, request):
        def delete_by_id(self):
            return dbpool.runOperation("DELETE FROM alarms where id = %s " % cgi.escape(request.args["id_alarm"][0]))
        def delete_all(self):
            return dbpool.runOperation("DELETE FROM alarms")
 
        def onResult(self):
            request.write("""<!DOCTYPE html>
                            <html>
                            <head>
                            """+str(src_url)+"""
                            <style>body {
                            padding-top: 50px;
                            }
                            .starter-template {
                            padding: 40px 15px;
                            text-align: center;
                            }
                            #logout{
                            position: fixed;
                            left:1225px;
                            top:0;
                            }
                            </style>
                            </head>
                            <body>
                            <nav class="navbar navbar-inverse navbar-fixed-top">
                            <div class="container">
                            <div class="navbar-header">
                            <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                            <span class="sr-only">Toggle navigation</span>
                            <span class="icon-bar"></span>
                            <span class="icon-bar"></span>
                            <span class="icon-bar"></span>
                            </button>
                            <a class="navbar-brand" href="#">HACA SDR</a>
                            </div>
                            <div id="navbar" class="collapse navbar-collapse">
                            <ul class="nav navbar-nav">
                            <li class="active"><a href="/db"><b>Surveillance</b></a></li>
                            <li><a href="#about"><b>Ploting and updating</b></a></li>
                            <li><a href="#contact"><b>recording history</b></a></li>
                            <li><a href="#contact"><b>Alarms</b></a></li>
                            <li><a href="http://"""+str(get_lan_ip())+""":8001/streaming/" onclick="window.open('http://"""+str(get_lan_ip())+""":8001/streaming/', 'exemple', 'height=600, width=800, top=90, left=350, toolbar=no, menubar=no, location=yes, resizable=yes, scrollbars=yes, status=no'); return false;"><b>Real Time Streaming</b></a></li>
                            <li id="logout"><a href="/logout"><i class="glyphicon glyphicon-lock"></i> <b>Logout</b></a></li>
                            </ul> 
                            </div>
                            </div>
                            </nav>
                            <div class="container">
                            <br>
                            """+msg+"""
                            </div>
                            </body>
                            </html>""")
            request.finish()

        if cgi.escape(cgi.escape(request.args["action"][0]))=="Remove": 
            msg = """<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a><strong> Well done  !</strong> You successfully deleted this registration ...</div>"""
            d1 = delete_by_id(self)   
            d1.addCallback(onResult)
        elif cgi.escape(cgi.escape(request.args["action"][0]))=="Remove all":
            msg = """<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a><strong> Well done  !</strong> You successfully deleted all registrations ...</div>"""
            d2 = delete_all(self)
            d2.addCallback(onResult)

 
        return NOT_DONE_YET
############################################################################################################
#Send data with jsonp about one frequency
############################################################################################################
class RealTimeOneFrequency(Resource):
    isLeaf = True
    f = 87
    def __init__(self):
        self.throttle = 1
        self.delayed_requests = []
        loopingCall = task.LoopingCall(self.processDelayedRequests)
        loopingCall.start(self.throttle, False)
        Resource.__init__(self)
    def render(self, request):
        request.setHeader('Content-Type', 'application/json')
        args = request.args
        if 'callback' in args:
            request.jsonpcallback =  args['callback'][0]
        if 'lastupdate' in args:
            request.lastupdate =  args['lastupdate'][0]
        else:
            request.lastupdate = 0
        data = self.getData(request)
        if len(data) > 0:
            return self.__format_response(request, data) 
        self.delayed_requests.append(request)
        return server.NOT_DONE_YET   
    def getData(self, request):
        sdr = RtlSdr()
        sdr.gain = 50
        data = {}
        def get_decibel_frequency(f):
            sdr.fc = (f*1000000)
            decibel = 0
            samples = sdr.read_samples(512*1024)
            decibel = 10*log10(var(samples))
            print (str(f)+"value got :" +str(decibel))
            return decibel        
        value = get_decibel_frequency(self.f)
        data = {'messages':[{'value':value},]}  
        return data
    def processDelayedRequests(self):
        for request in self.delayed_requests:
            data = self.getData(request)
            if len(data) > 0:
                try:
                    request.write(self.__format_response(request, data))
                    request.finish()
                except:
                    print 'connection lost before complete.'
                finally:
                    self.delayed_requests.remove(request)
    def __format_response(self, request, data):
        response = json.dumps({'data':data})
        if hasattr(request, 'jsonpcallback'):
            return request.jsonpcallback+'('+response+')'
        else:
            return response
############################################################################################################ 
class RealTimeRegistrationsOneFrequency(Resource):
    isLeaf = True
    def render_GET(self, request):
        RealTimeOneFrequency.f = float(cgi.escape(request.args["form-field0"][0]))
        frequency_alarms = list()
        time_alarms = list()
        situation_alarms = list()
        def get_result(self):
            return dbpool.runQuery("SELECT f, ts, tp FROM alarms order by id desc")
        def on_result(data):
            for row in data:
                frequency_alarms.append(row[0])
                time_alarms.append( row[1])
                situation_alarms.append( row[2])
            Alarm_notif = """<ul class="dropdown-menu" id ="messages">"""
            for i in range(3):
                try:
                    if frequency_alarms[i]:
                        if situation_alarms[i].endswith("begining.."):
                            Alarm_notif += """<li class="list-group-item list-group-item-danger"><a href="#" >"""+str(frequency_alarms[i])+""" Mhz :"""+str(situation_alarms[i])+""" at """+str(time_alarms[i])+"""</a></li>"""
                        elif situation_alarms[i].startswith("Low Alarm finished"):
                            Alarm_notif += """<li class="list-group-item list-group-item-success"><a href="#" >"""+str(frequency_alarms[i])+""" Mhz :"""+str(situation_alarms[i])+""" at """+str(time_alarms[i])+"""</a></li>"""
                except IndexError:
                    Alarm_notif += ''

            request.write("""
            <!DOCTYPE HTML>
            <html>
            <head>
            <title>Simulation of real time</title>
            """+str(src_url)+"""
            <style>body {
                padding-top: 70px;
            }
            .starter-template {
                padding: 40px 15px;
                text-align: center;
            }
            #logout{
            position: fixed;
            left:1225px;
            top:0;
            }
            </style>
            <style>
            #mycontent {
                height: 100px;
                }
            .active a {
                    border: 2px solid black;
                    }
            ul.nav-pills {
                    top: 207px;
                    position: fixed;
                    }
            </style>
            <script type="text/javascript" src="scripts/notifjs.js"></script>
            <script>
            function zeroNumber(){                                
            if(document.getElementById('number').innerHTML==0){
                document.getElementById('box').style.display="none";
            }else{
                document.getElementById('box').style.display="block";
            }}
            function RazNumber(){
                document.getElementById('number').innerHTML=0;
                zeroNumber();
            }
            function decreaseNumber(){
                n = n-1;
                document.getElementById('number').innerHTML=n;
            zeroNumber();
            }
            </script>
            </head>
            <style type="text/css">
            #box{
                width:25px;
                height:20px;
                background: red;
                position: fixed;
                left:729px;
                top:0;
                z-index: 9999;
                border-radius: 10px;
                color: white;
            }
            #number{
                text-align: center;
            }
            .dropdown-menu {
                max-height: 340px;
                overflow-y: scroll;
            }
            .pull-left{
                width:60px;
                height:51px;
                position: fixed;
                left:0.25px;
                top:1.75px;
                }
            </style>
            <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
            <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.0/jquery.min.js"></script>
            <script type="text/javascript" src="scripts/realonefreq.js"></script>
            <script src="http://code.highcharts.com/highcharts.js"></script>
            <script src="http://code.highcharts.com/highcharts-more.js"></script>
            <script src="http://code.highcharts.com/modules/exporting.js"></script>
            </head>
            <body onload=zeroNumber() data-spy="scroll" data-target="#sidebar" data-spy="affix" data-offset-top="28">
            <nav class="navbar navbar-inverse navbar-fixed-top">
            <a href="#" class="pull-left"><img src="scripts/logo_smallm.png" width="60" height="51" hspace="1" style=" margin-top: 1px; margin-buttum: 10px;"></a> 
            <div class="container">
            <div class="navbar-header">
            <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            </button>
            <a class="navbar-brand" href="/sl">HACA SDR</a>
            </div>
            <div id="navbar" class="collapse navbar-collapse">              
            <ul class="nav navbar-nav">
            <li class="active"><a href="/db"><b>Surveillance</b></a></li>
            <li class="dropdown"><a class="dropdown-toggle" data-toggle="dropdown" href="#"><b>Ploting and updating</b><span class="caret"></span></a><ul class="dropdown-menu"><li><a href="/form"><b>Band of frequencies</b></a></li><li role="presentation" class="divider"></li><li><a href="/parametersonefres"><b>One frequency</b></a></li></ul></li>
            <li><a href="/hom" ><b>Recording history</b></a></li>
            <li class="dropdown scrollable"><a class="dropdown-toggle" data-toggle="dropdown" onclick="RazNumber()"><b>Alarms</b><span class="caret"></span></a>"""+str(Alarm_notif)+"""<li><a href="/disall"><center>Display all</center></a></li></ul></li>
            <li><a href="/somestatistics"><b>Statistics</b></a></li>
            <li><a href="http://"""+str(get_lan_ip())+""":8001/streaming/" onclick="window.open('http://"""+str(get_lan_ip())+""":8001/streaming/', 'exemple', 'height=600, width=800, top=90, left=350, toolbar=no, menubar=no, location=yes, resizable=yes, scrollbars=yes, status=no'); return false;"><b>Real Time Streaming</b></a></li>
            <li id="logout"><a href="/logout"><i class="glyphicon glyphicon-lock"></i> <b>Logout</b></a></li>
            </ul>              
            </div>
            </div>
            </nav>
            <center><h1 id="title" >Frequency %s MHz</h1></center>
            <div id="container" style="min-width: 310px; height: 400px; margin: 0 auto"></div>
            </body>
            </html>
                    """ % RealTimeOneFrequency.f)
            request.finish()
        d= get_result(self)
        d.addCallback(on_result)

        return NOT_DONE_YET
############################################################################################################
#Some stastics about alarms per frequency 
############################################################################################################
class SomeStatisticsAlarms(Resource):
    isLeaf = True
    def render_GET(self, request):
        freq_alarm = list()
        freq_res = list()
        result = list()
        frequency_alarms = list()
        time_alarms = list()
        situation_alarms = list()
        filename = "toto"
        conn = sqlite3.connect(filename)
        ti = ctime(int(time()))
        curs = conn.cursor()
        curs.execute("select distinct f from alarms order by id desc")
        conn.commit()
        result_f = curs.fetchall()
        for row in result_f:
            freq_alarm.append( row[0] )
        def satistics(freq):
            resul = list()
            curs.execute("select count(id) from alarms where f = %s order by id desc" % freq )
            conn.commit()
            resul = curs.fetchall()
            for row in resul:
                result.append( row[0])
            return result
        for res in range(len(freq_alarm)):
            freq_res.append( satistics(freq_alarm[res]) )
        try:
            value_statistics_per_frequency = freq_res[0]
        except IndexError:
            value_statistics_per_frequency = []
        curs.execute("SELECT f, ts, tp FROM alarms order by id desc")
        conn.commit()
        resul_notif = curs.fetchall()
        for row in resul_notif:
            frequency_alarms.append(row[0])
            time_alarms.append( row[1])
            situation_alarms.append( row[2])
        texto_html_statics = ""
        for i in range(len(freq_alarm)-1):
            try:
                texto_html_statics += """{  y: """+str(value_statistics_per_frequency[i])+""", indexLabel: "  """+str(freq_alarm[i])+""" MHz" },"""
            except IndexError:
                texto_html_statics += ''
        try:
            texto_html_statics += """{  y: """+str(value_statistics_per_frequency[len(freq_alarm)-1])+""", indexLabel: "  """+str(freq_alarm[len(freq_alarm)-1])+""" MHz" }"""
        except IndexError:
            texto_html_statics += ''
        Alarm_notif = """<ul class="dropdown-menu" id ="messages">"""
        for i in range(3):
            try:
                if frequency_alarms[i]:
                    if situation_alarms[i].endswith("begining.."):
                        Alarm_notif += """<li class="list-group-item list-group-item-danger"><a href="#" >"""+str(frequency_alarms[i])+""" Mhz :"""+str(situation_alarms[i])+""" at """+str(time_alarms[i])+"""</a></li>"""
                    elif situation_alarms[i].startswith("Low Alarm finished"):
                        Alarm_notif += """<li class="list-group-item list-group-item-success"><a href="#" >"""+str(frequency_alarms[i])+""" Mhz :"""+str(situation_alarms[i])+""" at """+str(time_alarms[i])+"""</a></li>"""
            except IndexError:
                Alarm_notif += ''
        return """
                <!DOCTYPE HTML>
                <html>
                <head>
                """+str(src_url)+"""
                <style >
                #logout{
                position: fixed;
                left:1225px;
                top:0;
                }
                </style>
                <script type="text/javascript">
                window.onload = function () {
                  var chart = new CanvasJS.Chart("chartContainer",
                  {
                    theme: "theme2",
                    title:{
                      text: "Some statistics about alarms per frequency :"
                    },    
                    data: [
                    {       
                      type: "pie",
                      showInLegend: true,
                      toolTipContent: "{y} - #percent %",
                      yValueFormatString: "## Alarms",
                      legendText: "{indexLabel}",
                      dataPoints: [
                        """+texto_html_statics+"""
                      ]
                    }
                    ]
                  });
                  chart.render();
                }
                </script>
                <script type="text/javascript" src="scripts/canvasjs.min.js"></script></head>
                <script>
                function zeroNumber(){                                
                    if(document.getElementById('number').innerHTML==0){
                            document.getElementById('box').style.display="none";
                    }else{
                            document.getElementById('box').style.display="block";
                    }}
                function RazNumber(){
                            document.getElementById('number').innerHTML=0;
                            zeroNumber();
                    }
                function decreaseNumber(){
                            n = n-1;
                            document.getElementById('number').innerHTML=n;
                            zeroNumber();
                                }
                </script>
                <style type="text/css">
                    #box{
                            width:25px;
                            height:20px;
                            background: red;
                            position: fixed;
                            left:729px;
                            top:0;
                            z-index: 9999;
                            border-radius: 10px;
                            color: white;
                            }
                    #number{
                            text-align: center;
                             }
                    .dropdown-menu {
                            max-height: 340px;
                            overflow-y: scroll;
                             }
                    #chartContainer{
                              top: 80px;
                              position: fixed;
                    }
                    .pull-left{
                        width:60px;
                        height:51px;
                        position: fixed;
                        left:0.25px;
                        top:1.75px;
                            }
                </style>
                <body onload=zeroNumber() data-spy="scroll" data-target="#sidebar" data-spy="affix" data-offset-top="28">
                <nav class="navbar navbar-inverse navbar-fixed-top">
                <a href="#" class="pull-left"><img src="scripts/logo_smallm.png" width="60" height="51" hspace="1" style=" margin-top: 1px; margin-buttum: 10px;"></a>
                <div class="container">
                <div class="navbar-header">
                <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                <span class="sr-only">Toggle navigation</span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
                </button>
                <a class="navbar-brand" href="/sl">HACA SDR</a>
                </div>
                <div id="navbar" class="collapse navbar-collapse">              
                <ul class="nav navbar-nav">
                <li><a href="/db"><b>Surveillance</b></a></li>
                <li class="dropdown"><a class="dropdown-toggle" data-toggle="dropdown" href="#"><b>Ploting and updating</b><span class="caret"></span></a><ul class="dropdown-menu"><li><a href="/form"><b>Band of frequencies</b></a></li><li role="presentation" class="divider"></li><li><a href="/rof"><b>One frequency</b></a></li></ul></li>
                <li><a href="/hom" ><b>recording history</b></a></li>
                <li class="dropdown scrollable"><a class="dropdown-toggle" data-toggle="dropdown" onclick="RazNumber()"><b>Alarms</b><span class="caret"></span></a>"""+str(Alarm_notif)+"""<li><a href="/disall"><center>Display all</center></a></li></ul></li>
                <li class="active"><a href="/somestatistics"><b>Statistics</b></a></li>
                <li><a href="http://"""+str(get_lan_ip())+""":8001/streaming/" onclick="window.open('http://"""+str(get_lan_ip())+""":8001/streaming/', 'exemple', 'height=600, width=800, top=90, left=350, toolbar=no, menubar=no, location=yes, resizable=yes, scrollbars=yes, status=no'); return false;"><b>Real Time Streaming</b></a></li>
                <li id="logout"><a href="/logout"><i class="glyphicon glyphicon-lock"></i> <b>Logout</b></a></li>
                </ul>              
                </div>
                </div>
                </nav>
                <div id="box"><p id="number">0</p></div>
                <div id="chartContainer" style="height: 525px; width: 100%;"></div>
                </body>
                </html>
                        """
#############################################################################################################
#Parameters of real time for one frequency :
#############################################################################################################
class ParametersOneFreq(Resource):
    isLeaf = True
    def render_GET(self, request):
        def _getresult(txn):
            txn.execute("SELECT f, description, time, statut, highthreshold, lowthreshold  FROM monitor")
            result = txn.fetchall()
            txn.execute("SELECT f, ts, tp, value, id FROM alarms order by id desc")
            result1 = txn.fetchall()
            return result, result1
        def getresult():
            return dbpool.runInteraction(_getresult)
        def onResult(data):
            frequency = list()
            descriptions = list()
            ti = list()
            st = list()
            highthreshold = list()
            lowthreshold = list()
            frequency_alarms = list()
            time_alarms = list()
            situation_alarms = list()
            for row in data[0]:
                frequency.append( row[0] )
                descriptions.append( row[1] )
                ti.append( row[2] )
                st.append( row[3] )
                highthreshold.append( row[4] )
                lowthreshold.append( row[5] )
            for row in data[1]:
                frequency_alarms.append(row[0])
                time_alarms.append( row[1])
                situation_alarms.append( row[2])
            table_frequencies = """<div class="panel panel-primary" id="delfrequencies" ><div class="panel-heading"><b>Frequencies : </b></div><div class="panel-body"><div class="table-responsive" id ="showfrequencies"><table class="table"><thead><tr class=""><th>frequency</th><th><center>Description</center></th><th><center>Time</center></th><th>Status</th><th><center>Lowthreshold</center></th><th><center>Highthreshold</center></th></tr></thead><tbody>"""
            for i in range(len(frequency)):
                table_frequencies += "<tr><td><b>" + str(frequency[i]) +" MHz </b></td><td><b><center>" +str(descriptions[i])+ "</center></b></td><td><b><center>" +str(ti[i])+ "</center></b></td><td><b>" + str(st[i]) + "</b></td><td><center><b>" + str(lowthreshold[i]) + "</b></center></td><td><center><b>" + str(highthreshold[i]) + "</b></center></td></tr>"
            table_frequencies += "</tbody></table></div></div></div>"
            Alarm_notif = """<ul class="dropdown-menu" id ="messages">"""
            for i in range(3):
                try:
                    if frequency_alarms[i]:
                        if situation_alarms[i].endswith("begining.."):
                            Alarm_notif += """<li class="list-group-item list-group-item-danger"><a href="#" >"""+str(frequency_alarms[i])+""" Mhz :"""+str(situation_alarms[i])+""" at """+str(time_alarms[i])+"""</a></li>"""
                        elif situation_alarms[i].startswith("Low Alarm finished"):
                            Alarm_notif += """<li class="list-group-item list-group-item-success"><a href="#" >"""+str(frequency_alarms[i])+""" Mhz :"""+str(situation_alarms[i])+""" at """+str(time_alarms[i])+"""</a></li>"""
                except IndexError:
                    Alarm_notif += ''
            request.write("""<!DOCTYPE html>
                             <html>
                             <title> SDR Monitoring..</title>
                             <link rel="icon" type="image/png" href="scripts/logo_smallm.png">
                             <head>"""+str(src_url)+"""
                             <style>body {
                                    padding-top: 70px;
                                        }
                             .starter-template {
                                padding: 40px 15px;
                                text-align: center;
                             }
                             
                             #mycontent {
                                height: 100px;
                            }
                            .active a {
                                border: 2px solid black;
                            }
                            ul.nav-pills {
                              top: 208px;
                              position: fixed;
                            }
                            #logout{
                            position: fixed;
                            left:1225px;
                            top:0;
                            }
                             </style>
                             <script type="text/javascript" src="scripts/notifjs.js"></script>
                             <script>
                             function zeroNumber(){                                
                             if(document.getElementById('number').innerHTML==0){
                                document.getElementById('box').style.display="none";
                             }else{
                                document.getElementById('box').style.display="block";
                             }}
                             function RazNumber(){
                                document.getElementById('number').innerHTML=0;
                                zeroNumber();
                             }
                             function decreaseNumber(){
                                n = n-1;
                                document.getElementById('number').innerHTML=n;
                                zeroNumber();
                                  }
                             </script>
                        
                             <style type="text/css">
                             #box{
                                width:25px;
                                height:20px;
                                background: red;
                                position: fixed;
                                left:729px;
                                top:0;
                                z-index: 9999;
                                border-radius: 10px;
                                color: white;
                             }
                             #number{
                                text-align: center;
                             }
                             .dropdown-menu {
                                max-height: 340px;
                                overflow-y: scroll;
                             }
                            .pull-left{
                                width:60px;
                                height:51px;
                                position: fixed;
                                left:0.25px;
                                top:2px;
                             }
                             </style>
                             </head>
                             <body onload=zeroNumber() data-spy="scroll" data-target="#sidebar" data-spy="affix" data-offset-top="28">
                             <nav class="navbar navbar-inverse navbar-fixed-top">
                             <a href="#" class="pull-left"><img src="scripts/logo_smallm.png" width="60" height="51" hspace="1" style=" margin-top: 1px; margin-buttum: 1px;"></a> 
                             <div class="container">
                             <div class="navbar-header">
                             <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                             <span class="sr-only">Toggle navigation</span>
                             <span class="icon-bar"></span>
                             <span class="icon-bar"></span>
                             <span class="icon-bar"></span>
                             </button>
                             <a class="navbar-brand" href="/sl">HACA SDR</a>
                             </div>
                             <div id="navbar" class="collapse navbar-collapse">              
                             <ul class="nav navbar-nav">
                             <li><a href="/db"><b>Surveillance</b></a></li>
                             <li class="dropdown" ><a class="dropdown-toggle" data-toggle="dropdown" href="#"><b>Ploting and updating</b><span class="caret"></span></a><ul class="dropdown-menu"><li><a href="/form"><b>Band of frequencies</b></a></li><li role="presentation" class="divider"></li><li class="active"><a href="/parametersonefres"><b>One frequency</b></a></li></ul></li>
                             <li ><a href="/hom"><b>Recording history</b></a></li>
                             <li class="dropdown scrollable" ><a class="dropdown-toggle" data-toggle="dropdown" onclick="RazNumber()"><b>Alarms</b><span class="caret"></span></a>"""+str(Alarm_notif)+"""<li><a href="/disall"><center>Display all</center></a></li></ul></li>
                             <li><a href="/somestatistics"><b>Statistics</b></a></li>
                             <li><a href="http://"""+str(get_lan_ip())+""":8001/streaming/" onclick="window.open('http://"""+str(get_lan_ip())+""":8001/streaming/', 'exemple', 'height=600, width=800, top=90, left=350, toolbar=no, menubar=no, location=yes, resizable=yes, scrollbars=yes, status=no'); return false;"><b>Real Time Streaming</b></a></li>
                             <li id="logout"><a href="logout"><i class="glyphicon glyphicon-lock"></i> <b>Logout</b></a></li>
                             </ul>              
                             </div>
                             </div>
                             </nav>
                             <div id="box"><p id="number">0</p></div>
                             <div class="container">
                            <div class="page-header">
                            <h1>Real Time for One Frequency :</h1>      
                            </div>
                             """+str(table_frequencies)+"""
                             <div class="panel panel-primary" id="delfrequencies" ><div class="panel-heading"><b>The concerned Frequency : </b></div><div class="panel-body"><form action="/rof" method="GET" ><label>Frequency (MHz) :  </label><input type="float" class="form-control"  name="form-field0" placeholder="Type your frequency in MHz"><br><button  class="btn btn-primary" type="submit" value="add Frequency" size="1" ><b>Show Real time graph</b></button></form></div></div>
                             </div>
                             </div>
                             </div>
                             </body>
                             </html>""")
            request.finish()

        d= getresult()
        d.addCallback(onResult)

        return NOT_DONE_YET
#############################################################################################################
#Make thresholds and the duration before alarms 
#############################################################################################################   
class MakeParametersWithAlarms(Resource):
    isLeaf = True
    def render_GET(self, request):
        frequency_alarms =list()
        time_alarms = list()
        situation_alarms = list()
        def make_thresholds(self):
            low_threshold = float(cgi.escape(request.args["form-field1"][0]))
            high_threshold = float(cgi.escape(request.args["form-field3"][0]))
            frequency = float(cgi.escape(request.args["form-field0"][0]))
            return dbpool.runOperation("update monitor set  highthreshold="+str(high_threshold)+", lowthreshold ="+str(low_threshold)+"  where f="+str(frequency))
        def make_duration(self):
            duration = float(cgi.escape(request.args["form-field4"][0]))
            f = open("scripts/duration.json","w")
            d = {'duration':duration}
            json.dump(d,f)
            f.close()
            return f
        def begin_process(self):
            return dbpool.runOperation("update credential set control='with' where id=1 ")
        def onResult(self):
            conn = sqlite3.connect(filename)
            curs = conn.cursor()
            curs.execute("SELECT f, ts, tp FROM alarms order by id desc")
            conn.commit()
            resul_notif = curs.fetchall()
            for row in resul_notif:
                frequency_alarms.append(row[0])
                time_alarms.append( row[1])
                situation_alarms.append( row[2])
            Alarm_notif = """<ul class="dropdown-menu" id ="messages">"""
            for i in range(3):
                try:
                    if frequency_alarms[i]:
                        if situation_alarms[i].endswith("begining.."):
                            Alarm_notif += """<li class="list-group-item list-group-item-danger"><a href="#" >"""+str(frequency_alarms[i])+""" Mhz :"""+str(situation_alarms[i])+""" at """+str(time_alarms[i])+"""</a></li>"""
                        elif situation_alarms[i].startswith("Low Alarm finished"):
                            Alarm_notif += """<li class="list-group-item list-group-item-success"><a href="#" >"""+str(frequency_alarms[i])+""" Mhz :"""+str(situation_alarms[i])+""" at """+str(time_alarms[i])+"""</a></li>"""
                except IndexError:
                    Alarm_notif += ''
            request.write("""<!DOCTYPE html>
                            <html>
                            <head>
                            """+str(src_url)+"""
                            <style>body {
                            padding-top: 50px;
                            }
                            .starter-template {
                            padding: 40px 15px;
                            text-align: center;
                            }
                            #logout{
                            position: fixed;
                            left:1225px;
                            top:0;
                            }
                            </style>
                            </head>
                            <body>
                            <nav class="navbar navbar-inverse navbar-fixed-top">
                            <div class="container">
                            <div class="navbar-header">
                            <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                            <span class="sr-only">Toggle navigation</span>
                            <span class="icon-bar"></span>
                            <span class="icon-bar"></span>
                            <span class="icon-bar"></span>
                            </button>
                            <a class="navbar-brand" href="#">HACA SDR</a>
                            </div>
                            <div id="navbar" class="collapse navbar-collapse">
                            <ul class="nav navbar-nav">
                            <li class="active"><a href="/db"><b>Surveillance</b></a></li>
                            <li class="dropdown"><a class="dropdown-toggle" data-toggle="dropdown" href="#"><b>Ploting and updating</b><span class="caret"></span></a><ul class="dropdown-menu"><li><a href="/form"><b>Band of frequencies</b></a></li><li role="presentation" class="divider"></li><li><a href="/parametersonefres"><b>One frequency</b></a></li></ul></li>
                            <li><a href="/hom" ><b>Recording history</b></a></li>
                            <li class="dropdown scrollable"><a class="dropdown-toggle" data-toggle="dropdown" onclick="RazNumber()"><b>Alarms</b><span class="caret"></span></a>"""+str(Alarm_notif)+"""<li><a href="/disall"><center>Display all</center></a></li></ul></li>
                            <li><a href="/somestatistics"><b>Statistics</b></a></li>
                            <li><a href="http://"""+str(get_lan_ip())+""":8001/streaming/" onclick="window.open('http://"""+str(get_lan_ip())+""":8001/streaming/', 'exemple', 'height=600, width=800, top=90, left=350, toolbar=no, menubar=no, location=yes, resizable=yes, scrollbars=yes, status=no'); return false;"><b>Real Time Streaming</b></a></li>
                            <li id="logout"><a href="/logout"><i class="glyphicon glyphicon-lock"></i> <b>Logout</b></a></li>
                            </ul> 
                            </div>
                            </div>
                            </nav>
                            <div class="container">
                            <br>
                            """+msg+"""
                            </div>
                            </body>
                            </html>""")
            request.finish()

        if cgi.escape(cgi.escape(request.args["action"][0]))=="Make Thresholds": 
            msg = """<div class="alert alert-info"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a><strong> Well done  !</strong> You successfully made thresholds ...</div>"""
            d1 = make_thresholds(self)   
            d1.addCallback(onResult)
        elif cgi.escape(cgi.escape(request.args["action"][0]))=="Make the duration":
            msg = """<div class="alert alert-info"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a><strong> Well done  !</strong> You successfully made duration ...</div>"""
            d2 = make_duration(self)
            onResult(self)
        elif cgi.escape(cgi.escape(request.args["action"][0]))=="Begin Surveillance":
            msg = """<div class="alert alert-info"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a><strong> Well done  !</strong> You successfully turn on the system (mode with alarms) ...</div>"""
            d3 = begin_process(self)   
            d3.addCallback(onResult)

 
        return NOT_DONE_YET
#############################################################################################################
#History about measurement 
#############################################################################################################
class HistoryOfMeasure(Resource):
    isLeaf = True
    def render_GET(self, request):
        def _getresult(txn):
            txn.execute("SELECT f, ts, tp, value, id FROM alarms order by id desc")
            result1 = txn.fetchall()
            txn.execute("SELECT id, f, deci, ts FROM measurement ")
            result2 = txn.fetchall()
            return result1, result2
        def getresult():
            return dbpool.runInteraction(_getresult)
        def onResult(data):
            frequency_alarms = list()
            time_alarms = list()
            situation_alarms = list()
            value_alarms = list()
            id_alarms = list()
            frequency_mesure = list()
            id_mesure = list()
            deci_mesure = list()
            ts_mesure = list()
            if data[0]:
                for row in data[0]:
                    frequency_alarms.append(row[0])
                    time_alarms.append( row[1])
                    situation_alarms.append( row[2])
                    value_alarms.append( row[3])
                    id_alarms.append( row[4])
            for row in data[1]:
                id_mesure.append( row[0] )
                frequency_mesure.append( row[1] ) 
                deci_mesure.append(row[2])
                ts_mesure.append(row[3])
            ID_html = """<div class="panel panel-primary"><div class="panel-heading">Delete some registrations :</div><div class="panel-body"><form class="form-inline" action="/delmeasurement" method="GET"><label for="title">Id_measure : </label> <select class="form-control" name="id_mesure" >"""
            texto_html = """<table class="table"><thead><tr class="info" ><th><center>ID_ measure</center></th><th><center>Frequency</center></th><th><center>Power(DB)</center></th><th><center>Time</center></th></tr></thead><tbody><tbody>"""
            for tr in range(len(frequency_mesure)):
                    texto_html += """<tr ><td><center>"""+str(id_mesure[tr])+"""</center></td><td><center>"""+str(frequency_mesure[tr])+"""</center></td><td><center>"""+str(deci_mesure[tr])+"""</center></td><td><center>"""+str(ctime(ts_mesure[tr]))+"""</center></td></tr>"""
                    ID_html += """<option class="info">"""+str(id_mesure[tr])+"""</option>"""
            texto_html += "</tbody></table>"
            Alarm_notif = """<ul class="dropdown-menu" id ="messages">"""
            ID_html +="""</select> <input type="submit" name="action" value="Remove" class="btn btn-primary" />   <input type="submit" name="action" value="Remove all" class="btn btn-primary" /></form></div>""" 
            for i in range(3):
                try:
                    if frequency_alarms[i]:
                        if situation_alarms[i].endswith("begining.."):
                            Alarm_notif += """<li class="list-group-item list-group-item-danger"><a href="#" >"""+str(frequency_alarms[i])+""" Mhz :"""+str(situation_alarms[i])+""" at """+str(time_alarms[i])+"""</a></li>"""
                        elif situation_alarms[i].startswith("Low Alarm finished"):
                            Alarm_notif += """<li class="list-group-item list-group-item-success"><a href="#" >"""+str(frequency_alarms[i])+""" Mhz :"""+str(situation_alarms[i])+""" at """+str(time_alarms[i])+"""</a></li>"""

                except IndexError:
                    Alarm_notif += ''

            request.write("""<!DOCTYPE html>
                                <html>
                                <title> SDR Monitoring..</title>
                                <link rel="icon" type="image/png" href="scripts/logo_smallm.png">
                                <head>
                                """+str(src_url)+"""
                                <script type="text/javascript" src="scripts/notifjs.js"></script>
                                <style>body {
                                              padding-top: 50px;
                                            }
                                            .starter-template {
                                              pa
                                              dding: 40px 15px;
                                              text-align: center;
                                            }
                                #logout{
                                 position: fixed;
                                 left:1225px;
                                 top:0;
                                 }
                                </style>

                                <script>
                                function zeroNumber(){                                
                                    if(document.getElementById('number').innerHTML==0){
                                       document.getElementById('box').style.display="none";
                                    }else{
                                       document.getElementById('box').style.display="block";
                                   }}
                                function RazNumber(){
                                 document.getElementById('number').innerHTML=0;
                                 zeroNumber();
                                }
                                function decreaseNumber(){
                                n = n-1;
                                document.getElementById('number').innerHTML=n;
                                zeroNumber();
                                  }
                                </script>
                                </head>
                                <style type="text/css">
                                #box{
                                width:25px;
                                height:20px;
                                background: red;
                                position: fixed;
                                left:720px;
                                top:0;
                                z-index: 9999;
                                border-radius: 10px;
                                color: white;

                                }
                                #number{
                                   text-align: center;

                                }
                                .dropdown-menu {
                                max-height: 340px;
                                overflow-y: scroll;

                            }
                            .pull-left{
                                width:60px;
                                height:51px;
                                position: fixed;
                                left:0.25px;
                                top:1.75px;
                             }
                                </style>
                                <body onload=zeroNumber()>
                                <nav class="navbar navbar-inverse navbar-fixed-top">
                                <a href="#" class="pull-left"><img src="scripts/logo_smallm.png" width="60" height="51" hspace="1" style=" margin-top: 1px; margin-buttum: 10px;"></a> 
                                      <div class="container">
                                        <div class="navbar-header">
                                          <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                                            <span class="sr-only">Toggle navigation</span>
                                            <span class="icon-bar"></span>
                                            <span class="icon-bar"></span>
                                            <span class="icon-bar"></span>
                                          </button>
                                          <a class="navbar-brand" href="/sl">HACA SDR</a>
                                        </div>
                                        <div id="navbar" class="collapse navbar-collapse">
                                          
                                          <ul class="nav navbar-nav">
                                            <li><a href="/db"><b>Surveillance</b></a></li>
                                            <li><a href="/form"><b>Ploting and updating</b></a></li>
                                            <li><a href="/hom" ><b>Recording history</b></a></li>
                                            <li class="dropdown scrollable"><a class="dropdown-toggle" data-toggle="dropdown" onclick="RazNumber()"><b>Alarms</b><span class="caret"></span></a>"""+str(Alarm_notif)+"""<li><a href="/disall"><center>Display all</center></a></li> </ul></li>
                                            <li><a href="/somestatistics"><b>Statistics</b></a></li>
                                            <li><a href="http://"""+str(get_lan_ip())+""":8001/streaming/" onclick="window.open('http://"""+str(get_lan_ip())+""":8001/streaming/', 'exemple', 'height=600, width=800, top=90, left=350, toolbar=no, menubar=no, location=yes, resizable=yes, scrollbars=yes, status=no'); return false;"><b>Real Time Streaming</b></a></li>
                                            <li id="logout"><a href="/logout"><i class="glyphicon glyphicon-lock"></i> <b>Logout</b></a></li>
                                          </ul>
                                          
                                        </div><!--/.nav-collapse -->
                                      </div>
                                    </nav>
                                <div id="box"><p id="number">0</p></div>
                                <div class="container">
                                <br>
                                """+str(texto_html)+str(ID_html)+"""
                                </div>
                                </body>
                                </html>""")
            request.finish()

        d= getresult()
        d.addCallback(onResult)

        return NOT_DONE_YET
#############################################################################################################
#Delete Some measurement 
#############################################################################################################
class DeleteSomeMeasurement(Resource):
    isLeaf = True
    def render_GET(self, request):
        def delete_by_id(self):
            return dbpool.runOperation("DELETE FROM measurement where id = %s " % cgi.escape(request.args["id_mesure"][0]))
        def delete_all(self):
            return dbpool.runOperation("DELETE FROM measurement")
 
        def onResult(self):
            request.write("""<!DOCTYPE html>
                            <html>
                            <head>
                            """+str(src_url)+"""
                            <style>body {
                            padding-top: 50px;
                            }
                            .starter-template {
                            padding: 40px 15px;
                            text-align: center;
                            }
                            #logout{
                            position: fixed;
                            left:1225px;
                            top:0;
                             }
                            </style>
                            </head>
                            <body>
                            <nav class="navbar navbar-inverse navbar-fixed-top">
                            <div class="container">
                            <div class="navbar-header">
                            <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                            <span class="sr-only">Toggle navigation</span>
                            <span class="icon-bar"></span>
                            <span class="icon-bar"></span>
                            <span class="icon-bar"></span>
                            </button>
                            <a class="navbar-brand" href="#">HACA SDR</a>
                            </div>
                            <div id="navbar" class="collapse navbar-collapse">
                            <ul class="nav navbar-nav">
                            <li class="active"><a href="/db"><b>Surveillance</b></a></li>
                            <li><a href="#about"><b>Ploting and updating</b></a></li>
                            <li><a href="#contact"><b>recording history</b></a></li>
                            <li><a href="#contact"><b>Alarms</b></a></li>
                            <li><a href="http://"""+str(get_lan_ip())+""":8001/streaming/" onclick="window.open('http://"""+str(get_lan_ip())+""":8001/streaming/', 'exemple', 'height=600, width=800, top=90, left=350, toolbar=no, menubar=no, location=yes, resizable=yes, scrollbars=yes, status=no'); return false;"><b>Real Time Streaming</b></a></li>
                            <li id="logout"><a href="#"><i class="glyphicon glyphicon-lock"></i> <b>Logout</b></a></li>
                            </ul> 
                            </div>
                            </div>
                            </nav>
                            <div class="container">
                            <br>
                            """+msg+"""
                            </div>
                            </body>
                            </html>""")
            request.finish()

        if cgi.escape(cgi.escape(request.args["action"][0]))=="Remove": 
            msg = """<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a><strong> Well done  !</strong> You successfully deleted this registration ...</div>"""
            d1 = delete_by_id(self)   
            d1.addCallback(onResult)
        elif cgi.escape(cgi.escape(request.args["action"][0]))=="Remove all":
            msg = """<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a><strong> Well done  !</strong> You successfully deleted all registrations ...</div>"""
            d2 = delete_all(self)
            d2.addCallback(onResult)

 
        return NOT_DONE_YET

##############################################################################################################
#Interface d'authentification
##############################################################################################################
class AuthentificationInterface(Resource):
    isLeaf = True
    def render_GET(self, request):
        return """
        <!DOCTYPE html>
        <html>
        <title> SDR Monitoring..</title>
        <link rel="icon" type="image/png" href="scripts/logo_smallm.png">
        <head>"""+str(src_url)+"""
        <style>
        body, html {
            height: 100%;
            background-repeat: no-repeat;
            background-image: linear-gradient(rgb(104, 145, 162), rgb(12, 97, 33));
        }

        .card-container.card {
            width: 350px;
            padding: 40px 40px;
        }

        .btn {
            font-weight: 700;
            height: 36px;
            -moz-user-select: none;
            -webkit-user-select: none;
            user-select: none;
            cursor: default;
        }
        .card {
            background-color: #F7F7F7;
            /* just in case there no content*/
            padding: 20px 25px 30px;
            margin: 0 auto 25px;
            margin-top: 50px;
            /* shadows and rounded borders */
            -moz-border-radius: 2px;
            -webkit-border-radius: 2px;
            border-radius: 2px;
            -moz-box-shadow: 0px 2px 2px rgba(0, 0, 0, 0.3);
            -webkit-box-shadow: 0px 2px 2px rgba(0, 0, 0, 0.3);
            box-shadow: 0px 2px 2px rgba(0, 0, 0, 0.3);
        }

        .profile-img-card {
            width: 96px;
            height: 96px;
            margin: 0 auto 10px;
            display: block;
            -moz-border-radius: 50%;
            -webkit-border-radius: 50%;
            border-radius: 50%;
        }
        .profile-name-card {
            font-size: 16px;
            font-weight: bold;
            text-align: center;
            margin: 10px 0 0;
            min-height: 1em;
        }
        .reauth-email {
            display: block;
            color: #404040;
            line-height: 2;
            margin-bottom: 10px;
            font-size: 14px;
            text-align: center;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            -moz-box-sizing: border-box;
            -webkit-box-sizing: border-box;
            box-sizing: border-box;
        }
        .form-signin #inputEmail,
        .form-signin #inputPassword {
            direction: ltr;
            height: 44px;
            font-size: 16px;
        }
        .form-signin input[type=email],
        .form-signin input[type=password],
        .form-signin input[type=text],
        .form-signin button {
            width: 100%;
            display: block;
            margin-bottom: 10px;
            z-index: 1;
            position: relative;
            -moz-box-sizing: border-box;
            -webkit-box-sizing: border-box;
            box-sizing: border-box;
        }
        .form-signin .form-control:focus {
            border-color: rgb(104, 145, 162);
            outline: 0;
            -webkit-box-shadow: inset 0 1px 1px rgba(0,0,0,.075),0 0 8px rgb(104, 145, 162);
            box-shadow: inset 0 1px 1px rgba(0,0,0,.075),0 0 8px rgb(104, 145, 162);
        }
        .btn-signin {
            /*background-color: #4d90fe; */
            background-color: rgb(104, 145, 162);
            /* background-color: linear-gradient(rgb(104, 145, 162), rgb(12, 97, 33));*/
            padding: 0px;
            font-weight: 700;
            font-size: 14px;
            height: 36px;
            -moz-border-radius: 3px;
            -webkit-border-radius: 3px;
            border-radius: 3px;
            border: none;
            -o-transition: all 0.218s;
            -moz-transition: all 0.218s;
            -webkit-transition: all 0.218s;
            transition: all 0.218s;
        }

        .btn-signin:hover,
        .btn-signin:active,
        .btn-signin:focus {
            background-color: rgb(12, 97, 33);
        }

        .forgot-password {
            color: rgb(104, 145, 162);
        }

        .forgot-password:hover,
        .forgot-password:active,
        .forgot-password:focus{
            color: rgb(12, 97, 33);
        }
        </style>
        <script type="text/javascript">
        function supportsHTML5Storage() {
            try {
                return 'localStorage' in window && window['localStorage'] !== null;
            } catch (e) {
                return false;
            }
        }

        /**
         * Test data. This data will be safe by the web app
         * in the first successful login of a auth user.
         * To Test the scripts, delete the localstorage data
         * and comment this call.
         *
         * @returns {boolean}
         */
        function testLocalStorageData() {
            if(!supportsHTML5Storage()) { return false; }
            localStorage.setItem("PROFILE_IMG_SRC", "//lh3.googleusercontent.com/-6V8xOA6M7BA/AAAAAAAAAAI/AAAAAAAAAAA/rzlHcD0KYwo/photo.jpg?sz=120" );
            localStorage.setItem("PROFILE_NAME", "César Izquierdo Tello");
            localStorage.setItem("PROFILE_REAUTH_EMAIL", "oneaccount@gmail.com");
        }
        </script>
        <head>
        <body>
        <div class="container">
        <div class="card card-container">
            <!-- <img class="profile-img-card" src="scripts/logo_smallm.png" alt="" /> -->
            <img id="profile-img" class="profile-img-card" src="//ssl.gstatic.com/accounts/ui/avatar_2x.png" />
            <p id="profile-name" class="profile-name-card"></p>
            <form class="form-signin" action="/home" method="POST">
                <span id="reauth-email" class="reauth-email"></span>
                <input type="string" name="username" id="inputEmail" class="form-control" placeholder="UserName" required autofocus>
                <input type="password" name="password" id="inputPassword" class="form-control" placeholder="Password" required>
                <div id="remember" class="checkbox">
                    <label>
                        <input type="checkbox" value="remember-me"> Remember me
                    </label>
                </div>
                <button class="btn btn-lg btn-primary btn-block btn-signin" type="submit">Sign in</button>
            </form><!-- /form -->

        </div><!-- /card-container -->
    </div><!-- /container -->
        </body>
        </html>

        """
class LogOutInterface(Resource):
    isLeaf = True
    def render_GET(self, request):
        global password, username
        password = "out"
        username = "out"
        return """
        <!DOCTYPE html>
        <html>
        <title> SDR Monitoring..</title>
        <link rel="icon" type="image/png" href="scripts/logo_smallm.png">
        <head>"""+str(src_url)+"""
        <style>
        body, html {
            height: 100%;
            background-repeat: no-repeat;
            background-image: linear-gradient(rgb(104, 145, 162), rgb(12, 97, 33));
        }

        .card-container.card {
            width: 350px;
            padding: 40px 40px;
        }

        .btn {
            font-weight: 700;
            height: 36px;
            -moz-user-select: none;
            -webkit-user-select: none;
            user-select: none;
            cursor: default;
        }
        .card {
            background-color: #F7F7F7;
            /* just in case there no content*/
            padding: 20px 25px 30px;
            margin: 0 auto 25px;
            margin-top: 50px;
            /* shadows and rounded borders */
            -moz-border-radius: 2px;
            -webkit-border-radius: 2px;
            border-radius: 2px;
            -moz-box-shadow: 0px 2px 2px rgba(0, 0, 0, 0.3);
            -webkit-box-shadow: 0px 2px 2px rgba(0, 0, 0, 0.3);
            box-shadow: 0px 2px 2px rgba(0, 0, 0, 0.3);
        }

        .profile-img-card {
            width: 96px;
            height: 96px;
            margin: 0 auto 10px;
            display: block;
            -moz-border-radius: 50%;
            -webkit-border-radius: 50%;
            border-radius: 50%;
        }
        .profile-name-card {
            font-size: 16px;
            font-weight: bold;
            text-align: center;
            margin: 10px 0 0;
            min-height: 1em;
        }
        .reauth-email {
            display: block;
            color: #404040;
            line-height: 2;
            margin-bottom: 10px;
            font-size: 14px;
            text-align: center;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            -moz-box-sizing: border-box;
            -webkit-box-sizing: border-box;
            box-sizing: border-box;
        }
        .form-signin #inputEmail,
        .form-signin #inputPassword {
            direction: ltr;
            height: 44px;
            font-size: 16px;
        }
        .form-signin input[type=email],
        .form-signin input[type=password],
        .form-signin input[type=text],
        .form-signin button {
            width: 100%;
            display: block;
            margin-bottom: 10px;
            z-index: 1;
            position: relative;
            -moz-box-sizing: border-box;
            -webkit-box-sizing: border-box;
            box-sizing: border-box;
        }
        .form-signin .form-control:focus {
            border-color: rgb(104, 145, 162);
            outline: 0;
            -webkit-box-shadow: inset 0 1px 1px rgba(0,0,0,.075),0 0 8px rgb(104, 145, 162);
            box-shadow: inset 0 1px 1px rgba(0,0,0,.075),0 0 8px rgb(104, 145, 162);
        }
        .btn-signin {
            /*background-color: #4d90fe; */
            background-color: rgb(104, 145, 162);
            /* background-color: linear-gradient(rgb(104, 145, 162), rgb(12, 97, 33));*/
            padding: 0px;
            font-weight: 700;
            font-size: 14px;
            height: 36px;
            -moz-border-radius: 3px;
            -webkit-border-radius: 3px;
            border-radius: 3px;
            border: none;
            -o-transition: all 0.218s;
            -moz-transition: all 0.218s;
            -webkit-transition: all 0.218s;
            transition: all 0.218s;
        }

        .btn-signin:hover,
        .btn-signin:active,
        .btn-signin:focus {
            background-color: rgb(12, 97, 33);
        }

        .forgot-password {
            color: rgb(104, 145, 162);
        }

        .forgot-password:hover,
        .forgot-password:active,
        .forgot-password:focus{
            color: rgb(12, 97, 33);
        }
        </style>
        <script type="text/javascript">
        function supportsHTML5Storage() {
            try {
                return 'localStorage' in window && window['localStorage'] !== null;
            } catch (e) {
                return false;
            }
        }

        /**
         * Test data. This data will be safe by the web app
         * in the first successful login of a auth user.
         * To Test the scripts, delete the localstorage data
         * and comment this call.
         *
         * @returns {boolean}
         */
        function testLocalStorageData() {
            if(!supportsHTML5Storage()) { return false; }
            localStorage.setItem("PROFILE_IMG_SRC", "//lh3.googleusercontent.com/-6V8xOA6M7BA/AAAAAAAAAAI/AAAAAAAAAAA/rzlHcD0KYwo/photo.jpg?sz=120" );
            localStorage.setItem("PROFILE_NAME", "César Izquierdo Tello");
            localStorage.setItem("PROFILE_REAUTH_EMAIL", "oneaccount@gmail.com");
        }
        </script>
        <head>
        <body>
        <div class="container">
        <div class="card card-container">
            <!-- <img class="profile-img-card" src="scripts/logo_smallm.png" alt="" /> -->
            <img id="profile-img" class="profile-img-card" src="//ssl.gstatic.com/accounts/ui/avatar_2x.png" />
            <p id="profile-name" class="profile-name-card"></p>
            <form class="form-signin" action="/home" method="POST">
                <span id="reauth-email" class="reauth-email"></span>
                <input type="string" name="username" id="inputEmail" class="form-control" placeholder="UserName" required autofocus>
                <input type="password" name="password" id="inputPassword" class="form-control" placeholder="Password" required>
                <div id="remember" class="checkbox">
                    <label>
                        <input type="checkbox" value="remember-me"> Remember me
                    </label>
                </div>
                <button class="btn btn-lg btn-primary btn-block btn-signin" type="submit">Sign in</button>
            </form><!-- /form -->

        </div><!-- /card-container -->
    </div><!-- /container -->
        </body>
        </html>

        """

#############################################################################################################
# Start listening as HTTP server
print """Web server started.  Visit http://"""+str(get_lan_ip())+""":8000/index"""
#log.startLogging(sys.stdout)
root = Resource()
root.putChild("", InfoServer())
root.putChild("disall", Allmesure())
root.putChild("delsomereg", DeleteSomeRegistrations())
root.putChild("notif", InfoNotification())
root.putChild("up", Updtaed())
root.putChild("form", Formulaire())
root.putChild("db", Home())
root.putChild("home", DatabasePage())
root.putChild("gra", Graph())
root.putChild("add", Add_frequ())
root.putChild("del", Del_frequ())
root.putChild("sg", Show_gra())
root.putChild('scripts', static.File("./scripts"))
root.putChild("cgi-bin", twcgi.CGIDirectory("./cgi-bin"))
root.putChild("ch", ChangeState())
root.putChild("st", ChangeStateTostop())
root.putChild("sl", Slide())
root.putChild("change", ChangeOnff())
root.putChild("rtof", RealTimeOneFrequency())
root.putChild("rof", RealTimeRegistrationsOneFrequency())
root.putChild("somestatistics", SomeStatisticsAlarms())
root.putChild("parametersonefres",ParametersOneFreq())
root.putChild("parameterswithalarms", MakeParametersWithAlarms())
root.putChild("hom",HistoryOfMeasure())
root.putChild("delmeasurement", DeleteSomeMeasurement())
root.putChild("index", AuthentificationInterface())
root.putChild("logout", LogOutInterface())
factory = Site(root)
reactor.listenTCP(8000, factory)
reactor.run()
exit()
#if you have the problem of port already used !! use this command lsof -i:numeroPort and kill the processus
#<button type="button" class="btn btn-default" onclick="window.location='/ch';">Start monitoring</button>
