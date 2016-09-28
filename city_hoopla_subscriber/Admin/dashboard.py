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

# HTTP Response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
import string
import random
from django.views.decorators.cache import cache_control
import ast

from geopy.geocoders import Nominatim
import datetime
from datetime import datetime
import calendar
from django.db.models import Count


#SERVER_URL = "http://52.40.205.128"
SERVER_URL = "http://192.168.0.151:9090"

@csrf_exempt
def get_advert_date(request):
    advert_id = request.GET.get('advert_id')
    advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)
    start_date = advert_sub_obj.business_id.start_date
    start_date = start_date
    print 'start.............',start_date
    start_date = datetime.strptime(start_date, "%m/%d/%Y")
    start_date = start_date.strftime("%d/%m/%Y")
    pre_date = datetime.now().strftime("%d/%m/%Y")
    data = {
        'success': 'true',
        'start_date':str(start_date),
        'present_date':str(pre_date)
    }
    return HttpResponse(json.dumps(data), content_type='application/json')

def get_advert_health(request):
    try:
        data = {}
        final_list = []
        try:
            if request.GET.get('advert_id'):
                from_date = request.GET.get('from_date')
                to_date = request.GET.get('to_date')
                from_date = datetime.strptime(from_date, "%d/%m/%Y")
                to_date = datetime.strptime(to_date, "%d/%m/%Y")
                from_date = from_date.strftime("%Y-%m-%d")
                to_date = to_date.strftime("%Y-%m-%d")
                advert = Advert.objects.get(advert_id=request.GET.get('advert_id'))
                coupon_objs = CouponCode.objects.filter(advert_id=str(advert.advert_id),creation_date__range=[from_date,to_date])
                advert_fav_objs = AdvertFavourite.objects.filter(advert_id=str(advert.advert_id),creation_date__range=[from_date,to_date])
                advert_like_objs = AdvertLike.objects.filter(advert_id=str(advert.advert_id),creation_date__range=[from_date,to_date])
                if advert.advert_views:
                    advert_views = advert.advert_views
                else:
                    advert_views = 0
                advert_data = {
                    'advert_id': advert.advert_id,
                    'advert_title': advert.advert_name,
                    'advert_views': advert_views,
                    'advert_likes': advert_like_objs.count(),
                    'advert_favourites': advert_fav_objs.count(),
                    'advert_calls': '0',
                    'advert_call_backs': '0',
                    'advert_emails': '0',
                    'advert_coupons': coupon_objs.count(),
                    'advert_reviews': '0',
                    'advert_sms': '0',
                    'advert_whatsapp': '0',
                    'advert_facebook': '0',
                    'advert_twitter': '0'
                }
                final_list.append(advert_data)
                print final_list
            
            else:
                advert_list = Advert.objects.filter(status = '1')
                for advert in advert_list:
                    coupon_objs = CouponCode.objects.filter(advert_id = str(advert.advert_id))
                    advert_fav_objs = AdvertFavourite.objects.filter(advert_id = str(advert.advert_id))
                    advert_like_objs = AdvertLike.objects.filter(advert_id = str(advert.advert_id))
                    if advert.advert_views:
                        advert_views = advert.advert_views
                    else:
                        advert_views = 0
                    advert_data={
                        'advert_id':advert.advert_id,
                        'advert_title':advert.advert_name,
                        'advert_views':advert_views,
                        'advert_likes':advert_like_objs.count(),
                        'advert_favourites':advert_fav_objs.count(),
                        'advert_calls':'0',
                        'advert_call_backs':'0',
                        'advert_emails':'0',
                        'advert_coupons':coupon_objs.count(),
                        'advert_reviews':'0',
                        'advert_sms':'0',
                        'advert_whatsapp':'0',
                        'advert_facebook':'0',
                        'advert_twitter': '0'
                    }
                    final_list.append(advert_data)
            data = {'success': 'true', 'data': final_list}
        except IntegrityError as e:
            print e
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')

def get_subscription_plan(request):
    try:
        data = {}
        final_list = []
        try:
            if request.GET.get('subscriber_id'):
                business_obj = Business.objects.filter(supplier=request.GET.get('subscriber_id'))
                for business in business_obj:
                    advert_sub_obj = AdvertSubscriptionMap.objects.get(business_id=str(business.business_id))
                    start_date = advert_sub_obj.business_id.start_date
                    end_date = advert_sub_obj.business_id.end_date

                    pre_ser_obj_list = PremiumService.objects.filter(business_id=str(advert_sub_obj.business_id))
                    premium_service, advert_slider, top_advert = 'N/A', 'No', 'No'
                    premium_start_date, slider_start_date, top_advert_start_date = 'N/A', 'N/A', 'N/A'
                    premium_end_date, slider_end_date, top_advert_end_date = 'N/A', 'N/A', 'N/A'

                    for pre_ser_obj in pre_ser_obj_list:
                        if pre_ser_obj.premium_service_name != "Advert Slider" and pre_ser_obj.premium_service_name != "Top Advert":
                            premium_service = pre_ser_obj.premium_service_name
                            premium_start_date = pre_ser_obj.start_date
                            premium_end_date = pre_ser_obj.end_date
                        if pre_ser_obj.premium_service_name == "Advert Slider":
                            advert_slider = 'Yes'
                            slider_start_date = pre_ser_obj.start_date
                            slider_end_date = pre_ser_obj.end_date
                        if pre_ser_obj.premium_service_name == "Top Advert":
                            top_advert = 'No'
                            top_advert_start_date = pre_ser_obj.start_date
                            top_advert_end_date = pre_ser_obj.end_date
                    try:
                        payment_obj = PaymentDetail.objects.get(business_id=str(advert_sub_obj.business_id))
                        if payment_obj.total_amount:
                            total_amount = payment_obj.payable_amount
                        else:
                            total_amount = 0
                        if payment_obj.paid_amount:
                            paid_amount = payment_obj.paid_amount
                        else:
                            paid_amount = 0
                    except Exception as e:
                        total_amount = 0
                        paid_amount = 0
                    video_count = Advert_Video.objects.filter(advert_id=str(advert_sub_obj.advert_id)).count()
                    image_count = AdvertImage.objects.filter(advert_id=str(advert_sub_obj.advert_id)).count()

                    advert_data = {
                        'advert_id': str(advert_sub_obj.advert_id),
                        'advert_title': advert_sub_obj.advert_id.advert_name,
                        'category': advert_sub_obj.advert_id.category_id.category_name,
                        'start_date': start_date,
                        'end_date': end_date,
                        'premium_service': premium_service,
                        'premium_start_date': premium_start_date,
                        'premium_end_date': premium_end_date,
                        'advert_slider': advert_slider,
                        'slider_start_date': slider_start_date,
                        'slider_end_date': slider_end_date,
                        'top_advert': top_advert,
                        'top_advert_start_date': top_advert_start_date,
                        'top_advert_end_date': top_advert_end_date,
                        'uploaded_pictures': image_count,
                        'uploaded_videos': video_count,
                        'memory_usages': '0',
                        'total_service_cost': total_amount,
                        'total_amount_paid': paid_amount,
                        'saleman_name': '',
                        'saleman_number': ''
                    }
                    final_list.append(advert_data)
            else:
                supplier_list = Supplier.objects.filter(supplier_status = '1')
                for supplier in supplier_list:
                    business_obj = Business.objects.filter(supplier=str(supplier.supplier_id))
                    for business in business_obj:
                        try:
                            advert_sub_obj = AdvertSubscriptionMap.objects.get(business_id=str(business.business_id))
                            start_date = advert_sub_obj.business_id.start_date
                            end_date = advert_sub_obj.business_id.end_date

                            pre_ser_obj_list = PremiumService.objects.filter(business_id=str(advert_sub_obj.business_id))
                            premium_service, advert_slider, top_advert = 'N/A', 'No', 'No'
                            premium_start_date, slider_start_date, top_advert_start_date = 'N/A', 'N/A', 'N/A'
                            premium_end_date, slider_end_date, top_advert_end_date = 'N/A', 'N/A', 'N/A'

                            for pre_ser_obj in pre_ser_obj_list:
                                if pre_ser_obj.premium_service_name != "Advert Slider" and pre_ser_obj.premium_service_name != "Top Advert":
                                    premium_service = pre_ser_obj.premium_service_name
                                    premium_start_date = pre_ser_obj.start_date
                                    premium_end_date = pre_ser_obj.end_date
                                if pre_ser_obj.premium_service_name == "Advert Slider":
                                    advert_slider = 'Yes'
                                    slider_start_date = pre_ser_obj.start_date
                                    slider_end_date = pre_ser_obj.end_date
                                if pre_ser_obj.premium_service_name == "Top Advert":
                                    top_advert = 'No'
                                    top_advert_start_date = pre_ser_obj.start_date
                                    top_advert_end_date = pre_ser_obj.end_date
                            try:
                                payment_obj = PaymentDetail.objects.get(business_id=str(advert_sub_obj.business_id))
                                if payment_obj.total_amount:
                                    total_amount = payment_obj.payable_amount
                                else:
                                    total_amount = 0
                                if payment_obj.paid_amount:
                                    paid_amount = payment_obj.paid_amount
                                else:
                                    paid_amount = 0
                            except Exception as e:
                                total_amount = 0
                                paid_amount = 0
                            video_count = Advert_Video.objects.filter(advert_id=str(advert_sub_obj.advert_id)).count()
                            image_count = AdvertImage.objects.filter(advert_id=str(advert_sub_obj.advert_id)).count()

                            advert_data={
                                'advert_id':str(advert_sub_obj.advert_id),
                                'advert_title':advert_sub_obj.advert_id.advert_name,
                                'category':advert_sub_obj.advert_id.category_id.category_name,
                                'start_date':start_date,
                                'end_date':end_date,
                                'premium_service':premium_service,
                                'premium_start_date':premium_start_date,
                                'premium_end_date':premium_end_date,
                                'advert_slider':advert_slider,
                                'slider_start_date':slider_start_date,
                                'slider_end_date':slider_end_date,
                                'top_advert':top_advert,
                                'top_advert_start_date':top_advert_start_date,
                                'top_advert_end_date':top_advert_end_date,
                                'uploaded_pictures':image_count,
                                'uploaded_videos':video_count,
                                'memory_usages':'0',
                                'total_service_cost':total_amount,
                                'total_amount_paid':paid_amount,
                                'saleman_name':'',
                                'saleman_number': ''
                            }
                            final_list.append(advert_data)
                        except Exception:
                            pass
            data = {'success': 'true', 'data': final_list}
        except IntegrityError as e:
            print e
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')

def my_subscribers_list(request):
    try:
        data = {}
        final_list = []
        last_total_amount = 0
        sub_city_id = request.GET.get('sub_city')
        print '..........sub_city_id...........',sub_city_id
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        from_date = datetime.strptime(from_date, "%d/%m/%Y")
        to_date = datetime.strptime(to_date, "%d/%m/%Y") + timedelta(days=1)
        from_date = from_date.strftime("%Y-%m-%d")
        to_date = to_date.strftime("%Y-%m-%d")
        try:
            if sub_city_id != '':
                supplier_obj = Supplier.objects.filter(date_joined__range=[from_date, to_date],city_place_id=sub_city_id)
                print "===========Supplier=================",supplier_obj
                for supplier in supplier_obj:
                    if supplier.supplier_status == '1':
                        status = '<span style="cursor: default;" class="btn btn-success">Active</span>'
                    else:
                        status = '<span style="cursor: default;" class="btn btn-danger">Inactive</span>'
                    business_obj = Business.objects.filter(supplier=str(supplier.supplier_id))

                    total_amount = 0

                    for business in business_obj:
                        try:
                            payment_obj = PaymentDetail.objects.get(business_id=str(business.business_id))
                            if payment_obj.paid_amount:
                                total_amount = total_amount + int(payment_obj.paid_amount) 
                                last_total_amount = last_total_amount + int(payment_obj.paid_amount)
                            else:
                                total_amount = total_amount + 0
                                last_total_amount = last_total_amount + 0
                        except Exception as e:
                            print e

                    subscriber_data = {
                        'subscriber_id': str(supplier.supplier_id),
                        'business_name': supplier.business_name,
                        'poc_name': supplier.contact_person,
                        'poc_no': supplier.contact_no,
                        'area': '',
                        'city': supplier.city_place_id.city_id.city_name,
                        'created_date': supplier.date_joined.strftime('%d/%m/%Y'),
                        'total_amount': total_amount,
                        'status': status
                    }
                    final_list.append(subscriber_data)
                print '.......last_total_amount..last..',last_total_amount
                subscriber_data = {
                    'subscriber_id': '',
                    'business_name': '',
                    'poc_name': '',
                    'poc_no': '',
                    'area': '',
                    'city': '',
                    'created_date': '',
                    'total_amount': last_total_amount,
                    'status': ''
                }
                final_list.append(subscriber_data)

            else :
                supplier_obj = Supplier.objects.filter(date_joined__range=[from_date, to_date])
                print "===========Supplier=================",supplier_obj
                for supplier in supplier_obj:
                    if supplier.supplier_status == '1':
                        status = '<span style="cursor: default;" class="btn btn-success">Active</span>'
                    else:
                        status = '<span style="cursor: default;" class="btn btn-danger">Inactive</span>'
                    business_obj = Business.objects.filter(supplier=str(supplier.supplier_id))

                    total_amount = 0
                    for business in business_obj:
                        try:
                            payment_obj = PaymentDetail.objects.get(business_id=str(business.business_id))
                            if payment_obj.paid_amount:
                                total_amount = total_amount + int(payment_obj.paid_amount)
                                last_total_amount = last_total_amount + int(payment_obj.paid_amount)
                            
                            else:
                                total_amount = total_amount + 0
                                last_total_amount = last_total_amount + 0

                        except Exception as e:
                            print e
                    subscriber_data = {
                        'subscriber_id': str(supplier.supplier_id),
                        'business_name': supplier.business_name,
                        'poc_name': supplier.contact_person,
                        'poc_no': supplier.contact_no,
                        'area': '',
                        'city': supplier.city_place_id.city_id.city_name,
                        'created_date': supplier.date_joined.strftime('%m/%d/%Y'),
                        'total_amount': total_amount,
                        'status': status
                    }
                    final_list.append(subscriber_data)
                subscriber_data = {
                    'subscriber_id': '',
                    'business_name': '',
                    'poc_name': '',
                    'poc_no': '',
                    'area': '',
                    'city': '',
                    'created_date': '',
                    'total_amount': last_total_amount,
                    'status': ''
                }
                final_list.append(subscriber_data)

            data = {'success': 'true', 'data': final_list}

        except IntegrityError as e:
            print e
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')

def my_subscription_sale(request):
    try:
        data = {}
        final_list = []
        print "-----------EE-----------"

        sale_city_id = request.GET.get('sale_city')
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        print from_date,to_date
        from_date = datetime.strptime(from_date, "%d/%m/%Y")
        to_date = datetime.strptime(to_date, "%d/%m/%Y") + timedelta(days=1)
        from_date = from_date.strftime("%Y-%m-%d")
        to_date = to_date.strftime("%Y-%m-%d")

        try:
            if sale_city_id != '':

                supplier_list = Supplier.objects.filter(supplier_status = '1',city_place_id=sale_city_id)
                total_paid_amount = 0
                last_total_amount = 0
                for supplier in supplier_list:
                    business_obj = Business.objects.filter(supplier=str(supplier.supplier_id),business_created_date__range=[from_date, to_date])
                    for business in business_obj:
                        try:
                            advert_sub_obj = AdvertSubscriptionMap.objects.get(business_id=str(business.business_id))
                            start_date = advert_sub_obj.business_id.start_date
                            end_date = advert_sub_obj.business_id.end_date

                            pre_ser_obj_list = PremiumService.objects.filter(business_id=str(advert_sub_obj.business_id))
                            premium_service, advert_slider, top_advert = 'N/A', 'No', 'No'
                            premium_start_date, slider_start_date, top_advert_start_date = 'N/A', 'N/A', 'N/A'
                            premium_end_date, slider_end_date, top_advert_end_date = 'N/A', 'N/A', 'N/A'

                            for pre_ser_obj in pre_ser_obj_list:
                                if pre_ser_obj.premium_service_name != "Advert Slider" and pre_ser_obj.premium_service_name != "Top Advert":
                                    premium_service = pre_ser_obj.premium_service_name
                                    premium_start_date = pre_ser_obj.start_date
                                    premium_end_date = pre_ser_obj.end_date
                                if pre_ser_obj.premium_service_name == "Advert Slider":
                                    advert_slider = 'Yes'
                                    slider_start_date = pre_ser_obj.start_date
                                    slider_end_date = pre_ser_obj.end_date
                                if pre_ser_obj.premium_service_name == "Top Advert":
                                    top_advert = 'No'
                                    top_advert_start_date = pre_ser_obj.start_date
                                    top_advert_end_date = pre_ser_obj.end_date
                            try:
                                payment_obj = PaymentDetail.objects.get(business_id=str(advert_sub_obj.business_id))
                                 
                                if payment_obj.total_amount:
                                    total_amount = payment_obj.total_amount
                                    last_total_amount = last_total_amount + int(payment_obj.total_amount)
                                else:
                                    total_amount = 0
                                    last_total_amount = last_total_amount + 0

                                if payment_obj.paid_amount:
                                    paid_amount = payment_obj.paid_amount
                                    total_paid_amount = total_paid_amount + int(payment_obj.paid_amount)
                                else:
                                    paid_amount = 0
                                    total_paid_amount = total_paid_amount + 0
                            except Exception as e:
                                total_amount = 0
                                paid_amount = 0

                            advert_data={
                                'advert_title':advert_sub_obj.advert_id.advert_name,
                                'business_name':supplier.business_name,
                                'area':advert_sub_obj.advert_id.area,
                                'city':advert_sub_obj.advert_id.city_place_id.city_id.city_name,
                                'category':advert_sub_obj.advert_id.category_id.category_name,
                                'subs_start_date':start_date,
                                'subs_end_date':end_date,
                                'premium_service':premium_service,
                                'premium_start_date':premium_start_date,
                                'premium_end_date':premium_end_date,
                                'advert_slider':advert_slider,
                                'slider_start_date':slider_start_date,
                                'slider_end_date':slider_end_date,
                                'top_advert':top_advert,
                                'top_advert_start_date':top_advert_start_date,
                                'top_advert_end_date':top_advert_end_date,
                                'total_service_cost':total_amount,
                                'total_amount_paid':paid_amount
                            }
                            final_list.append(advert_data)
                        except Exception as e:
                            print e
                            pass

                advert_data={
                    'advert_title':'',
                    'business_name':'',
                    'area':'',
                    'city':'',
                    'category':'',
                    'subs_start_date':'',
                    'subs_end_date':'',
                    'premium_service':'',
                    'premium_start_date':'',
                    'premium_end_date':'',
                    'advert_slider':'',
                    'slider_start_date':'',
                    'slider_end_date':'',
                    'top_advert':'',
                    'top_advert_start_date':'',
                    'top_advert_end_date':'',
                    'total_service_cost':last_total_amount,
                    'total_amount_paid':total_paid_amount
                }
                final_list.append(advert_data)


            else :
                supplier_list = Supplier.objects.filter(supplier_status = '1')
                total_paid_amount = 0
                last_total_amount = 0
                for supplier in supplier_list:
                    business_obj = Business.objects.filter(supplier=str(supplier.supplier_id),business_created_date__range=[from_date, to_date])
                    for business in business_obj:
                        try:
                            advert_sub_obj = AdvertSubscriptionMap.objects.get(business_id=str(business.business_id))
                            start_date = advert_sub_obj.business_id.start_date
                            end_date = advert_sub_obj.business_id.end_date

                            pre_ser_obj_list = PremiumService.objects.filter(business_id=str(advert_sub_obj.business_id))
                            premium_service, advert_slider, top_advert = 'N/A', 'No', 'No'
                            premium_start_date, slider_start_date, top_advert_start_date = 'N/A', 'N/A', 'N/A'
                            premium_end_date, slider_end_date, top_advert_end_date = 'N/A', 'N/A', 'N/A'

                            for pre_ser_obj in pre_ser_obj_list:
                                if pre_ser_obj.premium_service_name != "Advert Slider" and pre_ser_obj.premium_service_name != "Top Advert":
                                    premium_service = pre_ser_obj.premium_service_name
                                    premium_start_date = pre_ser_obj.start_date
                                    premium_end_date = pre_ser_obj.end_date
                                if pre_ser_obj.premium_service_name == "Advert Slider":
                                    advert_slider = 'Yes'
                                    slider_start_date = pre_ser_obj.start_date
                                    slider_end_date = pre_ser_obj.end_date
                                if pre_ser_obj.premium_service_name == "Top Advert":
                                    top_advert = 'No'
                                    top_advert_start_date = pre_ser_obj.start_date
                                    top_advert_end_date = pre_ser_obj.end_date
                            try:
                                payment_obj = PaymentDetail.objects.get(business_id=str(advert_sub_obj.business_id))
                           
                                if payment_obj.total_amount:
                                    total_amount = payment_obj.total_amount
                                    last_total_amount = last_total_amount + int(payment_obj.total_amount)
                                else:
                                    total_amount = 0
                                    last_total_amount = last_total_amount + 0

                                if payment_obj.paid_amount:
                                    paid_amount = payment_obj.paid_amount
                                    total_paid_amount = total_paid_amount + int(payment_obj.paid_amount)
                                else:
                                    paid_amount = 0
                                    total_paid_amount = total_paid_amount + 0

                            except Exception as e:
                                total_amount = 0
                                paid_amount = 0

                            advert_data={
                                'advert_title':advert_sub_obj.advert_id.advert_name,
                                'business_name':supplier.business_name,
                                'area':advert_sub_obj.advert_id.area,
                                'city':advert_sub_obj.advert_id.city_place_id.city_id.city_name,
                                'category':advert_sub_obj.advert_id.category_id.category_name,
                                'subs_start_date':start_date,
                                'subs_end_date':end_date,
                                'premium_service':premium_service,
                                'premium_start_date':premium_start_date,
                                'premium_end_date':premium_end_date,
                                'advert_slider':advert_slider,
                                'slider_start_date':slider_start_date,
                                'slider_end_date':slider_end_date,
                                'top_advert':top_advert,
                                'top_advert_start_date':top_advert_start_date,
                                'top_advert_end_date':top_advert_end_date,
                                'total_service_cost':total_amount,
                                'total_amount_paid':paid_amount
                            }
                            final_list.append(advert_data)
                        except Exception as e:
                            print e
                            pass

                advert_data={
                    'advert_title':'',
                    'business_name':'',
                    'area':'',
                    'city':'',
                    'category':'',
                    'subs_start_date':'',
                    'subs_end_date':'',
                    'premium_service':'',
                    'premium_start_date':'',
                    'premium_end_date':'',
                    'advert_slider':'',
                    'slider_start_date':'',
                    'slider_end_date':'',
                    'top_advert':'',
                    'top_advert_start_date':'',
                    'top_advert_end_date':'',
                    'total_service_cost':last_total_amount,
                    'total_amount_paid':total_paid_amount
                }
                final_list.append(advert_data)

            data = {'success': 'true', 'data': final_list}
        except IntegrityError as e:
            print e
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')

def get_advert_databse(request):
    try:
        data = {}
        final_list = []

        try:
            print '..>>><<<...????.......<<<>>>>',request.GET.get('city_id')
            category_list = []
            if request.GET.get('city_id') and request.GET.get('city_id') != '0':
                cat_list = CategoryCityMap.objects.filter(city_place_id = request.GET.get('city_id'))
                for category in cat_list:
                    cat_obj = Category.objects.get(category_id=str(category.category_id))
                    category_list.append(cat_obj)
                category_active_list = Category.objects.filter(category_status='1')
                for category in category_active_list:
                    cat_city_obj = CategoryCityMap.objects.filter(category_id=str(category.category_id))
                    if not cat_city_obj:
                        category_list.append(category)

            else:
                category_list = Category.objects.filter(category_status='1')
            for category in category_list:
                category_name = category.category_name
                business_obj = Business.objects.filter(category_id=str(category.category_id))
                count = 0
                try :
                    for business in business_obj:
                        advert_sub_obj = AdvertSubscriptionMap.objects.get(business_id=str(business.business_id))
                        print '..........advert_sub_obj..........',advert_sub_obj
                        pre_date = datetime.now().strftime("%m/%d/%Y")
                        pre_date = datetime.strptime(pre_date, "%m/%d/%Y")
                        print 'pre_date>>>>>>>>',pre_date
                        end_date = advert_sub_obj.business_id.end_date
                        end_date = datetime.strptime(end_date, "%m/%d/%Y")
                        print 'end_date>>>>>>>',end_date
                        date_gap = end_date - pre_date
                        if int(date_gap.days) >= 0:
                            count = count + 1
                    advert_data = {
                        'category': category_name,
                        'count': str(count)
                    }
                    final_list.append(advert_data)

                except Exception as e:
                    print e
                    pass

            data = {'success': 'true', 'data': final_list}
        except IntegrityError as e:
            print e
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception, e:
        print 'Exception ', e
    print 'HHH................DATA..............HHHH',data
    return HttpResponse(json.dumps(data), content_type='application/json')

def get_new_registered_consumer(request):
    try:
        data = {}
        final_list = []
        area = ''
        city = ''
        print "===================get_new_registered_consumer================"
        try:
            from_date = request.GET.get('from_date')
            to_date = request.GET.get('to_date')
            print from_date,to_date
            from_date = datetime.strptime(from_date, "%d/%m/%Y")
            to_date = datetime.strptime(to_date, "%d/%m/%Y") + timedelta(days=1)
            from_date = from_date.strftime("%Y-%m-%d")
            to_date = to_date.strftime("%Y-%m-%d")

            geolocator = Nominatim()
            #location = geolocator.reverse("18.5204, 73.8567")
            #print '---------location------',location

            consumer_list = ConsumerProfile.objects.filter(date_joined__range=[from_date, to_date])

            n = 0
            for consumer in consumer_list:
                n=n+1
                user_name = consumer.consumer_full_name
                date = consumer.consumer_created_date.strftime('%d/%m/%Y')
                lat = consumer.latitude
                long = consumer.longitude

                if lat:
                    try:
                        geolocator = Nominatim()
                        location = geolocator.reverse((lat, long))
                        print '---------location------',location
                        loc = str(location)
                        city = loc.split(", ")[-4]
                        area = loc.split(", ")[-5]
                        consumer_data={
                            'sr_no':n,
                            'user_name':user_name,
                            'date':date,
                            'area':area,
                            'city':city
                        }
                        final_list.append(consumer_data)

                    except:
                        location = ''
                else:
                    pass

                consumer_data={
                    'sr_no':n,
                    'user_name':user_name,
                    'date':date,
                    'area':'',
                    'city':''
                }
                final_list.append(consumer_data)
            data = {'success': 'true', 'data': final_list}
        except Exception as e:
            print "==============Exception===============================",e
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')


def get_consumer_activity(request):
    try:
        data = {}
        final_list = []
        try:
            print "==========================SS2=====get_consumer_activity================"
            from_date = request.GET.get('from_date')
            to_date = request.GET.get('to_date')
            print from_date,to_date
            from_date = datetime.strptime(from_date, "%d/%m/%Y")
            to_date = datetime.strptime(to_date, "%d/%m/%Y") + timedelta(days=1)
            from_date = from_date.strftime("%Y-%m-%d")
            to_date = to_date.strftime("%Y-%m-%d")

            #consumer_list = ConsumerProfile.objects.all()
            consumer_list = ConsumerProfile.objects.filter(date_joined__range=[from_date, to_date])
            n = 0
            for consumer in consumer_list:
                n=n+1
                user_id = consumer.consumer_id
                date = consumer.consumer_created_date.strftime('%d/%m/%Y')

                lat = consumer.latitude
                long = consumer.longitude

                if lat:
                    try:
                        geolocator = Nominatim()
                        location = geolocator.reverse((lat, long))
                        print '---------location------',location
                        loc = str(location)
                        city = loc.split(", ")[-4]
                        area = loc.split(", ")[-5]
                        consumer_data={
                            'sr_no':n,
                            'user_id':user_id,
                            'date':date,
                            'area':area,
                            'city':city,
                            'app_usage':'',
                        }
                        final_list.append(consumer_data)

                    except:
                        location = ''
                else:
                    pass

                app_usage = ""

                consumer_data={
                    'sr_no':n,
                    'user_id':user_id,
                    'date':date,
                    'area':'',
                    'city':'',
                    'app_usage':'',
                }
                final_list.append(consumer_data)
            data = {'success': 'true', 'data': final_list}
        except Exception as e:
            print e
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception, e:
        print 'Exception ', e
    #   print data
    return HttpResponse(json.dumps(data), content_type='application/json')


def get_consumer_usage(request):
    try:
        data = {}
        final_list = []
        try:
            print "==========================SS3=====get_consumer_usage================"        
            from_date = request.GET.get('from_date')
            to_date = request.GET.get('to_date')
            print from_date,to_date
            from_date = datetime.strptime(from_date, "%d/%m/%Y")
            to_date = datetime.strptime(to_date, "%d/%m/%Y") + timedelta(days=1)
            from_date = from_date.strftime("%Y-%m-%d")
            to_date = to_date.strftime("%Y-%m-%d")

            #consumer_list = ConsumerProfile.objects.all()
            consumer_list = ConsumerProfile.objects.filter(date_joined__range=[from_date, to_date])
            n = 0
            for consumer in consumer_list:
                n=n+1
                user_id = consumer.consumer_id
                if consumer.no_of_login:
                    login_count = consumer.no_of_login
                else:
                    login_count = 0
            

                consumer_data={
                    'sr_no':n,
                    'user_id':user_id,
                    'login_count':login_count,
                }
                final_list.append(consumer_data)
            data = {'success': 'true', 'data': final_list}
        except Exception as e:
            print e
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')


####################%%%%%%%$$$$$$$$$$$$$$%%%%%%%%%%%##########

@csrf_exempt
def admin_dashboard(request):
    try:
        data = {}
        final_list = []
        final_list1 = []
        try:
            # to find out subscriber list
            subscriber_obj = Supplier.objects.filter(city_place_id = '1')

            # to find last 1 month previous date
            today_date = datetime.now().strftime("%m/%d/%Y")
            dates = today_date.split('/')
            if dates[0] == '1':
                dates[0] = 12
            else:
                dates[0] = int(dates[0]) - 1
                if int(dates[0]) < 10:
                    dates[0] = '0'+str(dates[0])
            pre_date = str(dates[0]) +'/'+dates[1]+'/'+dates[2]

            #to find out logo of supplier
            # Supplier_obj = Supplier.objects.get(supplier_id=request.session['supplier_id'])
            # print "..................Supplier_obj.........",Supplier_obj
            # supplier_id = Supplier_obj.supplier_id

            # logo= SERVER_URL + Supplier_obj.logo.url

            #########.............Dashboard Stats.........................#####
            total_payment_count = 0
            total_new_subscriber = 0
            total_new_booking = 0
            total_advert_expiring = 0


            current_date = datetime.now()
            first = calendar.day_name[current_date.weekday()]

            last_date = (datetime.now() - timedelta(days=7))
            last_date2 = calendar.day_name[last_date.weekday()]
            #Payment Received
            paymentdetail_list = PaymentDetail.objects.filter(payment_created_date__range=[last_date,current_date])

            for pay_obj in paymentdetail_list:
                if pay_obj.paid_amount:
                    paid_amount = pay_obj.paid_amount
                    total_payment_count = total_payment_count + int(paid_amount)
                    
            #New Subscribers
            total_new_subscriber = Business.objects.filter(business_created_date__range=[last_date,current_date]).count()
            
            #New Bookings
            total_new_booking = CouponCode.objects.filter(creation_date__range=[last_date,current_date]).count()
            # Adverts Expiring
            current_date = datetime.now().strftime("%m/%d/%Y")
            last_date = (datetime.now() + timedelta(days=7)).strftime("%m/%d/%Y")
            total_advert_expiring = Business.objects.filter(end_date__range=[current_date,last_date]).count()
            print "..#########......total_advert_expiring.........",total_advert_expiring

            
            #######.............Total subscription  Graph......(1)....########
            
            FY_MONTH_LIST = [1,2,3,4,5,6,7,8,9,10,11,12]
            today = date.today()
            start_date = date(today.year,01,01)
            end_date = date(today.year,12,31) 
            monthly_count = []
            # jan,feb,mar,apr,may,jun,jul,aug,sep,octo,nov,dec


            subscriptions = Business.objects.filter(business_created_date__range=[start_date,end_date]).extra(select={'month': "EXTRACT(month FROM business_created_date)"}).values('month').annotate(count=Count('business_id'))
            list={}


            for sub in subscriptions:
                if sub.get('month'):
                    list[sub.get('month')]=sub.get('count') or '0.00'
            

            for m in FY_MONTH_LIST:
                try:
                    monthly_count.append(list[m])
                except:
                    monthly_count.append(0)
                    
            jan=monthly_count[0]
            feb=monthly_count[1]
            mar=monthly_count[2]
            apr=monthly_count[3]
            may=monthly_count[4]
            jun=monthly_count[5]
            jul=monthly_count[6]
            aug=monthly_count[7]
            sep=monthly_count[8]
            octo=monthly_count[9]
            nov=monthly_count[10]
            dec=monthly_count[11]

            ##########..................Today's Payment received.....(2)................############

            current_date = datetime.now()
            first = calendar.day_name[current_date.weekday()]

            last_date = (datetime.now() - timedelta(days=7))
            last_date2 = calendar.day_name[last_date.weekday()]

            list = []
            consumer_list = PaymentDetail.objects.filter(payment_created_date__range=[last_date,current_date])
            mon=tue=wen=thus=fri=sat=sun=0
            if consumer_list:
                for view_obj in consumer_list:
                    payment_created_date=view_obj.payment_created_date
                    consumer_day = calendar.day_name[payment_created_date.weekday()]
                    if consumer_day== 'Monday' :
                        if view_obj.paid_amount:
                            mon = mon+int(view_obj.paid_amount)
                    elif consumer_day== 'Tuesday' :
                        if view_obj.paid_amount:
                            tue = tue+int(view_obj.paid_amount)
                    elif consumer_day== 'Wednesday' :
                        if view_obj.paid_amount:
                            wen = wen+int(view_obj.paid_amount)
                    elif consumer_day== 'Thursday' :
                        if view_obj.paid_amount:
                            thus = thus+int(view_obj.paid_amount)
                    elif consumer_day== 'Friday' :
                        if view_obj.paid_amount:
                            fri = fri+int(view_obj.paid_amount)
                    elif consumer_day== 'Saturday' :
                        if view_obj.paid_amount:
                            sat = sat+int(view_obj.paid_amount)
                    elif consumer_day== 'Sunday' :
                        if view_obj.paid_amount:
                            sun = sun+int(view_obj.paid_amount)
                    else :
                        pass


            ############################...Todays Login.....(3)....###############################
            count_zero = 0
            count_first = 0
            count_second = 0
            count_third = 0

            consumer_list0= ConsumerProfile.objects.filter(last_time_login__regex = ' 0:').count()
            count_zero = count_zero + consumer_list0

            for hour in range(0,9):
                hour = ' 0'+ str(hour) + ':'
                consumer_list= ConsumerProfile.objects.filter(last_time_login__regex = hour).count()
                count_first = count_first + consumer_list
            count_1 = str(count_first)

            for hour in range(9,17):
                if hour == 9:
                    hour = ' 0'+ str(hour) + ':'
                else:
                    hour = ' '+ str(hour) + ':'
                consumer_list1= ConsumerProfile.objects.filter(last_time_login__regex = hour).count()
                count_second = count_second + consumer_list1
            count_2 = str(count_second)

            for hour in range(17,24):
                hour = ' '+ str(hour) + ':'
                consumer_list2= ConsumerProfile.objects.filter(last_time_login__regex = hour).count()
                count_third = count_third + consumer_list2
            count_3 = str(count_third)

            today_date = datetime.now().strftime("%m/%d/%Y")
            dates = today_date.split('/')
            if dates[0] == '1':
                dates[0] = 12
            else:
                dates[0] = int(dates[0]) - 1
                if int(dates[0]) < 10:
                    dates[0] = '0'+str(dates[0])
            pre_date = str(dates[0]) +'/'+dates[1]+'/'+dates[2]

            print '..........count_zero..........',count_zero
            print '..........count_1..........',count_1
            print '..........count_2..........',count_2
            print '..........count_3..........',count_3


            ###########################....... New subscription view...(4).....######################
            current_date = datetime.now()
            first = calendar.day_name[current_date.weekday()]

            last_date = (datetime.now() - timedelta(days=7))
            last_date2 = calendar.day_name[last_date.weekday()]

            list = []
            consumer_obj_list = Business.objects.filter(business_created_date__range=[last_date,current_date])
            mon1=tue1=wen1=thus1=fri1=sat1=sun1=0
            if consumer_obj_list:
                for consumer_obj in consumer_obj_list:
                    business_created_date=consumer_obj.business_created_date
                    consumer_day = calendar.day_name[business_created_date.weekday()]
                    if consumer_day== 'Monday' :
                        mon1 = mon1+1
                    elif consumer_day== 'Tuesday' :
                        tue1 = tue1+1
                    elif consumer_day== 'Wednesday' :
                        wen1 = wen1+1
                    elif consumer_day== 'Thursday' :
                        thus1 = thus1+1
                    elif consumer_day== 'Friday' :
                        fri1 = fri1+1
                    elif consumer_day== 'Saturday' :
                        sat1 = sat1+1
                    elif consumer_day== 'Sunday' :
                        sun1 = sun1+1
                    else :
                        pass

            data = {'success':'true','subscriber_data':subscriber_obj,'today_date':today_date,'pre_date':pre_date,'count_zero':count_zero,'count_1':count_1,'count_2':count_2,'count_3':count_3,'total_payment_count':total_payment_count,'total_new_subscriber':total_new_subscriber,
                'total_new_booking':total_new_booking,'total_advert_expiring':total_advert_expiring,'jan':jan,'feb':feb,'mar':mar,'apr':apr,'may':may,'jun':jun,'jul':jul,
               'aug':aug,'sep':sep,'oct':octo,'nov':nov,'dec':dec,'mon':mon,'tue':tue,'wen':wen,'thus':thus,'fri':fri,'sat':sat,'sun':sun,'mon1':mon1,'tue1':tue1,'wen1':wen1,'thus1':thus1,'fri1':fri1,'sat1':sat1,'sun1':sun1,'city_places_list':get_city_places(request),
               'count_zero':count_zero,'count_1':count_1,'count_2':count_2,'count_3':count_3}

        except IntegrityError as e:
            print e
            data = {'success':'false','message':'Error in  loading page. Please try after some time','username':request.session['login_user']}
    except MySQLdb.OperationalError, e:
        print e
    except Exception,e:
        print 'Exception ',e

    print data
    return render(request,'Admin/index.html',data)


# TO GET THE CITY
def get_city_places(request):
   
    city_list=[]
    try:
        city_objs=City_Place.objects.filter(city_status='1')
        for city in city_objs:
            city_list.append({'city_place_id': city.city_place_id,'city': city.city_id.city_name})
        data =  city_list
        return data

    except Exception, ke:
        print ke
        data={'city_list': 'none','message':'No city available'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def get_admin_filter(request):
    try:
        data = {}
        final_list = []
        final_list1 = []
        try: 
            city_front = request.GET.get('citys_var')
            print '//......$$$$$$$$.....city_front......//',city_front                                 
            if city_front == 'all':
                #to find out logo of supplier
                # Supplier_obj = Supplier.objects.get(supplier_id=request.session['supplier_id'])
                # print "..................Supplier_obj.........",Supplier_obj
                # supplier_id = Supplier_obj.supplier_id

                # logo= SERVER_URL + Supplier_obj.logo.url


                #######.............Total subscription  Graph......(1)....########
                
                FY_MONTH_LIST = [1,2,3,4,5,6,7,8,9,10,11,12]
                today = date.today()
                start_date = date(today.year,01,01)
                end_date = date(today.year,12,31) 
                monthly_count = []
                # jan,feb,mar,apr,may,jun,jul,aug,sep,octo,nov,dec
                subscriptions = Business.objects.filter(business_created_date__range=[start_date,end_date]).extra(select={'month': "EXTRACT(month FROM business_created_date)"}).values('month').annotate(count=Count('business_id'))
                list={}


                for sub in subscriptions:
                    print "sub.get('count')",sub.get('count')
                    if sub.get('month'):
                        list[sub.get('month')]=sub.get('count') or '0.00'
                

                for m in FY_MONTH_LIST:
                    try:
                        monthly_count.append(list[m])
                    except:
                        monthly_count.append(0)
                        
                jan1=monthly_count[0]
                feb1=monthly_count[1]
                mar1=monthly_count[2]
                apr1=monthly_count[3]
                may1=monthly_count[4]
                jun1=monthly_count[5]
                jul1=monthly_count[6]
                aug1=monthly_count[7]
                sep1=monthly_count[8]
                octo1=monthly_count[9]
                nov1=monthly_count[10]
                dec1=monthly_count[11]



                ##########................Todays Payment received.....(2).......for a week.............############

                current_date = datetime.now()
                last_date = (datetime.now() - timedelta(days=7))

                list = []
                total_view_list = PaymentDetail.objects.filter(payment_created_date__range=[last_date,current_date])
                mon2=tue2=wen2=thus2=fri2=sat2=sun2=0
                if total_view_list:
                    for view_obj in total_view_list:
                        payment_created_date=view_obj.payment_created_date
                        consumer_day = calendar.day_name[payment_created_date.weekday()]
                        if consumer_day== 'Monday'  :
                            mon2 = mon2+1
                        elif consumer_day== 'Tuesday'  :
                            tue2 = tue2+1
                        elif consumer_day== 'Wednesday' :
                            wen2 = wen2+1
                        elif consumer_day== 'Thursday' :
                            thus2 = thus2+1
                        elif consumer_day== 'Friday' :
                            fri2 = fri2+1
                        elif consumer_day== 'Saturday':
                            sat2 = sat2+1
                        elif consumer_day== 'Sunday' :
                            sun2 = sun2+1
                        else :
                            pass

                # ##########.....Todays Login.(3)... for a week  ##########
                count_zero1 = 0
                count_first = 0
                count_second = 0
                count_third = 0

                consumer_list0= ConsumerProfile.objects.filter(last_time_login__regex = ' 0:').count()
                count_zero1 = count_zero1 + consumer_list0

                for hour in range(0,9):
                    print "HOur",hour
                    hour = ' 0'+ str(hour) + ':'
                    print "hour",hour
                    consumer_list= ConsumerProfile.objects.filter(last_time_login__regex = hour).count()
                    count_first = count_first + consumer_list
                count_11 = str(count_first)

                for hour in range(9,17):
                    if hour == 9:
                        hour = ' 0'+ str(hour) + ':'
                    else:
                        hour = ' '+ str(hour) + ':'
                    consumer_list1= ConsumerProfile.objects.filter(last_time_login__regex = hour).count()
                    count_second = count_second + consumer_list1
                count_22 = str(count_second)

                for hour in range(17,24):
                    hour = ' '+ str(hour) + ':'
                    consumer_list2= ConsumerProfile.objects.filter(last_time_login__regex = hour).count()
                    count_third = count_third + consumer_list2
                count_33 = str(count_third)


                print '..........count_zero..........',count_zero1
                print '..........count_1..........',count_11
                print '..........count_2..........',count_22
                print '..........count_3..........',count_33


                ##########..... New subscription view...(4).... for a week  ##########
                current_date = datetime.now()
                last_date = (datetime.now() - timedelta(days=7))

                list = []
                total_view_list = Business.objects.filter(business_created_date__range=[last_date,current_date])
                mon4=tue4=wen4=thus4=fri4=sat4=sun4=0
                if total_view_list:
                    for view_obj in total_view_list:
                        business_created_date=view_obj.business_created_date
                        consumer_day = calendar.day_name[business_created_date.weekday()]
                        if consumer_day== 'Monday' :
                            mon4 = mon4+1
                        elif consumer_day== 'Tuesday':
                            tue4 = tue4+1
                        elif consumer_day== 'Wednesday':
                            wen4 = wen4+1
                        elif consumer_day== 'Thursday':
                            thus4 = thus4+1
                        elif consumer_day== 'Friday' :
                            fri4 = fri4+1
                        elif consumer_day== 'Saturday' :
                            sat4 = sat4+1
                        elif consumer_day== 'Sunday' :
                            sun4 = sun4+1
                        else :
                            pass
            else :
                #to find out logo of supplier
                # Supplier_obj = Supplier.objects.get(supplier_id=request.session['supplier_id'])
                # print "..................Supplier_obj.........",Supplier_obj
                # supplier_id = Supplier_obj.supplier_id

                # logo= SERVER_URL + Supplier_obj.logo.url


                #######.............Total subscription  Graph......(1)....########
                
                FY_MONTH_LIST = [1,2,3,4,5,6,7,8,9,10,11,12]
                today = date.today()
                start_date = date(today.year,01,01)
                end_date = date(today.year,12,31) 
                monthly_count = []
                # jan,feb,mar,apr,may,jun,jul,aug,sep,octo,nov,dec
                supplier_id_list = []
                sup_obj = Supplier.objects.filter(supplier_status = '1',city_place_id=city_front)
                for supplier in sup_obj:
                    supplier_id_list.append(str(supplier.supplier_id))
                subscriptions = Business.objects.filter(business_created_date__range=[start_date,end_date],
                    supplier_id__in=supplier_id_list).extra(select={'month': "EXTRACT(month FROM business_created_date)"}).values('month').annotate(count=Count('business_id'))
                list={}

                for sub in subscriptions:
                    if sub.get('month'):
                        list[sub.get('month')]=sub.get('count') or '0.00'
                

                for m in FY_MONTH_LIST:
                    try:
                        monthly_count.append(list[m])
                    except:
                        monthly_count.append(0)
                        
                jan1=monthly_count[0]
                feb1=monthly_count[1]
                mar1=monthly_count[2]
                apr1=monthly_count[3]
                may1=monthly_count[4]
                jun1=monthly_count[5]
                jul1=monthly_count[6]
                aug1=monthly_count[7]
                sep1=monthly_count[8]
                octo1=monthly_count[9]
                nov1=monthly_count[10]
                dec1=monthly_count[11]



                ##########................Todays Payment received.....(2).......for a week.............############

                current_date = datetime.now()
                last_date = (datetime.now() - timedelta(days=7))

                list = []
                total_view_list = PaymentDetail.objects.filter(payment_created_date__range=[last_date,current_date])
                mon2=tue2=wen2=thus2=fri2=sat2=sun2=0
                if total_view_list:
                    for view_obj in total_view_list:
                        city_nm = view_obj.business_id.supplier.city_place_id
                        payment_created_date=view_obj.payment_created_date
                        consumer_day = calendar.day_name[payment_created_date.weekday()]
                        if consumer_day== 'Monday' and str(city_front) == str(city_nm) :
                            mon2 = mon2+1
                        elif consumer_day== 'Tuesday' and str(city_front) == str(city_nm) :
                            tue2 = tue2+1
                        elif consumer_day== 'Wednesday' and str(city_front) == str(city_nm):
                            wen2 = wen2+1
                        elif consumer_day== 'Thursday' and str(city_front) == str(city_nm):
                            thus2 = thus2+1
                        elif consumer_day== 'Friday' and str(city_front) == str(city_nm):
                            fri2 = fri2+1
                        elif consumer_day== 'Saturday' and str(city_front) == str(city_nm):
                            sat2 = sat2+1
                        elif consumer_day== 'Sunday' and str(city_front) == str(city_nm):
                            sun2 = sun2+1
                        else :
                            pass


                # ##########.....Todays Login.(3)... for a week  ##########
                count_zero1 = 0
                count_first = 0
                count_second = 0
                count_third = 0

                consumer_list0= ConsumerProfile.objects.filter(last_time_login__regex = ' 0:',city_place_id = city_front).count()
                count_zero1 = count_zero1 + consumer_list0

                for hour in range(0,9):
                    hour = ' 0'+ str(hour) + ':'
                    consumer_list= ConsumerProfile.objects.filter(last_time_login__regex = hour,city_place_id = city_front).count()
                    count_first = count_first + consumer_list
                count_11 = count_first

                for hour in range(9,17):
                    if hour == 9:
                        hour = ' 0'+ str(hour) + ':'
                    else:
                        hour = ' '+ str(hour) + ':'
                    consumer_list1= ConsumerProfile.objects.filter(last_time_login__regex = hour,city_place_id = city_front).count()
                    count_second = count_second + consumer_list1
                count_22 = count_second

                for hour in range(17,24):
                    hour = ' '+ str(hour) + ':'
                    consumer_list2= ConsumerProfile.objects.filter(last_time_login__regex = hour,city_place_id = city_front).count()
                    count_third = count_third + consumer_list2
                count_33 = count_third


                print '..........count_zero..........',count_zero1
                print '..........count_1..........',count_11
                print '..........count_2..........',count_22
                print '..........count_3..........',count_33


                ##########..... New subscription view...(4).... for a week  ##########
                current_date = datetime.now()
                last_date = (datetime.now() - timedelta(days=7))

                list = []
                total_view_list = Business.objects.filter(business_created_date__range=[last_date,current_date])
                mon4=tue4=wen4=thus4=fri4=sat4=sun4=0
                if total_view_list:
                    for view_obj in total_view_list:
                        city_nm = view_obj.supplier.city_place_id.city_id
                        business_created_date=view_obj.business_created_date
                        consumer_day = calendar.day_name[business_created_date.weekday()]
                        if consumer_day== 'Monday' and str(city_front) == str(city_nm):
                            mon4 = mon4+1
                        elif consumer_day== 'Tuesday' and str(city_front) == str(city_nm):
                            tue4 = tue4+1
                        elif consumer_day== 'Wednesday' and str(city_front) == str(city_nm):
                            wen4 = wen4+1
                        elif consumer_day== 'Thursday' and str(city_front) == str(city_nm):
                            thus4 = thus4+1
                        elif consumer_day== 'Friday' and str(city_front) == str(city_nm):
                            fri4 = fri4+1
                        elif consumer_day== 'Saturday' and str(city_front) == str(city_nm):
                            sat4 = sat4+1
                        elif consumer_day== 'Sunday' and str(city_front) == str(city_nm):
                            sun4 = sun4+1
                        else :
                            pass

            data = {'success':'true','jan1':jan1,'feb1':feb1,'mar1':mar1,'apr1':apr1,'may1':may1,'jun1':jun1,'jul1':jul1,
               'aug1':aug1,'sep1':sep1,'oct1':octo1,'nov1':nov1,'dec1':dec1,'mon2':mon2,'tue2':tue2,'wen2':wen2,'thus2':thus2,
               'fri2':fri2,'sat2':sat2,'sun2':sun2,'mon4':mon4,'tue4':tue4,'wen4':wen4,'thus4':thus4,'fri4':fri4,'sat4':sat4,'sun4':sun4,'city_places_list':get_city_places(request),
               'count_zero1':count_zero1,'count_11':count_11,'count_22':count_22,'count_33':count_33}

         
        except IntegrityError as e:
            print e
            data = {'success':'false','message':'Error in  loading page. Please try after some time','username':request.session['login_user']}
    except MySQLdb.OperationalError, e:
        print e
    except Exception,e:
        print 'Exception ',e

    print data
    return HttpResponse(json.dumps(data),content_type='application/json')


@csrf_exempt
def get_admin_stat(request):
    try:
        data = {}
        final_list = []
        final_list1 = []
        try: 
            if request.GET.get('week_var') == 'month' and request.GET.get('citys_var') != 'all':
                print '/........$$$......... month.. &&  city........./'

                var1 = str(request.GET.get('week_var'))
                city_front = request.GET.get('citys_var')

                # Supplier_obj = Supplier.objects.get(supplier_id=request.GET.get('supplier_id'))

                # logo= SERVER_URL + Supplier_obj.logo.url

                #########.............Dashboard Stats...........For a Month................#####
                total_payment_count = 0
                total_new_subscriber = 0
                total_new_booking = 0
                total_advert_expiring    = 0


                current_date = datetime.now()
                first = calendar.day_name[current_date.weekday()]

                last_date = (datetime.now() - timedelta(days=30))
                last_date2 = calendar.day_name[last_date.weekday()]
                #Payment Received
                paymentdetail_list = PaymentDetail.objects.filter(payment_created_date__range=[last_date,current_date])

                for pay_obj in paymentdetail_list:
                    if pay_obj.paid_amount:
                        city_nm = pay_obj.business_id.supplier.city_place_id
                        if str(city_front) == str(city_nm) :
                            paid_amount = pay_obj.paid_amount
                            total_payment_count = total_payment_count + float(paid_amount)
                            



                #New Subscribers
                total_new_subscriber_list = Business.objects.filter(business_created_date__range=[last_date,current_date])
                for subscr_obj in total_new_subscriber_list:
                    city_nm = subscr_obj.supplier.city_place_id
                    if str(city_front) == str(city_nm) :
                        total_new_subscriber = total_new_subscriber + 1

                #New Bookings
                total_new_booking_list = CouponCode.objects.filter(creation_date__range=[last_date,current_date])
                for subscr_obj in total_new_booking_list:
                    city_nm = subscr_obj.advert_id.city_place_id
                    if str(city_front) == str(city_nm) :
                        total_new_booking = total_new_booking + 1
                

                # Adverts Expiring
                current_dt = datetime.now().strftime("%m/%d/%Y")
                last_dt = (datetime.now() + timedelta(days=30)).strftime("%m/%d/%Y")
                total_advert_expiring = Business.objects.filter(end_date__range=[current_dt,last_dt],city_place_id = city_front ).count()

            if request.GET.get('week_var') == 'month' and request.GET.get('citys_var') == 'all':
                print '/.......$$$$..........only month.........../'
                var1 = str(request.GET.get('week_var'))

                # Supplier_obj = Supplier.objects.get(supplier_id=request.GET.get('supplier_id'))

                # logo= SERVER_URL + Supplier_obj.logo.url

                #########.............Dashboard Stats...........For a Month................#####
                total_payment_count = 0
                total_new_subscriber = 0
                total_new_booking = 0
                total_advert_expiring = 0


                current_date = datetime.now()
                first = calendar.day_name[current_date.weekday()]

                last_date = (datetime.now() - timedelta(days=30))
                last_date2 = calendar.day_name[last_date.weekday()]
                #Payment Received
                paymentdetail_list = PaymentDetail.objects.filter(payment_created_date__range=[last_date,current_date])

                for pay_obj in paymentdetail_list:
                    if pay_obj.paid_amount:
                        paid_amount = pay_obj.paid_amount
                        total_payment_count = total_payment_count + float(paid_amount)
                        

                #New Subscribers
                total_new_subscriber = Business.objects.filter(business_created_date__range=[last_date,current_date]).count()
                
                #New Bookings
                total_new_booking = CouponCode.objects.filter(creation_date__range=[last_date,current_date]).count()
 
                # Adverts Expiring
                current_dt = datetime.now().strftime("%m/%d/%Y")
                last_dt = (datetime.now() + timedelta(days=30)).strftime("%m/%d/%Y")
                total_advert_expiring = Business.objects.filter(end_date__range=[current_dt,last_dt]).count()
                print "..#########......total_advert_expiring.........",total_advert_expiring


            if request.GET.get('week_var') == 'week' and request.GET.get('citys_var') != 'all':
                print '/.......$$$.......... week.. &&  city........./'

                var1 = str(request.GET.get('week_var'))
                city_front = request.GET.get('citys_var')

                # Supplier_obj = Supplier.objects.get(supplier_id=request.GET.get('supplier_id'))

                # logo= SERVER_URL + Supplier_obj.logo.url

                #########.............Dashboard Stats...........For a Month................#####
                total_payment_count = 0
                total_new_subscriber = 0
                total_new_booking = 0
                total_advert_expiring    = 0


                current_date = datetime.now()
                first = calendar.day_name[current_date.weekday()]

                last_date = (datetime.now() - timedelta(days=7))
                last_date2 = calendar.day_name[last_date.weekday()]
                #Payment Received
                paymentdetail_list = PaymentDetail.objects.filter(payment_created_date__range=[last_date,current_date])

                for pay_obj in paymentdetail_list:
                    if pay_obj.paid_amount:
                        city_nm = pay_obj.business_id.supplier.city_place_id
                        if str(city_front) == str(city_nm) :
                            paid_amount = pay_obj.paid_amount
                            total_payment_count = total_payment_count + float(paid_amount)


                #New Subscribers
                total_new_subscriber_list = Business.objects.filter(business_created_date__range=[last_date,current_date])
                for subscr_obj in total_new_subscriber_list:
                    city_nm = subscr_obj.supplier.city_place_id
                    if str(city_front) == str(city_nm) :
                        total_new_subscriber = total_new_subscriber + 1
                
                #New Bookings
                total_new_booking_list = CouponCode.objects.filter(creation_date__range=[last_date,current_date])
                for subscr_obj in total_new_booking_list:
                    city_nm = subscr_obj.advert_id.city_place_id
                    if str(city_front) == str(city_nm) :
                        total_new_booking = total_new_booking + 1

                # Adverts Expiring
                current_dt = datetime.now().strftime("%m/%d/%Y")
                last_dt = (datetime.now() + timedelta(days=7)).strftime("%m/%d/%Y")
                total_advert_expiring = Business.objects.filter(end_date__range=[current_dt,last_dt],city_place_id = city_front).count()
                print "..#########......total_advert_expiring.........",total_advert_expiring

            if request.GET.get('week_var') == 'week' and request.GET.get('citys_var') == 'all':
                print '/.......@$$$.......... only week........./'

                var1 = str(request.GET.get('week_var'))

                # Supplier_obj = Supplier.objects.get(supplier_id=request.GET.get('supplier_id'))

                # logo= SERVER_URL + Supplier_obj.logo.url

                #########.............Dashboard Stats...........For a Month................#####
                total_payment_count = 0
                total_new_subscriber = 0
                total_new_booking = 0
                total_advert_expiring = 0


                current_date = datetime.now()
                first = calendar.day_name[current_date.weekday()]

                last_date = (datetime.now() - timedelta(days=7))
                last_date2 = calendar.day_name[last_date.weekday()]
                #Payment Received
                paymentdetail_list = PaymentDetail.objects.filter(payment_created_date__range=[last_date,current_date])

                for pay_obj in paymentdetail_list:
                    if pay_obj.paid_amount:
                        paid_amount = pay_obj.paid_amount
                        total_payment_count = total_payment_count + float(paid_amount)
                        

                #New Subscribers
                total_new_subscriber = Business.objects.filter(business_created_date__range=[last_date,current_date]).count()
                
                #New Bookings
                total_new_booking = CouponCode.objects.filter(creation_date__range=[last_date,current_date]).count()
 
                # Adverts Expiring
                current_dt = datetime.now().strftime("%m/%d/%Y")
                last_dt = (datetime.now() + timedelta(days=7)).strftime("%m/%d/%Y")
                total_advert_expiring = Business.objects.filter(end_date__range=[current_dt,last_dt]).count()
                print "..#########......total_advert_expiring.........",total_advert_expiring



            data = {'var1':var1,'success':'true','total_payment_count':total_payment_count,
                    'total_new_subscriber':total_new_subscriber,
                    'total_new_booking':total_new_booking,
                    'total_advert_expiring':total_advert_expiring}

             

        except IntegrityError as e:
            print e
            data = {'success':'false','message':'Error in  loading page. Please try after some time','username':request.session['login_user']}
    except MySQLdb.OperationalError, e:
        print e
    except Exception,e:
        print 'Exception ',e

    print data
    return HttpResponse(json.dumps(data),content_type='application/json')


@csrf_exempt
def admin_report(request):
    try:
        data = {}
        final_list = []
        final_list1 = []
        try:
            # to find out subscriber list
            subscriber_obj = Supplier.objects.filter(supplier_status = '1')

            # to find last 1 month previous date
            today_date = datetime.now().strftime("%d/%m/%Y")
            dates = today_date.split('/')
            if dates[1] == '1':
                dates[1] = 12
            else:
                dates[1] = int(dates[1]) - 1
                if int(dates[1]) < 10:
                    dates[1] = '0'+str(dates[1])
            pre_date = str(dates[0]) +'/'+dates[1]+'/'+dates[2]

            #to find out logo of supplier
            # Supplier_obj = Supplier.objects.get(supplier_id=request.session['supplier_id'])
            # print "..................Supplier_obj.........",Supplier_obj
            # supplier_id = Supplier_obj.supplier_id

            # logo= SERVER_URL + Supplier_obj.logo.url
            Supplier_list = Supplier.objects.all().values('sales_person_name').distinct()

      

            data = {'success':'true','subscriber_data':subscriber_obj,'Supplier_data':Supplier_list,'today_date':today_date,'pre_date':pre_date,'city_places_list':get_city_places(request)}

        except IntegrityError as e:
            print e
            data = {'success':'false','message':'Error in  loading page. Please try after some time','username':request.session['login_user']}
    except MySQLdb.OperationalError, e:
        print e
    except Exception,e:
        print 'Exception ',e

    print data
    return render(request,'Admin/admin_report.html',data)

####################..............Admin REPORT..............############################

@csrf_exempt
def get_subscriber_list(request):
    city_id = request.GET.get('city_id')
    advert_obj = CategoryCityMap.objects.filter(city_place_id = city_id)
    advert_list = []
    for ad_obj in advert_obj:
        advert_data = {
            'category_id' : ad_obj.category_id.category_id,
            'category_nm' : ad_obj.category_id.category_name,
        }
        advert_list.append(advert_data)


    supplier_obj = Supplier.objects.filter(city_place_id = city_id)
    supplier_list = []
    for supply in supplier_obj:
        supplier_data = {
            'supplier_obj_name' : supply.business_name,
            'supplier_obj_id' : supply.supplier_id
        }
        supplier_list.append(supplier_data)
    data = {
        'success': 'true',
        'supplier_list':supplier_list,
        'advert_list':advert_list
    }
    print data
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def get_catlevel1_list(request):
    cat_id = request.GET.get('cat_id')
    category_lst = CategoryLevel1.objects.filter(parent_category_id = cat_id)
    category1_list = []
    for cat_obj in category_lst:
        cat1_data = {
            'category_id' : cat_obj.category_id,
            'category_nm' : cat_obj.category_name
        }
        category1_list.append(cat1_data)

    data = {
        'success': 'true',
        'category1_list':category1_list
    }
    print data
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def get_catlevel2_list(request):
    cat_id = request.GET.get('cat_id')
    category_lst = CategoryLevel2.objects.filter(parent_category_id = cat_id)
    category2_list = []
    for cat_obj in category_lst:
        cat2_data = {
            'category_id' : cat_obj.category_id,
            'category_nm' : cat_obj.category_name
        }
        category2_list.append(cat2_data)

    data = {
        'success': 'true',
        'category2_list':category2_list
    }
    print data
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def get_catlevel3_list(request):
    cat_id = request.GET.get('cat_id')
    category_lst = CategoryLevel3.objects.filter(parent_category_id = cat_id)
    category3_list = []
    for cat_obj in category_lst:
        cat3_data = {
            'category_id' : cat_obj.category_id,
            'category_nm' : cat_obj.category_name
        }
        category3_list.append(cat3_data)

    data = {
        'success': 'true',
        'category3_list':category3_list
    }
    print data
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def get_catlevel4_list(request):
    cat_id = request.GET.get('cat_id')
    category_lst = CategoryLevel4.objects.filter(parent_category_id = cat_id)
    category4_list = []
    for cat_obj in category_lst:
        cat4_data = {
            'category_id' : cat_obj.category_id,
            'category_nm' : cat_obj.category_name
        }
        category4_list.append(cat4_data)

    data = {
        'success': 'true',
        'category4_list':category4_list
    }
    print data
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def get_catlevel5_list(request):
    cat_id = request.GET.get('cat_id')
    category_lst = CategoryLevel5.objects.filter(parent_category_id = cat_id)
    category5_list = []
    for cat_obj in category_lst:
        cat5_data = {
            'category_id' : cat_obj.category_id,
            'category_nm' : cat_obj.category_name
        }
        category5_list.append(cat5_data)

    data = {
        'success': 'true',
        'category5_list':category5_list
    }
    print data
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def get_advert_list(request):
    supplier_id = request.GET.get('supplier_id')
    advert_obj = Advert.objects.filter(supplier_id = supplier_id)
    advert_list = []
    for advert in advert_obj:
        advert_data = {
            'advert_obj_name' : advert.advert_name,
            'advert_obj_id' : advert.advert_id
        }
        advert_list.append(advert_data)
    data = {
        'success': 'true',
        'advert_list':advert_list
    }
    return HttpResponse(json.dumps(data), content_type='application/json')

def get_advert_table_data(request):
    try:
        data = {}
        final_list = []
        try:
            advert_list = Advert.objects.filter(supplier_id=request.GET.get('sub_id'),category_id=request.GET.get('cat_id'))
            for adve_obj in advert_list: 
                coupon_objs = CouponCode.objects.filter(advert_id=str(adve_obj.advert_id))
                advert_fav_objs = AdvertFavourite.objects.filter(advert_id=str(adve_obj.advert_id))
                advert_like_objs = AdvertLike.objects.filter(advert_id=str(adve_obj.advert_id))
                if adve_obj.advert_views:
                    advert_views = adve_obj.advert_views
                else:
                    advert_views = 0
                advert_data = {
                    'advert_id': adve_obj.advert_id,
                    'advert_title': adve_obj.advert_name,
                    'advert_views': advert_views,
                    'advert_likes': advert_like_objs.count(),
                    'advert_favourites': advert_fav_objs.count(),
                    'advert_calls': '0',
                    'advert_call_backs': '0',
                    'advert_emails': '0',
                    'advert_coupons': coupon_objs.count(),
                    'advert_reviews': '0',
                    'advert_sms': '0',
                    'advert_whatsapp': '0',
                    'advert_facebook': '0',
                    'advert_twitter': '0',
                }
                final_list.append(advert_data)

            data = {'success': 'true', 'data': final_list}
        except IntegrityError as e:
            print e
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception, e:
        print 'Exception ', e
    print final_list
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def get_advert_list1(request):
    supplier_id = request.GET.get('supplier_id')
    cat_id = request.GET.get('cat_id')
    
    advert_obj = Advert.objects.filter(supplier_id = supplier_id,category_id = cat_id)
    advert_list = []
    for advert in advert_obj:
        advert_data = {
            'advert_obj_name' : advert.advert_name,
            'advert_obj_id' : advert.advert_id
        }
        advert_list.append(advert_data)
    data = {
        'success': 'true',
        'advert_list':advert_list
    }
    return HttpResponse(json.dumps(data), content_type='application/json')

def get_advert_table_data1(request):
    try:
        data = {}
        final_list = []
        try:
            advert_list = Advert.objects.filter(supplier_id=request.GET.get('sub_id'),category_id=request.GET.get('cat_id'),category_level_1=request.GET.get('cat1_id'))
            for adve_obj in advert_list: 
                coupon_objs = CouponCode.objects.filter(advert_id=str(adve_obj.advert_id))
                advert_fav_objs = AdvertFavourite.objects.filter(advert_id=str(adve_obj.advert_id))
                advert_like_objs = AdvertLike.objects.filter(advert_id=str(adve_obj.advert_id))
                if adve_obj.advert_views:
                    advert_views = adve_obj.advert_views
                else:
                    advert_views = 0
                advert_data = {
                    'advert_id': adve_obj.advert_id,
                    'advert_title': adve_obj.advert_name,
                    'advert_views': advert_views,
                    'advert_likes': advert_like_objs.count(),
                    'advert_favourites': advert_fav_objs.count(),
                    'advert_calls': '0',
                    'advert_call_backs': '0',
                    'advert_emails': '0',
                    'advert_coupons': coupon_objs.count(),
                    'advert_reviews': '0',
                    'advert_sms': '0',
                    'advert_whatsapp': '0',
                    'advert_facebook': '0',
                    'advert_twitter': '0'
                }
                final_list.append(advert_data)

            data = {'success': 'true', 'data': final_list}
        except IntegrityError as e:
            print e
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def get_advert_list2(request):
    supplier_id = request.GET.get('supplier_id')
    cat_id = request.GET.get('cat_id')
    cat1_id = request.GET.get('cat1_id')
    
    advert_obj = Advert.objects.filter(supplier_id = supplier_id,category_id = cat_id,category_level_1 = cat1_id)
    advert_list = []
    for advert in advert_obj:
        advert_data = {
            'advert_obj_name' : advert.advert_name,
            'advert_obj_id' : advert.advert_id
        }
        advert_list.append(advert_data)
    data = {
        'success': 'true',
        'advert_list':advert_list
    }
    return HttpResponse(json.dumps(data), content_type='application/json')


def get_advert_table_data2(request):
    try:
        data = {}
        final_list = []
        try:
            advert_list = Advert.objects.filter(supplier_id=request.GET.get('sub_id'),category_id=request.GET.get('cat_id'),category_level_1=request.GET.get('cat1_id'),category_level_2=request.GET.get('cat2_id'))
            for adve_obj in advert_list: 
                coupon_objs = CouponCode.objects.filter(advert_id=str(adve_obj.advert_id))
                advert_fav_objs = AdvertFavourite.objects.filter(advert_id=str(adve_obj.advert_id))
                advert_like_objs = AdvertLike.objects.filter(advert_id=str(adve_obj.advert_id))
                if adve_obj.advert_views:
                    advert_views = adve_obj.advert_views
                else:
                    advert_views = 0
                advert_data = {
                    'advert_id': adve_obj.advert_id,
                    'advert_title': adve_obj.advert_name,
                    'advert_views': advert_views,
                    'advert_likes': advert_like_objs.count(),
                    'advert_favourites': advert_fav_objs.count(),
                    'advert_calls': '0',
                    'advert_call_backs': '0',
                    'advert_emails': '0',
                    'advert_coupons': coupon_objs.count(),
                    'advert_reviews': '0',
                    'advert_sms': '0',
                    'advert_whatsapp': '0',
                    'advert_facebook': '0',
                    'advert_twitter': '0'
                }
                final_list.append(advert_data)

            data = {'success': 'true', 'data': final_list}
        except IntegrityError as e:
            print e
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def get_advert_list3(request):
    supplier_id = request.GET.get('supplier_id')
    cat_id = request.GET.get('cat_id')
    cat1_id = request.GET.get('cat1_id')
    cat2_id = request.GET.get('cat2_id')
    advert_obj = Advert.objects.filter(supplier_id = supplier_id,category_id = cat_id,category_level_1 = cat1_id,category_level_2 = cat2_id)
    advert_list = []
    for advert in advert_obj:
        advert_data = {
            'advert_obj_name' : advert.advert_name,
            'advert_obj_id' : advert.advert_id
        }
        advert_list.append(advert_data)
    data = {
        'success': 'true',
        'advert_list':advert_list
    }
    return HttpResponse(json.dumps(data), content_type='application/json')

def get_advert_table_data3(request):
    try:
        data = {}
        final_list = []
        try:
            advert_list = Advert.objects.filter(supplier_id=request.GET.get('sub_id'),category_id=request.GET.get('cat_id'),category_level_1=request.GET.get('cat1_id'),category_level_2=request.GET.get('cat2_id'),category_level_3=request.GET.get('cat3_id'))
            for adve_obj in advert_list: 
                coupon_objs = CouponCode.objects.filter(advert_id=str(adve_obj.advert_id))
                advert_fav_objs = AdvertFavourite.objects.filter(advert_id=str(adve_obj.advert_id))
                advert_like_objs = AdvertLike.objects.filter(advert_id=str(adve_obj.advert_id))
                if adve_obj.advert_views:
                    advert_views = adve_obj.advert_views
                else:
                    advert_views = 0
                advert_data = {
                    'advert_id': adve_obj.advert_id,
                    'advert_title': adve_obj.advert_name,
                    'advert_views': advert_views,
                    'advert_likes': advert_like_objs.count(),
                    'advert_favourites': advert_fav_objs.count(),
                    'advert_calls': '0',
                    'advert_call_backs': '0',
                    'advert_emails': '0',
                    'advert_coupons': coupon_objs.count(),
                    'advert_reviews': '0',
                    'advert_sms': '0',
                    'advert_whatsapp': '0',
                    'advert_facebook': '0',
                    'advert_twitter': '0'
                }
                final_list.append(advert_data)

            data = {'success': 'true', 'data': final_list}
        except IntegrityError as e:
            print e
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def get_advert_list4(request):
    supplier_id = request.GET.get('supplier_id')
    cat_id = request.GET.get('cat_id')
    cat1_id = request.GET.get('cat1_id')
    cat2_id = request.GET.get('cat2_id')
    cat3_id = request.GET.get('cat3_id')
    advert_obj = Advert.objects.filter(supplier_id = supplier_id,category_id = cat_id,category_level_1 = cat1_id,category_level_2 = cat2_id,category_level_3 = cat3_id)
    advert_list = []
    for advert in advert_obj:
        advert_data = {
            'advert_obj_name' : advert.advert_name,
            'advert_obj_id' : advert.advert_id
        }
        advert_list.append(advert_data)
    data = {
        'success': 'true',
        'advert_list':advert_list
    }
    return HttpResponse(json.dumps(data), content_type='application/json')

def get_advert_table_data4(request):
    try:
        data = {}
        final_list = []
        try:
            advert_list = Advert.objects.filter(supplier_id=request.GET.get('sub_id'),category_id=request.GET.get('cat_id'),category_level_1=request.GET.get('cat1_id'),category_level_2=request.GET.get('cat2_id'),category_level_3=request.GET.get('cat3_id'),category_level_4=request.GET.get('cat4_id'))
            for adve_obj in advert_list: 
                coupon_objs = CouponCode.objects.filter(advert_id=str(adve_obj.advert_id))
                advert_fav_objs = AdvertFavourite.objects.filter(advert_id=str(adve_obj.advert_id))
                advert_like_objs = AdvertLike.objects.filter(advert_id=str(adve_obj.advert_id))
                if adve_obj.advert_views:
                    advert_views = adve_obj.advert_views
                else:
                    advert_views = 0
                advert_data = {
                    'advert_id': adve_obj.advert_id,
                    'advert_title': adve_obj.advert_name,
                    'advert_views': advert_views,
                    'advert_likes': advert_like_objs.count(),
                    'advert_favourites': advert_fav_objs.count(),
                    'advert_calls': '0',
                    'advert_call_backs': '0',
                    'advert_emails': '0',
                    'advert_coupons': coupon_objs.count(),
                    'advert_reviews': '0',
                    'advert_sms': '0',
                    'advert_whatsapp': '0',
                    'advert_facebook': '0',
                    'advert_twitter': '0'
                }
                final_list.append(advert_data)

            data = {'success': 'true', 'data': final_list}
        except IntegrityError as e:
            print e
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def get_advert_list5(request):
    supplier_id = request.GET.get('supplier_id')
    cat_id = request.GET.get('cat_id')
    cat1_id = request.GET.get('cat1_id')
    cat2_id = request.GET.get('cat2_id')
    cat3_id = request.GET.get('cat3_id')
    cat4_id = request.GET.get('cat4_id')
    advert_obj = Advert.objects.filter(supplier_id = supplier_id,category_id = cat_id,category_level_1 = cat1_id,category_level_2 = cat2_id,category_level_3 = cat3_id,category_level_4 = cat4_id)
    advert_list = []
    for advert in advert_obj:
        advert_data = {
            'advert_obj_name' : advert.advert_name,
            'advert_obj_id' : advert.advert_id
        }
        advert_list.append(advert_data)
    data = {
        'success': 'true',
        'advert_list':advert_list
    }
    return HttpResponse(json.dumps(data), content_type='application/json')

def get_advert_table_data5(request):
    try:
        data = {}
        final_list = []
        try:
            advert_list = Advert.objects.filter(supplier_id=request.GET.get('sub_id'),category_id=request.GET.get('cat_id'),category_level_1=request.GET.get('cat1_id'),category_level_2=request.GET.get('cat2_id'),category_level_3=request.GET.get('cat3_id'),category_level_4=request.GET.get('cat4_id'),category_level_5=request.GET.get('cat5_id'))
            for adve_obj in advert_list: 
                coupon_objs = CouponCode.objects.filter(advert_id=str(adve_obj.advert_id))
                advert_fav_objs = AdvertFavourite.objects.filter(advert_id=str(adve_obj.advert_id))
                advert_like_objs = AdvertLike.objects.filter(advert_id=str(adve_obj.advert_id))
                if adve_obj.advert_views:
                    advert_views = adve_obj.advert_views
                else:
                    advert_views = 0
                advert_data = {
                    'advert_id': adve_obj.advert_id,
                    'advert_title': adve_obj.advert_name,
                    'advert_views': advert_views,
                    'advert_likes': advert_like_objs.count(),
                    'advert_favourites': advert_fav_objs.count(),
                    'advert_calls': '0',
                    'advert_call_backs': '0',
                    'advert_emails': '0',
                    'advert_coupons': coupon_objs.count(),
                    'advert_reviews': '0',
                    'advert_sms': '0',
                    'advert_whatsapp': '0',
                    'advert_facebook': '0',
                    'advert_twitter': '0'
                }
                final_list.append(advert_data)

            data = {'success': 'true', 'data': final_list}
        except IntegrityError as e:
            print e
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def get_advert_list6(request):
    supplier_id = request.GET.get('supplier_id')
    cat_id = request.GET.get('cat_id')
    cat1_id = request.GET.get('cat1_id')
    cat2_id = request.GET.get('cat2_id')
    cat3_id = request.GET.get('cat3_id')
    cat4_id = request.GET.get('cat4_id')
    cat5_id = request.GET.get('cat5_id')
    advert_obj = Advert.objects.filter(supplier_id = supplier_id,category_id = cat_id,category_level_1 = cat1_id,category_level_2 = cat2_id,category_level_3 = cat3_id,category_level_4 = cat4_id,category_level_5 = cat5_id)
    advert_list = []
    for advert in advert_obj:
        advert_data = {
            'advert_obj_name' : advert.advert_name,
            'advert_obj_id' : advert.advert_id
        }
        advert_list.append(advert_data)
    data = {
        'success': 'true',
        'advert_list':advert_list
    }
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def sub_city_list(request):
    city_id = request.GET.get('city_id')
    advert_obj = CategoryCityMap.objects.filter(city_place_id = city_id)
    advert_list = []
    for ad_obj in advert_obj:
        advert_data = {
            'category_id' : ad_obj.category_id.category_id,
            'category_nm' : ad_obj.category_id.category_name,
        }
        advert_list.append(advert_data)


    supplier_obj = Supplier.objects.filter(city_place_id = city_id)
    supplier_list = []
    for supply in supplier_obj:
        supplier_data = {
            'supplier_obj_name' : supply.business_name,
            'supplier_obj_id' : supply.supplier_id
        }
        supplier_list.append(supplier_data)
    data = {
        'success': 'true',
        'supplier_list':supplier_list,
        'advert_list':advert_list
    }
    print data
    return HttpResponse(json.dumps(data), content_type='application/json')

def get_subtable_data1(request):
    try:
        data = {}
        final_list = []
        try:
            advert_obj = Advert.objects.filter(supplier_id=request.GET.get('sub_id'),category_id=request.GET.get('cat_id'))
            for advert in advert_obj:
                advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=str(advert.advert_id))
                start_date = advert_sub_obj.business_id.start_date
                end_date = advert_sub_obj.business_id.end_date

                pre_ser_obj_list = PremiumService.objects.filter(business_id=str(advert_sub_obj.business_id))
                premium_service, advert_slider, top_advert = 'N/A', 'No', 'No'
                premium_start_date, slider_start_date, top_advert_start_date = 'N/A', 'N/A', 'N/A'
                premium_end_date, slider_end_date, top_advert_end_date = 'N/A', 'N/A', 'N/A'

                for pre_ser_obj in pre_ser_obj_list:
                    if pre_ser_obj.premium_service_name != "Advert Slider" and pre_ser_obj.premium_service_name != "Top Advert":
                        premium_service = pre_ser_obj.premium_service_name
                        premium_start_date = pre_ser_obj.start_date
                        premium_end_date = pre_ser_obj.end_date
                    if pre_ser_obj.premium_service_name == "Advert Slider":
                        advert_slider = 'Yes'
                        slider_start_date = pre_ser_obj.start_date
                        slider_end_date = pre_ser_obj.end_date
                    if pre_ser_obj.premium_service_name == "Top Advert":
                        top_advert = 'No'
                        top_advert_start_date = pre_ser_obj.start_date
                        top_advert_end_date = pre_ser_obj.end_date
                try:
                    payment_obj = PaymentDetail.objects.get(business_id=str(advert_sub_obj.business_id))
                    if payment_obj.total_amount:
                        total_amount = payment_obj.payable_amount
                    else:
                        total_amount = 0
                    if payment_obj.paid_amount:
                        paid_amount = payment_obj.paid_amount
                    else:
                        paid_amount = 0
                except Exception as e:
                    total_amount = 0
                    paid_amount = 0
                video_count = Advert_Video.objects.filter(advert_id=str(advert_sub_obj.advert_id)).count()
                image_count = AdvertImage.objects.filter(advert_id=str(advert_sub_obj.advert_id)).count()

                advert_data = {
                    'advert_id': str(advert_sub_obj.advert_id),
                    'advert_title': advert_sub_obj.advert_id.advert_name,
                    'category': advert_sub_obj.advert_id.category_id.category_name,
                    'start_date': start_date,
                    'end_date': end_date,
                    'premium_service': premium_service,
                    'premium_start_date': premium_start_date,
                    'premium_end_date': premium_end_date,
                    'advert_slider': advert_slider,
                    'slider_start_date': slider_start_date,
                    'slider_end_date': slider_end_date,
                    'top_advert': top_advert,
                    'top_advert_start_date': top_advert_start_date,
                    'top_advert_end_date': top_advert_end_date,
                    'uploaded_pictures': image_count,
                    'uploaded_videos': video_count,
                    'memory_usages': '0',
                    'total_service_cost': total_amount,
                    'total_amount_paid': paid_amount,
                    'saleman_name': '',
                    'saleman_number': ''
                }
                final_list.append(advert_data)
            data = {'success': 'true', 'data': final_list}

        except IntegrityError as e:
            print e
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')


def get_subtable_data2(request):
    try:
        data = {}
        final_list = []
        try:
            advert_obj = Advert.objects.filter(supplier_id=request.GET.get('sub_id'),category_id=request.GET.get('cat_id'),category_level_1=request.GET.get('cat_id1'))
            for advert in advert_obj:
                advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=str(advert.advert_id))
                start_date = advert_sub_obj.business_id.start_date
                end_date = advert_sub_obj.business_id.end_date

                pre_ser_obj_list = PremiumService.objects.filter(business_id=str(advert_sub_obj.business_id))
                premium_service, advert_slider, top_advert = 'N/A', 'No', 'No'
                premium_start_date, slider_start_date, top_advert_start_date = 'N/A', 'N/A', 'N/A'
                premium_end_date, slider_end_date, top_advert_end_date = 'N/A', 'N/A', 'N/A'

                for pre_ser_obj in pre_ser_obj_list:
                    if pre_ser_obj.premium_service_name != "Advert Slider" and pre_ser_obj.premium_service_name != "Top Advert":
                        premium_service = pre_ser_obj.premium_service_name
                        premium_start_date = pre_ser_obj.start_date
                        premium_end_date = pre_ser_obj.end_date
                    if pre_ser_obj.premium_service_name == "Advert Slider":
                        advert_slider = 'Yes'
                        slider_start_date = pre_ser_obj.start_date
                        slider_end_date = pre_ser_obj.end_date
                    if pre_ser_obj.premium_service_name == "Top Advert":
                        top_advert = 'No'
                        top_advert_start_date = pre_ser_obj.start_date
                        top_advert_end_date = pre_ser_obj.end_date
                try:
                    payment_obj = PaymentDetail.objects.get(business_id=str(advert_sub_obj.business_id))
                    if payment_obj.total_amount:
                        total_amount = payment_obj.payable_amount
                    else:
                        total_amount = 0
                    if payment_obj.paid_amount:
                        paid_amount = payment_obj.paid_amount
                    else:
                        paid_amount = 0
                except Exception as e:
                    total_amount = 0
                    paid_amount = 0
                video_count = Advert_Video.objects.filter(advert_id=str(advert_sub_obj.advert_id)).count()
                image_count = AdvertImage.objects.filter(advert_id=str(advert_sub_obj.advert_id)).count()

                advert_data = {
                    'advert_id': str(advert_sub_obj.advert_id),
                    'advert_title': advert_sub_obj.advert_id.advert_name,
                    'category': advert_sub_obj.advert_id.category_id.category_name,
                    'start_date': start_date,
                    'end_date': end_date,
                    'premium_service': premium_service,
                    'premium_start_date': premium_start_date,
                    'premium_end_date': premium_end_date,
                    'advert_slider': advert_slider,
                    'slider_start_date': slider_start_date,
                    'slider_end_date': slider_end_date,
                    'top_advert': top_advert,
                    'top_advert_start_date': top_advert_start_date,
                    'top_advert_end_date': top_advert_end_date,
                    'uploaded_pictures': image_count,
                    'uploaded_videos': video_count,
                    'memory_usages': '0',
                    'total_service_cost': total_amount,
                    'total_amount_paid': paid_amount,
                    'saleman_name': '',
                    'saleman_number': ''
                }
                final_list.append(advert_data)
            data = {'success': 'true', 'data': final_list}

        except IntegrityError as e:
            print e
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')

def get_subtable_data3(request):
    try:
        data = {}
        final_list = []
        try:
            advert_obj = Advert.objects.filter(supplier_id=request.GET.get('sub_id'),category_id=request.GET.get('cat_id'),category_level_1=request.GET.get('cat_id1'),category_level_2=request.GET.get('cat_id2'))
            for advert in advert_obj:
                advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=str(advert.advert_id))
                start_date = advert_sub_obj.business_id.start_date
                end_date = advert_sub_obj.business_id.end_date

                pre_ser_obj_list = PremiumService.objects.filter(business_id=str(advert_sub_obj.business_id))
                premium_service, advert_slider, top_advert = 'N/A', 'No', 'No'
                premium_start_date, slider_start_date, top_advert_start_date = 'N/A', 'N/A', 'N/A'
                premium_end_date, slider_end_date, top_advert_end_date = 'N/A', 'N/A', 'N/A'

                for pre_ser_obj in pre_ser_obj_list:
                    if pre_ser_obj.premium_service_name != "Advert Slider" and pre_ser_obj.premium_service_name != "Top Advert":
                        premium_service = pre_ser_obj.premium_service_name
                        premium_start_date = pre_ser_obj.start_date
                        premium_end_date = pre_ser_obj.end_date
                    if pre_ser_obj.premium_service_name == "Advert Slider":
                        advert_slider = 'Yes'
                        slider_start_date = pre_ser_obj.start_date
                        slider_end_date = pre_ser_obj.end_date
                    if pre_ser_obj.premium_service_name == "Top Advert":
                        top_advert = 'No'
                        top_advert_start_date = pre_ser_obj.start_date
                        top_advert_end_date = pre_ser_obj.end_date
                try:
                    payment_obj = PaymentDetail.objects.get(business_id=str(advert_sub_obj.business_id))
                    if payment_obj.total_amount:
                        total_amount = payment_obj.payable_amount
                    else:
                        total_amount = 0
                    if payment_obj.paid_amount:
                        paid_amount = payment_obj.paid_amount
                    else:
                        paid_amount = 0
                except Exception as e:
                    total_amount = 0
                    paid_amount = 0
                video_count = Advert_Video.objects.filter(advert_id=str(advert_sub_obj.advert_id)).count()
                image_count = AdvertImage.objects.filter(advert_id=str(advert_sub_obj.advert_id)).count()

                advert_data = {
                    'advert_id': str(advert_sub_obj.advert_id),
                    'advert_title': advert_sub_obj.advert_id.advert_name,
                    'category': advert_sub_obj.advert_id.category_id.category_name,
                    'start_date': start_date,
                    'end_date': end_date,
                    'premium_service': premium_service,
                    'premium_start_date': premium_start_date,
                    'premium_end_date': premium_end_date,
                    'advert_slider': advert_slider,
                    'slider_start_date': slider_start_date,
                    'slider_end_date': slider_end_date,
                    'top_advert': top_advert,
                    'top_advert_start_date': top_advert_start_date,
                    'top_advert_end_date': top_advert_end_date,
                    'uploaded_pictures': image_count,
                    'uploaded_videos': video_count,
                    'memory_usages': '0',
                    'total_service_cost': total_amount,
                    'total_amount_paid': paid_amount,
                    'saleman_name': '',
                    'saleman_number': ''
                }
                final_list.append(advert_data)
            data = {'success': 'true', 'data': final_list}

        except IntegrityError as e:
            print e
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')

def get_subtable_data4(request):
    try:
        data = {}
        final_list = []
        try:
            advert_obj = Advert.objects.filter(supplier_id=request.GET.get('sub_id'),category_id=request.GET.get('cat_id'),category_level_1=request.GET.get('cat_id1'),category_level_3=request.GET.get('cat_id3'),category_level_4=request.GET.get('cat_id4'))
            for advert in advert_obj:
                advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=str(advert.advert_id))
                start_date = advert_sub_obj.business_id.start_date
                end_date = advert_sub_obj.business_id.end_date

                pre_ser_obj_list = PremiumService.objects.filter(business_id=str(advert_sub_obj.business_id))
                premium_service, advert_slider, top_advert = 'N/A', 'No', 'No'
                premium_start_date, slider_start_date, top_advert_start_date = 'N/A', 'N/A', 'N/A'
                premium_end_date, slider_end_date, top_advert_end_date = 'N/A', 'N/A', 'N/A'

                for pre_ser_obj in pre_ser_obj_list:
                    if pre_ser_obj.premium_service_name != "Advert Slider" and pre_ser_obj.premium_service_name != "Top Advert":
                        premium_service = pre_ser_obj.premium_service_name
                        premium_start_date = pre_ser_obj.start_date
                        premium_end_date = pre_ser_obj.end_date
                    if pre_ser_obj.premium_service_name == "Advert Slider":
                        advert_slider = 'Yes'
                        slider_start_date = pre_ser_obj.start_date
                        slider_end_date = pre_ser_obj.end_date
                    if pre_ser_obj.premium_service_name == "Top Advert":
                        top_advert = 'No'
                        top_advert_start_date = pre_ser_obj.start_date
                        top_advert_end_date = pre_ser_obj.end_date
                try:
                    payment_obj = PaymentDetail.objects.get(business_id=str(advert_sub_obj.business_id))
                    if payment_obj.total_amount:
                        total_amount = payment_obj.payable_amount
                    else:
                        total_amount = 0
                    if payment_obj.paid_amount:
                        paid_amount = payment_obj.paid_amount
                    else:
                        paid_amount = 0
                except Exception as e:
                    total_amount = 0
                    paid_amount = 0
                video_count = Advert_Video.objects.filter(advert_id=str(advert_sub_obj.advert_id)).count()
                image_count = AdvertImage.objects.filter(advert_id=str(advert_sub_obj.advert_id)).count()

                advert_data = {
                    'advert_id': str(advert_sub_obj.advert_id),
                    'advert_title': advert_sub_obj.advert_id.advert_name,
                    'category': advert_sub_obj.advert_id.category_id.category_name,
                    'start_date': start_date,
                    'end_date': end_date,
                    'premium_service': premium_service,
                    'premium_start_date': premium_start_date,
                    'premium_end_date': premium_end_date,
                    'advert_slider': advert_slider,
                    'slider_start_date': slider_start_date,
                    'slider_end_date': slider_end_date,
                    'top_advert': top_advert,
                    'top_advert_start_date': top_advert_start_date,
                    'top_advert_end_date': top_advert_end_date,
                    'uploaded_pictures': image_count,
                    'uploaded_videos': video_count,
                    'memory_usages': '0',
                    'total_service_cost': total_amount,
                    'total_amount_paid': paid_amount,
                    'saleman_name': '',
                    'saleman_number': ''
                }
                final_list.append(advert_data)
            data = {'success': 'true', 'data': final_list}

        except IntegrityError as e:
            print e
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')

def get_subtable_data5(request):
    try:
        data = {}
        final_list = []
        try:
            advert_obj = Advert.objects.filter(supplier_id=request.GET.get('sub_id'),category_id=request.GET.get('cat_id'),category_level_1=request.GET.get('cat_id1'),category_level_3=request.GET.get('cat_id3'),category_level_4=request.GET.get('cat_id4'),category_level_5=request.GET.get('cat_id5'))
            for advert in advert_obj:
                advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=str(advert.advert_id))
                start_date = advert_sub_obj.business_id.start_date
                end_date = advert_sub_obj.business_id.end_date

                pre_ser_obj_list = PremiumService.objects.filter(business_id=str(advert_sub_obj.business_id))
                premium_service, advert_slider, top_advert = 'N/A', 'No', 'No'
                premium_start_date, slider_start_date, top_advert_start_date = 'N/A', 'N/A', 'N/A'
                premium_end_date, slider_end_date, top_advert_end_date = 'N/A', 'N/A', 'N/A'

                for pre_ser_obj in pre_ser_obj_list:
                    if pre_ser_obj.premium_service_name != "Advert Slider" and pre_ser_obj.premium_service_name != "Top Advert":
                        premium_service = pre_ser_obj.premium_service_name
                        premium_start_date = pre_ser_obj.start_date
                        premium_end_date = pre_ser_obj.end_date
                    if pre_ser_obj.premium_service_name == "Advert Slider":
                        advert_slider = 'Yes'
                        slider_start_date = pre_ser_obj.start_date
                        slider_end_date = pre_ser_obj.end_date
                    if pre_ser_obj.premium_service_name == "Top Advert":
                        top_advert = 'No'
                        top_advert_start_date = pre_ser_obj.start_date
                        top_advert_end_date = pre_ser_obj.end_date
                try:
                    payment_obj = PaymentDetail.objects.get(business_id=str(advert_sub_obj.business_id))
                    if payment_obj.total_amount:
                        total_amount = payment_obj.payable_amount
                    else:
                        total_amount = 0
                    if payment_obj.paid_amount:
                        paid_amount = payment_obj.paid_amount
                    else:
                        paid_amount = 0
                except Exception as e:
                    total_amount = 0
                    paid_amount = 0
                video_count = Advert_Video.objects.filter(advert_id=str(advert_sub_obj.advert_id)).count()
                image_count = AdvertImage.objects.filter(advert_id=str(advert_sub_obj.advert_id)).count()

                advert_data = {
                    'advert_id': str(advert_sub_obj.advert_id),
                    'advert_title': advert_sub_obj.advert_id.advert_name,
                    'category': advert_sub_obj.advert_id.category_id.category_name,
                    'start_date': start_date,
                    'end_date': end_date,
                    'premium_service': premium_service,
                    'premium_start_date': premium_start_date,
                    'premium_end_date': premium_end_date,
                    'advert_slider': advert_slider,
                    'slider_start_date': slider_start_date,
                    'slider_end_date': slider_end_date,
                    'top_advert': top_advert,
                    'top_advert_start_date': top_advert_start_date,
                    'top_advert_end_date': top_advert_end_date,
                    'uploaded_pictures': image_count,
                    'uploaded_videos': video_count,
                    'memory_usages': '0',
                    'total_service_cost': total_amount,
                    'total_amount_paid': paid_amount,
                    'saleman_name': '',
                    'saleman_number': ''
                }
                final_list.append(advert_data)
            data = {'success': 'true', 'data': final_list}

        except IntegrityError as e:
            print e
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')


def get_advert_health_citybase(request):
    try:
        data = {}
        final_list = []
        try:
            from_date = request.GET.get('from_date')
            to_date = request.GET.get('to_date')
            from_date = datetime.strptime(from_date, "%d/%m/%Y")
            to_date = datetime.strptime(to_date, "%d/%m/%Y")
            from_date = from_date.strftime("%Y-%m-%d")
            to_date = to_date.strftime("%Y-%m-%d")
            advert_list = Advert.objects.filter(city_place_id=request.GET.get('city_id'),creation_date__range=[from_date, to_date])
            for adv_obj in advert_list :
                coupon_objs = CouponCode.objects.filter(advert_id=str(adv_obj.advert_id))
                advert_fav_objs = AdvertFavourite.objects.filter(advert_id=str(adv_obj.advert_id))
                advert_like_objs = AdvertLike.objects.filter(advert_id=str(adv_obj.advert_id))
                if adv_obj.advert_views:
                    advert_views = adv_obj.advert_views
                else:
                    advert_views = 0
                advert_data = {
                    'advert_id': adv_obj.advert_id,
                    'advert_title': adv_obj.advert_name,
                    'advert_views': advert_views,
                    'advert_likes': advert_like_objs.count(),
                    'advert_favourites': advert_fav_objs.count(),
                    'advert_calls': '0',
                    'advert_call_backs': '0',
                    'advert_emails': '0',
                    'advert_coupons': coupon_objs.count(),
                    'advert_reviews': '0',
                    'advert_sms': '0',
                    'advert_whatsapp': '0',
                    'advert_facebook': '0',
                    'advert_twitter': '0'
                }
                final_list.append(advert_data)

            data = {'success': 'true', 'data': final_list}
        except IntegrityError as e:
            print e
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')

def get_subscription_plan_citybase(request):
    try:
        data = {}
        final_list = []
        try:
            advert_obj = Advert.objects.filter(city_place_id=request.GET.get('city_id'))
            for advert in advert_obj:
                advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=str(advert.advert_id))
                start_date = advert_sub_obj.business_id.start_date
                end_date = advert_sub_obj.business_id.end_date

                pre_ser_obj_list = PremiumService.objects.filter(business_id=str(advert_sub_obj.business_id))
                premium_service, advert_slider, top_advert = 'N/A', 'No', 'No'
                premium_start_date, slider_start_date, top_advert_start_date = 'N/A', 'N/A', 'N/A'
                premium_end_date, slider_end_date, top_advert_end_date = 'N/A', 'N/A', 'N/A'

                for pre_ser_obj in pre_ser_obj_list:
                    if pre_ser_obj.premium_service_name != "Advert Slider" and pre_ser_obj.premium_service_name != "Top Advert":
                        premium_service = pre_ser_obj.premium_service_name
                        premium_start_date = pre_ser_obj.start_date
                        premium_end_date = pre_ser_obj.end_date
                    if pre_ser_obj.premium_service_name == "Advert Slider":
                        advert_slider = 'Yes'
                        slider_start_date = pre_ser_obj.start_date
                        slider_end_date = pre_ser_obj.end_date
                    if pre_ser_obj.premium_service_name == "Top Advert":
                        top_advert = 'No'
                        top_advert_start_date = pre_ser_obj.start_date
                        top_advert_end_date = pre_ser_obj.end_date
                try:
                    payment_obj = PaymentDetail.objects.get(business_id=str(advert_sub_obj.business_id))
                    if payment_obj.total_amount:
                        total_amount = payment_obj.payable_amount
                    else:
                        total_amount = 0
                    if payment_obj.paid_amount:
                        paid_amount = payment_obj.paid_amount
                    else:
                        paid_amount = 0
                except Exception as e:
                    total_amount = 0
                    paid_amount = 0
                video_count = Advert_Video.objects.filter(advert_id=str(advert_sub_obj.advert_id)).count()
                image_count = AdvertImage.objects.filter(advert_id=str(advert_sub_obj.advert_id)).count()

                advert_data = {
                    'advert_id': str(advert_sub_obj.advert_id),
                    'advert_title': advert_sub_obj.advert_id.advert_name,
                    'category': advert_sub_obj.advert_id.category_id.category_name,
                    'start_date': start_date,
                    'end_date': end_date,
                    'premium_service': premium_service,
                    'premium_start_date': premium_start_date,
                    'premium_end_date': premium_end_date,
                    'advert_slider': advert_slider,
                    'slider_start_date': slider_start_date,
                    'slider_end_date': slider_end_date,
                    'top_advert': top_advert,
                    'top_advert_start_date': top_advert_start_date,
                    'top_advert_end_date': top_advert_end_date,
                    'uploaded_pictures': image_count,
                    'uploaded_videos': video_count,
                    'memory_usages': '0',
                    'total_service_cost': total_amount,
                    'total_amount_paid': paid_amount,
                    'saleman_name': '',
                    'saleman_number': ''
                }
                final_list.append(advert_data)

            data = {'success': 'true', 'data': final_list}
        except IntegrityError as e:
            print e
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')

def get_advert_health_datebase(request):
    try:
        data = {}
        final_list = []
        try:
            from_date = request.GET.get('from_date')
            to_date = request.GET.get('to_date')
            from_date = datetime.strptime(from_date, "%d/%m/%Y")
            to_date = datetime.strptime(to_date, "%d/%m/%Y")
            from_date = from_date.strftime("%Y-%m-%d")
            to_date = to_date.strftime("%Y-%m-%d")

            advert_list = Advert.objects.filter(status = '1',creation_date__range=[from_date, to_date])
            for advert in advert_list:
                coupon_objs = CouponCode.objects.filter(advert_id = str(advert.advert_id))
                advert_fav_objs = AdvertFavourite.objects.filter(advert_id = str(advert.advert_id))
                advert_like_objs = AdvertLike.objects.filter(advert_id = str(advert.advert_id))
                if advert.advert_views:
                    advert_views = advert.advert_views
                else:
                    advert_views = 0
                advert_data={
                    'advert_id':advert.advert_id,
                    'advert_title':advert.advert_name,
                    'advert_views':advert_views,
                    'advert_likes':advert_like_objs.count(),
                    'advert_favourites':advert_fav_objs.count(),
                    'advert_calls':'0',
                    'advert_call_backs':'0',
                    'advert_emails':'0',
                    'advert_coupons':coupon_objs.count(),
                    'advert_reviews':'0',
                    'advert_sms':'0',
                    'advert_whatsapp':'0',
                    'advert_facebook':'0',
                    'advert_twitter': '0'
                }
                final_list.append(advert_data)
            data = {'success': 'true', 'data': final_list}
        except IntegrityError as e:
            print e
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception, e:
        print 'Exception ', e
    print data
    return HttpResponse(json.dumps(data), content_type='application/json')

def get_advert_health_supplierbase(request):
    try:
        data = {}
        final_list = []
        try:
            from_date = request.GET.get('from_date')
            to_date = request.GET.get('to_date')
            from_date = datetime.strptime(from_date, "%d/%m/%Y")
            to_date = datetime.strptime(to_date, "%d/%m/%Y")
            from_date = from_date.strftime("%Y-%m-%d")
            to_date = to_date.strftime("%Y-%m-%d")
            advert = Advert.objects.filter(supplier_id=request.GET.get('sub_id'))
            for ad_ob in advert:
                coupon_objs = CouponCode.objects.filter(advert_id=str(ad_ob.advert_id),creation_date__range=[from_date,to_date])
                advert_fav_objs = AdvertFavourite.objects.filter(advert_id=str(ad_ob.advert_id),creation_date__range=[from_date,to_date])
                advert_like_objs = AdvertLike.objects.filter(advert_id=str(ad_ob.advert_id),creation_date__range=[from_date,to_date])
                if ad_ob.advert_views:
                    advert_views = ad_ob.advert_views
                else:
                    advert_views = 0
                advert_data = {
                    'advert_id': ad_ob.advert_id,
                    'advert_title': ad_ob.advert_name,
                    'advert_views': advert_views,
                    'advert_likes': advert_like_objs.count(),
                    'advert_favourites': advert_fav_objs.count(),
                    'advert_calls': '0',
                    'advert_call_backs': '0',
                    'advert_emails': '0',
                    'advert_coupons': coupon_objs.count(),
                    'advert_reviews': '0',
                    'advert_sms': '0',
                    'advert_whatsapp': '0',
                    'advert_facebook': '0',
                    'advert_twitter': '0'
                }
                final_list.append(advert_data)
                print final_list

            data = {'success': 'true', 'data': final_list}
        except IntegrityError as e:
            print e
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')

def get_subscription_plan_supplier(request):
    try:
        data = {}
        final_list = []
        try:
            business_obj = Business.objects.filter(supplier=request.GET.get('sub_id'))
            for business in business_obj:   
                advert_sub_obj = AdvertSubscriptionMap.objects.get(business_id=str(business.business_id))
                start_date = advert_sub_obj.business_id.start_date
                end_date = advert_sub_obj.business_id.end_date

                pre_ser_obj_list = PremiumService.objects.filter(business_id=str(advert_sub_obj.business_id))
                premium_service, advert_slider, top_advert = 'N/A', 'No', 'No'
                premium_start_date, slider_start_date, top_advert_start_date = 'N/A', 'N/A', 'N/A'
                premium_end_date, slider_end_date, top_advert_end_date = 'N/A', 'N/A', 'N/A'

                for pre_ser_obj in pre_ser_obj_list:
                    if pre_ser_obj.premium_service_name != "Advert Slider" and pre_ser_obj.premium_service_name != "Top Advert":
                        premium_service = pre_ser_obj.premium_service_name
                        premium_start_date = pre_ser_obj.start_date
                        premium_end_date = pre_ser_obj.end_date
                    if pre_ser_obj.premium_service_name == "Advert Slider":
                        advert_slider = 'Yes'
                        slider_start_date = pre_ser_obj.start_date
                        slider_end_date = pre_ser_obj.end_date
                    if pre_ser_obj.premium_service_name == "Top Advert":
                        top_advert = 'No'
                        top_advert_start_date = pre_ser_obj.start_date
                        top_advert_end_date = pre_ser_obj.end_date
                try:
                    payment_obj = PaymentDetail.objects.get(business_id=str(advert_sub_obj.business_id))
                    if payment_obj.total_amount:
                        total_amount = payment_obj.payable_amount
                    else:
                        total_amount = 0
                    if payment_obj.paid_amount:
                        paid_amount = payment_obj.paid_amount
                    else:
                        paid_amount = 0
                except Exception as e:
                    total_amount = 0
                    paid_amount = 0
                video_count = Advert_Video.objects.filter(advert_id=str(advert_sub_obj.advert_id)).count()
                image_count = AdvertImage.objects.filter(advert_id=str(advert_sub_obj.advert_id)).count()

                advert_data = {
                    'advert_id': str(advert_sub_obj.advert_id),
                    'advert_title': advert_sub_obj.advert_id.advert_name,
                    'category': advert_sub_obj.advert_id.category_id.category_name,
                    'start_date': start_date,
                    'end_date': end_date,
                    'premium_service': premium_service,
                    'premium_start_date': premium_start_date,
                    'premium_end_date': premium_end_date,
                    'advert_slider': advert_slider,
                    'slider_start_date': slider_start_date,
                    'slider_end_date': slider_end_date,
                    'top_advert': top_advert,
                    'top_advert_start_date': top_advert_start_date,
                    'top_advert_end_date': top_advert_end_date,
                    'uploaded_pictures': image_count,
                    'uploaded_videos': video_count,
                    'memory_usages': '0',
                    'total_service_cost': total_amount,
                    'total_amount_paid': paid_amount,
                    'saleman_name': '',
                    'saleman_number': ''
                }
                final_list.append(advert_data)

            data = {'success': 'true', 'data': final_list}
        except IntegrityError as e:
            print e
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')


def get_sales(request):
    try:
        data = {}
        final_list = []
        try:
            if request.GET.get('sales_nm'): 
                from_date = request.GET.get('from_date')
                to_date = request.GET.get('to_date')
                print from_date,to_date
                from_date = datetime.strptime(from_date, "%d/%m/%Y")
                to_date = datetime.strptime(to_date, "%d/%m/%Y") + timedelta(days=1)
                from_date = from_date.strftime("%Y-%m-%d")
                to_date = to_date.strftime("%Y-%m-%d")


                Supplier_list = Supplier.objects.filter(supplier_created_date__range=[from_date, to_date],sales_person_name = request.GET.get('sales_nm'))
                print Supplier_list

                for supp_obj in Supplier_list:
                    sales_person_name = supp_obj.sales_person_name
                    area = supp_obj.area
                    city_place = supp_obj.city_place_id.city_id.city_name
                    business_name = supp_obj.business_name
                    supplier_id = supp_obj.supplier_id

                    business_list = Business.objects.filter(supplier = supplier_id)

                    for bus_obj in  business_list:
                        business_id = bus_obj.business_id
                        payment_obj = PaymentDetail.objects.get(business_id = business_id)
                        payment_date = payment_obj.payment_created_date
                        if payment_obj.total_amount:
                            total_ser_cost = payment_obj.total_amount
                        else:
                            total_ser_cost = 0
                        if payment_obj.paid_amount:   
                            total_pay_amt = payment_obj.paid_amount
                        else:
                            total_pay_amt = 0

                        advert_obj = AdvertSubscriptionMap.objects.get(business_id = business_id)
                        
                        advert_name = advert_obj.advert_id.advert_name
                        category_level_1 = advert_obj.advert_id.category_level_1.category_name
                        category_level_2 = advert_obj.advert_id.category_level_2.category_name

                        consumer_data={
                            'sales_by':sales_person_name,
                            'title':advert_name,
                            'busi_name':business_name,
                            'Area':area,
                            'City':city_place,
                            'cat_L1':category_level_1,
                            'cat_L2':category_level_2,
                            'sold_date':'sws',
                            'ser_cost':total_ser_cost,
                            'pay_amt':total_pay_amt,
                            'pay_date':payment_date
                        }
                        final_list.append(consumer_data)
            else :
                from_date = request.GET.get('from_date')
                to_date = request.GET.get('to_date')
                print from_date,to_date
                from_date = datetime.strptime(from_date, "%d/%m/%Y")
                to_date = datetime.strptime(to_date, "%d/%m/%Y") + timedelta(days=1)
                from_date = from_date.strftime("%Y-%m-%d")
                to_date = to_date.strftime("%Y-%m-%d")

                Supplier_list = Supplier.objects.filter(supplier_created_date__range=[from_date, to_date])
                print Supplier_list

                for supp_obj in Supplier_list:
                    sales_person_name = supp_obj.sales_person_name
                    area = supp_obj.area
                    city_place = supp_obj.city_place_id.city_id.city_name
                    business_name = supp_obj.business_name
                    supplier_id = supp_obj.supplier_id

                    business_list = Business.objects.filter(supplier = supplier_id)

                    for bus_obj in  business_list:
                        business_id = bus_obj.business_id
                        payment_obj = PaymentDetail.objects.get(business_id = business_id)
                        payment_date = payment_obj.payment_created_date
                        if payment_obj.total_amount:
                            total_ser_cost = payment_obj.total_amount
                        else:
                            total_ser_cost = 0
                        if payment_obj.paid_amount:   
                            total_pay_amt = payment_obj.paid_amount
                        else:
                            total_pay_amt = 0

                        advert_obj = AdvertSubscriptionMap.objects.get(business_id = business_id)
                        
                        advert_name = advert_obj.advert_id.advert_name
                        category_level_1 = advert_obj.advert_id.category_level_1.category_name
                        category_level_2 = advert_obj.advert_id.category_level_2.category_name

                        consumer_data={
                            'sales_by':sales_person_name,
                            'title':advert_name,
                            'busi_name':business_name,
                            'Area':area,
                            'City':city_place,
                            'cat_L1':category_level_1,
                            'cat_L2':category_level_2,
                            'sold_date':'sws',
                            'ser_cost':total_ser_cost,
                            'pay_amt':total_pay_amt,
                            'pay_date':payment_date
                        }
                        final_list.append(consumer_data)
            data = {'success': 'true', 'data': final_list}
        except Exception as e:
            print e
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')


def get_new_sub_data(request):
    try:
        data = {}
        final_list = []
        try:
            if request.GET.get('sales_nm'): 
                from_date = request.GET.get('from_date')
                to_date = request.GET.get('to_date')
                from_date = datetime.strptime(from_date, "%d/%m/%Y")
                to_date = datetime.strptime(to_date, "%d/%m/%Y") + timedelta(days=1)
                from_date = from_date.strftime("%Y-%m-%d")
                to_date = to_date.strftime("%Y-%m-%d")

                Supplier_list = Supplier.objects.filter(supplier_created_date__range=[from_date, to_date],sales_person_name = request.GET.get('sales_nm'))
                print Supplier_list

                for supp_obj in Supplier_list:
                    sales_person_name = supp_obj.sales_person_name
                    area = supp_obj.area
                    city_place = supp_obj.city_place_id.city_id.city_name
                    business_name = supp_obj.business_name
                    supplier_id = supp_obj.supplier_id

                    business_list = Business.objects.filter(supplier = supplier_id)

                    for bus_obj in  business_list:
                        business_id = bus_obj.business_id

                        advert_obj = AdvertSubscriptionMap.objects.get(business_id = business_id)
                        
                        status = advert_obj.advert_id.status
                        if status == '1':
                            category_level_1 = advert_obj.advert_id.category_level_1.category_name
                            category_level_2 = advert_obj.advert_id.category_level_2.category_name
                        else :
                            category_level_1 = ''
                            category_level_2 = ''

                        consumer_data={
                            'sales_by':sales_person_name,
                            'busi_name':business_name,
                            'Area':area,
                            'City':city_place,
                            'cat_L1':category_level_1,
                            'cat_L2':category_level_2,
                            'pend_pay':'sws'
                        }
                        final_list.append(consumer_data)
            else :
                from_date = request.GET.get('from_date')
                to_date = request.GET.get('to_date')
                print from_date,to_date
                from_date = datetime.strptime(from_date, "%d/%m/%Y")
                to_date = datetime.strptime(to_date, "%d/%m/%Y") + timedelta(days=1)
                from_date = from_date.strftime("%Y-%m-%d")
                to_date = to_date.strftime("%Y-%m-%d")

                Supplier_list = Supplier.objects.filter(supplier_created_date__range=[from_date, to_date])
                print Supplier_list

                for supp_obj in Supplier_list:
                    sales_person_name = supp_obj.sales_person_name
                    area = supp_obj.area
                    city_place = supp_obj.city_place_id.city_id.city_name
                    business_name = supp_obj.business_name
                    supplier_id = supp_obj.supplier_id

                    business_list = Business.objects.filter(supplier = supplier_id)

                    for bus_obj in  business_list:
                        business_id = bus_obj.business_id

                        advert_obj = AdvertSubscriptionMap.objects.get(business_id = business_id)
                        
                        status = advert_obj.advert_id.status
                        if status == '1':
                            category_level_1 = advert_obj.advert_id.category_level_1.category_name
                            category_level_2 = advert_obj.advert_id.category_level_2.category_name
                        else :
                            category_level_1 = ''
                            category_level_2 = ''

                        consumer_data={
                            'sales_by':sales_person_name,
                            'busi_name':business_name,
                            'Area':area,
                            'City':city_place,
                            'cat_L1':category_level_1,
                            'cat_L2':category_level_2,
                            'pend_pay':'sws'
                        }
                        final_list.append(consumer_data)
            data = {'success': 'true', 'data': final_list}
        except Exception as e:
            print e
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')

