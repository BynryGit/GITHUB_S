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
    temp = 1
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
        
        #if es_name=='P':
        #    send_p1(bname,phone,searchfor,area,c_name,c_number)
        #if es_name=='D':
        #    time.sleep(10*60)
        #    send_p1(bname,phone,searchfor,area,c_name,c_number)
        #elif es_name=='G':
        #    time.sleep(10*60)
        #    send_p1(bname,phone,searchfor,area,c_name,c_number)
        #elif es_name=='S1':
        #    time.sleep(5*60)
        #    send_p1(bname,phone,searchfor,area,c_name,c_number)
        #elif es_name=='S2':
        #    send_p1(bname,phone,searchfor,area,c_name,c_number)
        #
        #elif es_name=='B1':
        #    time.sleep(5*60)
        #    send_p1(bname,phone,searchfor,area,c_name,c_number)
        #elif es_name=='B2':
        #    send_p1(bname,phone,searchfor,area,c_name,c_number)
        #elif es_name=='B3':
        #    send_p1(bname,phone,searchfor,area,c_name,c_number)
        #elif es_name=='V1':
        #    time.sleep(5*60)
        #    send_p1(bname,phone,searchfor,area,c_name,c_number)
        #elif es_name=='V2':
        #    send_p1(bname,phone,searchfor,area,c_name,c_number)

    
        #temp=1
        
        if es_name=='P':
            temp = 1
            send_p1(bname,phone,searchfor,area,c_name,c_number)
        if es_name=='D':
            if temp == 1:
                time.sleep(10*60)
                temp=2
                send_p1(bname,phone,searchfor,area,c_name,c_number)
            else :
                time.sleep(10*60)
                temp = 2 
                send_p1(bname,phone,searchfor,area,c_name,c_number)
        elif es_name=='G':
            if temp == 1:
                time.sleep(20*60)
                temp = 3
                send_p1(bname,phone,searchfor,area,c_name,c_number)
            elif temp == 2:
                time.sleep(10*60)
                temp = 3
                send_p1(bname,phone,searchfor,area,c_name,c_number)
        elif es_name=='S1':
            if temp == 1:
                time.sleep(25*60)
                temp = 4
                send_p1(bname,phone,searchfor,area,c_name,c_number)
            elif temp == 2:
                time.sleep(15*60)
                temp = 4
                send_p1(bname,phone,searchfor,area,c_name,c_number)
            elif temp == 3:
                time.sleep(5*60)
                temp = 4
                send_p1(bname,phone,searchfor,area,c_name,c_number)
        elif es_name=='S2':
            send_p1(bname,phone,searchfor,area,c_name,c_number)
        elif es_name=='B1':
            if temp == 1:
                time.sleep(30*60)
                temp = 5
                send_p1(bname,phone,searchfor,area,c_name,c_number)
            elif temp == 2:
                time.sleep(20*60)
                temp = 5
                send_p1(bname,phone,searchfor,area,c_name,c_number)
            elif temp == 3:
                time.sleep(10*60)
                temp = 5
                send_p1(bname,phone,searchfor,area,c_name,c_number)
            elif temp == 4:
                time.sleep(5*60)
                temp = 5
                send_p1(bname,phone,searchfor,area,c_name,c_number)
        elif es_name=='B2':
            send_p1(bname,phone,searchfor,area,c_name,c_number)                
        elif es_name=='B3':
            send_p1(bname,phone,searchfor,area,c_name,c_number)
        elif es_name=='V1':
            if temp == 1:
                time.sleep(35*60)
                temp = 6
                send_p1(bname,phone,searchfor,area,c_name,c_number)
            if temp == 2:
                time.sleep(25*60)
                temp = 6
                send_p1(bname,phone,searchfor,area,c_name,c_number)
            if temp == 3:
                time.sleep(15*60)
                temp = 6
                send_p1(bname,phone,searchfor,area,c_name,c_number)
            if temp == 4:
                time.sleep(10*60)
                temp = 6
                send_p1(bname,phone,searchfor,area,c_name,c_number)
            if temp == 5:
                time.sleep(5*60)
                temp = 6
                send_p1(bname,phone,searchfor,area,c_name,c_number)   
            
        elif es_name=='V2':
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
        city = a.get('city')
        c_name = a.get('c_name')
        c_number = a.get('c_number')
        description=description+str(i+1)+". "+bname+'\n'+address+" "+'\n'+"ph: "+phone+'\n\n'
        

    authkey = "118994AIG5vJOpg157989f23"
    mobiles = consumer_number
    message = "Dear "+c_name+","+'\n'+"Please find the businesses for your search "+searchfor+" in "+area+", "+city+":"+'\n\n'+description+'\n\n'+"Best Wishes,"+'\n'+"Team CityHoopla"    
    sender = "CTHPLA"
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
    description = "You have a new sales lead."+'\n\n'+"Looking for : "+searchfor+'\n'+"Caller : "+c_name+" "+'\n'+"Contact Number : "+c_number+'\n\n'+"Best Wishes,"+'\n'+"Team CityHoopla"
    authkey = "118994AIG5vJOpg157989f23"
    mobiles = phone
    message = description
    sender = "CTHPLA"
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
        city = a.get('city')
        c_email = a.get('c_email')
        c_name = a.get('c_name')
        c_number = a.get('c_number')
        description=description+str(i+1)+"."+bname+'\n'+address+" "+'\n'+"ph: "+phone+'\n\n'

    
    gmail_user =  "donotreply@city-hoopla.com"
    gmail_pwd =  "Hoopla123#"
    FROM = 'Team CityHoopla <donotreply@city-hoopla.com>'
    TO = [consumer_email]
    try:
        TEXT = "Dear "+c_name+","+'\n'+"Please find the businesses for your search "+searchfor+" in "+area+", "+city+":"+'\n\n'+description+'\n'+"Best Wishes,"+'\n\n'+"Team CityHoopla"
        SUBJECT = "Your Recent Enquiry "
        #server = smtplib.SMTP_SSL()
        #server = smtplib.SMTP("smtp.gmail.com", 587) 
        server = smtplib.SMTP("smtpout.asia.secureserver.net", 80)
        server.ehlo()
        #server.starttls()
        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException,e:
        print e
    



