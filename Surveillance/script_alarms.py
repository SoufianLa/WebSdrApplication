#!/usr/bin/env python
from __future__ import division
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.enterprise import adbapi
from twisted.web.server import NOT_DONE_YET
from twisted.internet.task import deferLater
from twisted.internet import task
from twisted.web.static import File
from twisted.web import static
from rtlsdr import *
from time import time
from time import *
from time import sleep
import sqlite3
from pylab import *
import sys
import argparse
from bottle import request
import cgi
import string
import json
from twisted.python import log
import getpass
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import os
filename = "toto"
dbpool = adbapi.ConnectionPool("sqlite3", filename, check_same_thread=False)

print "process begin ..."

#recuperer les frequences de l etat ON

def retrieve_all_freq_m():
        f = list()
        filename = "toto"
        var = "ON"
        conn = sqlite3.connect(filename)
        curs = conn.cursor()
        conn.commit()
        curs.execute("select f from monitor  where statut like 'ON' ")
        rows = curs.fetchall()
        for row in rows:
            f.append(row[0])
        conn.close()
        return f
def verify():
    f = list()
    filename = "toto"
    conn = sqlite3.connect(filename)
    curs = conn.cursor()
    conn.commit()
    curs.execute("select control from credential")
    rows = curs.fetchall()
    for row in rows:
            f.append(row[0])
    conn.close()
    return f

def association_indices_alarmes(retrieve_all_freq_m):
    indices = list()
    for i in range(len(retrieve_all_freq_m)):
        indices.append(0)
    return indices

def retrieve_highthreshold(f):
    filename = "toto"
    conn = sqlite3.connect(filename)
    curs = conn.cursor()
    curs.execute("select highthreshold from monitor  where f="+str(f))
    conn.commit()
    threshold = curs.fetchone()
    conn.close()
    return threshold

def retrieve_lowthreshold(f):
    filename = "toto"
    conn = sqlite3.connect(filename)
    curs = conn.cursor()
    curs.execute("select lowthreshold from monitor  where f="+str(f))
    conn.commit()
    threshold = curs.fetchone()
    conn.close()
    return threshold

def fichjson(idd, ff, valuee, tss, tpp):
    f = open("scripts/alarms.json","w")
    d = {'id':idd,'f':ff,'value':valuee,'ts':tss,'tp':tpp}
    json.dump(d,f)
    f.close()
    
def retrieve_duration_before():
    f= open("scripts/duration.json", "r")
    d=json.load(f)
    duration = d["duration"]
    f.close()
    return duration

duration_before = retrieve_duration_before()

######################Mailing ###########################

def login():
   global gmail_user, gmail_pwd
   gmail_user = "##" #Your mail here
   gmail_pwd = "##"  #Your password
   
def mail(to, subject, text, attach=None):
   msg = MIMEMultipart()
   msg['From'] = gmail_user
   msg['To'] = to
   msg['Subject'] = subject
   msg.attach(MIMEText(text))
   if attach:
      part = MIMEBase('application', 'octet-stream')
      part.set_payload(open(attach, 'rb').read())
      Encoders.encode_base64(part)
      part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(attach))
      msg.attach(part)
   mailServer = smtplib.SMTP("smtp.gmail.com", 587)
   mailServer.ehlo()
   mailServer.starttls()
   mailServer.ehlo()
   mailServer.login(gmail_user, gmail_pwd)
   mailServer.sendmail(gmail_user, to, msg.as_string())
   mailServer.close()

def main():
    ##########################################
    login()
    #########################################
    conn = sqlite3.connect(filename)
    curs = conn.cursor()
    starttime = int(time())
    i=0
    while True:
        v = verify()
        if 'without' in v: #si la surveillance est sans alarmes 
            if i == 0:
                sdr = RtlSdr()
            i=i+1
            sdr.gain = 50
            d = retrieve_all_freq_m()
            for f in d:
                sdr.fc = f * 1000000
                decibel = 0
                timestamp = int(time()) #ctime(int(time()))
                samples = sdr.read_samples(256*1024)
                decibel = 10*log10(var(samples))
                curs.execute("INSERT INTO measurement(f, deci, ts) VALUES(?, ?, ?)", (f, decibel, timestamp))
                conn.commit()
                print(" "+str(f)+" was INSERTED  !  time is: "+str(timestamp)+"and decibel is"+str(decibel)+"  signal mean :", +sum(samples)/len(samples))
        elif 'with' in v: #si la surveillance est avec alarmes
            if i == 0:
                sdr = RtlSdr()
            sdr.gain = 50
            d = retrieve_all_freq_m()
            indices_alarms_high = association_indices_alarmes(d)
            indices_stables_high = association_indices_alarmes(d)
            indices_alarms_low = association_indices_alarmes(d)
            indices_stables_low = association_indices_alarmes(d)
            if i>0:
                for i in range(len(old_indices_alarms_high)):
                    indices_alarms_high[i] = old_indices_alarms_high[i]
                    indices_stables_high[i] = old_indices_stable_high[i]
                    indices_alarms_low[i] = old_indices_alarms_low[i]
                    indices_stables_low[i] = old_indices_stable_low[i]
            for j in range(len(d)):
                sdr.fc = d[j] * 1000000
                decibel = 0
                t_high = retrieve_highthreshold(d[j])   
                t_low = retrieve_lowthreshold(d[j])
                timestamp = int(time())
                samples = sdr.read_samples(256*1024)
                decibel = 10*log10(var(samples))
                curs.execute("INSERT INTO measurement(f, deci, ts) VALUES(?, ?, ?)", (d[j], decibel, timestamp))
                conn.commit()
                #print(" "+str(d[j])+" was INSERTED  !  time is: "+str(timestamp)+"and decibel is"+str(decibel))
                #############################Testing if there is an increase in power#######################
                if all(t_high): 

                    if( decibel > t_high):
                        indices_alarms_high[j] = indices_alarms_high[j] + 1
                        if(indices_alarms_high[j] == duration_before):
                            idd = 'Red'
                            t1 = int(time())
                            timstp = ctime(t1)
                            tp = "High Alarm is begining.."
                            #suivi = indices_alarms[j]
                            print("High Alamre for "+str(d[j])+" is begining and this its threshold : "+str(t_high)+" !!")
                            curs.execute("INSERT INTO alarms(f, value, ts, tp, t_high) VALUES(?, ?, ?, ?, ?)", (d[j], decibel, timstp, tp, t_high[0]))
                            conn.commit()
                            fichjson(idd, d[j], decibel, timstp, tp)
                            sleep(1)
                            fichjson(0, 0, 0, 0, 0)
                            try:
                                mail("#Your mail here#", " Alarm detected at"+str(timstp), "Frequecy :"+str(d[j])+".."+str(tp)+"!! threshold (DB) is fixed :"+str(t_low)+".. power level(DB) :"+str(decibel))
                                #fonction d'envoi des SMS
                            except:
                                pass
                            
                       
                    elif(decibel<t_high):
                        if(indices_alarms_high[j] < duration_before):
                            indices_alarms_high[j]=0
                        if (indices_alarms_high[j] > duration_before):
                            #if (indices_alarms[j] == suivi):
                                indices_stables_high[j] = indices_stables_high[j] + 1
                                #suivi = indices_alarms[j]
                            #else:
                                #suivi = indices_alarms[j]
                        if (indices_stables_high[j] == duration_before):
                            t2 = int(time())
                            timstp2 = ctime(t2)
                            duration = t2-t1
                            tp = "High alarm finished ...its duration is "+str(duration)+" sec "
                            print("High alarme finished for: "+str(d[j])+"!! and this its duration "+str(duration)+" sec!!")
                            curs.execute("INSERT INTO alarms(f, value, ts, tp, t_high) VALUES(?, ?, ?, ?, ?)", (d[j], decibel, timstp2, tp, t_high[0]))
                            conn.commit()
                            fichjson("Green", d[j], decibel, timstp2, tp)
                            sleep(1)
                            fichjson(0, 0, 0, 0, 0)
                            indices_alarms_high[j] = 0
                            indices_stables_high[j] = 0
                            try:
                                mail("#Your mail here#", " Alarm detected at"+str(timstp2), "Frequecy :"+str(d[j])+".."+str(tp)+"!! threshold (DB) is fixed :"+str(t_low)+".. power level(DB) :"+str(decibel))
                                #fonction d'envoi des SMS
                            except:
                                pass
                #####################################################Testing if there is a power loss######################################################################
                if all(t_low):

                    if( decibel < t_low):
                        
                        indices_alarms_low[j] = indices_alarms_low[j] + 1
                        if(indices_alarms_low[j] == duration_before):
                            idd = 'Red'
                            t1 = int(time())
                            timstp3 = ctime(t1)
                            tp = "Low Alarm is begining.."
                            print("Low Alamre for "+str(d[j])+" is begining and this its threshold : "+str(t_low)+" !!")
                            curs.execute("INSERT INTO alarms(f, value, ts, tp, t_low) VALUES(?, ?, ?, ?, ?)", (d[j], decibel, timstp3, tp, t_low[0]))
                            conn.commit()
                            fichjson(idd, d[j], decibel, timstp3, tp)
                            sleep(1)
                            fichjson(0, 0, 0, 0, 0)
                            try:
                                mail("#Your mail here#", " Alarm detected at"+str(timstp3), "Frequecy :"+str(d[j])+".."+str(tp)+"!! threshold (DB) is fixed :"+str(t_low)+".. power level(DB) :"+str(decibel))
                                #fonction d envoi des SMS
                            except:
                                pass
                            print "mail sent !!"
                        print indices_alarms_low
                    elif(decibel > t_low):
                        if(indices_alarms_low[j] < duration_before):
                            indices_alarms_low[j]=0
                        if (indices_alarms_low[j] > duration_before):
                                indices_stables_low[j] = indices_stables_low[j] + 1
                    
                        if (indices_stables_low[j] == duration_before):
                            t2 = int(time())
                            timstp4 = ctime(t2)
                            duration = t2-t1
                            tp = "Low Alarm finished ... its duration is "+str(duration)+" sec "
                            print("Low alarme finished for: "+str(d[j])+"!! and this its duration "+str(duration)+" sec!!")
                            curs.execute("INSERT INTO alarms(f, value, ts, tp,t_low ) VALUES(?, ?, ?, ?, ?)", (d[j], decibel, timstp4, tp, t_low[0]))
                            conn.commit()
                            fichjson("Green", d[j], decibel, timstp4, tp)
                            sleep(1)
                            fichjson(0, 0, 0, 0, 0)
                            indices_alarms_low[j] = 0
                            indices_stables_low[j] = 0
                            try:
                                mail("HACASDR@gmail.com", " Alarm detected at"+str(timstp4), "Frequecy :"+str(d[j])+".."+str(tp)+"!! threshold (DB) is fixed :"+str(t_low)+".. power level(DB) :"+str(decibel))
                                #fonction d envoi des SMS
                            except:
                                pass
            old_indices_alarms_high = indices_alarms_high 
            old_indices_stable_high = indices_stables_high
            old_indices_alarms_low = indices_alarms_low 
            old_indices_stable_low = indices_stables_low

            i = i+1
        else :
            break
    print" terminated !!"
    conn.close()

if __name__ == '__main__':
    main()
