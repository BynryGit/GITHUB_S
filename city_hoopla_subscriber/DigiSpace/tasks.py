from celery import task
from django.test import TestCase
import time
import datetime
from datetime import datetime
from datetime import timedelta 
import threading
from threading import Timer
#import sched
import urllib
import smtplib
from smtplib import SMTPException
import urllib2

# Create your tests here.

#from consumerapp.models import SimpleCount

@task
def send_to_subscriber(slist):
    i=0
    description=''
    for i in range(len(slist)):
        print '------i-------',i
        a = slist[i]
        sid = a.get('supplier_id')
        bname = a.get('bname')
        phone = a.get('phone')
        address = a.get('address')   
        searchfor = a.get('searchfor')
        area = a.get('area')
        c_name = a.get('c_name')
        c_number = a.get('c_number')
        enquiry_service_name = a.get('enquiry_service_name')
        es_name = a.get('es_name')
        n = a.get('n')
        print '------n------',n
        print '------list-------',a
        print '-------enquiry_service_name------',enquiry_service_name
        
        if es_name=='P':
            send_p1(bname,phone,searchfor,area,c_name,c_number)
        if es_name=='D':
            time.sleep(10*60)
            send_p1(bname,phone,searchfor,area,c_name,c_number)
        elif es_name=='G':
            time.sleep(10*60)
            send_p1(bname,phone,searchfor,area,c_name,c_number)
        elif es_name=='S':
            time.sleep(5*60)
            send_p1(bname,phone,searchfor,area,c_name,c_number)
        elif es_name=='S':
            send_p1(bname,phone,searchfor,area,c_name,c_number)
        elif es_name=='B':
            time.sleep(5*60)
            send_p1(bname,phone,searchfor,area,c_name,c_number)
        elif es_name=='B':
            send_p1(bname,phone,searchfor,area,c_name,c_number)
        elif es_name=='B':
            send_p1(bname,phone,searchfor,area,c_name,c_number)
        elif es_name=='V':
            time.sleep(5*60)
            send_p1(bname,phone,searchfor,area,c_name,c_number)
        elif es_name=='V':
            send_p1(bname,phone,searchfor,area,c_name,c_number)

    

@task
def send_sms_to_consumer(slist,c_number):
    print '============in sms function---------'
    description=''
    consumer_number = c_number
    for i in range(len(slist)):
        a = slist[i]
        sid = a.get('supplier_id')
        bname = a.get('bname')
        phone = a.get('phone')
        address = a.get('address')   
        searchfor = a.get('searchfor')
        area = a.get('area')
        c_name = a.get('c_name')
        c_number = a.get('c_number')
        description=description+str(i+1)+". "+bname+'\n'+address+" "+'\n'+"ph: "+phone+'\n\n'
        

    authkey = "118994AIG5vJOpg157989f23"
    mobiles = consumer_number
    message = "Hi "+c_name+","+'\n'+"Find info requested by you"+'\n\n'+description+'\n'+"Regards,"+'\n'+"City Hoopla Team"    
    sender = "DGSPCE"
    route = "4"
    country = "91"
    values = {
              'authkey' : authkey,
              'mobiles' : mobiles,
              'message' : message,
              'sender' : sender,
              'route' : route,
              'country' : country
              }

    url = "http://api.msg91.com/api/sendhttp.php"
    postdata = urllib.urlencode(values)
    req = urllib2.Request(url, postdata)
    response = urllib2.urlopen(req)
    output = response.read()
    print output

            
def send_p1(bname,phone,searchfor,area,c_name,c_number):
    print '---------------phone-------------------------'    
    description = "Following Caller enquired about "+searchfor+'\n'+"Name : "+c_name+" "+'\n'+"Phone Number : "+c_number+'\n'+"Regards,"+'\n'+"City Hoopla Team"
    authkey = "118994AIG5vJOpg157989f23"
    mobiles = phone
    message = description
    sender = "DGSPCE"
    route = "4"
    country = "91"
    values = {
              'authkey' : authkey,
              'mobiles' : mobiles,
              'message' : message,
              'sender' : sender,
              'route' : route,
              'country' : country
              }

    url = "http://api.msg91.com/api/sendhttp.php"
    postdata = urllib.urlencode(values)
    req = urllib2.Request(url, postdata)
    response = urllib2.urlopen(req)
    output = response.read()
    print output
    

@task
def send_email_to_consumer(slist,c_email):
    print '============in email function---------'
    consumer_email = c_email
    i=0
    description=''
    for i in range(len(slist)):
        print '--------i in email-----'
        a = slist[i]
        sid = a.get('supplier_id')
        bname = a.get('bname')
        phone = a.get('phone')
        address = a.get('address')   
        searchfor = a.get('searchfor')
        area = a.get('area')
        c_email = a.get('c_email')
        c_name = a.get('c_name')
        c_number = a.get('c_number')
        description=description+str(i+1)+"."+bname+'\n'+address+" "+'\n'+"ph: "+phone+'\n\n'

    
    gmail_user =  "cityhoopla2016"
    gmail_pwd =  "cityhoopla@2016"
    FROM = 'CityHoopla Admin: <cityhoopla2016@gmail.com>'
    TO = [consumer_email]
    try:
        TEXT = "Hi "+c_name+","+'\n'+"Find info requested by you"+'\n\n'+description+'\n'+"Regards,"+'\n'+"City Hoopla Team"
        SUBJECT = "City Hoopla Enquiry "
        server = smtplib.SMTP_SSL()
        server = smtplib.SMTP("smtp.gmail.com", 587) 
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException,e:
        print e
    



