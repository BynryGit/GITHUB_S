from django.shortcuts import render
# Create your views here.
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import logout
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_control
from django.contrib import auth
from erozgarapp.models import *
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.template import RequestContext
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
# importing mysqldb and system packages
import MySQLdb, sys
from django.db.models import Q
from django.db.models import F
from django.db import transaction
import pdb
import csv
import json
# importing exceptions
from smtplib import SMTPException
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from erozgarapp import models
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.cache import cache_control
# Create your views here.
import smtplib
import re
import string
import random
import urllib
from datetime import date, timedelta
# HTTP Response
from django.http import HttpResponse
from django.http import HttpResponseRedirect

import os
from subprocess import check_output

#pip install django-crontab

# ('*/5 * * * *', 'myapp.cron.my_scheduled_job')

#python manage.py crontab add

#python manage.py crontab show

#python manage.py crontab remove

#Add this in settings - CRONJOBS = [
#    ('0 0 * * *', 'digispaceapp.cron_sms_digispace .my_scheduled_job'),
#]

#INSTALLED_APPS = (
#    'django_crontab',
#    'django.contrib.contenttypes',
#    'django.contrib.sessions',
#)




#def screen_present(name):
#    #name = 'screen_for_celery'
#    var = check_output(["screen -ls; true"],shell=True)
#    if "."+name+"\t(" in var:
#        print name+" is running"
#    else:
#        print name+" is not running"
#        #os.system("screen -S screen_for_celery")
#        run_commands_for_screen()
#        os.system("python /home/ec2-user/DigiSpace/manage.py celeryd")
#        
#screen_present("new_screen_002")

#def run_commands_for_screen():
#    os.system("screen -S screen_for_celery")
#    os.system("ls")
    

def screen_present():
    name='new-screen'
    var = check_output(["screen -ls; true"],shell=True)
    if "."+name+"\t(" in var:
        print name+" is running"
    else:
        run_commands_for_screen()                
        print name+" is not running"      
        
def run_commands_for_screen():
    os.system("screen -DRS admin python /home/ec2-user/DigiSpace/manage.py celeryd")
    
    
    
    
    
    
          
