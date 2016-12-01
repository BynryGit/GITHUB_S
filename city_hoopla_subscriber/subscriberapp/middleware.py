import datetime
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib import auth
#from subscriberapp import views.py

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
from digispaceapp.models import *
import urllib
import smtplib
from smtplib import SMTPException
from django.shortcuts import *
from digispaceapp.models import UserProfile
import dateutil.relativedelta
# import Admin
from captcha_form import CaptchaForm

# importing mysqldb and system packages
import MySQLdb, sys
from django.db.models import Q
from django.db.models import F
from django.db import transaction
import pdb
import csv
import json
# importing exceptions
from django.db import IntegrityError
import operator
from django.db.models import Q
from datetime import date, timedelta
from django.views.decorators.cache import cache_control
# HTTP Response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
import dateutil.relativedelta
from django.db.models import Count
from datetime import date

import string
import random
from dateutil import parser as date_parser
class AutoLogout:
  def process_request(self, request):
    if not request.user.is_authenticated():
      #Can't log out if not logged in
      print '......request.user.is_authenticated..CHECKING....',request.user.is_authenticated()

    try:
      last_touch = request.GET.get('last_touch')
      last_touch = str(last_touch)
      #print 'AAAAAAAA',last_touch
      #request.session['last_touch'] = datetime.now()
      #last_touch = last_touch.strftime("%d/%m/%Y")
      #print date_parser.parse(last_touch)
      #print 'SSSSCCCXXXXXXX...............XXXXXXXXXXXSSSSSSSSSSSSSS',last_touch
      #print '...........NEWWWWWW.........',request.session['last_touch']
      if datetime.now() - request.session['last_touch'] > timedelta( 0, settings.AUTO_LOGOUT_DELAY * 60, 0):
        auth.logout(request)
        print '##........after auth logout..........##'
        del request.session['last_touch']
        form = CaptchaForm()
        return render_to_response('Subscriber/user_login.html', dict(
            form=form, message_logout='Your session has been expired'
        ), context_instance=RequestContext(request))
    except KeyError:
      pass

    request.session['last_touch'] = datetime.now()

