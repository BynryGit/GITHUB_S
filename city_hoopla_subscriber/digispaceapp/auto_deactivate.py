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
import datetime
from datetime import datetime
from datetime import date, timedelta
# HTTP Response
from django.http import HttpResponse
from django.http import HttpResponseRedirect

# Create your views here.
#from datetime import date, timedelta
# HTTP Response

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

def auto_deactivate_citystar():
    print '---------activation date--------',datetime.now().strftime("%d/%m/%Y")
    try:

        past_date = date.today() + timedelta(1)
        past_date = past_date.strftime("%Y-%m-%d 00:00:00")

        tdate = datetime.now()
        tdate = tdate.strftime("%Y-%m-%d 00:00:00")

        td = [tdate,past_date]


        #eact_date = datetime.now().strftime("%d/%m/%Y")
        #star_obj = CityStarDetails.objects.filter(end_date=deact_date)
        star_obj = CityStarDetails.objects.filter(end_date__range=td)
        for cs in star_obj:
            cs.status = 'deactivated'
            cs.end_date=datetime.now()
            cs.save()

    except:
        pass
        

