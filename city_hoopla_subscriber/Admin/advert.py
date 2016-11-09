from django.shortcuts import render
import os
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
from captcha_form import CaptchaForm
from django.shortcuts import *

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
import string
import random
# HTTP Response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
import urllib2
import os
from django.db.models import Count

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import textwrap
import StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile

#SERVER_URL = "http://52.66.169.65"   
SERVER_URL = "http://192.168.0.14:8088" 

#SERVER_URL="http://192.168.0.180:9999"
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def advert_management(request):
    try:
        subscriber_info=[]
        subscriber_id=request.GET.get('subscriber_id')
        subscriber_obj = Supplier.objects.get(supplier_id=request.GET.get('subscriber_id'))
        business_name = subscriber_obj.business_name
        user_id=str(subscriber_obj.supplier_id)
        if subscriber_obj.logo:
           logo = SERVER_URL + subscriber_obj.logo.url
        else:
            logo = SERVER_URL + '/static/assets/layouts/layout2/img/City_Hoopla_Logo.png'

        if subscriber_obj.supplier_email:
           supplier_email = subscriber_obj.supplier_email
        else:
            supplier_email = '--'   
            
        if subscriber_obj.secondary_phone_no:
           secondary_phone_no = subscriber_obj.secondary_phone_no
        else:
            secondary_phone_no = '--'  


        if subscriber_obj.phone_no:
           phone_no = subscriber_obj.phone_no
        else:
            phone_no = '--' 

        # contact_person=subscriber_obj.contact_person
        # title=subscriber_obj.title

        # contact_person_name = str(title + " " +contact_person)


        temp_data ={
        'business_name':subscriber_obj.business_name,
        'subscriber_id':subscriber_obj.supplier_id,
        'subscriber_city':subscriber_obj.city_place_id.city_id.city_name,
        'business_details' :subscriber_obj.business_details,
        'phone_no':phone_no,
        'secondary_phone_no':secondary_phone_no,
        'supplier_email':supplier_email,
        'contact_person':subscriber_obj.contact_person,
        'contact_no':subscriber_obj.contact_no,
        'contact_email':subscriber_obj.contact_email,
        'address1':subscriber_obj.address1,
        'logo':logo,
        
        }
        subscriber_info.append(temp_data)

        advert_list = []
        category_list = []
        pre_date = datetime.now().strftime("%d/%m/%Y")
        pre_date = datetime.strptime(pre_date, "%d/%m/%Y")


        supplier_id = request.GET.get('subscriber_id')
        print "supplier_id=====",supplier_id
        start_date_var = request.GET.get('start_date_var')
        end_date_var = request.GET.get('end_date_var')
        category_var = request.GET.get('category_var')
        status_var = request.GET.get('status_var')
        print "status_var",status_var
        sort_by = request.GET.get('sort_by')
        print "sort_by",sort_by

        if start_date_var:
                start_date = datetime.strptime(start_date_var, "%d/%m/%Y")- timedelta(days=1)
        if end_date_var:
            end_date = datetime.strptime(end_date_var, "%d/%m/%Y")+ timedelta(days=1)
        if start_date_var and end_date_var and status_var and category_var:
            Advert_list1 = Advert.objects.filter(
                category_id=request.GET.get('category_var'),
                supplier_id=supplier_id,
                creation_date__range=[start_date, end_date],
                status=request.GET.get('status_var')
            )
        elif start_date_var and end_date_var and category_var:
            Advert_list1 = Advert.objects.filter(
                category_id=request.GET.get('category_var'),
                supplier_id=supplier_id,
                creation_date__range=[start_date, end_date]
            )
        elif start_date_var and end_date_var and status_var:
            Advert_list1 = Advert.objects.filter(
                supplier_id=supplier_id,
                creation_date__range=[start_date, end_date],
                status=request.GET.get('status_var')
            )
        elif start_date_var and end_date_var:
            Advert_list1 = Advert.objects.filter(
                supplier_id=supplier_id,
                creation_date__range=[start_date, end_date]
            )
        elif category_var and status_var:
            Advert_list1 = Advert.objects.filter(
                supplier_id=supplier_id,
                category_id=request.GET.get('category_var')
            )
        elif status_var:
            print "In status "
            Advert_list1 = Advert.objects.filter(
                status=request.GET.get('status_var'),supplier_id=supplier_id
            )
            print 'Advert_list1',Advert_list1
        elif sort_by == "oldest_first":
            print "In sort"
            Advert_list1 = Advert.objects.filter(supplier_id=supplier_id).order_by('-creation_date').reverse()
        else:
            print "In else"
            Advert_list1 = Advert.objects.filter(supplier_id=supplier_id).order_by('-creation_date')

        
        adv_count=Advert.objects.filter(supplier_id=user_id).count()

        category_objs = Category.objects.all()
        for category_obj in category_objs:
            category_id = category_obj.category_id
            category_name = category_obj.category_name
            cat_data = {'category_name': category_name, 'category_id': category_id}
            category_list.append(cat_data)

        business_obj = Business.objects.filter(supplier_id=user_id)
        for business in business_obj:
            try:
                advert_sub_obj = AdvertSubscriptionMap.objects.get(business_id=business.business_id)
            except:
                print business
                start_date = business.start_date
                start_date = datetime.strptime(start_date, "%d/%m/%Y")
                end_date = business.end_date
                end_date = datetime.strptime(end_date, "%d/%m/%Y")

                date_gap = (end_date - pre_date).days

                if date_gap > 0:
                    date_gap = date_gap
                else:
                    date_gap = 0

                if date_gap <= 10 and date_gap >= 3:
                    advert_status = 1
                    subscription_days = "( " + str(date_gap) + " days Remaining )"
                    subscription_text = "Starts on " + start_date.strftime("%d %b %y")
                    subscriber_color = "orange"
                    advert_color = "orange"
                elif date_gap == 0:
                    advert_status = 0
                    subscription_days = ""
                    subscription_text = "Expired on " + start_date.strftime("%d %b %y")
                    subscriber_color = "red"
                    advert_color = "red"
                elif date_gap == 2:
                    print "In date gap 2"
                    advert_status = 0
                    subscription_days = ""
                    subscription_text = "Started on " + start_date.strftime("%d %b %y")
                    subscriber_color = "orange"
                    advert_color = "orange"
                else:
                    advert_status = 2
                    subscription_days = "( " + str(date_gap) + " days Remaining )"
                    subscription_text = "Starts on " + start_date.strftime("%d %b %y")
                    subscriber_color = "#333"
                    advert_color = "green"

                premium_serv_list = premium_list(business.business_id)

                advert_data = {
                    'advert_id': '',
                    'business_id': business.business_id,
                    'advert_status': advert_status,
                    'advert_name': 'No Advert is added for this subscription.',
                    'advert_area': '',
                    'advert_city': '',
                    'category_name': '',
                    'display_image': SERVER_URL + '/static/assets/layouts/layout2/img/City_Hoopla_Logo.jpg',
                    'advert_views': '',
                    'advert_likes': '',
                    'advert_shares': '',
                    'subscription_days': subscription_days,
                    'subscription_text': subscription_text,
                    'subscriber_color': subscriber_color,
                    'premium_service_list': premium_serv_list,
                    'advert_bookings': '',
                    'advert_color': advert_color,
                }
                advert_list.append(advert_data)

        for advert_obj in Advert_list1:
            premium_service_list = []
            advert_id = advert_obj.advert_id


            advert_views = AdvertView.objects.filter(advert_id=advert_id).count()
            advert_likes = AdvertLike.objects.filter(advert_id=advert_id).count()
            advert_shares = AdvertShares.objects.filter(advert_id=advert_id).count()
            advert_bookings = CouponCode.objects.filter(advert_id=advert_id).count()

            advert_name = advert_obj.advert_name
            advert_area = advert_obj.area
            advert_city = advert_obj.city_place_id.city_id.city_name
            category_name = advert_obj.category_id.category_name

            if advert_obj.display_image:
                display_image = SERVER_URL + advert_obj.display_image.url
            else:
                display_image = SERVER_URL + '/static/assets/layouts/layout2/img/City_Hoopla_Logo.jpg'

            advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)

            start_date = advert_sub_obj.business_id.start_date
            start_date = datetime.strptime(start_date, "%d/%m/%Y")
            end_date = advert_sub_obj.business_id.end_date
            end_date = datetime.strptime(end_date, "%d/%m/%Y")

            date_gap = (end_date - pre_date).days

            if date_gap > 0:
                date_gap = date_gap
            else:
                date_gap = 0

            if date_gap <= 10 and date_gap >= 3:
                advert_status = 1
                subscription_days = "( "+ str(date_gap) +" days Remaining )"
                subscription_text = "Starts on " + start_date.strftime("%d %b %y")
                subscriber_color = "orange"
                advert_color = "orange"
            elif date_gap == 0:
                advert_status = 0
                subscription_days = ""
                subscription_text = "Expired on " + start_date.strftime("%d %b %y")
                subscriber_color = "red"
                advert_color = "red"
            elif date_gap == 2:
                    print "In date gap 2"
                    advert_status = 0
                    subscription_days = "( "+ str(date_gap) +" days Remaining )"
                    subscription_text = "Started on " + start_date.strftime("%d %b %y")
                    subscriber_color = "orange"
                    advert_color = "orange"
            else:
                advert_status = 2
                subscription_days = "( " + str(date_gap) + " days Remaining )"
                subscription_text = "Starts on " + start_date.strftime("%d %b %y")
                subscriber_color = "#333"
                advert_color = "green"

            business_id = advert_sub_obj.business_id
            premium_service_list = premium_list(business_id)
            advert_data = {
                'advert_id': advert_id,
                'advert_status': advert_status,
                'status':advert_obj.status,
                'advert_name': advert_name,
                'advert_area': advert_area,
                'advert_city': advert_city,
                'category_name': category_name,
                'display_image' : display_image,
                'advert_views': advert_views,
                'advert_likes': advert_likes,
                'advert_shares': advert_shares,
                'subscription_days': subscription_days,
                'subscription_text': subscription_text,
                'subscriber_color': subscriber_color,
                'premium_service_list': premium_service_list,
                'advert_bookings': advert_bookings,
                'advert_color': advert_color,
                'date_gap': date_gap
            }
            advert_list.append(advert_data)


        data = {'username': request.session['login_user'],'sort_by':sort_by,'status_var':status_var,'subscriber_id':subscriber_id,'category_list': category_list,'adv_count':adv_count, 'advert_list': advert_list,'business_name':business_name,'user_id':user_id,'subscriber_info':subscriber_info}
    except Exception, e:
        raise e
        data = {'success':'false' }
    return render(request, 'Admin/advert_management.html', data)

@csrf_exempt
def advert_stat(request):
    try:
        data = {}
        final_list = []
        final_list1 = []
        final_list2 = []
        print "----------------request--------------", request.GET
        try:


            #########################advert_views_total#############################
            advert_views_total = 0
            thumbs_count_total = 0
            shares_count_total = 0

            jan1 = feb1 = mar1 = apr1 = may1 = jun1 = jul1 = aug1 = sep1 = oct1 = nov1 = dec1 = 0
            jan2 = feb2 = mar2 = apr2 = may2 = jun2 = jul2 = aug2 = sep2 = oct2 = nov2 = dec2 = 0
            jan3 = feb3 = mar3 = apr3 = may3 = jun3 = jul3 = aug3 = sep3 = oct3 = nov3 = dec3 = 0

            FY_MONTH_LIST = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
            today = date.today()
            print '.......today.........', today
            start_date = date(today.year, 01, 01)
            print '...........start_date..........', start_date
            end_date = date(today.year, 12, 31)

            #for advert_obj in Advert_list1:
            advert_obj = Advert.objects.get(advert_id = request.GET.get('advert_id'))
            advert_id = advert_obj.advert_id
            advert_nm=advert_obj.advert_name
            print 'advert_nm',advert_nm
            supplier_id =advert_obj.supplier_id
            business_name = advert_obj.supplier_id.business_name
            advert_views = AdvertView.objects.filter(advert_id=advert_id,
                                                 creation_date__range=[start_date, end_date]).count()
            thumbs_count = AdvertLike.objects.filter(advert_id=advert_id,
                                                     creation_date__range=[start_date, end_date]).count()
            shares_count = AdvertShares.objects.filter(advert_id=advert_id,
                                                       creation_date__range=[start_date, end_date]).count()

            advert_views_total = advert_views_total + advert_views
            thumbs_count_total = thumbs_count_total + thumbs_count
            shares_count_total = shares_count_total + shares_count

            #######.................Total views Graph........for a year.......########

            FY_MONTH_LIST = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
            today = date.today()
            start_date = date(today.year, 01, 01)
            end_date = date(today.year, 12, 31)
            monthly_count = []
            # jan,feb,mar,apr,may,jun,jul,aug,sep,octo,nov,dec

            coupon_code_list = AdvertView.objects.filter(advert_id=advert_id,
                                                     creation_date__range=[start_date, end_date]).extra(
                select={'month': "EXTRACT(month FROM creation_date)"}).values('month').annotate(
                count=Count('advert_id'))
            print "...........coupon_code_list...11....", coupon_code_list
            list = {}

            for sub_obj in coupon_code_list:
                # advert_id = sub_obj.advert_id
                # print 'SS advert SS',advert_id
                print "sub_obj.get('count')", sub_obj.get('count')
                if sub_obj.get('month'):
                    list[sub_obj.get('month')] = sub_obj.get('count') or '0.00'
                    print list

            for i in FY_MONTH_LIST:
                try:
                    monthly_count.append(list[i])
                except:
                    monthly_count.append(0)

            jan1 = jan1 + monthly_count[0]
            print jan1
            feb1 = feb1 + monthly_count[1]
            print feb1
            mar1 = mar1 + monthly_count[2]
            print mar1
            apr1 = apr1 + monthly_count[3]
            may1 = may1 + monthly_count[4]
            jun1 = jun1 + monthly_count[5]
            jul1 = jul1 + monthly_count[6]
            aug1 = aug1 + monthly_count[7]
            print aug1
            sep1 = sep1 + monthly_count[8]
            oct1 = oct1 + monthly_count[9]
            nov1 = nov1 + monthly_count[10]
            dec1 = dec1 + monthly_count[11]

            #######.................Total Like Graph........for a year.......########

            FY_MONTH_LIST = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
            today = date.today()
            print '.......today......AdvertLike...', today
            start_date = date(today.year, 01, 01)
            print '...........start_date....AdvertLike......', start_date
            end_date = date(today.year, 12, 31)
            monthly_count = []
            # jan,feb,mar,apr,may,jun,jul,aug,sep,octo,nov,dec
            coupon_code_list = AdvertLike.objects.filter(advert_id=advert_id,
                                                         creation_date__range=[start_date, end_date]).extra(
                select={'month': "EXTRACT(month FROM creation_date)"}).values('month').annotate(
                count=Count('advert_id'))
            print "...........coupon_code_list....AdvertLike...", coupon_code_list
            list = {}

            for sub_obj in coupon_code_list:

                print "sub_obj.get('count')", sub_obj.get('count')
                if sub_obj.get('month'):
                    list[sub_obj.get('month')] = sub_obj.get('count') or '0.00'
                    print list

            for i in FY_MONTH_LIST:
                try:
                    monthly_count.append(list[i])
                except:
                    monthly_count.append(0)

            jan2 = jan2 + monthly_count[0]
            print jan2
            feb2 = feb2 + monthly_count[1]
            print feb2
            mar2 = mar2 + monthly_count[2]
            print mar2
            apr2 = apr2 + monthly_count[3]
            may2 = may2 + monthly_count[4]
            jun2 = jun2 + monthly_count[5]
            jul2 = jul2 + monthly_count[6]
            print jul2
            aug2 = aug2 + monthly_count[7]
            print aug2
            sep2 = sep2 + monthly_count[8]
            oct2 = oct2 + monthly_count[9]
            nov2 = nov2 + monthly_count[10]
            dec2 = dec2 + monthly_count[11]

            #######.................Total shares Graph........for a year.......########

            FY_MONTH_LIST = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
            today = date.today()
            print '.......today.........', today
            start_date = date(today.year, 01, 01)
            print '...........start_date..........', start_date
            end_date = date(today.year, 12, 31)
            monthly_count = []
            # jan,feb,mar,apr,may,jun,jul,aug,sep,octo,nov,dec
            coupon_code_list = AdvertShares.objects.filter(advert_id=advert_id,
                                                           creation_date__range=[start_date, end_date]).extra(
                select={'month': "EXTRACT(month FROM creation_date)"}).values('month').annotate(
                count=Count('advert_id'))
            print "...........coupon_code_list.......", coupon_code_list
            list = {}

            for sub_obj in coupon_code_list:
                print "sub_obj.get('count')", sub_obj.get('count')
                if sub_obj.get('month'):
                    list[sub_obj.get('month')] = sub_obj.get('count') or '0.00'
                    print list

            for i in FY_MONTH_LIST:
                try:
                    monthly_count.append(list[i])
                except:
                    monthly_count.append(0)

            jan3 = jan3 + monthly_count[0]
            print jan3
            feb3 = feb3 + monthly_count[1]
            print feb3
            mar3 = mar3 + monthly_count[2]
            print mar3
            apr3 = apr3 + monthly_count[3]
            may3 = may3 + monthly_count[4]
            jun3 = jun3 + monthly_count[5]
            jul3 = jul3 + monthly_count[6]
            aug3 = aug3 + monthly_count[7]
            print aug3
            sep3 = sep3 + monthly_count[8]
            oct3 = oct3 + monthly_count[9]
            nov3 = nov3 + monthly_count[10]
            dec3 = dec3 + monthly_count[11]

            data = {'success': 'true', 'advert_nm': advert_nm, 'supplier_id': supplier_id, 
                    'advert_views_total': advert_views_total, 'thumbs_count_total': thumbs_count_total,
                    'shares_count_total': shares_count_total, 'jan1': jan1, 'feb1': feb1, 'mar1': mar1, 'apr1': apr1,
                    'may1': may1, 'jun1': jun1, 'jul1': jul1, 'aug1': aug1, 'sep1': sep1, 'oct1': oct1, 'nov1': nov1,
                    'dec1': dec1,'business_name':business_name,
                    'jan2': jan2, 'feb2': feb2, 'mar2': mar2, 'apr2': apr2, 'may2': may2, 'jun2': jun2, 'jul2': jul2,
                    'aug2': aug2, 'sep2': sep2, 'oct2': oct2, 'nov2': nov2, 'dec2': dec2,
                    'jan3': jan3, 'feb3': feb3, 'mar3': mar3, 'apr3': apr3, 'may3': may3, 'jun3': jun3, 'jul3': jul3,
                    'aug3': aug3, 'sep3': sep3, 'oct3': oct3, 'nov3': nov3, 'dec3': dec3}

        except IntegrityError as e:
            print e
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time',
                    'username': request.session['login_user']}
    except MySQLdb.OperationalError, e:
        print e
    except Exception, e:
        print 'Exception ', e
    print './........777..........', data
    return render(request, 'Admin/advert-stat.html', data)


def premium_list(business_id):
    premium_ser_list = PremiumService.objects.filter(business_id=business_id)
    premium_service_list = []
    pre_date = datetime.now().strftime("%d/%m/%Y")
    pre_date = datetime.strptime(pre_date, "%d/%m/%Y")
    for premium_obj in premium_ser_list:
        status_advert = ''
        date_gap = ''
        premium_service_name = premium_obj.premium_service_name
        start_date = premium_obj.start_date
        start_date = datetime.strptime(start_date, "%d/%m/%Y")
        end_date = premium_obj.end_date
        end_date = datetime.strptime(end_date, "%d/%m/%Y")
        date_gap = (end_date - pre_date).days

        if date_gap > 0:
            date_gap = date_gap
        else:
            date_gap = 0

        if date_gap <= 10 and date_gap >= 3:
            status_advert = 1
            premium_days = "( " + str(date_gap) + " days Remaining )"
            premium_text = "Starts on " + start_date.strftime("%d %b %y")
            premium_color = "orange"
        elif date_gap == 0:
            status_advert = 0
            premium_days = ""
            premium_text = "Expired on " + start_date.strftime("%d %b %y")
            premium_color = "red"
        elif date_gap == 2:
            status_advert = 0
            premium_days = "( " + str(date_gap) + " days Remaining )"
            premium_text = "Started on " + start_date.strftime("%d %b %y")
            premium_color = "orange"
        else:
            status_advert = 2
            premium_days = "( " + str(date_gap) + " days Remaining )"
            premium_text = "Starts on " + start_date.strftime("%d %b %y")
            premium_color = "#333"

        premium_data = {
            'premium_service_name': premium_service_name,
            'premium_days': premium_days,
            'premium_text': premium_text,
            'premium_color': premium_color
        }
        premium_service_list.append(premium_data)
    return premium_service_list


# TO GET THE CATEGOTRY
def get_phone_category(request):
    ##    pdb.set_trace()
    phone_cat_list = []
    try:
        ph_category = PhoneCategory.objects.filter(phone_category_status='1')
        for ph_cat in ph_category:
            phone_cat_list.append(
                {'ph_category_id': ph_cat.phone_category_id, 'ph_category_name': ph_cat.phone_category_name})

    except Exception, e:
        print 'Exception ', e
    return phone_cat_list

    # TO GET THE Country
def get_country(request):
##    pdb.set_trace()
    country_list = []
    try:
        country = Country.objects.filter(country_status='1')
        for sta in country:
            country_list.append(
                {'country_id': sta.country_id, 'country_name': sta.country_name})

    except Exception, e:
        print 'Exception ', e
    return country_list


# TO GET THE CITY
def get_city_place(request):
    # pdb.set_trace()
    state_id = request.GET.get('state_id')
    city_list = []
    try:
        city_objs = City_Place.objects.filter(state_id=state_id, city_status='1')

        print "======city_objs", city_objs
        for city in city_objs:
            options_data = '<option value=' + str(
                city.city_place_id) + '>' + city.city_id.city_name + '</option>'
            city_list.append(options_data)
            print city_list
        data = {'city_list': city_list}

    except Exception, ke:
        print ke
        data = {'city_list': 'none', 'message': 'No city available'}
    return HttpResponse(json.dumps(data), content_type='application/json')


# TO GET THE PINCODE
def get_pincode_place(request):
    # pdb.set_trace()

    pincode_list = []
    try:
        city_id = request.GET.get('city_id')
        city_id1 = City_Place.objects.get(city_place_id=str(city_id))
        city_id2 = City.objects.get(city_id=str(city_id1.city_id.city_id))
        pincode_list1 = Pincode.objects.filter(city_id=city_id2.city_id).order_by('pincode')
        pincode_objs = pincode_list1.values('pincode').distinct()
        for pincode in pincode_objs:
            options_data = '<option>' + pincode['pincode'] + '</option>'
            pincode_list.append(options_data)
            print pincode_list
        data = {'pincode_list': pincode_list}

    except Exception, ke:
        print ke
        data = {'city_list': 'none', 'message': 'No city available'}
    return HttpResponse(json.dumps(data), content_type='application/json')



# TO GET THE PINCODE
def get_pincode_places(request):
    pincode_list = []
    try:
        city_id = request.GET.get('city_id')
        city_id1 = City_Place.objects.get(city_place_id=str(city_id))
        city_id2 = City.objects.get(city_id=str(city_id1.city_id.city_id))
        pincode_list1 = Pincode.objects.filter(city_id=city_id2.city_id).order_by('pincode')
        for pincode in pincode_list1:
            options_data = '<option value="'+ str(pincode.pincode_id) +'">' + str(pincode.pincode) + '</option>'
            pincode_list.append(options_data)
        data = {'pincode_list': pincode_list}

    except Exception, ke:
        print ke
        data = {'city_list': 'none', 'message': 'No city available'}
    return HttpResponse(json.dumps(data), content_type='application/json')


# TO GET THE STATE
def get_states(request):
   
   country_id=request.GET.get('country_id')
   print '.................country_id.....................',country_id
   state_list=[]
   try:
      state_objs=State.objects.filter(country_id=country_id,state_status='1').order_by('state_name')
      for state in state_objs:
         options_data = '<option value="' + str(
                   state.state_id) + '">' + state.state_name + '</option>'
         state_list.append(options_data)
         print state_list
      data = {'state_list': state_list}
      print '........data..........',data

   except Exception, ke:
      print ke
      data={'state_list': 'none','message':'No city available'}
   return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def save_advert(request):
    # pdb.set_trace()
    try:
        if request.method == "POST":
            print '===request========', request.POST.get('product_name_list')
            advert_obj = Advert(
                supplier_id=Supplier.objects.get(supplier_id=request.POST.get('supplier_id')),
                category_id=Category.objects.get(category_id=request.POST.get('categ')),
                advert_name=request.POST.get('advert_title'),
                contact_name=request.POST.get('contact_name'),
                contact_no=request.POST.get('phone_no'),
                website=request.POST.get('website'),
                latitude=request.POST.get('lat'),
                longitude=request.POST.get('lng'),
                short_description=request.POST.get('short_discription'),
                product_description=request.POST.get('product_discription'),
                currency=request.POST.get('currency'),
                country_id = Country.objects.get(country_id=request.POST.get('country')) if request.POST.get('country') else None,
                # product_price=request.POST.get('product_price'),
                discount_description=request.POST.get('discount_discription'),
                email_primary=request.POST.get('email_primary'),
                email_secondary=request.POST.get('email_secondary'),
                address_line_1=request.POST.get('address_line1'),
                address_line_2=request.POST.get('address_line2'),
                area=request.POST.get('area'),
                landmark=request.POST.get('landmark'),
                state_id=State.objects.get(state_id=request.POST.get('statec')) if request.POST.get('statec') else None,
                city_place_id=City_Place.objects.get(city_place_id=request.POST.get('city')) if request.POST.get(
                    'city') else None,
                pincode_id=Pincode.objects.get(pincode=request.POST.get('pincode')) if request.POST.get(
                    'pincode') else None,
                property_market_rate=request.POST.get('pro_mark_rate'),
                possesion_status=request.POST.get('possesion_status'),
                date_of_delivery=request.POST.get('date_of_delivery'),
                other_projects=request.POST.get('other_projects'),
                distance_frm_railway_station=request.POST.get('dis_rail_stat'),
                distance_frm_railway_airport=request.POST.get('dis_airport'),
                speciality=request.POST.get('speciality'),
                affilated_to=request.POST.get('affilated'),
                course_duration=request.POST.get('course_duration'),
                happy_hour_offer=request.POST.get('happy_hour_offer'),
                facility=request.POST.get('facility'),
                keywords=request.POST.get('advert_keywords'),
                image_video_space_used=request.POST.get('image_and_video_space'),
                other_amenity=request.POST.get('any_other_amenity'),
                title=request.POST.get('title'),
                created_by=request.session['login_user'],
            );
            advert_obj.save()
            advert_id=advert_obj.advert_id

            if request.POST.get('any_other_details'):
                advert_obj.any_other_details = request.POST.get('any_other_details')
                advert_obj.save()
            if request.POST.get('subscription_id'):
                map_subscription(request.POST.get('subscription_id'), advert_obj)

            subcat_list = request.POST.get('subcat_list')
            print subcat_list
            subcat_lvl = 1
            # String to list
            subcat_list = subcat_list.split(',')
            if subcat_list != '':
                for subcat in subcat_list:
                    if subcat:
                        print 'Subcat: ', subcat, subcat_lvl
                        if subcat_lvl == 1:
                            advert_obj.category_level_1 = CategoryLevel1.objects.get(category_id=subcat)
                            advert_obj.save()
                        if subcat_lvl == 2:
                            advert_obj.category_level_2 = CategoryLevel2.objects.get(category_id=subcat)
                            advert_obj.save()
                        if subcat_lvl == 3:
                            advert_obj.category_level_3 = CategoryLevel3.objects.get(category_id=subcat)
                            advert_obj.save()
                        if subcat_lvl == 4:
                            advert_obj.category_level_4 = CategoryLevel4.objects.get(category_id=subcat)
                            advert_obj.save()
                        if subcat_lvl == 5:
                            advert_obj.category_level_5 = CategoryLevel5.objects.get(category_id=subcat)
                            advert_obj.save()
                        print 'Advert Subcat Mapping saved'
                        subcat_lvl += 1
            if request.POST['check_image'] == "1":
                advert_obj.display_image = request.FILES['display_image']
                advert_obj.save()

                save_advert_image(advert_obj)

            attachment_list = []
            attachment_list = request.POST.get('attachments')
            save_attachments(attachment_list, advert_obj)

            video_list = []
            video_list = request.POST.get('ac_attachment')
            save_video(video_list, advert_obj)

            # phone_category_list = request.POST.get('phone_category_list')
            # phone_category_list = phone_category_list.split(',')
            # phone_number_list = request.POST.get('phone_number_list')
            # phone_number_list = phone_number_list.split(',')
            # zipped = zip(phone_category_list, phone_number_list)
            # save_phone_number(zipped, advert_obj)

            product_name_list = request.POST.get('product_name_list')
            product_name_list = product_name_list.split('_PRODUCT_NAME_IS_SEPARATED')
            product_price_list = request.POST.get('product_price_list')
            product_price_list = product_price_list.split('_PRODUCT_PRICE_IS_SEPARATED')
            zipped_product = zip(product_name_list, product_price_list)
            save_product(zipped_product, advert_obj)

            opening_day_list = request.POST.get('opening_day_list')
            opening_day_list = opening_day_list.split(',')

            start_time_list = request.POST.get('start_time_list')
            start_time_list = start_time_list.split(',')

            end_time_list = request.POST.get('end_time_list')
            end_time_list = end_time_list.split(',')

            zipped_wk = zip(opening_day_list, start_time_list, end_time_list)
            save_working_hours(zipped_wk, advert_obj)

            amenity_list = request.POST.get('amenity_list')
            amenity_list = amenity_list.split(',')
            save_amenity(amenity_list, advert_obj)

            near_attr_list = request.POST.get('near_attraction')
            near_attr_list = near_attr_list.split(',')
            save_near_attr(near_attr_list, advert_obj)

            near_shopnmal = request.POST.get('near_shopnmal')
            near_shopnmal = near_shopnmal.split(',')

            near_shonmald = request.POST.get('near_shonmald')
            near_shonmald = near_shonmald.split(',')

            zipped_shopmal = zip(near_shopnmal, near_shonmald)
            save_shpnmal(zipped_shopmal, advert_obj)

            cat = advert_obj.category_id.category_name
            if cat == 'Real Estate':
                print "SCHOOL", request.POST.get('near_schol')
                near_schol = request.POST.get('near_schol')
                near_schol = near_schol.split(',')

                print "SCHOOL DI SORTING", request.POST.get('near_schold')
                near_schold = request.POST.get('near_schold')
                near_schold = near_schold.split(',')

                print "AFTER SCHOOL"

                zipped_school = zip(near_schol, near_schold)
                save_school(zipped_school, advert_obj)

                near_hosp = request.POST.get('near_hosp')
                near_hosp = near_hosp.split(',')

                near_hospd = request.POST.get('near_hospd')
                near_hospd = near_hospd.split(',')

                zipped_hospital = zip(near_hosp, near_hospd)
                save_hospital(zipped_hospital, advert_obj)
            #advert_add_sms(advert_obj)
            #advert_add_mail(advert_obj)
            data = {'success': 'true','advert_id':advert_id}

    except Exception, e:
        print 'Exception :', e
        data = {'data': 'none'}
    return HttpResponse(json.dumps(data), content_type='application/json')

def save_advert_image(advert_obj):
    os_path = '/home/ec2-user/DigiSpace'
    # os_path = '/home/admin1/Prod_backup/DigiSpace'

    discount_description = advert_obj.discount_description
    advert_tilte = advert_obj.advert_name
    contact_no = advert_obj.contact_no
    address = advert_obj.address_line_1
    if advert_obj.address_line_2:
        address = address + ', ' + advert_obj.address_line_2
    if advert_obj.area:
        address = address + ', ' + advert_obj.area
        landmark = advert_obj.area
    if advert_obj.city_place_id:
        address = address + ', ' + advert_obj.city_place_id.city_id.city_name
        landmark = landmark + ' ' + advert_obj.city_place_id.city_id.city_name
    if advert_obj.state_id:
        address = address + ', ' + advert_obj.state_id.state_name
    if advert_obj.pincode_id:
        address = address + '-' + advert_obj.pincode_id.pincode
    advert_address = address

    # font = ImageFont.truetype("/home/admin1/Downloads/Khula-Regular.ttf", 20)
    # bold_font = ImageFont.truetype("/home/admin1/Downloads/Khula-Bold.ttf", 30)
    # semi_bold_font = ImageFont.truetype("/home/admin1/Downloads/Khula-SemiBold.ttf", 20)
    font = ImageFont.truetype("/home/ec2-user/DigiSpace/static/Khula-Regular.ttf", 20)
    bold_font = ImageFont.truetype("/home/ec2-user/DigiSpace/static/Khula-Bold.ttf", 30)
    semi_bold_font = ImageFont.truetype("/home/ec2-user/DigiSpace/static/Khula-SemiBold.ttf", 20)

    title_txt = Image.new('RGBA', (566, 100), (255, 255, 255, 255))
    draw = ImageDraw.Draw(title_txt)

    margin = 187
    offset = 10
    for line in textwrap.wrap(advert_tilte, width=30):
        draw.text((margin, offset), line, font=bold_font, fill="#00448b")
        offset += font.getsize(line)[1]

    dis_img = Image.open(os_path + advert_obj.display_image.url)
    dis_img = dis_img.resize((566, 570), Image.ANTIALIAS)

    dis_txt = Image.new('RGBA', (566, 150), (255, 255, 255, 255))
    draw = ImageDraw.Draw(dis_txt)

    margin = 10
    offset = 10
    i = 0
    for line in textwrap.wrap(discount_description, width=60):
        if i > 1:
            draw.text((margin, offset), "... and many more.", font=semi_bold_font, fill="#2EA489")
            break
        else:
            draw.text((margin, offset), line, font=semi_bold_font, fill="#2EA489")
            offset += font.getsize(line)[1] + 5
        i = i + 1

    margin = 180
    offset = offset + 40
    for line in textwrap.wrap(advert_address, width=35):
        print line
        draw.text((margin, offset), line, font=font, fill="#00448b")
        offset += font.getsize(line)[1]

    image_name = "new_advert_" + str(advert_obj.advert_id) + ".jpg"
    blank_image = Image.new('RGBA', (566, 820), (255, 255, 255, 255))
    draw = ImageDraw.Draw(blank_image)
    blank_image.paste(title_txt, (0, 0))
    blank_image.paste(dis_img, (0, 100))
    blank_image.paste(dis_txt, (0, 670))
    tempfile = blank_image
    tempfile_io = StringIO.StringIO()
    tempfile.save(tempfile_io, format='JPEG')
    image_file = InMemoryUploadedFile(tempfile_io, None, image_name, 'image/jpeg', tempfile_io.len, None)
    advert_obj.advert_image.save(image_name, image_file)
    advert_obj.save()
    return 1

@csrf_exempt
def save_advert_form(request):
    # pdb.set_trace()
    try:
        if request.method == "POST":
            print '===request========', request.POST.get('advert_keywords')
            advert_obj = Advert(
                supplier_id=Supplier.objects.get(supplier_id=request.POST.get('supplier_id')),
                category_id=Category.objects.get(category_id=request.POST.get('categ')),
                advert_name=request.POST.get('advert_title'),
                contact_name=request.POST.get('contact_name'),
                contact_no=request.POST.get('phone_no'),
                website=request.POST.get('website'),
                latitude=request.POST.get('lat'),
                longitude=request.POST.get('lng'),
                short_description=request.POST.get('short_discription'),
                product_description=request.POST.get('product_discription'),
                currency=request.POST.get('currency'),
                country_id = Country.objects.get(country_id=request.POST.get('country')) if request.POST.get('country') else None,
                # product_price=request.POST.get('product_price'),
                discount_description=request.POST.get('discount_discription'),
                email_primary=request.POST.get('email_primary'),
                email_secondary=request.POST.get('email_secondary'),
                address_line_1=request.POST.get('address_line1'),
                address_line_2=request.POST.get('address_line2'),
                area=request.POST.get('area'),
                landmark=request.POST.get('landmark'),
                state_id=State.objects.get(state_id=request.POST.get('statec')) if request.POST.get('statec') else None,
                city_place_id=City_Place.objects.get(city_place_id=request.POST.get('city')) if request.POST.get(
                    'city') else None,
                pincode_id=Pincode.objects.get(pincode=request.POST.get('pincode')) if request.POST.get(
                    'pincode') else None,
                property_market_rate=request.POST.get('pro_mark_rate'),
                possesion_status=request.POST.get('possesion_status'),
                date_of_delivery=request.POST.get('date_of_delivery'),
                other_projects=request.POST.get('other_projects'),
                distance_frm_railway_station=request.POST.get('dis_rail_stat'),
                distance_frm_railway_airport=request.POST.get('dis_airport'),
                speciality=request.POST.get('speciality'),
                affilated_to=request.POST.get('affilated'),
                course_duration=request.POST.get('course_duration'),
                happy_hour_offer=request.POST.get('happy_hour_offer'),
                facility=request.POST.get('facility'),
                keywords=request.POST.get('advert_keywords'),
                image_video_space_used=request.POST.get('image_and_video_space')
            );
            advert_obj.save()
            advert_id=advert_obj.advert_id

            if request.POST.get('any_other_details'):
                advert_obj.any_other_details = request.POST.get('any_other_details')
                advert_obj.save()
            if request.POST.get('subscription_id'):
                map_subscription(request.POST.get('subscription_id'), advert_obj)

            subcat_list = request.POST.getlist('subcat_list')
            print subcat_list
            subcat_lvl = 1
            # String to list
            if subcat_list != '':
                for subcat in subcat_list:
                    if subcat:
                        print 'Subcat: ', subcat, subcat_lvl
                        if subcat_lvl == 1:
                            advert_obj.category_level_1 = CategoryLevel1.objects.get(category_id=subcat)
                            advert_obj.save()
                        if subcat_lvl == 2:
                            advert_obj.category_level_2 = CategoryLevel2.objects.get(category_id=subcat)
                            advert_obj.save()
                        if subcat_lvl == 3:
                            advert_obj.category_level_3 = CategoryLevel3.objects.get(category_id=subcat)
                            advert_obj.save()
                        if subcat_lvl == 4:
                            advert_obj.category_level_4 = CategoryLevel4.objects.get(category_id=subcat)
                            advert_obj.save()
                        if subcat_lvl == 5:
                            advert_obj.category_level_5 = CategoryLevel5.objects.get(category_id=subcat)
                            advert_obj.save()
                        print 'Advert Subcat Mapping saved'
                        subcat_lvl += 1
            if request.POST['check_image'] == "1":
                advert_obj.display_image = request.FILES['display_image']
                advert_obj.save()

                save_advert_image(advert_obj)

            attachment_list = []
            attachment_list = request.POST.get('attachments')
            save_attachments(attachment_list, advert_obj)

            video_list = []
            video_list = request.POST.get('ac_attachment')
            save_video(video_list, advert_obj)

            # phone_category_list = request.POST.get('phone_category_list')
            # phone_category_list = phone_category_list.split(',')
            # phone_number_list = request.POST.get('phone_number_list')
            # phone_number_list = phone_number_list.split(',')
            # zipped = zip(phone_category_list, phone_number_list)
            # save_phone_number(zipped, advert_obj)

            product_name_list = request.POST.get('product_name_list')
            product_name_list = product_name_list.split('_PRODUCT_NAME_IS_SEPARATED')
            product_price_list = request.POST.get('product_price_list')
            product_price_list = product_price_list.split('_PRODUCT_PRICE_IS_SEPARATED')
            zipped_product = zip(product_name_list, product_price_list)
            save_product(zipped_product, advert_obj)

            opening_day_list = request.POST.get('opening_day_list')
            opening_day_list = opening_day_list.split(',')

            start_time_list = request.POST.get('start_time_list')
            start_time_list = start_time_list.split(',')

            end_time_list = request.POST.get('end_time_list')
            end_time_list = end_time_list.split(',')

            zipped_wk = zip(opening_day_list, start_time_list, end_time_list)
            save_working_hours(zipped_wk, advert_obj)

            amenity_list = request.POST.get('amenity_list')
            amenity_list = amenity_list.split(',')
            save_amenity(amenity_list, advert_obj)



            near_attr_list = request.POST.get('near_attraction')
            near_attr_list = near_attr_list.split(',')
            save_near_attr(near_attr_list, advert_obj)

            near_shopnmal = request.POST.get('near_shopnmal')
            near_shopnmal = near_shopnmal.split(',')

            near_shonmald = request.POST.get('near_shonmald')
            near_shonmald = near_shonmald.split(',')

            zipped_shopmal = zip(near_shopnmal, near_shonmald)
            save_shpnmal(zipped_shopmal, advert_obj)

            cat = advert_obj.category_id.category_name
            if cat == 'Real Estate':
                print "SCHOOL", request.POST.get('near_schol')
                near_schol = request.POST.get('near_schol')
                near_schol = near_schol.split(',')

                print "SCHOOL DI SORTING", request.POST.get('near_schold')
                near_schold = request.POST.get('near_schold')
                near_schold = near_schold.split(',')

                print "AFTER SCHOOL"

                zipped_school = zip(near_schol, near_schold)
                save_school(zipped_school, advert_obj)

                near_hosp = request.POST.get('near_hosp')
                near_hosp = near_hosp.split(',')

                near_hospd = request.POST.get('near_hospd')
                near_hospd = near_hospd.split(',')

                zipped_hospital = zip(near_hosp, near_hospd)
                save_hospital(zipped_hospital, advert_obj)
            #advert_add_sms(advert_obj)
            #advert_add_mail(advert_obj)
            data = {'success': 'true','advert_id':advert_id}

    except Exception, e:
        print 'Exception :', e
        data = {'data': 'none'}
    return HttpResponse(json.dumps(data), content_type='application/json')

def map_subscription(subscription_id, advert_obj):
    business_obj = Business.objects.get(business_id=str(subscription_id))
    business_obj.is_active = 1
    business_obj.save()
    sub_obj = AdvertSubscriptionMap(
        business_id=Business.objects.get(business_id=str(subscription_id)),
        advert_id=advert_obj
    )
    sub_obj.save()

def save_attachments(attachment_list, advert_id):
    try:
        attachment_list = attachment_list.split(',')
        attachment_list = filter(None, attachment_list)
        print attachment_list
        for attached_id in attachment_list:
            attachment_obj = AdvertImage.objects.get(advert_image_id=attached_id)
            attachment_obj.advert_id = advert_id
            attachment_obj.save()

        data = {'success': 'true'}
    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')

def save_video(video_list, advert_id):
    try:
        video_list = video_list.split(',')
        video_list = filter(None, video_list)
        print video_list
        for attached_id in video_list:
            attachment_obj = Advert_Video.objects.get(advert_video_id=attached_id)
            attachment_obj.advert_id = advert_id
            attachment_obj.save()

        data = {'success': 'true'}
    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')

def save_phone_number(zipped, advert_id):
    ##    pdb.set_trace()
    print "IN SAVE PHONE NUMBER"
    try:
        for phone_no_id, phone_no in zipped:
            if phone_no_id != '' and phone_no != '':
                print 'Phone number ID: ', phone_no_id
                phoneno_obj = PhoneNo(
                    advert_id=advert_id,
                    phone_category_id=PhoneCategory.objects.get(phone_category_id=phone_no_id),
                    phone_no=phone_no
                )
                phoneno_obj.save()
            data = {'success': 'true'}

    except Exception, e:
        print 'Exception ', e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')

def save_product(zipped_product, advert_id):
    ##    pdb.set_trace()
    print "IN SAVE PRODUCT"
    try:
        i = 0
        j = 0
        for product_name, product_price in zipped_product:
            product_name = product_name.strip()
            if i != 0:
                product_name = product_name[1:]
            i = i + 1
            product_price = product_price.strip()
            if j != 0:
                product_price = product_price[1:]
            j = j + 1
            if product_name:
                if product_price =='TEST$PRICE$BLANK':
                    product_price = ""
                else:
                    product_price == product_price
                product_obj = Product(
                    advert_id=advert_id,
                    product_name=product_name,
                    product_price=product_price
                )
                product_obj.save()
            data = {'success': 'true'}

    except Exception, e:
        print 'Exception ', e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')

def save_working_hours(zipped_wk, advert_id):
    ##    pdb.set_trace()
    print "IN SAVE WORKING HOURS"
    try:
        for wk_day, strt_tm, end_tm in zipped_wk:
            if wk_day != '' and strt_tm != '' and end_tm != '':
                wk_obj = WorkingHours(
                    advert_id=advert_id,
                    day=wk_day,
                    start_time=strt_tm,
                    end_time=end_tm
                )
                wk_obj.save()
            data = {'success': 'true'}

    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')


def save_amenity(amenity_list, advert_id):
    ##    pdb.set_trace()
    print "IN SAVE AMENITY"
    try:
        print "Advert Id", advert_id
        for amenity in amenity_list:
            if amenity != '':
                ame_obj = Amenities(
                    advert_id=advert_id,
                    categorywise_amenity_id=CategorywiseAmenity.objects.get(categorywise_amenity_id=amenity)
                )
                ame_obj.save()
            else:
                Amenities.objects.filter(advert_id=advert_id).delete()

            data = {'success': 'true'}

    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')


def save_exe_amenity(exe_amenity_list, advert_id):
    ##    pdb.set_trace()
    print "IN SAVE EXTRA AMENITY"
    try:
        for exe_am in exe_amenity_list:
            if exe_am != '':
                ame_obj = AdditionalAmenities(
                    advert_id=advert_id,
                    extra_amenity=exe_am
                )
                ame_obj.save()
            data = {'success': 'true'}

    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')


def save_near_attr(near_attr_list, advert_id):
    ##    pdb.set_trace()
    print "IN SAVE NEAR ATTRACTION"
    try:
        for ner_attr in near_attr_list:
            if ner_attr != '':
                ner_attr_obj = NearByAttraction(
                    advert_id=advert_id,
                    attraction=ner_attr
                )
                ner_attr_obj.save()
            data = {'success': 'true'}

    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')


def save_shpnmal(zipped_shopmal, advert_id):
    ##    pdb.set_trace()
    print "IN SAVE SHOP N MAL"
    try:
        for shpnml, shpnmld in zipped_shopmal:
            if shpnml != '' and shpnmld != '':
                shopnmal_obj = NearestShopping(
                    advert_id=advert_id,
                    shop_name=shpnml,
                    distance_frm_property=shpnmld
                )
                shopnmal_obj.save()
            data = {'success': 'true'}

    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')


def save_school(zipped_school, advert_id):
    ##    pdb.set_trace()
    print "IN SAVE SCHOOL"
    try:
        for school, schoold in zipped_school:
            if school != '' and schoold != '':
                school_obj = NearestSchool(
                    advert_id=advert_id,
                    school_name=school,
                    distance_frm_property=schoold
                )
                school_obj.save()
            data = {'success': 'true'}

    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')


def save_hospital(zipped_hospital, advert_id):
    ##    pdb.set_trace()
    print "IN SAVE HOSPITAL"
    try:
        for hospital, hospitald in zipped_hospital:
            if hospital != '' and hospitald != '':
                hospital_obj = NearestHospital(
                    advert_id=advert_id,
                    hospital_name=hospital,
                    distance_frm_property=hospitald
                )
                hospital_obj.save()
            data = {'success': 'true'}

    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def review_advert(request):
    try:
        # pdb.set_trace()

        advert_id = request.GET.get('advert_id')
        advert_obj = Advert.objects.get(advert_id = advert_id)
        advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)
        business_obj = Business.objects.get(business_id=str(advert_sub_obj.business_id))
        business_id= str(business_obj.business_id)

        img_data = ""
        image_list = []
        attach_id=[]
        attch_paths =[]
        attch_files =[]
        att = ""
        img_list = AdvertImage.objects.filter(advert_id = advert_obj)
        if img_list.count()>0:
            for img in img_list:
                attch_path = SERVER_URL + img.advert_image.url
                attch_file = str(img.advert_image)
                attahment_id =str(img.advert_image_id)
                
                attch_paths.append(attch_path)
                print 'attch_path',attch_path
                # attch_files.append(attch_file)
                # attach_id.append(attahment_id)
                # att=','.join(attach_id)
        else:
            pass

        video_data = ""
        video_list = []
        attach_video_id=[]
        attch_video_paths =[]
        attch_files =[]
        att = ""
        video_list = Advert_Video.objects.filter(advert_id = advert_obj)
        if video_list.count()>0:
            for vid in video_list:
                attch_video_path = SERVER_URL + vid.advert_video_name.url
                attch_video_paths.append(attch_video_path)
                print 'attch_path',attch_video_paths
                # attch_files.append(attch_file)
                # attach_id.append(attahment_id)
                # att=','.join(attach_id)
        else:
            pass

        print "video_list",video_list


        subscriber_info=[]
        subscriber_id=business_obj.supplier.supplier_id
        subscriber_obj = Supplier.objects.get(supplier_id=subscriber_id)
        business_name = subscriber_obj.business_name
        user_id=str(subscriber_obj.supplier_id)
        if subscriber_obj.logo:
           logo = SERVER_URL + subscriber_obj.logo.url
        else:
            logo = SERVER_URL + '/static/assets/layouts/layout2/img/City_Hoopla_Logo.png'

        if subscriber_obj.secondary_email:
           secondary_email = subscriber_obj.secondary_email
        else:
            secondary_email = '--'    
            
        if subscriber_obj.secondary_phone_no:
           secondary_phone_no = subscriber_obj.secondary_phone_no
        else:
            secondary_phone_no = '--' 

        start_date = business_obj.start_date
        start_date = datetime.strptime(start_date, "%d/%m/%Y")
        end_date = business_obj.end_date
        end_date = datetime.strptime(end_date, "%d/%m/%Y")

        if business_obj.category_level_1:
            cat = business_obj.category.category_name
            cat1 = business_obj.category_level_1.category_name
            category_name = str(cat + ", "+ cat1)

        if business_obj.category_level_2:
            cat = business_obj.category.category_name
            cat1 = business_obj.category_level_1.category_name
            cat2 = business_obj.category_level_2.category_name
            category_name = str(cat + ", "+ cat1 + ", " +cat2)

        if business_obj.category_level_3:
            cat = business_obj.category.category_name
            cat1 = business_obj.category_level_1.category_name
            cat2 = business_obj.category_level_2.category_name
            cat3 = business_obj.category_level_3.category_name
            category_name = str(cat + ", "+ cat1 + ", " +cat2 + ", " + cat3)

        if business_obj.category_level_4:
            cat = business_obj.category.category_name
            cat1 = business_obj.category_level_1.category_name
            cat2 = business_obj.category_level_2.category_name
            cat3 = business_obj.category_level_3.category_name
            cat4 = business_obj.category_level_4.category_name
            category_name = str(cat + ", "+ cat1 + ", " +cat2 + ", " + cat3 + ", " + cat4)

        if business_obj.category_level_5:
            cat = business_obj.category.category_name
            cat1 = business_obj.category_level_1.category_name
            cat2 = business_obj.category_level_2.category_name
            cat3 = business_obj.category_level_3.category_name
            cat4 = business_obj.category_level_4.category_name
            cat5 = business_obj.category_level_5.category_name
            category_name = str(cat + ", "+ cat1 + ", " +cat2 + ", " + cat3 + ", " + cat4 + ", " + cat5)



        business_data = {
            'business_id': str(business_obj.business_id),
            'category_name': category_name,
            'service_rate_card_duration': int(business_obj.duration),
            'start_date': str(start_date.strftime("%d %b %y")),
            'end_date': str(end_date.strftime("%d %b %y")),
        }

        try:
            enquiry_service_obj = EnquiryService.objects.get(business_id=str(business_obj.business_id))
            start_date = enquiry_service_obj.start_date
            start_date = datetime.strptime(start_date, "%d/%m/%Y")
            end_date = enquiry_service_obj.end_date
            end_date = datetime.strptime(end_date, "%d/%m/%Y")

            enquiry_service_data = {
                'enquiry_service_name': enquiry_service_obj.enquiry_service_name,
                'enquiry_service_duration': enquiry_service_obj.no_of_days,
                'enquiry_service_start_date': str(start_date.strftime("%d %b %y")),
                'enquiry_service_end_date': str(end_date.strftime("%d %b %y"))
                }
        except Exception as e:
            print e
            enquiry_service_data = {}
            pass

        product_obj = Product.objects.filter(advert_id = advert_id)
        product_list = []
        if product_obj:
            for products in product_obj:
                product_data = {
                    "product_name":products.product_name,
                    "product_price":products.product_price
                }
                product_list.append(product_data)

        time_list = []
        time_obj = WorkingHours.objects.filter(advert_id = advert_id)
        if time_obj:
            for time in time_obj:
                time_data = {
                    "day":time.day,
                    "start_time":time.start_time,
                    "end_time":time.end_time,
                }
                time_list.append(time_data)


        premium_service_list = []
        premium_service_obj = PremiumService.objects.filter(business_id=str(business_obj.business_id))
        for premium_service in premium_service_obj:


            start_date = premium_service.start_date
            start_date = datetime.strptime(start_date, "%d/%m/%Y")
            end_date = premium_service.end_date
            end_date = datetime.strptime(end_date, "%d/%m/%Y")

      
            premium_service_data = {
                'premium_service_name': premium_service.premium_service_name,
                'premium_service_duration': premium_service.no_of_days,
                'premium_service_start_date': str(start_date.strftime("%d %b %y")),
                'premium_service_end_date': str(end_date.strftime("%d %b %y"))
            }
            premium_service_list.append(premium_service_data)

        try:
            payment_obj = PaymentDetail.objects.get(business_id=str(business_obj.business_id))
            if payment_obj.payment_mode == 'cash':
                payment_mode = "Cash"
            else:
                payment_mode = "Cheque"
            tax=round(float(payment_obj.payable_amount), 2)-round(float(payment_obj.total_amount), 2)
            payment_details = {

                'payment_mode': payment_mode,
                'paid_amount': round(float(payment_obj.paid_amount), 2),
                'payable_amount': round(float(payment_obj.payable_amount), 2),
                'total_amount': round(float(payment_obj.total_amount), 2),
                'tax': tax,
                'note': payment_obj.note,
            }
            # print payment_details
        except Exception:
            payment_details = {
                'payment_mode': '',
                'paid_amount': '',
                'payable_amount': '',
                'total_amount': '',
                'tax_type': '',
                'note': '',
                'bank_name': '',
                'branch_name': '',
                'cheque_number': ''
            }
            pass

        if advert_obj.any_other_details:
            any_other_details =advert_obj.any_other_details
        else:
            any_other_details = ""


        temp_data ={
        'display_image':SERVER_URL + advert_obj.display_image.url if advert_obj.display_image else SERVER_URL + '/static/assets/layouts/layout2/img/City_Hoopla_Logo.png',
        'advert_name':advert_obj.advert_name,
        'area': advert_obj.area,
        'email_primary': advert_obj.email_primary,
        'contact_no':advert_obj.contact_no,
        'currency':advert_obj.currency,
        'address_line_1': advert_obj.address_line_1,
        'area': advert_obj.area,
        'state_id': advert_obj.state_id.state_name,
        'city_place_id': advert_obj.city_place_id.city_id.city_name,
        'pincode_id': advert_obj.pincode_id.pincode,
        'short_description':advert_obj.short_description,
        'product_description':advert_obj.product_description,
        'discount_description':advert_obj.discount_description,
        'any_other_details': any_other_details,
        'business_name':subscriber_obj.business_name,
        'subscriber_id':subscriber_obj.supplier_id,
        'subscriber_city':subscriber_obj.city_place_id.city_id.city_name,
        'premium_service_list': premium_service_list,
        'payment_details': payment_details,
        'business_data': business_data,
        'business_id':business_id,
        'product_list':product_list,
        'time_list':time_list,
        'attch_paths':attch_paths,
        'enquiry_service_data':enquiry_service_data,
        'attch_video_paths':attch_video_paths,
        'flag':"1"
        }
        subscriber_info.append(temp_data)

        data = {
            'success': 'true',
            'subscriber_info':subscriber_info,'business_id':business_id,'business_name':subscriber_obj.business_name,
            'advert_id':advert_id,'subscriber_id':subscriber_id,
        }

        print "DATA",data


    except Exception, e:
        data = {
            'success': 'false',
            'message': str(e)
        }
    # return HttpResponse(json.dumps(data), content_type='application/json')
    return render(request,'Admin/review_advert.html', data)

@csrf_exempt
def review_edit_advert(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        advert_id = request.GET.get('advert_id')
        tax_list = Tax.objects.all()
        temp_data = ''
        cat_amenities = []

        
        advert_obj = Advert.objects.get(advert_id = advert_id)
        supplier_id=str(advert_obj.supplier_id)
        supplier_name=str(advert_obj.supplier_id.business_name)

        if advert_obj.category_level_1:
            category_l1_list = CategoryLevel1.objects.filter(parent_category_id = str(advert_obj.category_id.category_id))
        else:
            category_l1_list = []

        if advert_obj.category_level_2:
            category_l2_list = CategoryLevel2.objects.filter(
                parent_category_id=str(advert_obj.category_level_1.category_id))
        else:
            category_l2_list = []

        if advert_obj.category_level_3:
            category_l3_list = CategoryLevel3.objects.filter(
                parent_category_id=str(advert_obj.category_level_2.category_id))
        else:
            category_l3_list = []

        if advert_obj.category_level_4:
            category_l4_list = CategoryLevel4.objects.filter(
                parent_category_id=str(advert_obj.category_level_3.category_id))
        else:
            category_l4_list = []

        if advert_obj.category_level_5:
            category_l5_list = CategoryLevel5.objects.filter(
                parent_category_id=str(advert_obj.category_level_4.category_id))
        else:
            category_l5_list = []

        business_id = request.GET.get('business_id')
        business_obj = Business.objects.get(business_id = business_id)
        premium_obj = PremiumService.objects.filter(business_id=business_id)
        advert_flag = 'false'
        if premium_obj:
            for premium in premium_obj:
                if premium.premium_service_name == "Top Advert":
                    advert_flag = 'true'
                elif premium.premium_service_name == "Advert Slider":
                    advert_flag = 'true'
        category_level_1 = ''
        category_level_2 = ''
        category_level_3 = ''
        category_level_4 = ''
        category_level_5 = ''
        business_obj = Business.objects.get(business_id=business_id)
        if business_obj.category:
            category_id = str(business_obj.category.category_id)
        if business_obj.category_level_1:
            category_level_1 = str(business_obj.category_level_1.category_id)
        if business_obj.category_level_2:
            category_level_2 = str(business_obj.category_level_2.category_id)
        if business_obj.category_level_3:
            category_level_3 = str(business_obj.category_level_3.category_id)
        if business_obj.category_level_4:
            category_level_4 = str(business_obj.category_level_4.category_id)
        if business_obj.category_level_5:
            category_level_5 = str(business_obj.category_level_5.category_id)

        cl1 = ''
        if business_obj.category:
            amenity_list = CategorywiseAmenity.objects.filter(status="1",category=category_id)
            for ck in amenity_list:
                cl1= ck.category_level_1

            if cl1:
                if business_obj.category and business_obj.category_level_1: 
                    amenity_list = CategorywiseAmenity.objects.filter(status="1",category=category_id,category_level_1=category_level_1)

                if business_obj.category and business_obj.category_level_1 and business_obj.category_level_2:
                    amenity_list = CategorywiseAmenity.objects.filter(status="1",category=category_id,category_level_1=category_level_1,category_level_2=category_level_2)

                if business_obj.category and business_obj.category_level_1 and business_obj.category_level_2 and business_obj.category_level_3:
                    amenity_list = CategorywiseAmenity.objects.filter(status="1",category=category_id,category_level_1=category_level_1,category_level_3=category_level_3)

                if business_obj.category and business_obj.category_level_1 and business_obj.category_level_2 and business_obj.category_level_3 and business_obj.category_level_4:
                    amenity_list = CategorywiseAmenity.objects.filter(status="1",category=category_id,category_level_1=category_level_1,category_level_3=category_level_3,category_level_4=category_level_4)

                if business_obj.category and business_obj.category_level_1 and business_obj.category_level_2 and business_obj.category_level_3 and business_obj.category_level_4 and business_obj.category_level_5:
                    amenity_list = CategorywiseAmenity.objects.filter(status="1",category=category_id,category_level_1=category_level_1,category_level_3=category_level_3,category_level_4=category_level_4,category_level_5=category_level_5)

        
                ameninty_checked = "false"
                for amnenity in amenity_list:
                    try:
                        amenities_obj = Amenities.objects.get(advert_id=advert_id,categorywise_amenity_id =str(amnenity.categorywise_amenity_id) )
                        ameninty_checked = "true"
                    except:
                        ameninty_checked = "false"
                        pass                
                    temp_data ={
                    'id':str(amnenity.categorywise_amenity_id),
                    'amenity':str(amnenity.amenity),
                    'checkced':ameninty_checked
                    }
                    cat_amenities.append(temp_data)
                print "cat_amenities",cat_amenities

            else:
                amenity_list = CategorywiseAmenity.objects.filter(status="1",category=category_id)
                ameninty_checked = "false"
                for amnenity in amenity_list:
                    try:
                        amenities_obj = Amenities.objects.get(advert_id=advert_id,categorywise_amenity_id =str(amnenity.categorywise_amenity_id) )
                        ameninty_checked = "true"
                    except:
                        ameninty_checked = "false"
                        pass                
                    temp_data ={
                    'id':str(amnenity.categorywise_amenity_id),
                    'amenity':str(amnenity.amenity),
                    'checkced':ameninty_checked
                    }
                    cat_amenities.append(temp_data)




        advert_data = {
            'category_id':advert_obj.category_id.category_id,
            'category_level_1':advert_obj.category_level_1.category_id if advert_obj.category_level_1 else '',
            'category_level_2':advert_obj.category_level_2.category_id if advert_obj.category_level_2 else '',
            'category_level_3':advert_obj.category_level_3.category_id if advert_obj.category_level_3 else '',
            'category_level_4':advert_obj.category_level_4.category_id if advert_obj.category_level_4 else '',
            'category_level_5':advert_obj.category_level_5.category_id if advert_obj.category_level_5 else '',
            'advert_name':advert_obj.advert_name,
            'contact_name':advert_obj.contact_name,
            'contact_no':advert_obj.contact_no,
            'latitude':advert_obj.latitude,
            'longitude':advert_obj.longitude,
            'short_description':advert_obj.short_description,
            'product_description':advert_obj.product_description,
            'discount_description':advert_obj.discount_description,
            'currency':advert_obj.currency,
            'display_image':SERVER_URL + advert_obj.display_image.url if advert_obj.display_image else '',
            'address_line_1': advert_obj.address_line_1,
            'address_line_2': advert_obj.address_line_2,
            'country_id': advert_obj.country_id.country_id,
            'currency': advert_obj.currency,
            'state_id': advert_obj.state_id.state_id,
            'city_place_id': advert_obj.city_place_id.city_place_id,
            'pincode_id': advert_obj.pincode_id.pincode_id,
            'area': advert_obj.area,
            'landmark': advert_obj.landmark,
            'email_primary': advert_obj.email_primary,
            'property_market_rate': advert_obj.property_market_rate,
            'possesion_status': advert_obj.possesion_status,
            'other_projects': advert_obj.other_projects,
            'date_of_delivery': advert_obj.date_of_delivery,
            'any_other_details': advert_obj.any_other_details,
            'speciality': advert_obj.speciality,
            'happy_hour_offer': advert_obj.happy_hour_offer,
            'course_duration': advert_obj.course_duration,
            'affilated_to': advert_obj.affilated_to,
            'image_video_space_used': advert_obj.image_video_space_used,
            'facility': advert_obj.facility,
            'keywords': advert_obj.keywords,
            'distance_frm_railway_station': advert_obj.distance_frm_railway_station,
            'distance_frm_airport': advert_obj.distance_frm_railway_airport,
            'other_amenity':advert_obj.other_amenity
        }

        product_obj = Product.objects.filter(advert_id = advert_id)
        product_list = []
        if product_obj:
            for products in product_obj:
                product_data = {
                    "product_id":products.product_id,
                    "product_name":products.product_name,
                    "product_price":products.product_price
                }
                product_list.append(product_data)

        time_list = []
        time_obj = WorkingHours.objects.filter(advert_id = advert_id)
        if time_obj:
            for time in time_obj:
                time_data = {
                    "day":time.day,
                    "start_time":time.start_time,
                    "end_time":time.end_time,
                }
                time_list.append(time_data)



        nr_attr_obj = NearByAttraction.objects.filter(advert_id = advert_id)
        nr_attr_list = []
        if nr_attr_obj:
            for nr_attr in nr_attr_obj:
                nr_attr_data = {
                    "attraction": nr_attr.attraction
                }
                nr_attr_list.append(nr_attr_data)

        nr_shop_obj = NearestShopping.objects.filter(advert_id = advert_id)
        nr_shop_list = []
        if nr_shop_obj:
            for nr_shop in nr_shop_obj:
                nr_shop_data = {
                    "shop_name": nr_shop.shop_name,
                    "distance_frm_property": nr_shop.distance_frm_property
                }
                nr_shop_list.append(nr_shop_data)

        nr_shcl_obj = NearestSchool.objects.filter(advert_id = advert_id)
        nr_shcl_list = []
        if nr_shcl_obj:
            for schools in nr_shcl_obj:
                schools_data = {
                    "school_name": schools.school_name,
                    "distance_frm_property": schools.distance_frm_property
                }
                nr_shcl_list.append(schools_data)

        nr_hosp_obj = NearestHospital.objects.filter(advert_id = advert_id)
        nr_hosp_list = []
        if nr_hosp_obj:
            for hospitals in nr_hosp_obj:
                hospital_data = {
                    "hospital_name": hospitals.hospital_name,
                    "distance_frm_property": hospitals.distance_frm_property
                }
                nr_hosp_list.append(hospital_data)

        data = { 
                'username': request.session['login_user'], 'category_list': get_category(request),
                'country_list': get_country(request), 'phone_category': get_phone_category(request),
                'state_list': get_states(request), 'advert_flag':advert_flag,
                'product_list':product_list,'time_list':time_list,'cat_amenities':cat_amenities,
                'advert_data':advert_data, 'advert_id':advert_id,'supplier_id':supplier_id,
                'nr_attr_list':nr_attr_list,'title' :advert_obj.title,'supplier_name':supplier_name,
                'nr_shop_list':nr_shop_list,'nr_shcl_list':nr_shcl_list,'nr_hosp_list':nr_hosp_list,
                'category_l1_list':category_l1_list,'category_l2_list':category_l2_list,'category_l3_list':category_l3_list,
                'category_l4_list':category_l4_list,'category_l5_list':category_l5_list
                }
        return render(request, 'Admin/review_edit_advert.html', data)


@csrf_exempt
def delete_product(request):
    try:
        print "product_id", request.POST.get('product_id')
        request.POST.get('product_id')
        pro_obj = Product.objects.filter(product_id=request.POST.get('product_id'))
        pro_obj.delete()

        data = {'message': 'Product Deleted Successfully', 'success': 'true','del_flag':'3'}
    except IntegrityError as e:
        print e
    except Exception, e:
        print e
    print "Final Data: ", data
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def add_subscription(request):
    # pdb.set_trace()v
    print "IN ADD SUBSCRIPTION SAVE ADVERT METHOD"
    try:
        if request.method == "POST":
            print '==========request==========', request.POST.get('advert_keywords')
            try:
                serv_obj = ServiceRateCard.objects.get(service_name=request.POST.get('service'),
                                                       duration=request.POST.get('selected_duration'))
                try:
                    premium_service_list = request.POST.get('premium_service')
                    no_of_days_list = request.POST.get('premium_day_list')
                    if (premium_service_list):
                        print '------------after premium servuice------------'
                        final_data = check_subscription_detail(premium_service_list, no_of_days_list)
                        if final_data['success'] == 'true':
                            category_obj = Category.objects.get(category_id=request.POST.get('categ'))
                            business_obj = ''
                            date_validation = check_date(premium_service_list, request.POST.get('premium_start_date'),
                                                         request.POST.get('premium_end_date'), category_obj,
                                                         business_obj)
                            if date_validation['success'] == 'true':
                                advert_obj = Advert(
                                    supplier_id=Supplier.objects.get(supplier_id=request.POST.get('user_id')),
                                    category_id=Category.objects.get(category_id=request.POST.get('categ')),
                                    advert_name=request.POST.get('advert_title'),
                                    website=request.POST.get('website'),
                                    latitude=request.POST.get('lat'),
                                    longitude=request.POST.get('lng'),
                                    short_description=request.POST.get('short_discription'),
                                    product_description=request.POST.get('product_discription'),
                                    currency=request.POST.get('currency'),
                                    # product_price=request.POST.get('product_price'),
                                    discount_description=request.POST.get('discount_discription'),
                                    email_primary=request.POST.get('email_primary'),
                                    email_secondary=request.POST.get('email_secondary'),
                                    address_line_1=request.POST.get('address_line1'),
                                    address_line_2=request.POST.get('address_line2'),
                                    area=request.POST.get('area'),
                                    landmark=request.POST.get('landmark'),
                                    country_id=Country.objects.get(country_id=request.POST.get('country')),
                                    state_id=State.objects.get(state_id=request.POST.get('statec')) if request.POST.get(
                                        'statec') else None,
                                    city_place_id=City_Place.objects.get(
                                        city_place_id=request.POST.get('city')) if request.POST.get('city') else None,
                                    pincode_id=Pincode.objects.get(
                                        pincode=request.POST.get('pincode')) if request.POST.get('pincode') else None,
                                    property_market_rate=request.POST.get('pro_mark_rate'),
                                    possesion_status=request.POST.get('possesion_status'),
                                    any_other_details=request.POST.get('any_other_details'),
                                    other_projects=request.POST.get('other_projects'),
                                    date_of_delivery=request.POST.get('date_of_delivery'),
                                    distance_frm_railway_station=request.POST.get('dis_rail_stat'),
                                    distance_frm_railway_airport=request.POST.get('dis_airport'),
                                    speciality=request.POST.get('speciality'),
                                    affilated_to=request.POST.get('affilated'),
                                    course_duration=request.POST.get('course_duration'),
                                    happy_hour_offer=request.POST.get('happy_hour_offer'),
                                    facility=request.POST.get('facility'),
                                    keywords=request.POST.get('advert_keywords'),
                                    image_video_space_used=request.POST.get('image_and_video_space')
                                );
                                advert_obj.save()
                                print '===============after save advert================='
                                subcat_list = request.POST.getlist('subcat_list')
                                print subcat_list
                                subcat_lvl = 1
                                # String to list
                                if subcat_list != '':
                                    for subcat in subcat_list:
                                        print 'Subcat: ', subcat, subcat_lvl
                                        if subcat_lvl == 1:
                                            advert_obj.category_level_1 = CategoryLevel1.objects.get(category_id=subcat)
                                            advert_obj.save()
                                        if subcat_lvl == 2:
                                            advert_obj.category_level_2 = CategoryLevel2.objects.get(category_id=subcat)
                                            advert_obj.save()
                                        if subcat_lvl == 3:
                                            advert_obj.category_level_3 = CategoryLevel3.objects.get(category_id=subcat)
                                            advert_obj.save()
                                        if subcat_lvl == 4:
                                            advert_obj.category_level_4 = CategoryLevel4.objects.get(category_id=subcat)
                                            advert_obj.save()
                                        if subcat_lvl == 5:
                                            advert_obj.category_level_5 = CategoryLevel5.objects.get(category_id=subcat)
                                            advert_obj.save()
                                        print 'Advert Subcat Mapping saved'
                                        subcat_lvl += 1
                                if request.POST['check_image'] == "1":
                                    advert_obj.display_image = request.FILES['display_image']
                                    advert_obj.save()

                                    save_advert_image(advert_obj)

                                attachment_list = []
                                attachment_list = request.POST.get('attachments')
                                save_attachments(attachment_list, advert_obj)

                                video_list = []
                                video_list = request.POST.get('ac_attachment')
                                save_video(video_list, advert_obj)

                                phone_category_list = request.POST.get('phone_category_list')
                                phone_category_list = phone_category_list.split(',')
                                phone_number_list = request.POST.get('phone_number_list')
                                phone_number_list = phone_number_list.split(',')
                                zipped = zip(phone_category_list, phone_number_list)
                                save_phone_number(zipped, advert_obj)

                                product_name_list = request.POST.get('product_name_list')
                                product_name_list = product_name_list.split('_PRODUCT_NAME_IS_SEPARATED')
                                product_price_list = request.POST.get('product_price_list')
                                product_price_list = product_price_list.split('_PRODUCT_PRICE_IS_SEPARATED')
                                zipped_product = zip(product_name_list, product_price_list)
                                save_product(zipped_product, advert_obj)

                                opening_day_list = request.POST.get('opening_day_list')
                                opening_day_list = opening_day_list.split(',')

                                start_time_list = request.POST.get('start_time_list')
                                start_time_list = start_time_list.split(',')

                                end_time_list = request.POST.get('end_time_list')
                                end_time_list = end_time_list.split(',')

                                zipped_wk = zip(opening_day_list, start_time_list, end_time_list)
                                save_working_hours(zipped_wk, advert_obj)

                                amenity_list = request.POST.get('amenity_list')
                                amenity_list = amenity_list.split(',')
                                save_amenity(amenity_list, advert_obj)


                                near_attr_list = request.POST.get('near_attraction')
                                near_attr_list = near_attr_list.split(',')
                                save_near_attr(near_attr_list, advert_obj)

                                near_shopnmal = request.POST.get('near_shopnmal')
                                near_shopnmal = near_shopnmal.split(',')

                                near_shonmald = request.POST.get('near_shonmald')
                                near_shonmald = near_shonmald.split(',')

                                zipped_shopmal = zip(near_shopnmal, near_shonmald)
                                save_shpnmal(zipped_shopmal, advert_obj)

                                cat = advert_obj.category_id.category_name
                                if cat == 'Real Estate':
                                    print "SCHOOL", request.POST.get('near_schol')
                                    near_schol = request.POST.get('near_schol')
                                    near_schol = near_schol.split(',')

                                    print "SCHOOL DI SORTING", request.POST.get('near_schold')
                                    near_schold = request.POST.get('near_schold')
                                    near_schold = near_schold.split(',')

                                    print "AFTER SCHOOL"

                                    zipped_school = zip(near_schol, near_schold)
                                    save_school(zipped_school, advert_obj)

                                    near_hosp = request.POST.get('near_hosp')
                                    near_hosp = near_hosp.split(',')

                                    near_hospd = request.POST.get('near_hospd')
                                    near_hospd = near_hospd.split(',')

                                    zipped_hospital = zip(near_hosp, near_hospd)
                                    save_hospital(zipped_hospital, advert_obj)
                                advert_add_mail(advert_obj)
                                advert_add_sms(advert_obj)
                                data = {'success': 'true'}

                                print '============after save==========='
                                chars = string.digits
                                pwdSize = 8
                                password = ''.join(random.choice(chars) for _ in range(pwdSize))
                                supplier_obj = Supplier.objects.get(supplier_id=request.POST.get('user_id'))
                                business_obj = Business(
                                    category=Category.objects.get(category_id=request.POST.get('categ')),
                                    service_rate_card_id=ServiceRateCard.objects.get(
                                        service_name=request.POST.get('service'),
                                        duration=request.POST.get('selected_duration')),
                                    duration=request.POST.get('selected_duration'),
                                    start_date=request.POST.get('duration_start_date'),
                                    end_date=request.POST.get('duration_end_date'),
                                    supplier=supplier_obj,
                                    transaction_code="TID" + str(password),
                                    is_active=0
                                )
                                business_obj.save()
                                map_subscription(business_obj, advert_obj)

                                premium_service_list = request.POST.get('premium_service')
                                if (premium_service_list != ['']):
                                    premium_service_list = str(premium_service_list).split(',')
                                    no_of_days_list = request.POST.get('premium_day_list')
                                    no_of_days_list = str(no_of_days_list).split(',')
                                    start_date_list = request.POST.get('premium_start_date')
                                    start_date_list = str(start_date_list).split(',')

                                    end_date_list = request.POST.get('premium_end_date')
                                    end_date_list = str(end_date_list).split(',')
                                    zipped_wk = zip(premium_service_list, no_of_days_list, start_date_list,
                                                    end_date_list)
                                    save_premium_service(zipped_wk, business_obj)

                                data = {
                                    'success': 'true',
                                    'message': "Supplier added successfully",
                                    'transaction_code': str(business_obj.transaction_code),
                                    'subscriber_id': str(supplier_obj.supplier_id),
                                    'business_id': str(business_obj.business_id)
                                }
                            else:
                                data = {
                                    'success': 'false',
                                    'message': date_validation['message']
                                }
                        else:
                            data = {
                                'success': 'false',
                                'message': final_data['message']
                            }
                    else:
                        print ""
                        advert_obj = Advert(
                            supplier_id=Supplier.objects.get(supplier_id=request.POST.get('user_id')),
                            category_id=Category.objects.get(category_id=request.POST.get('categ')),
                            advert_name=request.POST.get('advert_title'),
                            website=request.POST.get('website'),
                            latitude=request.POST.get('lat'),
                            longitude=request.POST.get('lng'),
                            short_description=request.POST.get('short_discription'),
                            product_description=request.POST.get('product_discription'),
                            currency=request.POST.get('currency'),
                            # product_price=request.POST.get('product_price'),
                            discount_description=request.POST.get('discount_discription'),
                            email_primary=request.POST.get('email_primary'),
                            email_secondary=request.POST.get('email_secondary'),
                            address_line_1=request.POST.get('address_line1'),
                            address_line_2=request.POST.get('address_line2'),
                            area=request.POST.get('area'),
                            landmark=request.POST.get('landmark'),
                            country_id=Country.objects.get(country_id=request.POST.get('country')),
                            state_id=State.objects.get(state_id=request.POST.get('statec')) if request.POST.get(
                                'statec') else None,
                            city_place_id=City_Place.objects.get(
                                city_place_id=request.POST.get('city')) if request.POST.get('city') else None,
                            pincode_id=Pincode.objects.get(pincode=request.POST.get('pincode')) if request.POST.get(
                                'pincode') else None,
                            property_market_rate=request.POST.get('pro_mark_rate'),
                            possesion_status=request.POST.get('possesion_status'),
                            any_other_details=request.POST.get('any_other_details'),
                            other_projects=request.POST.get('other_projects'),
                            date_of_delivery=request.POST.get('date_of_delivery'),
                            distance_frm_railway_station=request.POST.get('dis_rail_stat'),
                            distance_frm_railway_airport=request.POST.get('dis_airport'),
                            speciality=request.POST.get('speciality'),
                            affilated_to=request.POST.get('affilated'),
                            course_duration=request.POST.get('course_duration'),
                            happy_hour_offer=request.POST.get('happy_hour_offer'),
                            facility=request.POST.get('facility'),
                            keywords=request.POST.get('advert_keywords'),
                            image_video_space_used=request.POST.get('image_and_video_space')
                        );
                        advert_obj.save()
                        advert_add_mail(advert_obj)
                        advert_add_sms(advert_obj)
                        subcat_list = request.POST.getlist('subcat_list')
                        print subcat_list
                        subcat_lvl = 1
                        # String to list
                        if subcat_list != '':
                            for subcat in subcat_list:
                                print 'Subcat: ', subcat, subcat_lvl
                                if subcat_lvl == 1:
                                    advert_obj.category_level_1 = CategoryLevel1.objects.get(category_id=subcat)
                                    advert_obj.save()
                                if subcat_lvl == 2:
                                    advert_obj.category_level_2 = CategoryLevel2.objects.get(category_id=subcat)
                                    advert_obj.save()
                                if subcat_lvl == 3:
                                    advert_obj.category_level_3 = CategoryLevel3.objects.get(category_id=subcat)
                                    advert_obj.save()
                                if subcat_lvl == 4:
                                    advert_obj.category_level_4 = CategoryLevel4.objects.get(category_id=subcat)
                                    advert_obj.save()
                                if subcat_lvl == 5:
                                    advert_obj.category_level_5 = CategoryLevel5.objects.get(category_id=subcat)
                                    advert_obj.save()
                                print 'Advert Subcat Mapping saved'
                                subcat_lvl += 1
                        if request.POST['check_image'] == "1":
                            advert_obj.display_image = request.FILES['display_image']
                            advert_obj.save()

                            save_advert_image(advert_obj)

                        attachment_list = []
                        attachment_list = request.POST.get('attachments')
                        save_attachments(attachment_list, advert_obj)

                        video_list = []
                        video_list = request.POST.get('ac_attachment')
                        save_video(video_list, advert_obj)

                        phone_category_list = request.POST.get('phone_category_list')
                        phone_category_list = phone_category_list.split(',')
                        phone_number_list = request.POST.get('phone_number_list')
                        phone_number_list = phone_number_list.split(',')
                        zipped = zip(phone_category_list, phone_number_list)
                        save_phone_number(zipped, advert_obj)

                        product_name_list = request.POST.get('product_name_list')
                        product_name_list = product_name_list.split('_PRODUCT_NAME_IS_SEPARATED')
                        product_price_list = request.POST.get('product_price_list')
                        product_price_list = product_price_list.split('_PRODUCT_PRICE_IS_SEPARATED')
                        zipped_product = zip(product_name_list, product_price_list)
                        save_product(zipped_product, advert_obj)

                        opening_day_list = request.POST.get('opening_day_list')
                        opening_day_list = opening_day_list.split(',')

                        start_time_list = request.POST.get('start_time_list')
                        start_time_list = start_time_list.split(',')

                        end_time_list = request.POST.get('end_time_list')
                        end_time_list = end_time_list.split(',')

                        zipped_wk = zip(opening_day_list, start_time_list, end_time_list)
                        save_working_hours(zipped_wk, advert_obj)

                        amenity_list = request.POST.get('amenity_list')
                        amenity_list = amenity_list.split(',')
                        save_amenity(amenity_list, advert_obj)



                        near_attr_list = request.POST.get('near_attraction')
                        near_attr_list = near_attr_list.split(',')
                        save_near_attr(near_attr_list, advert_obj)

                        near_shopnmal = request.POST.get('near_shopnmal')
                        near_shopnmal = near_shopnmal.split(',')

                        near_shonmald = request.POST.get('near_shonmald')
                        near_shonmald = near_shonmald.split(',')

                        zipped_shopmal = zip(near_shopnmal, near_shonmald)
                        save_shpnmal(zipped_shopmal, advert_obj)

                        cat = advert_obj.category_id.category_name
                        if cat == 'Real Estate':
                            print "SCHOOL", request.POST.get('near_schol')
                            near_schol = request.POST.get('near_schol')
                            near_schol = near_schol.split(',')

                            print "SCHOOL DI SORTING", request.POST.get('near_schold')
                            near_schold = request.POST.get('near_schold')
                            near_schold = near_schold.split(',')

                            print "AFTER SCHOOL"

                            zipped_school = zip(near_schol, near_schold)
                            save_school(zipped_school, advert_obj)

                            near_hosp = request.POST.get('near_hosp')
                            near_hosp = near_hosp.split(',')

                            near_hospd = request.POST.get('near_hospd')
                            near_hospd = near_hospd.split(',')

                            zipped_hospital = zip(near_hosp, near_hospd)
                            save_hospital(zipped_hospital, advert_obj)
                        data = {'success': 'true'}

                        chars = string.digits
                        pwdSize = 8
                        password = ''.join(random.choice(chars) for _ in range(pwdSize))
                        supplier_obj = Supplier.objects.get(supplier_id=request.POST.get('user_id'))
                        business_obj = Business(
                            category=Category.objects.get(category_id=request.POST.get('categ')),
                            service_rate_card_id=ServiceRateCard.objects.get(service_name=request.POST.get('service'),
                                                                             duration=request.POST.get(
                                                                                 'selected_duration')),
                            duration=request.POST.get('selected_duration'),
                            start_date=request.POST.get('duration_start_date'),
                            end_date=request.POST.get('duration_end_date'),
                            supplier=supplier_obj,
                            transaction_code="TID" + str(password),
                            is_active=0
                        )
                        business_obj.save()
                        map_subscription(business_obj, advert_obj)

                        data = {
                            'success': 'true',
                            'message': "Supplier added successfully",
                            'transaction_code': str(business_obj.transaction_code),
                            'subscriber_id': str(supplier_obj.supplier_id),
                            'business_id':str(business_obj.business_id)

                        }
                except Exception, e:
                    data = {
                        'success': 'false',
                        'message': str(e)
                    }
            except:
                data = {
                    'success': 'false',
                    'message': 'Package ' + str(request.POST.get('service')) + ' ' + '(' + str(
                        request.POST.get('selected_duration')) + ' Days)' + ' not available'
                }

    except Exception, e:
        print 'Exception :', e
        data = {'data': 'none'}
    print '======data================', data
    return HttpResponse(json.dumps(data), content_type='application/json')


def check_video_size(user_id, status):
    print '=============user_id========', user_id
    if status == '1':
        subscription_obj = Business.objects.get(supplier=user_id)
        service = subscription_obj.service_rate_card_id.service_name
        print '========servcie========', service
        if (service == 'Bronze'):
            size = 10
        if (service == 'Silver'):
            size = 20
        if (service == 'Gold'):
            size = 10
        if (service == 'Platinum'):
            size = 20
        return 'true';
    else:
        return 'true';





@csrf_exempt
def main_listing_image_file_upload(request):
    ##    pdb.set_trace()
    try:
        if request.method == 'POST':
            attachment_file = AdvertImage(advert_image=request.FILES['file[]'])
            attachment_file.save()
            data = {'success': 'true', 'attachid': attachment_file.advert_image_id}
            print data
        else:
            data = {'success': 'false'}
            print data
    except MySQLdb.OperationalError, e:
        data = {'success': 'invalid request'}
    return HttpResponse(json.dumps(data), content_type='application/json')



@csrf_exempt
def advert_video_upload(request):
    ##    pdb.set_trace()
    print "IN UPLOAD VIDEO"
    try:
        if request.method == 'POST':
            attachment_file = Advert_Video(advert_video_name=request.FILES['file[]'])
            attachment_file.save()
            data = {'success': 'true', 'attachid': attachment_file.advert_video_id}
            print data
        else:
            data = {'success': 'false'}
            print data
    except MySQLdb.OperationalError, e:
        data = {'success': 'invalid request'}
    return HttpResponse(json.dumps(data), content_type='application/json')


def advert_add_sms(advert_obj):
    
    authkey = "118994AIG5vJOpg157989f23"
    # user_obj = Supplier.objects.get(supplier_id=su_id)
 #    contact_no = user_obj.contact_no
 #    print '---------contact_no------',contact_no

    mobiles = "+919403884595"
    message = "A new Advert \t" +str(advert_obj.advert_name) + "\t for your business \t"+ str(advert_obj.supplier_id.business_name) +"\t under category \t"+str(advert_obj.category_id.category_name)+"\t has been added successfully on your profile with CityHoopla"
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


# for get the client-list
def get_advert_list(request):
    try:
        # pdb.set_trace()
        print '=request=====', request

        print 'Advert List'
        user_id = request.GET.get('user_id')
        advert_list = Advert.objects.filter(supplier_id=request.GET.get('user_id'))
        adv_list = []
        for adv in advert_list:
            if adv.status == '1':
                detail = '<a style="text-align: center;letter-spacing: 5px;width:40%;" href="/advert-booking-list/?advert_id=' + str(
                    adv.advert_id) + '&user_id=' + str(user_id) + '"<i class="fa fa-search-plus "></i> ' + '</a>'

                edit = '<a style="text-align: center;letter-spacing: 5px;width:40%;" href="/edit-advert/?advert_id=' + str(
                    adv.advert_id) + '"<i class="fa fa-pencil "></i> ' + '</a>'

                delete = '<a id="' + str(
                    adv.advert_id) + '" onclick="delete_user_detail(this.id)" style="text-align: center;letter-spacing: 5px;width:15%;"<i class="fa fa-trash "  ></i></a>'

                ##                mark = '<input type="checkbox" class="checkboxes" value="1" />'

                # if adv.status == '1':
                #     status="Active"

                # if adv.status == '0':
                #     status="Inactive"

                if adv.area == None:
                    area = '--'
                else:
                    area = adv.area
                map_id = AdvertSubscriptionMap.objects.get(advert_id=str(adv.advert_id))
                business_obj = Business.objects.get(business_id=str(map_id.business_id))
                temp_obj = {
                    'advert_id': adv.advert_id,
                    'advert_name': adv.advert_name,
                    'category': adv.category_id.category_name,
                    'subscription': business_obj.service_rate_card_id.service_name,
                    'start_date': business_obj.start_date,
                    'end_date': business_obj.end_date,
                    'area': area,
                    'action': detail + edit + delete,
                    # 'status':status
                }
                adv_list.append(temp_obj)
            if adv.status == '0':

                active = '<a class="col-md-2" id="' + str(
                    adv.advert_id) + '" onclick="active_service(this.id);" style="text-align: center;letter-spacing: 5px;width:15%;margin-left: 20px !important;" title="Activate" class="edit" data-toggle="modal" href="#edit_subscription"><i class="fa fa-repeat"></i></a>'

                ##                mark = '<input type="checkbox" class="checkboxes" value="1" />'

                if adv.area == None:
                    area = '--'
                else:
                    area = adv.area

                if adv.status == '1':
                    status = "Active"

                if adv.status == '0':
                    status = "Inactive"

                temp_obj = {
                    'advert_id': adv.advert_id,
                    'advert_name': adv.advert_name,
                    'category': adv.category_id.category_name,
                    'subscription': '--',
                    'start_date': '--',
                    'end_date': '--',
                    'area': area,
                    ##                    'mark':mark,
                    'action': active,
                    'status': status
                }
                adv_list.append(temp_obj)

        data = {'data': adv_list}
    except Exception, e:
        print 'Exception : ', e
        data = {'data': 'none'}
    print '=========dat===========', data
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def delete_advert(request):
    try:
        print "ADV_ID", request.POST.get('advert_id')
        adv_obj = Advert.objects.get(advert_id=request.POST.get('advert_id'))
        adv_obj.status = '0'
        adv_obj.save()
        advert_inactive_mail(adv_obj)
        delete_add_sms(adv_obj)

        data = {'message': 'Advert Inactivated Successfully', 'success': 'true'}
    except IntegrityError as e:
        print e
    except Exception, e:
        print e
    print "Final Data: ", data
    return HttpResponse(json.dumps(data), content_type='application/json')


def delete_add_sms(advert_obj):
    
    authkey = "118994AIG5vJOpg157989f23"
    # user_obj = Supplier.objects.get(supplier_id=su_id)
 #    contact_no = user_obj.contact_no
 #    print '---------contact_no------',contact_no

    mobiles = "+919403884595"
    message = "Advert \t" +str(advert_obj.advert_name) + "\t for your business \t"+ str(advert_obj.supplier_id.business_name) +"\t under category \t"+str(advert_obj.category_id.category_name)+"\t has been deactivated  successfully on your profile with CityHoopla"
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
    print "sagar"


@csrf_exempt
def active_advert(request):
    # pdb.set_trace()
    try:
        adv_obj = Advert.objects.get(advert_id=request.POST.get('advert_id'))
        adv_obj.status = '1'
        adv_obj.save()
        advert_active_mail(adv_obj)

        data = {'message': 'Advert activated Successfully', 'success': 'true'}

    except IntegrityError as e:
        print e
    except Exception, e:
        print e
    print "Final Data: ", data
    return HttpResponse(json.dumps(data), content_type='application/json')


def advert_active_mail(adv_obj):
    gmail_user = "cityhoopla2016"
    gmail_pwd = "cityhoopla@2016"
    FROM = 'CityHoopla Admin <cityhoopla2016@gmail.com>'
    TO = ['cityhoopla2016@gmail.com']
    # pdb.set_trace()
    try:
        TEXT = "Hi Admin,\nAdvert " + str(adv_obj.advert_name) + " " + "for Subscriber " + str(
            adv_obj.supplier_id.contact_person) + " " + "has been added successfully.\nTo view complete details visit portal and follow - Customers -> Subscribers -> Adverts\n\n Thank You," + '\n' + "CityHoopla Team"
        SUBJECT = "Advert Activated Successfully!"
        # server = smtplib.SMTP_SSL()
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()

        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException, e:
        print e
    return 1


def get_category(request):
    ##    pdb.set_trace()
    cat_list = []
    try:
        category = Category.objects.filter(category_status='1').order_by('category_name')
        for cat in category:
            if cat.category_name !="Ticket Resell":
                cat_list.append(
                    {'category_id': cat.category_id, 'category': cat.category_name})

    except Exception, e:
        print 'Exception ', e
    return cat_list


# TO GET THE CURRENCY
def get_currency(request):
    ##    pdb.set_trace()
    currency_list = []
    try:
        currency = Currency.objects.filter(status='1')
        for cur in currency:
            currency_list.append(
                {'currency_id': cur.currency_id, 'currency': cur.currency})

    except Exception, e:
        print 'Exception ', e
    return currency_list

def edit_advert(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        advert_id = request.GET.get('advert_id')
        tax_list = Tax.objects.all()
        temp_data = ''
        cat_amenities = []

        advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)
        business_obj = Business.objects.get(business_id=str(advert_sub_obj.business_id))
        supplier_obj = Supplier.objects.get(supplier_id=str(advert_sub_obj.advert_id.supplier_id))
        supplier_name =supplier_obj.business_name
        city_place_id = str(supplier_obj.city_place_id)
        telephone_rate_card = TelephoneEnquiryRateCard.objects.filter(city_place_id=city_place_id)
        business_data = {
            'business_id': str(business_obj.business_id),
            'service_rate_card_duration': int(business_obj.duration),
            'start_date': str(business_obj.start_date),
            'end_date': str(business_obj.end_date)
        }

        supplier_id = str(advert_sub_obj.advert_id.supplier_id)
        category_lvl1_list = []
        category_lvl2_list = []
        category_lvl3_list = []
        category_lvl4_list = []
        category_lvl5_list = []
        cat_id = ''
        cat_lvl = ''

        if business_obj.category:
            business_data['category_id'] = business_obj.category.category_id
            cat_id = business_obj.category.category_id
            cat_lvl = ''

        if business_obj.category_level_1:
            business_data['category_level_1'] = business_obj.category_level_1.category_id
            cat_id = business_obj.category_level_1.category_id
            cat_lvl = '1'
            category_lvl1_list = CategoryLevel1.objects.filter(
                parent_category_id=str(business_obj.category.category_id))

        if business_obj.category_level_2:
            business_data['category_level_2'] = business_obj.category_level_2.category_id
            cat_id = business_obj.category_level_2.category_id
            cat_lvl = '2'
            category_lvl2_list = CategoryLevel2.objects.filter(
                parent_category_id=str(business_obj.category_level_1.category_id))

        if business_obj.category_level_3:
            cat_id = business_obj.category_level_3.category_id
            cat_lvl = '3'
            business_data['category_level_3'] = business_obj.category_level_3.category_id
            category_lvl3_list = CategoryLevel3.objects.filter(
                parent_category_id=str(business_obj.category_level_2.category_id))

        if business_obj.category_level_4:
            business_data['category_level_4'] = business_obj.category_level_4.category_id
            cat_id = business_obj.category_level_4.category_id
            cat_lvl = '4'
            category_lvl4_list = CategoryLevel4.objects.filter(
                parent_category_id=str(business_obj.category_level_3.category_id))

        if business_obj.category_level_5:
            business_data['category_level_5'] = business_obj.category_level_5.category_id
            cat_id = business_obj.category_level_5.category_id
            cat_lvl = '5'
            category_lvl5_list = CategoryLevel5.objects.filter(
                parent_category_id=str(business_obj.category_level_4.category_id))

        if business_obj.category:
            category_id = str(business_obj.category.category_id)
        if business_obj.category_level_1:
            category_level_1 = str(business_obj.category_level_1.category_id)
        if business_obj.category_level_2:
            category_level_2 = str(business_obj.category_level_2.category_id)
        if business_obj.category_level_3:
            category_level_3 = str(business_obj.category_level_3.category_id)
        if business_obj.category_level_4:
            category_level_4 = str(business_obj.category_level_4.category_id)
        if business_obj.category_level_5:
            category_level_5 = str(business_obj.category_level_5.category_id)


        cl1 = ''
        if business_obj.category:
            amenity_list = CategorywiseAmenity.objects.filter(status="1",category=category_id)
            for ck in amenity_list:
                cl1= ck.category_level_1

            if cl1:
                if business_obj.category and business_obj.category_level_1: 
                    amenity_list = CategorywiseAmenity.objects.filter(status="1",category=category_id,category_level_1=category_level_1)

                if business_obj.category and business_obj.category_level_1 and business_obj.category_level_2:
                    amenity_list = CategorywiseAmenity.objects.filter(status="1",category=category_id,category_level_1=category_level_1,category_level_2=category_level_2)

                if business_obj.category and business_obj.category_level_1 and business_obj.category_level_2 and business_obj.category_level_3:
                    amenity_list = CategorywiseAmenity.objects.filter(status="1",category=category_id,category_level_1=category_level_1,category_level_3=category_level_3)

                if business_obj.category and business_obj.category_level_1 and business_obj.category_level_2 and business_obj.category_level_3 and business_obj.category_level_4:
                    amenity_list = CategorywiseAmenity.objects.filter(status="1",category=category_id,category_level_1=category_level_1,category_level_3=category_level_3,category_level_4=category_level_4)

                if business_obj.category and business_obj.category_level_1 and business_obj.category_level_2 and business_obj.category_level_3 and business_obj.category_level_4 and business_obj.category_level_5:
                    amenity_list = CategorywiseAmenity.objects.filter(status="1",category=category_id,category_level_1=category_level_1,category_level_3=category_level_3,category_level_4=category_level_4,category_level_5=category_level_5)

        
                ameninty_checked = "false"
                for amnenity in amenity_list:
                    try:
                        amenities_obj = Amenities.objects.get(advert_id=advert_id,categorywise_amenity_id =str(amnenity.categorywise_amenity_id) )
                        ameninty_checked = "true"
                    except:
                        ameninty_checked = "false"
                        pass                
                    temp_data ={
                    'id':str(amnenity.categorywise_amenity_id),
                    'amenity':str(amnenity.amenity),
                    'checkced':ameninty_checked
                    }
                    cat_amenities.append(temp_data)
                print "cat_amenities",cat_amenities

            else:
                amenity_list = CategorywiseAmenity.objects.filter(status="1",category=category_id)
                ameninty_checked = "false"
                for amnenity in amenity_list:
                    try:
                        amenities_obj = Amenities.objects.get(advert_id=advert_id,categorywise_amenity_id =str(amnenity.categorywise_amenity_id) )
                        ameninty_checked = "true"
                    except:
                        ameninty_checked = "false"
                        pass                
                    temp_data ={
                    'id':str(amnenity.categorywise_amenity_id),
                    'amenity':str(amnenity.amenity),
                    'checkced':ameninty_checked
                    }
                    cat_amenities.append(temp_data)

        rate_obj = CategoryWiseRateCard.objects.get(
                        service_name='Subscription',
                        category_id=cat_id,
                        category_level=cat_lvl,
                        rate_card_status = 1,
                        city_place_id = city_place_id
                    )

        if business_obj.duration == '3':
            basic_amount = float(rate_obj.cost_for_3_days)
        if business_obj.duration == '7':
            basic_amount = float(rate_obj.cost_for_7_days)
        if business_obj.duration == '30':
            basic_amount = float(rate_obj.cost_for_30_days)
        if business_obj.duration == '90':
            basic_amount = float(rate_obj.cost_for_90_days)
        if business_obj.duration == '180':
            basic_amount = float(rate_obj.cost_for_180_days)
        amount_1 = 0
        amount_2 = 0
        amount_3 = 0
        amount_4 = 0
        amount_5 = 0

        tel_amount_1 = 0
        tel_amount_2 = 0
        tel_amount_3 = 0
        tel_amount_4 = 0
        tel_amount_5 = 0
        tel_amount_6 = 0

        premium_service_list = []
        try:
            premium_service_obj = PremiumService.objects.filter(business_id=str(business_obj.business_id))
            for premium_service in premium_service_obj:

                if premium_service.premium_service_name == 'No.1 Listing':
                    rate_obj = CategoryWiseRateCard.objects.get(
                        service_name=premium_service.premium_service_name,
                        category_id=str(premium_service.category_id),
                        category_level=str(premium_service.category_level),
                        rate_card_status = 1
                    )
                    if int(premium_service.no_of_days) == 3:
                        amount_1 = float(rate_obj.cost_for_3_days)
                    if int(premium_service.no_of_days) == 7:
                        amount_1 = float(rate_obj.cost_for_7_days)
                    if int(premium_service.no_of_days) == 30:
                        amount_1 = float(rate_obj.cost_for_30_days)
                    if int(premium_service.no_of_days) == 90:
                        amount_1 = float(rate_obj.cost_for_90_days)
                    if int(premium_service.no_of_days) == 180:
                        amount_1 = float(rate_obj.cost_for_180_days)

                if premium_service.premium_service_name == 'No.2 Listing':
                    rate_obj = CategoryWiseRateCard.objects.get(
                        service_name=premium_service.premium_service_name,
                        category_id=premium_service.category_id,
                        category_level=premium_service.category_level,
                        rate_card_status = 1
                    )
                    if int(premium_service.no_of_days) == 3:
                        amount_2 = float(rate_obj.cost_for_3_days)
                    if int(premium_service.no_of_days) == 7:
                        amount_2 = float(rate_obj.cost_for_7_days)
                    if int(premium_service.no_of_days) == 30:
                        amount_2 = float(rate_obj.cost_for_30_days)
                    if int(premium_service.no_of_days) == 90:
                        amount_2 = float(rate_obj.cost_for_90_days)
                    if int(premium_service.no_of_days) == 180:
                        amount_2 = float(rate_obj.cost_for_180_days)

                if premium_service.premium_service_name == 'No.3 Listing':
                    rate_obj = CategoryWiseRateCard.objects.get(
                        service_name=premium_service.premium_service_name,
                        category_id=premium_service.category_id,
                        category_level=premium_service.category_level,
                        rate_card_status = 1
                    )
                    if int(premium_service.no_of_days) == 3:
                        amount_3 = float(rate_obj.cost_for_3_days)
                    if int(premium_service.no_of_days) == 7:
                        amount_3 = float(rate_obj.cost_for_7_days)
                    if int(premium_service.no_of_days) == 30:
                        amount_3 = float(rate_obj.cost_for_30_days)
                    if int(premium_service.no_of_days) == 90:
                        amount_3 = float(rate_obj.cost_for_90_days)
                    if int(premium_service.no_of_days) == 180:
                        amount_3 = float(rate_obj.cost_for_180_days)

                if premium_service.premium_service_name == 'Advert Slider':
                    rate_obj = RateCard.objects.get(service_name=premium_service.premium_service_name,
                                                    city_place_id=premium_service.city_place_id,
                                                    rate_card_status = 1
                                                    )
                    if int(premium_service.no_of_days) == 3:
                        amount_4 = float(rate_obj.cost_for_3_days)
                    if int(premium_service.no_of_days) == 7:
                        amount_4 = float(rate_obj.cost_for_7_days)
                    if int(premium_service.no_of_days) == 30:
                        amount_4 = float(rate_obj.cost_for_30_days)
                    if int(premium_service.no_of_days) == 90:
                        amount_4 = float(rate_obj.cost_for_90_days)
                    if int(premium_service.no_of_days) == 180:
                        amount_4 = float(rate_obj.cost_for_180_days)

                if premium_service.premium_service_name == 'Top Advert':
                    rate_obj = RateCard.objects.get(service_name=premium_service.premium_service_name,
                                                    city_place_id=premium_service.city_place_id,
                                                    rate_card_status = 1
                                                    )
                    if int(premium_service.no_of_days) == 3:
                        amount_5 = float(rate_obj.cost_for_3_days)
                    if int(premium_service.no_of_days) == 7:
                        amount_5 = float(rate_obj.cost_for_7_days)
                    if int(premium_service.no_of_days) == 30:
                        amount_5 = float(rate_obj.cost_for_30_days)
                    if int(premium_service.no_of_days) == 90:
                        amount_5 = float(rate_obj.cost_for_90_days)
                    if int(premium_service.no_of_days) == 180:
                        amount_5 = float(rate_obj.cost_for_180_days)
        except Exception as e:
            pass

            premium_service_data = {
                'premium_service_name': premium_service.premium_service_name,
                'premium_service_duration': premium_service.no_of_days,
                'premium_service_start_date': premium_service.start_date,
                'premium_service_end_date': premium_service.end_date
            }
            premium_service_list.append(premium_service_data)



        try:
            enquiry_service_obj = EnquiryService.objects.get(business_id=str(business_obj.business_id))
            enquiry_service_data = {
                'enquiry_service_name': enquiry_service_obj.enquiry_service_name,
                'enquiry_service_duration': enquiry_service_obj.no_of_days,
                'enquiry_service_start_date': enquiry_service_obj.start_date,
                'enquiry_service_end_date': enquiry_service_obj.end_date
            }
            if enquiry_service_obj.enquiry_service_name == 'Platinum':
                rate_obj = TelephoneEnquiryRateCard.objects.get(
                    service_name=enquiry_service_obj.enquiry_service_name,
                    city_place_id=enquiry_service_obj.city_place_id
                )
                if enquiry_service_obj.no_of_days == '3':
                    tel_amount_1 = float(rate_obj.cost_for_3_days)
                if enquiry_service_obj.no_of_days == '7':
                    tel_amount_1 = float(rate_obj.cost_for_7_days)
                if enquiry_service_obj.no_of_days == '30':
                    tel_amount_1 = float(rate_obj.cost_for_30_days)
                if enquiry_service_obj.no_of_days == '90':
                    tel_amount_1 = float(rate_obj.cost_for_90_days)
                if enquiry_service_obj.no_of_days == '180':
                    tel_amount_1 = float(rate_obj.cost_for_180_days)
            if enquiry_service_obj.enquiry_service_name == 'Diamond':
                rate_obj = TelephoneEnquiryRateCard.objects.get(
                    service_name=enquiry_service_obj.enquiry_service_name,
                    city_place_id=enquiry_service_obj.city_place_id
                )
                if enquiry_service_obj.no_of_days == '3':
                    tel_amount_2 = float(rate_obj.cost_for_3_days)
                if enquiry_service_obj.no_of_days == '7':
                    tel_amount_2 = float(rate_obj.cost_for_7_days)
                if enquiry_service_obj.no_of_days == '30':
                    tel_amount_2 = float(rate_obj.cost_for_30_days)
                if enquiry_service_obj.no_of_days == '90':
                    tel_amount_2 = float(rate_obj.cost_for_90_days)
                if enquiry_service_obj.no_of_days == '180':
                    tel_amount_2 = float(rate_obj.cost_for_180_days)
            if enquiry_service_obj.enquiry_service_name == 'Gold':
                rate_obj = TelephoneEnquiryRateCard.objects.get(
                    service_name=enquiry_service_obj.enquiry_service_name,
                    city_place_id=enquiry_service_obj.city_place_id
                )
                if enquiry_service_obj.no_of_days == '3':
                    tel_amount_3 = float(rate_obj.cost_for_3_days)
                if enquiry_service_obj.no_of_days == '7':
                    tel_amount_3 = float(rate_obj.cost_for_7_days)
                if enquiry_service_obj.no_of_days == '30':
                    tel_amount_3 = float(rate_obj.cost_for_30_days)
                if enquiry_service_obj.no_of_days == '90':
                    tel_amount_3 = float(rate_obj.cost_for_90_days)
                if enquiry_service_obj.no_of_days == '180':
                    tel_amount_3 = float(rate_obj.cost_for_180_days)
            if enquiry_service_obj.enquiry_service_name == 'Silver':
                rate_obj = TelephoneEnquiryRateCard.objects.get(
                    service_name=enquiry_service_obj.enquiry_service_name,
                    city_place_id=enquiry_service_obj.city_place_id
                )
                if enquiry_service_obj.no_of_days == '3':
                    tel_amount_4 = float(rate_obj.cost_for_3_days)
                if enquiry_service_obj.no_of_days == '7':
                    tel_amount_4 = float(rate_obj.cost_for_7_days)
                if enquiry_service_obj.no_of_days == '30':
                    tel_amount_4 = float(rate_obj.cost_for_30_days)
                if enquiry_service_obj.no_of_days == '90':
                    tel_amount_4 = float(rate_obj.cost_for_90_days)
                if enquiry_service_obj.no_of_days == '180':
                    tel_amount_4 = float(rate_obj.cost_for_180_days)
            if enquiry_service_obj.enquiry_service_name == 'Bronze':
                rate_obj = TelephoneEnquiryRateCard.objects.get(
                    service_name=enquiry_service_obj.enquiry_service_name,
                    city_place_id=enquiry_service_obj.city_place_id
                )
                if enquiry_service_obj.no_of_days == '3':
                    tel_amount_5 = float(rate_obj.cost_for_3_days)
                if enquiry_service_obj.no_of_days == '7':
                    tel_amount_5 = float(rate_obj.cost_for_7_days)
                if enquiry_service_obj.no_of_days == '30':
                    tel_amount_5 = float(rate_obj.cost_for_30_days)
                if enquiry_service_obj.no_of_days == '90':
                    tel_amount_5 = float(rate_obj.cost_for_90_days)
                if enquiry_service_obj.no_of_days == '180':
                    tel_amount_5 = float(rate_obj.cost_for_180_days)
            if enquiry_service_obj.enquiry_service_name == 'Value':
                rate_obj = TelephoneEnquiryRateCard.objects.get(
                    service_name=enquiry_service_obj.enquiry_service_name,
                    city_place_id=enquiry_service_obj.city_place_id
                )
                if enquiry_service_obj.no_of_days == '3':
                    tel_amount_6 = float(rate_obj.cost_for_3_days)
                if enquiry_service_obj.no_of_days == '7':
                    tel_amount_6 = float(rate_obj.cost_for_7_days)
                if enquiry_service_obj.no_of_days == '30':
                    tel_amount_6 = float(rate_obj.cost_for_30_days)
                if enquiry_service_obj.no_of_days == '90':
                    tel_amount_6 = float(rate_obj.cost_for_90_days)
                if enquiry_service_obj.no_of_days == '180':
                    tel_amount_6 = float(rate_obj.cost_for_180_days)
        except Exception as e:
            print e
            enquiry_service_data = {}
            pass

        total_amount = basic_amount + amount_1 + amount_2 + amount_3 + amount_4 + amount_5
        total_amount = total_amount + tel_amount_1 + tel_amount_2 + tel_amount_3 + tel_amount_4 + tel_amount_5 + tel_amount_6

        advert_service_list = []
        advert_service_lists = []

        rate_card_obj = CategoryWiseRateCard.objects.filter(
            rate_card_status='1',
            category_id=cat_id,
            category_level=cat_lvl,
            city_place_id=city_place_id
        ).exclude(service_name='Subscription')
        advert_service_lists.extend(rate_card_obj)
        rate_card_obj = RateCard.objects.filter(
            rate_card_status='1',
            city_place_id=city_place_id
        )
        advert_service_lists.extend(rate_card_obj)

        for advert_service in advert_service_lists:
            print advert_service
            try:
                premium_obj = PremiumService.objects.get(
                    premium_service_name=advert_service.service_name,
                    business_id=str(business_obj.business_id),
                    category_id=cat_id,
                    category_level=cat_lvl,
                )
                advert_service_data = {
                    'service_name': advert_service.service_name,
                    'advert_rate_card_id': advert_service.rate_card_id,
                    'checked': 'true',
                    'service_duration': int(premium_obj.no_of_days),
                    'service_start_date': premium_obj.start_date,
                    'service_end_date': premium_obj.end_date
                }
                advert_service_list.append(advert_service_data)
            except Exception as e:
                print e
                advert_service_data = {
                    'service_name': advert_service.service_name,
                    'advert_rate_card_id': advert_service.rate_card_id,
                    'checked': 'false',
                    'service_duration': 0,
                    'service_start_date': '',
                    'service_end_date': ''
                }
                advert_service_list.append(advert_service_data)
                pass
        print advert_service_list
        try:
            payment_obj = PaymentDetail.objects.get(business_id=str(business_obj.business_id))
            payment_details = {
                'payment_mode': payment_obj.payment_mode,
                'paid_amount': round(float(payment_obj.paid_amount), 2),
                'payable_amount': round(float(payment_obj.payable_amount), 2),
                'total_amount': round(float(payment_obj.total_amount), 2),
                'tax_type': payment_obj.tax_type.tax_rate,
                'note': payment_obj.note,
                'bank_name': payment_obj.bank_name,
                'branch_name': payment_obj.branch_name,
                'cheque_number': payment_obj.cheque_number
            }
            # print payment_details
        except Exception:
            payment_details = {
                'payment_mode': '',
                'paid_amount': '',
                'payable_amount': '',
                'total_amount': '',
                'tax_type': '',
                'note': '',
                'bank_name': '',
                'branch_name': '',
                'cheque_number': ''
            }
            pass

        advert_obj = Advert.objects.get(advert_id=advert_id)

        if advert_obj.category_level_1:
            category_l1_list = CategoryLevel1.objects.filter(parent_category_id=str(advert_obj.category_id.category_id))
        else:
            category_l1_list = []

        if advert_obj.category_level_2:
            category_l2_list = CategoryLevel2.objects.filter(
                parent_category_id=str(advert_obj.category_level_1.category_id))
        else:
            category_l2_list = []

        if advert_obj.category_level_3:
            category_l3_list = CategoryLevel3.objects.filter(
                parent_category_id=str(advert_obj.category_level_2.category_id))
        else:
            category_l3_list = []

        if advert_obj.category_level_4:
            category_l4_list = CategoryLevel4.objects.filter(
                parent_category_id=str(advert_obj.category_level_3.category_id))
        else:
            category_l4_list = []

        if advert_obj.category_level_5:
            category_l5_list = CategoryLevel5.objects.filter(
                parent_category_id=str(advert_obj.category_level_4.category_id))
        else:
            category_l5_list = []


        if advert_obj.any_other_details:
            any_other_details =advert_obj.any_other_details
        else:
            any_other_details = ""

        advert_data = {
            'category_id': advert_obj.category_id.category_id,
            'category_level_1': advert_obj.category_level_1.category_id if advert_obj.category_level_1 else '',
            'category_level_2': advert_obj.category_level_2.category_id if advert_obj.category_level_2 else '',
            'category_level_3': advert_obj.category_level_3.category_id if advert_obj.category_level_3 else '',
            'category_level_4': advert_obj.category_level_4.category_id if advert_obj.category_level_4 else '',
            'category_level_5': advert_obj.category_level_5.category_id if advert_obj.category_level_5 else '',
            'advert_name': advert_obj.advert_name,'city_place_id':city_place_id,
            'contact_name': advert_obj.contact_name,
            'contact_no': advert_obj.contact_no,
            'latitude': advert_obj.latitude,
            'longitude': advert_obj.longitude,
            'short_description': advert_obj.short_description,
            'product_description': advert_obj.product_description,
            'discount_description': advert_obj.discount_description,
            'currency': advert_obj.currency,
            'display_image': SERVER_URL + advert_obj.display_image.url if advert_obj.display_image else '',
            'address_line_1': advert_obj.address_line_1,
            'address_line_2': advert_obj.address_line_2,
            'country_id': advert_obj.country_id.country_id,
            'currency': advert_obj.currency,
            'state_id': advert_obj.state_id.state_id,
            'city_place_id': advert_obj.city_place_id.city_place_id,
            'pincode_id': advert_obj.pincode_id.pincode_id,
            'area': advert_obj.area,
            'landmark': advert_obj.landmark,
            'email_primary': advert_obj.email_primary,
            'property_market_rate': advert_obj.property_market_rate,
            'possesion_status': advert_obj.possesion_status,
            'other_projects': advert_obj.other_projects,
            'date_of_delivery': advert_obj.date_of_delivery,
            'any_other_details': any_other_details,
            'speciality': advert_obj.speciality,
            'happy_hour_offer': advert_obj.happy_hour_offer,
            'course_duration': advert_obj.course_duration,
            'affilated_to': advert_obj.affilated_to,
            'image_video_space_used': advert_obj.image_video_space_used,
            'facility': advert_obj.facility,
            'keywords': advert_obj.keywords,
            'distance_frm_railway_station': advert_obj.distance_frm_railway_station,
            'distance_frm_airport': advert_obj.distance_frm_railway_airport,
            'other_amenity':advert_obj.other_amenity
        }

        product_obj = Product.objects.filter(advert_id=advert_id)
        product_list = []
        if product_obj:
            for products in product_obj:
                product_data = {
                    "product_id":products.product_id,
                    "product_name": products.product_name,
                    "product_price": products.product_price
                }
                product_list.append(product_data)

        time_list = []
        time_obj = WorkingHours.objects.filter(advert_id=advert_id)
        if time_obj:
            for time in time_obj:
                time_data = {
                    "day": time.day,
                    "start_time": time.start_time,
                    "end_time": time.end_time,
                }
                time_list.append(time_data)


        nr_attr_obj = NearByAttraction.objects.filter(advert_id=advert_id)
        nr_attr_list = []
        if nr_attr_obj:
            for nr_attr in nr_attr_obj:
                nr_attr_data = {
                    "attraction": nr_attr.attraction
                }
                nr_attr_list.append(nr_attr_data)

        nr_shop_obj = NearestShopping.objects.filter(advert_id=advert_id)
        nr_shop_list = []
        if nr_shop_obj:
            for nr_shop in nr_shop_obj:
                nr_shop_data = {
                    "shop_name": nr_shop.shop_name,
                    "distance_frm_property": nr_shop.distance_frm_property
                }
                nr_shop_list.append(nr_shop_data)

        nr_shcl_obj = NearestSchool.objects.filter(advert_id=advert_id)
        nr_shcl_list = []
        if nr_shcl_obj:
            for schools in nr_shcl_obj:
                schools_data = {
                    "school_name": schools.school_name,
                    "distance_frm_property": schools.distance_frm_property
                }
                nr_shcl_list.append(schools_data)

        nr_hosp_obj = NearestHospital.objects.filter(advert_id=advert_id)
        nr_hosp_list = []
        if nr_hosp_obj:
            for hospitals in nr_hosp_obj:
                hospital_data = {
                    "hospital_name": hospitals.hospital_name,
                    "distance_frm_property": hospitals.distance_frm_property
                }
                nr_hosp_list.append(hospital_data)

        data = {'tax_list': tax_list, 'advert_service_list': advert_service_list,
                'username': request.session['login_user'], 'category_list':get_city_category(city_place_id),
                'country_list': get_country(request), 'phone_category': get_phone_category(request),
                'state_list': get_states(request), 'business_data': business_data,
                'product_list': product_list, 'time_list': time_list,
                'total_amount': float(total_amount), 'basic_amount': basic_amount, 'amount_1': amount_1,
                'amount_2': amount_2, 'advert_data': advert_data, 'advert_id': advert_id,
                'amount_3': amount_3, 'amount_4': amount_4, 'amount_5': amount_5, 'payment_details': payment_details,
                'tel_amount_1': tel_amount_1, 'tel_amount_2': tel_amount_2, 'tel_amount_3': tel_amount_3,
                'tel_amount_4': tel_amount_4, 'tel_amount_5': tel_amount_5, 'tel_amount_6': tel_amount_6,
                'category_lvl1_list': category_lvl1_list,'supplier_id':supplier_id,
                'category_lvl2_list': category_lvl2_list,'city_place_id':city_place_id,
                'category_lvl3_list': category_lvl3_list,'supplier_name':supplier_name,
                'category_lvl4_list': category_lvl4_list,'title' :advert_obj.title,
                'category_lvl5_list': category_lvl5_list,'cat_amenities':cat_amenities,
                'cat_id': cat_id, 'cat_lvl': cat_lvl, 'telephone_rate_card': telephone_rate_card,
                'premium_service_list': premium_service_list,'enquiry_service_data':enquiry_service_data,
                'nr_attr_list': nr_attr_list,'advert_id':advert_id,
                'nr_shop_list': nr_shop_list, 'nr_shcl_list': nr_shcl_list, 'nr_hosp_list': nr_hosp_list,
                'category_l1_list': category_l1_list, 'category_l2_list': category_l2_list,
                'category_l3_list': category_l3_list,
                'category_l4_list': category_l4_list, 'category_l5_list': category_l5_list
                }
        return render(request, 'Admin/edit_advert.html', data)

def get_advert_images(request):
    advert_id = request.GET.get('advert_id')
    image_list = []
    advert_image = AdvertImage.objects.filter(advert_id=advert_id)
    for images in advert_image:
        image_path = images.advert_image.url
        filesize = os.stat('/home/ec2-user/DigiSpace/' + images.advert_image.url).st_size
        image_size = round(filesize,2) #/ float(1024)
        image_path = image_path.split('/')
        image_name = image_path[-1]
        image_url = SERVER_URL + images.advert_image.url
        image_id = images.advert_image_id
        advert_image_data = {
            "image_url": image_url,
            "image_size": image_size,
            "image_name": image_name,
            "image_id": image_id,
            "image_thumbnail": '/home/ec2-user/DigiSpace/' + images.advert_image.url
        }
        image_list.append(advert_image_data)
    data = {'data': 'true','image_list':image_list}
    return HttpResponse(json.dumps(data), content_type='application/json')

def get_advert_videos(request):
    advert_id = request.GET.get('advert_id')
    image_list = []
    advert_image = Advert_Video.objects.filter(advert_id=advert_id)
    for images in advert_image:
        image_path = images.advert_video_name.url
        filesize = os.stat('/home/ec2-user/DigiSpace/' + images.advert_video_name.url).st_size
        image_size = round(filesize,2) #/ float(1024)
        image_path = image_path.split('/')
        image_name = image_path[-1]
        image_url = SERVER_URL + images.advert_video_name.url
        image_id = images.advert_video_id
        advert_image_data = {
            "image_url": image_url,
            "image_size": image_size,
            "image_name": image_name,
            "image_id": image_id,
            "image_thumbnail": '/home/ec2-user/DigiSpace/' + images.advert_video_name.url
        }
        image_list.append(advert_image_data)
    data = {'data': 'true','image_list':image_list}
    return HttpResponse(json.dumps(data), content_type='application/json')

def get_city_category(city_place_id):
    ##    pdb.set_trace()
    cat_list = []
    try:
        cat_city_map = CategoryCityMap.objects.filter(city_place_id=city_place_id)
        for cat in cat_city_map:
            category = Category.objects.get(category_id=str(cat.category_id))
            if category.category_name != "Ticket Resell":
                cat_list.append(
                    {'category_id': category.category_id, 'category': category.category_name})
    except Exception, e:
        print 'Exception ', e
    return cat_list


@csrf_exempt
def update_advert(request):
    # pdb.set_trace()
    if not request.user.is_authenticated():
        data = {'success':'Expired'}

    else:    
        print "IN SAVE ADVERT METHOD", #request.POST
        try:
            if request.method == "POST":
                print '===request========', request.POST.get('supplier_id')
                advert_id = request.POST.get('advert_id')
                advert_obj = Advert.objects.get(advert_id = request.POST.get('advert_id'))

                advert_obj.supplier_id=Supplier.objects.get(supplier_id=request.POST.get('supplier_id'))
                advert_obj.category_id=Category.objects.get(category_id=request.POST.get('categ'))
                advert_obj.advert_name=request.POST.get('advert_title')
                advert_obj.contact_name=request.POST.get('contact_name')
                advert_obj.contact_no=request.POST.get('phone_no')
                advert_obj.website=request.POST.get('website')
                advert_obj.latitude=request.POST.get('lat')
                advert_obj.longitude=request.POST.get('lng')
                advert_obj.short_description=request.POST.get('short_discription')
                advert_obj.product_description=request.POST.get('product_discription')
                advert_obj.currency=request.POST.get('currency')
                advert_obj.country_id=Country.objects.get(country_id=request.POST.get('country')) if request.POST.get(
                    'country') else None
                # product_price=request.POST.get('product_price'),
                advert_obj.discount_description=request.POST.get('discount_discription')
                advert_obj.email_primary=request.POST.get('email_primary')
                advert_obj.email_secondary=request.POST.get('email_secondary')
                advert_obj.address_line_1=request.POST.get('address_line1')
                advert_obj.address_line_2=request.POST.get('address_line2')
                advert_obj.area=request.POST.get('area')
                advert_obj.landmark=request.POST.get('landmark')
                advert_obj.state_id=State.objects.get(state_id=request.POST.get('statec')) if request.POST.get('statec') else None
                advert_obj.city_place_id=City_Place.objects.get(city_place_id=request.POST.get('city')) if request.POST.get(
                    'city') else None
                advert_obj.pincode_id=Pincode.objects.get(pincode_id=request.POST.get('pincode')) if request.POST.get(
                    'pincode') else None
                advert_obj.property_market_rate=request.POST.get('pro_mark_rate')
                advert_obj.possesion_status=request.POST.get('possesion_status')
                advert_obj.date_of_delivery=request.POST.get('date_of_delivery')
                advert_obj.other_projects=request.POST.get('other_projects')
                advert_obj.distance_frm_railway_station=request.POST.get('dis_rail_stat')
                advert_obj.distance_frm_railway_airport=request.POST.get('dis_airport')
                advert_obj.speciality=request.POST.get('speciality')
                advert_obj.affilated_to=request.POST.get('affilated')
                advert_obj.course_duration=request.POST.get('course_duration')
                advert_obj.happy_hour_offer=request.POST.get('happy_hour_offer')
                advert_obj.facility=request.POST.get('facility')
                advert_obj.keywords=request.POST.get('advert_keywords')
                advert_obj.image_video_space_used=request.POST.get('image_and_video_space')
                advert_obj.other_amenity=request.POST.get('any_other_amenity')
                advert_obj.title =request.POST.get('title')
                advert_obj.save()
                print "advert updated"

                if request.POST.get('any_other_details'):
                    advert_obj.any_other_details = request.POST.get('any_other_details')
                    advert_obj.save()

                print "advert updated"

                subcat_list = request.POST.get('subcat_list')
                print subcat_list
                subcat_lvl = 1
                # String to list
                subcat_list = subcat_list.split(',')
                if subcat_list != '':
                    for subcat in subcat_list:
                        if subcat:
                            print 'Subcat: ', subcat, subcat_lvl
                            if subcat_lvl == 1:
                                advert_obj.category_level_1 = CategoryLevel1.objects.get(category_id=subcat)
                                advert_obj.save()
                            if subcat_lvl == 2:
                                advert_obj.category_level_2 = CategoryLevel2.objects.get(category_id=subcat)
                                advert_obj.save()
                            if subcat_lvl == 3:
                                advert_obj.category_level_3 = CategoryLevel3.objects.get(category_id=subcat)
                                advert_obj.save()
                            if subcat_lvl == 4:
                                advert_obj.category_level_4 = CategoryLevel4.objects.get(category_id=subcat)
                                advert_obj.save()
                            if subcat_lvl == 5:
                                advert_obj.category_level_5 = CategoryLevel5.objects.get(category_id=subcat)
                                advert_obj.save()
                            print 'Advert Subcat Mapping saved'
                            subcat_lvl += 1
                if request.POST['check_image'] == "1":
                    advert_obj.display_image = request.FILES['display_image']
                    advert_obj.save()

                    save_advert_image(advert_obj)

                attachment_list = []
                attachment_list = request.POST.get('attachments')
                save_attachments(attachment_list, advert_obj)

                video_list = []
                video_list = request.POST.get('ac_attachment')
                save_video(video_list, advert_obj)

                print "advert updated"

                # phone_category_list = request.POST.get('phone_category_list')
                # phone_category_list = phone_category_list.split(',')
                # phone_number_list = request.POST.get('phone_number_list')
                # phone_number_list = phone_number_list.split(',')
                # zipped = zip(phone_category_list, phone_number_list)
                # save_phone_number(zipped, advert_obj)

                if request.POST.get('product_name_list'):
                    Product.objects.filter(advert_id=advert_id).delete()
                if request.POST.get('opening_day_list'):
                    WorkingHours.objects.filter(advert_id=advert_id).delete()
                if request.POST.get('amenity_list'):
                    Amenities.objects.filter(advert_id=advert_id).delete()
                if request.POST.get('additional_amenity'):
                    AdditionalAmenities.objects.filter(advert_id=advert_id).delete()
                if request.POST.get('near_attraction'):
                    NearByAttraction.objects.filter(advert_id=advert_id).delete()
                if request.POST.get('near_shopnmal'):
                    NearestShopping.objects.filter(advert_id=advert_id).delete()

                product_name_list = request.POST.get('product_name_list')
                product_name_list = product_name_list.split('_PRODUCT_NAME_IS_SEPARATED')
                product_price_list = request.POST.get('product_price_list')
                product_price_list = product_price_list.split('_PRODUCT_PRICE_IS_SEPARATED')
                zipped_product = zip(product_name_list, product_price_list)
                save_product(zipped_product, advert_obj)

                opening_day_list = request.POST.get('opening_day_list')
                opening_day_list = opening_day_list.split(',')

                start_time_list = request.POST.get('start_time_list')
                start_time_list = start_time_list.split(',')

                end_time_list = request.POST.get('end_time_list')
                end_time_list = end_time_list.split(',')

                zipped_wk = zip(opening_day_list, start_time_list, end_time_list)
                save_working_hours(zipped_wk, advert_obj)

                amenity_list = request.POST.get('amenity_list')
                amenity_list = amenity_list.split(',')
                save_amenity(amenity_list, advert_obj)


                near_attr_list = request.POST.get('near_attraction')
                near_attr_list = near_attr_list.split(',')
                save_near_attr(near_attr_list, advert_obj)

                near_shopnmal = request.POST.get('near_shopnmal')
                near_shopnmal = near_shopnmal.split(',')

                near_shonmald = request.POST.get('near_shonmald')
                near_shonmald = near_shonmald.split(',')

                zipped_shopmal = zip(near_shopnmal, near_shonmald)
                save_shpnmal(zipped_shopmal, advert_obj)

                cat = advert_obj.category_id.category_name
                if cat == 'Real Estate':
                    print "SCHOOL", request.POST.get('near_schol')
                    if request.POST.get('near_schol'):
                        NearestSchool.objects.filter(advert_id=advert_id).delete()

                    near_schol = request.POST.get('near_schol')
                    near_schol = near_schol.split(',')

                    print "SCHOOL DI SORTING", request.POST.get('near_schold')
                    near_schold = request.POST.get('near_schold')
                    near_schold = near_schold.split(',')

                    print "AFTER SCHOOL"

                    zipped_school = zip(near_schol, near_schold)
                    save_school(zipped_school, advert_obj)

                    if request.POST.get('near_hosp'):
                        NearestHospital.objects.filter(advert_id=advert_id).delete()

                    near_hosp = request.POST.get('near_hosp')
                    near_hosp = near_hosp.split(',')

                    near_hospd = request.POST.get('near_hospd')
                    near_hospd = near_hospd.split(',')

                    zipped_hospital = zip(near_hosp, near_hospd)
                    save_hospital(zipped_hospital, advert_obj)
                # advert_add_sms(advert_obj)
                # advert_add_mail(advert_obj)
                data = {'success': 'true'}

        except Exception, e:
            print 'Exception :', e
            data = {'data': 'none'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def remove_advert_image(request):
    ##    pdb.set_trace()
    print "in the remove image"
    print request.GET
    try:
        image_id = request.GET.get('image_id')
        ##        temp=str(image_id).replace("L]", "")
        ##        print 'image id : - >',temp.replace("L]", "")
        image = AdvertImage.objects.get(advert_image_id=image_id)
        image.delete()

        data = {'success': 'true'}
    except MySQLdb.OperationalError, e:
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def remove_advert_video(request):
    # pdb.set_trace()
    print "in the remove video"
    print request.GET
    try:
        image_id = request.GET.get('image_id')
        ##        temp=str(image_id).replace("L]", "")
        ##        print 'image id : - >',temp.replace("L]", "")
        image = Advert_Video.objects.get(advert_video_id=image_id)
        image.delete()

        data = {'success': 'true'}
    except MySQLdb.OperationalError, e:
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def update_advert_image(request):
    print "in the upload image"
    ##    pdb.set_trace()
    try:
        print request.FILES['file']
        if request.method == 'POST':
            attachment_file = AdvertImage(advert_image=request.FILES['file'])
            attachment_file.save()
            data = {'success': 'true', 'attachid': attachment_file.advert_image_id}
            print data
        else:
            data = {'success': 'false'}
            print data
    except Exception as e:
        print 'Error ------------> ', e
        data = {'success': 'invalid request'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def update_advert_video(request):
    print "in the upload video"
    ##    pdb.set_trace()
    try:
        print request.FILES['file']
        if request.method == 'POST':
            attachment_file = Advert_Video(advert_video_name=request.FILES['file'])
            attachment_file.save()
            data = {'success': 'true', 'attachid': attachment_file.advert_video_id}
            print data
        else:
            data = {'success': 'false'}
            print data
    except Exception as e:
        print 'Error ------------> ', e
        data = {'success': 'invalid request'}
    return HttpResponse(json.dumps(data), content_type='application/json')


def advert_add_mail(advert_obj):
    gmail_user = "cityhoopla2016"
    gmail_pwd = "cityhoopla@2016"
    FROM = 'CityHoopla Admin <cityhoopla2016@gmail.com>'
    TO = ['cityhoopla2016@gmail.com']
    # pdb.set_trace()
    try:
        TEXT = "Hi Admin,\nAdvert " + str(advert_obj.advert_name) + " " + "for Subscriber " + str(
            advert_obj.supplier_id.contact_person) + " " + "has been added successfully.\nTo view complete details visit portal and follow - Customers -> Subscribers -> Adverts\n\n Thank You," + '\n' + "CityHoopla Team"
        SUBJECT = "Advert Added Successfully!"
        # server = smtplib.SMTP_SSL()
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()

        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException, e:
        print e
    return 1


def advert_edit_mail(advert_obj):
    gmail_user = "cityhoopla2016"
    gmail_pwd = "cityhoopla@2016"
    FROM = 'CityHoopla Admin <cityhoopla2016@gmail.com>'
    TO = ['cityhoopla2016@gmail.com']
    # pdb.set_trace()
    try:
        TEXT = "Hi Admin,\nAdvert " + str(advert_obj.advert_name) + " " + "for Subscriber " + str(
            advert_obj.supplier_id.contact_person) + " " + "has been updated successfully.\nTo view complete details visit portal and follow - Customers -> Subscribers -> Adverts\n\n Thank You," + '\n' + "CityHoopla Team"
        SUBJECT = "Advert Updated Successfully!"
        # server = smtplib.SMTP_SSL()
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()

        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException, e:
        print e
    return 1


def advert_inactive_mail(advert_obj):
    gmail_user = "cityhoopla2016"
    gmail_pwd = "cityhoopla@2016"
    FROM = 'CityHoopla Admin <cityhoopla2016@gmail.com>'
    TO = ['cityhoopla2016@gmail.com']
    # pdb.set_trace()
    try:
        TEXT = "Hi Admin,\nAdvert " + str(advert_obj.advert_name) + " " + "for Subscriber " + str(
            advert_obj.supplier_id.contact_person) + " " + "has been deactivated successfully.\n\n Thank You," + '\n' + "CityHoopla Team"
        SUBJECT = "Advert Deactivated Successfully!"
        # server = smtplib.SMTP_SSL()
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()

        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException, e:
        print e
    return 1


@csrf_exempt
def check_category(request):
    # pdb.set_trace()
    if not request.user.is_authenticated():
        data = {'success':'Expired'}

    else:
        print 'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS'
        print '.......request.POST......',request.POST
        try:
            if request.POST.get('cat_level') == '1':
                cat_obj = CategoryLevel1.objects.filter(parent_category_id=request.POST.get('category_id'))
            if request.POST.get('cat_level') == '2':
                cat_obj = CategoryLevel2.objects.filter(parent_category_id=request.POST.get('category_id'))
            if request.POST.get('cat_level') == '3':
                cat_obj = CategoryLevel3.objects.filter(parent_category_id=request.POST.get('category_id'))
            if request.POST.get('cat_level') == '4':
                cat_obj = CategoryLevel4.objects.filter(parent_category_id=request.POST.get('category_id'))
            if request.POST.get('cat_level') == '5':
                cat_obj = CategoryLevel5.objects.filter(parent_category_id=request.POST.get('category_id'))
            print '.........cat_obj.............',cat_obj
            cat_list = []
            if cat_obj:
                for cat in cat_obj:
                    options_data = '<option value=' + str(cat.category_id) + '>' + cat.category_name + '</option>'
                    cat_list.append(options_data)
                data = {'success': 'true','category_list': cat_list}
            else:
                data = {'success': 'false'}
            print 'SSSSSSSSSSSSSSSSSSSSSSSSS',data
        except Exception, e:
            print e
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def check_subscription(request):
    print request.POST
    try:
        business_obj = Business.objects.get(supplier=request.POST.get('subscriber_id'), is_active=0)
        subscription_id = str(business_obj.business_id)
        subscription_name = business_obj.service_rate_card_id.service_name
        duration = str(business_obj.start_date) + " to " + str(business_obj.end_date)
        data = {'duration': duration, 'subscription_id': subscription_id, 'subscription_name': subscription_name,
                'success': 'true'}
    except Exception, e:
        print '====e===========', e
        data = {'success': 'false'}
    print '=========data===========', data
    return HttpResponse(json.dumps(data), content_type='application/json')


def map_subscription(subscription_id, advert_obj):
    business_obj = Business.objects.get(business_id=str(subscription_id))
    business_obj.is_active = 1
    business_obj.save()
    sub_obj = AdvertSubscriptionMap(
        business_id=Business.objects.get(business_id=str(subscription_id)),
        advert_id=advert_obj
    )
    sub_obj.save()


def check_subscription_detail(premium_service_list, premium_day):
    premium_service_list = premium_service_list
    premium_service_list = str(premium_service_list).split(',')

    premium_day = premium_day
    premium_day = str(premium_day).split(',')
    zipped_wk = zip(premium_service_list, premium_day)
    service_list = []
    duration_list = []

    false_status = 0

    for serv, day in zipped_wk:
        try:
            service_rate_card_obj = AdvertRateCard.objects.get(advert_service_name=serv, duration=day)

        except Exception, e:
            service_list.append(str(serv))
            duration_list.append(day)
            false_status = 1
    if false_status == 0:
        data = {
            'success': 'true',
        }
    else:
        zipped_list = zip(service_list, duration_list)
        message = "Package "
        for i, j in zipped_list:
            message = message + str(i) + " " + "(" + str(j) + " Days)" + ", "

        message = message[:-2] + ' not available'

        data = {
            'success': 'false',
            'message': message
        }
    return data


@csrf_exempt
def advert_detail(request):
    try:
        print '==========request=========', request.POST
        advert_map_obj = AdvertSubscriptionMap.objects.get(business_id=request.POST.get('business_id'))
        chars = string.digits
        pwdSize = 8
        password = ''.join(random.choice(chars) for _ in range(pwdSize))
        supplier_obj = Supplier.objects.get(supplier_id=str(advert_map_obj.advert_id.supplier_id))

        payment_obj = PaymentDetail(
            business_id=Business.objects.get(business_id=str(advert_map_obj.business_id)),
            note=request.POST.get('note'),
            payment_mode=request.POST.get('payment_mode'),
            paid_amount=request.POST.get('paid_amount'),
            bank_name=request.POST.get('bank_name'),
            branch_name=request.POST.get('bank_branch_name'),
            cheque_number=request.POST.get('cheque_number'),
            payable_amount=request.POST.get('payable_amount'),
            total_amount=request.POST.get('generated_amount'),
            tax_type=Tax.objects.get(tax_type=request.POST.get('selected_tax_type')),
            payment_code="PMID" + str(password)
        )
        payment_obj.save()
        print '=================after payment=============='
        data = {
            'success': 'true',
            'message': "Supplier added successfully",
            'payment_code': str(payment_obj.payment_code),
            'user_id': str(supplier_obj.supplier_id)
        }

    except Exception, e:
        data = {
            'success': 'false',
            'message': str(e)
        }
    print '=========data============', data
    return HttpResponse(json.dumps(data), content_type='application/json')


def save_premium_service(zipped_wk, business_obj):
    try:
        for wk_serv, wk_day, strt_tm, end_tm in zipped_wk:
            wk_obj = PremiumService(
                business_id=business_obj,
                premium_service_name=wk_serv,
                no_of_days=wk_day,
                start_date=strt_tm,
                end_date=end_tm,
                premium_service_status='1',
                premium_service_created_date=datetime.now(),
                premium_service_created_by="Admin",
                premium_service_updated_by="Admin",
                premium_service_updated_date=datetime.now()
            )
            wk_obj.save()
            data = {'success': 'true'}

    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def update_subscription(request):
    try:
        serv_obj = ServiceRateCard.objects.get(service_name=request.POST.get('service'),
                                               duration=request.POST.get('selected_duration'))
        try:
            advert_map_obj = AdvertSubscriptionMap.objects.get(advert_id=request.POST.get('adv_id'))
            premium_service_list = request.POST.get('premium_service')
            no_of_days_list = request.POST.get('premium_day_list')
            if (premium_service_list):
                final_data = check_subscription_detail(premium_service_list, no_of_days_list)
                if final_data['success'] == 'true':
                    business_obj = Business.objects.get(business_id=str(advert_map_obj.business_id))
                    category_obj = Category.objects.get(category_id=request.POST.get('category'))

                    date_validation = check_date(request.POST.get('premium_service'),
                                                 request.POST.get('premium_start_date'),
                                                 request.POST.get('premium_end_date'), category_obj, business_obj)

                    if date_validation['success'] == 'true':

                        business_obj.category = Category.objects.get(category_id=request.POST.get('category'))
                        business_obj.service_rate_card_id = ServiceRateCard.objects.get(
                            service_name=request.POST.get('service'), duration=request.POST.get('selected_duration'))
                        business_obj.duration = request.POST.get('selected_duration')
                        business_obj.start_date = request.POST.get('duration_start_date')
                        business_obj.end_date = request.POST.get('duration_end_date')
                        business_obj.save()

                        premium_service_obj = PremiumService.objects.filter(business_id=business_obj).delete()
                        premium_service_list = request.POST.get('premium_service')
                        premium_service_list = str(premium_service_list).split(',')
                        no_of_days_list = request.POST.get('premium_day_list')
                        no_of_days_list = str(no_of_days_list).split(',')
                        start_date_list = request.POST.get('premium_start_date')
                        start_date_list = str(start_date_list).split(',')
                        end_date_list = request.POST.get('premium_end_date')
                        end_date_list = str(end_date_list).split(',')
                        zipped_wk = zip(premium_service_list, no_of_days_list, start_date_list, end_date_list)
                        save_premium_service(zipped_wk, business_obj)
                        data = {
                            'success': 'true',
                            'message': "Supplier profile edited successfully",
                            'transaction_code': str(business_obj.transaction_code),
                        }

                    else:
                        data = {
                            'success': 'false',
                            'message': date_validation['message']
                        }

                else:
                    data = {
                        'success': 'false',
                        'message': final_data['message']
                    }
            else:

                business_obj = Business.objects.get(business_id=str(advert_map_obj.business_id))
                business_obj.category = Category.objects.get(category_id=request.POST.get('category'))
                business_obj.service_rate_card_id = ServiceRateCard.objects.get(
                    service_name=request.POST.get('service'), duration=request.POST.get('selected_duration'))
                business_obj.duration = request.POST.get('selected_duration')
                business_obj.start_date = request.POST.get('duration_start_date')
                business_obj.end_date = request.POST.get('duration_end_date')
                business_obj.save()
                premium_service_obj = PremiumService.objects.filter(business_id=business_obj).delete()

                data = {
                    'success': 'true',
                    'message': "Supplier profile edited successfully",
                    'transaction_code': str(business_obj.transaction_code),
                }
        except Exception, e:
            data = {
                'success': 'false',
                'message': str(e)
            }
    except:
        data = {
            'success': 'false',
            'message': 'Package ' + str(request.POST.get('service')) + ' ' + '(' + str(
                request.POST.get('selected_duration')) + ' Days)' + ' not available'
        }
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def save_subscriber_detail(request):
    try:
        advert_map_obj = AdvertSubscriptionMap.objects.get(
            advert_id=Advert.objects.get(advert_id=request.POST.get('adv_id')))
        try:
            payment_obj = PaymentDetail.objects.get(business_id=str(advert_map_obj.business_id))
            payment_obj.note = request.POST.get('note')
            payment_obj.payment_mode = request.POST.get('payment_mode')
            if (request.POST.get('paid_amount') != 'None'):
                payment_obj.paid_amount = request.POST.get('paid_amount')
            else:
                payment_obj.paid_amount = ''
            payment_obj.payable_amount = request.POST.get('payable_amount')
            payment_obj.total_amount = request.POST.get('generated_amount')
            try:
                payment_obj.tax_type = Tax.objects.get(tax_type=request.POST.get('selected_tax_type'))
            except:
                pass
            payment_obj.save()
        except:
            chars = string.digits
            pwdSize = 8
            password = ''.join(random.choice(chars) for _ in range(pwdSize))
            payment_obj = PaymentDetail(
                business_id=Business.objects.get(business_id=str(advert_map_obj.business_id)),
                note=request.POST.get('note'),
                payment_mode=request.POST.get('payment_mode'),
                paid_amount=request.POST.get('paid_amount'),
                payable_amount=request.POST.get('payable_amount'),
                total_amount=request.POST.get('generated_amount'),
                tax_type=Tax.objects.get(tax_type=request.POST.get('selected_tax_type')),
                payment_code="PMID" + str(password)
            )
            payment_obj.save()
        data = {
            'success': 'true',
            'message': "Supplier added successfully",
            'payment_code': str(payment_obj.payment_code),
        }
    except Exception, e:
        data = {
            'success': 'false',
            'message': str(e)
        }
    print '=======data============', data
    return HttpResponse(json.dumps(data), content_type='application/json')


def check_date(premium_service_list, premium_start_date_list, premium_end_date_list, category_obj, business_obj):
    premium_service_list = premium_service_list
    premium_service_list = str(premium_service_list).split(',')

    premium_start_date_list = str(premium_start_date_list).split(',')
    premium_end_date_list = str(premium_end_date_list).split(',')

    zipped_wk = zip(premium_service_list, premium_start_date_list, premium_end_date_list)
    service_list = []
    start_day_list = []
    end_day_list = []
    false_status = 1
    slider_status = 1
    print '===============zipped_wk=============', zipped_wk
    for service, start_date, end_date in zipped_wk:
        print '===========start date=======', start_date
        print '===========end date=======', end_date

        if service == 'Advert Slider':
            if business_obj == '':
                service_rate_card_obj = PremiumService.objects.filter(Q(premium_service_name=service) & Q(
                    Q(start_date__range=(start_date, end_date)) | Q(end_date__range=(start_date, end_date)) | Q(
                        start_date__lte=start_date, end_date__gte=end_date)))
            else:
                business_id_list = Business.objects.all().exclude(business_id=str(business_obj))
                # service_rate_card_obj = PremiumService.objects.filter(premium_service_name=service,start_date__lte=start_date,end_date__gte=start_date,business_id__in=business_id_list)
                service_rate_card_obj = PremiumService.objects.filter(Q(premium_service_name=service) & Q(
                    Q(start_date__range=(start_date, end_date)) | Q(end_date__range=(start_date, end_date)) | Q(
                        start_date__lte=start_date, end_date__gte=end_date)) & Q(business_id__in=business_id_list))

            if len(service_rate_card_obj) >= 10:
                slider_status = 0
            else:
                slider_status = 1


        elif service == 'Top Advert':
            try:
                if business_obj == '':
                    service_rate_card_obj = PremiumService.objects.get(Q(premium_service_name=service) & Q(
                        Q(start_date__range=(start_date, end_date)) | Q(end_date__range=(start_date, end_date)) | Q(
                            start_date__lte=start_date, end_date__gte=end_date)))
                    # service_rate_card_obj = PremiumService.objects.get(Q(Q(start_date__range = (start_date,end_date)) | Q(end_date__range=(start_date,end_date)) | Q(start_date__lte=start_date,end_date__gte=end_date)))


                else:
                    business_id_list = Business.objects.all().exclude(business_id=str(business_obj))
                    service_rate_card_obj = PremiumService.objects.get(Q(premium_service_name=service) & Q(
                        Q(start_date__range=(start_date, end_date)) | Q(end_date__range=(start_date, end_date)) | Q(
                            start_date__lte=start_date, end_date__gte=end_date)) & Q(business_id__in=business_id_list))

                service_list.append(str(service))
                start_day_list.append(service_rate_card_obj.start_date)
                end_day_list.append(service_rate_card_obj.end_date)

                false_status = 0

            except Exception, e:
                print '=========e================', e
                false_status = 1

        else:
            try:
                business_obj_list = Business.objects.filter(category=category_obj.category_id)

                if (business_obj == ''):
                    service_rate_card_obj = PremiumService.objects.get(Q(premium_service_name=service) & Q(
                        Q(start_date__range=(start_date, end_date)) | Q(end_date__range=(start_date, end_date)) | Q(
                            start_date__lte=start_date, end_date__gte=end_date)) & Q(business_id__in=business_obj_list))
                else:
                    business_id_list = Business.objects.filter(category=category_obj.category_id).exclude(
                        business_id=str(business_obj))

                    service_rate_card_obj = PremiumService.objects.get(Q(premium_service_name=service) & Q(
                        Q(start_date__range=(start_date, end_date)) | Q(end_date__range=(start_date, end_date)) | Q(
                            start_date__lte=start_date, end_date__gte=end_date)) & Q(business_id__in=business_id_list))

                service_list.append(str(service))
                start_day_list.append(service_rate_card_obj.start_date)
                end_day_list.append(service_rate_card_obj.end_date)

                false_status = 0

            except Exception, e:
                false_status = 1

    if false_status == 1 and slider_status == 1:
        data = {
            'success': 'true',
        }

    if false_status == 0 and slider_status == 0:
        zipped_list = zip(service_list, start_day_list, end_day_list)
        message = "Package for Premium Service(s) "
        for i, j, k in zipped_list:
            message = message + str(i) + " " + "from " + str(j) + " to " + str(k) + ", \n"

        message = message[:-3] + " already exists"

        if slider_status == 0:
            message = message + " and Advert slider for selected date is not available"

        data = {
            'success': 'false',
            'message': message
        }

    if false_status == 1 and slider_status == 0:

        message = "Package for Premium Service(s) "

        if slider_status == 0:
            message = message + "\n Advert slider for selected date is not available"

        data = {
            'success': 'false',
            'message': message
        }

    if false_status == 0 and slider_status == 1:
        zipped_list = zip(service_list, start_day_list, end_day_list)
        message = "Package for Premium Service(s) "
        for i, j, k in zipped_list:
            message = message + str(i) + " " + "from " + str(j) + " to " + str(k) + ", \n"

        message = message[:-3] + " already exists"

        data = {
            'success': 'false',
            'message': message
        }

    return data


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def advert_booking_list(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        # pdb.set_trace()
        advert_id = request.GET.get('advert_id')
        advert_obj = Advert.objects.get(advert_id = advert_id)
        supplier_id=advert_obj.supplier_id
        coupon_user = CouponCode.objects.filter(advert_id = advert_id)
        coupon_list = []
        for coupons in coupon_user:
            advert_obj = Advert.objects.get(advert_id=str(coupons.advert_id))
            advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=str(coupons.advert_id))
            if coupons.user_id.consumer_profile_pic:
                user_img=SERVER_URL + coupons.user_id.consumer_profile_pic.url
            else:
                user_img=SERVER_URL + '/static/assets/layouts/layout2/img/avatar.png'
            start_date = advert_sub_obj.business_id.start_date
            end_date = advert_sub_obj.business_id.end_date
            start_date = datetime.strptime(start_date, "%d/%m/%Y")
            end_date = datetime.strptime(end_date, "%d/%m/%Y")
            pre_date = datetime.now().strftime("%d/%m/%Y")
            pre_date = datetime.strptime(pre_date, "%d/%m/%Y")
            date_gap = end_date - pre_date
            if int(date_gap.days) >= 0:
                status = 'Active'
            else:
                status = 'Inactive'
            print status
            coupon_obj = {
                'coupon_code': coupons.coupon_code,
                'avail_date': coupons.creation_date.strftime("%d/%m/%Y"),
                'user_id': str(coupons.user_id),
                'mobile_no': coupons.user_id.consumer_contact_no,
                'user_img': user_img,
                'user_name': coupons.user_id.consumer_full_name,
                'user_area': coupons.user_id.consumer_area,
                'user_email_id': coupons.user_id.consumer_email_id,
                'coupon_expiry_date':end_date.strftime("%d/%m/%Y"),
                'days_remaining':int(date_gap.days),
                'status':status
            }
            coupon_list.append(coupon_obj)
        data = {'supplier_id':supplier_id,'coupon_list':coupon_list,'advert_name':advert_obj.advert_name,'booking_count':len(coupon_list),
                'username': request.session['login_user']}
        return render(request, 'Admin/advert_bookings.html', data)



