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
import calendar
import urllib2
from datetime import datetime, timedelta
import string
import random

SERVER_URL = "http://52.66.133.35"
#SERVER_URL = "http://35.163.150.203" 
# SERVER_URL = "http://192.168.0.4:8080"
#SERVER_URL = "http://192.168.0.14:8088" 

import os
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import textwrap
import StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile


def signing_out(request):
    logout(request)
    form = CaptchaForm()
    return render_to_response('Subscriber/user_login.html', dict(
        form=form, message_logout=''
    ), context_instance=RequestContext(request))

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_advert(request):
    if not request.user.is_authenticated():
        logout(request)
        form = CaptchaForm()
        return render_to_response('Subscriber/user_login.html', dict(
            form=form, message_logout='Your session is timed out, Please login again.'
        ), context_instance=RequestContext(request))

    else:
        user_id = request.session['supplier_id']
        print 'user_id.....',user_id
        supplier_id=request.GET.get('user_id')
        supplier_obj = Supplier.objects.get(supplier_id = user_id)
        country_id= str(supplier_obj.country_id.country_id)
        state_id= str(supplier_obj.state.state_id) 
        city_place_id= str(supplier_obj.city_place_id.city_place_id)
        supplier_name = supplier_obj.business_name
        user_id=supplier_obj.contact_email
        business_id = request.GET.get('business_id')
        city_place_id = str(supplier_obj.city_place_id.city_place_id)
        tax_list = Tax.objects.all()
        temp_data = ''
        cat_amenities = []

        service_list = ServiceRateCard.objects.filter(service_rate_card_status='1').values('service_name').distinct()
        advert_service_list, item_ids = [], []
        for item in AdvertRateCard.objects.filter(advert_rate_card_status='1'):
            if item.advert_service_name not in item_ids:
                advert_service_list.append(str(item.advert_rate_card_id))
                item_ids.append(item.advert_service_name)

        advert_service_list = AdvertRateCard.objects.filter(advert_rate_card_id__in=advert_service_list)

        data = {'country_id':country_id,'state_id':state_id,'city_place_id':city_place_id,'supplier_name':supplier_name,'tax_list': tax_list, 'advert_service_list': advert_service_list, 'service_list': service_list,
                'username': request.session['login_user'],'supplier_id':supplier_id, 'user_id': user_id, 'category_list': get_category(request),
                'country_list': get_country(request), 'phone_category': get_phone_category(request), 'business_id':business_id,
                'state_list': get_states(request),'city_place_id':city_place_id}
        if business_id:
            business_obj = Business.objects.get(business_id = business_id)
            country_id= str(business_obj.country_id.country_id)
            state_id= str(business_obj.state_id.state_id)
            city_place_id= str(business_obj.city_place_id.city_place_id)
            start_date = business_obj.start_date
            end_date = business_obj.end_date
            advert_flag = 'false'
            premium_obj = PremiumService.objects.filter(business_id=business_id)
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

                    for amnenity in amenity_list:

                        temp_data ={
                        'id':str(amnenity.categorywise_amenity_id),
                        'amenity':str(amnenity.amenity)
                        }   
                        cat_amenities.append(temp_data)

                else:
                    amenity_list = CategorywiseAmenity.objects.filter(status="1",category=category_id)

                    for amnenity in amenity_list:

                        temp_data ={
                        'id':str(amnenity.categorywise_amenity_id),
                        'amenity':str(amnenity.amenity)
                        }
                        cat_amenities.append(temp_data)

            data = {'country_id':country_id,'state_id':state_id,'city_place_id':city_place_id,'supplier_name':supplier_name,'cat_amenities':cat_amenities,'tax_list': tax_list, 'advert_service_list': advert_service_list, 'service_list': service_list,
                    'username': request.session['login_user'],'supplier_id':supplier_id, 'user_id': user_id,'advert_flag':advert_flag,
                    'category_list': get_category(request), 'category_id':str(business_obj.category.category_id),
                    'country_list': get_country(request), 'phone_category': get_phone_category(request),'start_date':start_date,'end_date':end_date,
                    'business_id': business_id,'category_level_1':category_level_1,'category_level_2':category_level_2,
                    'category_level_3': category_level_3,'category_level_4': category_level_4,'category_level_5': category_level_5,
                    'state_list': get_states(request),'city_place_id':city_place_id}
            return render(request, 'Subscriber/add_advert_form.html', data)
        else:
            return render(request, 'Subscriber/add_advert.html', data)


# def get_city_category(city_place_id):
#     ##    pdb.set_trace()


#     cat_list = []
#     try:
#         cat_city_map = CategoryCityMap.objects.filter(city_place_id=city_place_id)
#         for cat in cat_city_map:
#             category = Category.objects.get(category_id=str(cat.category_id)).exclude(category_name= 'Ticket Resell')
#             if category.category_name != "Event Ticket Resale":
#                 cat_list.append(
#                     {'category_id': category.category_id, 'category': category.category_name})
#     except Exception, e:
#         print 'Exception ', e
#     return cat_list

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


# @csrf_exempt
# def check_category(request):
#     # pdb.set_trace()
#     if not request.user.is_authenticated():
#         data = {'success':'Expired'}

#     else:

#         print "IN CHECK NEW CATEGORY"
#         has_rate_card = 'false'
#         try:
#             temp_data = ''
#             cat_amenities = []
#             if request.POST.get('cat_level') != '6':
#                 if request.POST.get('cat_level') == '1':
#                     cat_obj = CategoryLevel1.objects.filter(parent_category_id=request.POST.get('category_id'))
#                 if request.POST.get('cat_level') == '2':
#                     cat_obj = CategoryLevel2.objects.filter(parent_category_id=request.POST.get('category_id'))
#                 if request.POST.get('cat_level') == '3':
#                     cat_obj = CategoryLevel3.objects.filter(parent_category_id=request.POST.get('category_id'))
#                 if request.POST.get('cat_level') == '4':
#                     cat_obj = CategoryLevel4.objects.filter(parent_category_id=request.POST.get('category_id'))
#                 if request.POST.get('cat_level') == '5':
#                     cat_obj = CategoryLevel5.objects.filter(parent_category_id=request.POST.get('category_id'))
#                 cat_list = []
#                 if cat_obj:
#                     for cat in cat_obj:
#                         options_data = '<option value=' + str(cat.category_id) + '>' + cat.category_name + '</option>'
#                         cat_list.append(options_data)
#                     data = {'category_list': cat_list}
#                 else:
#                     cat_level = int(request.POST.get('cat_level')) - 1

#                     supplier_obj = Supplier.objects.get(supplier_id=request.POST.get('supplier_id'))
#                     rate_card = RateCard.objects.filter(city_place_id=str(supplier_obj.city_place_id))
#                     service_rate_card = CategoryWiseRateCard.objects.filter(city_place_id=str(supplier_obj.city_place_id),
#                                                                             category_id=request.POST.get('category_id'))
#                     if rate_card and service_rate_card:
#                         has_rate_card = 'true'
#                     data = {
#                         'success': 'false', 'has_rate_card': has_rate_card
#                     }
#                     print data
#             else:
#                 cat_level = int(request.POST.get('cat_level')) - 1
#                 supplier_obj = Supplier.objects.get(supplier_id=request.session['supplier_id'])
#                 rate_card = RateCard.objects.filter(city_place_id=str(supplier_obj.city_place_id))
#                 service_rate_card = CategoryWiseRateCard.objects.filter(city_place_id=str(supplier_obj.city_place_id),
#                                                                         category_id=request.POST.get('category_id'),
#                                                                         category_level=cat_level,
#                                                                         rate_card_status='1')
#                 if rate_card and service_rate_card:
#                     has_rate_card = 'true'
#                 data = {'success': 'false', 'has_rate_card': has_rate_card}
#         except Exception, e:
#             print e
#         return HttpResponse(json.dumps(data), content_type='application/json')


def delete_advert(request):
    if not request.user.is_authenticated():
        data = {'success':'Expired'}

    else:
        try:
            advert_id = request.GET.get('advert_id')
            advert_obj = Advert.objects.get(advert_id=advert_id)
            advert_obj.status = '0'
            advert_obj.save()
            data = {'message': ''}
        except Exception, e:
            print 'Exception ', e
            data = {'state_list': 'No states available'}
    return HttpResponse(json.dumps(data), content_type='application/json')


def activate_advert(request):
    if not request.user.is_authenticated():
        data = {'success':'Expired'}

    else:

        try:
            advert_id = request.GET.get('advert_id')
            advert_obj = Advert.objects.get(advert_id=advert_id)
            advert_obj.status = '1'
            advert_obj.save()
            data = {'message': ''}
        except Exception, e:
            print 'Exception ', e
            data = {'state_list': 'No states available'}
        return HttpResponse(json.dumps(data), content_type='application/json')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def advert_bookings(request):
    if not request.user.is_authenticated():
        logout(request)
        form = CaptchaForm()
        return render_to_response('Subscriber/user_login.html', dict(
            form=form, message_logout='Your session is timed out, Please login again.'
        ), context_instance=RequestContext(request))

    else:
        advert_id = request.GET.get('advert_id')
        advert_obj = Advert.objects.get(advert_id=advert_id)
        coupon_user = CouponCode.objects.filter(advert_id=advert_id)
        coupon_list = []
        for coupons in coupon_user:
            advert_obj = Advert.objects.get(advert_id=str(coupons.advert_id))
            advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=str(coupons.advert_id))
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
            if coupons.user_id.consumer_profile_pic:
                user_img = SERVER_URL + coupons.user_id.consumer_profile_pic.url
            else:
                user_img = ''
            coupon_obj = {
                'coupon_code': coupons.coupon_code,
                'avail_date': coupons.creation_date.strftime('%b %d,%Y'),
                'user_id': str(coupons.user_id),
                'mobile_no': coupons.user_id.consumer_contact_no,
                'user_img': user_img,
                'user_name': coupons.user_id.consumer_full_name,
                'user_area': coupons.user_id.consumer_area,
                'user_email_id': coupons.user_id.consumer_email_id,
                'coupon_expiry_date': end_date.strftime('%b %d,%Y'),
                'days_remaining': int(date_gap.days),
                'status': status
            }
            coupon_list.append(coupon_obj)
        data = {'coupon_list': coupon_list, 'advert_name': advert_obj.advert_name, 'booking_count': len(coupon_list),
                'username': request.session['login_user']}
        return render(request, 'Subscriber/advert_bookings.html', data)


def get_country(request):
    ##    pdb.set_trace()
    country_list = []
    try:
        country_obj = Country.objects.filter(country_status='1')
        for country in country_obj:
            country_list.append(
                {'country_id': country.country_id, 'country_name': country.country_name})

    except Exception, e:
        print 'Exception ', e
    return country_list


# TO GET THE CATEGOTRY
def get_category(request):
    ##    pdb.set_trace()
    cat_list = []
    try:
        category = Category.objects.filter(category_status='1').order_by('category_name')
        for cat in category:
            cat_list.append(
                {'category_id': cat.category_id, 'category': cat.category_name})

    except Exception, e:
        print 'Exception ', e
    return cat_list


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


# TO GET THE STATE
def get_states(request):
    ##    pdb.set_trace()
    if not request.user.is_authenticated():
        data = {'success':'Expired'}

    else:    
        state_list = []
        try:
            state = State.objects.filter(state_status='1')
            for sta in state:
                options_data = {
                    'state_id': str(sta.state_id),
                    'state_name': str(sta.state_name)

                }
                state_list.append(options_data)
            return state_list
        except Exception, e:
            print 'Exception ', e
            data = {'state_list': 'No states available'}
        return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def save_subscription_plan(request):
    if not request.user.is_authenticated():
        data = {'success':'Expired'}

    else:
        try:
            supplier_id = request.session['supplier_id']
            supplier_obj = Supplier.objects.get(supplier_id=supplier_id)
            
            user_email = str(supplier_obj.sales_person_name.usre_email_id)
            user_first_name = supplier_obj.sales_person_name.user_first_name

            contact_person = supplier_obj.contact_person
            city_place_id = str(supplier_obj.city_place_id)
            category_id = request.POST.get('sub_category')
            duration = request.POST.get('duration_list')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')

            premium_service_list = request.POST.getlist('premium_service')
            premium_service_duration_list = request.POST.getlist('premium_ser_duration')
            premium_start_date_list = request.POST.getlist('premium_start_date')
            premium_end_date_list = request.POST.getlist('premium_end_date')
            premium_end_date_list = filter(None, premium_end_date_list)

            enquiry_service_list = request.POST.get('tel_service_name')
            enquiry_service_duration_list = request.POST.get('tel_ser_duration')
            enquiry_start_date_list = request.POST.getlist('tel_start_date')
            enquiry_end_date_list = request.POST.getlist('tel_end_date')
            enquiry_start_date_list = filter(None, enquiry_start_date_list)
            enquiry_end_date_list = filter(None, enquiry_end_date_list)

            cat_id = ''
            cat_lvl = ''
            if request.POST.get('lvl1'):
                cat_id = request.POST.get('lvl1')
                cat_lvl = '1'
            if request.POST.get('lvl2'):
                cat_id = request.POST.get('lvl2')
                cat_lvl = '2'
            if request.POST.get('lvl3'):
                cat_id = request.POST.get('lvl3')
                cat_lvl = '3'
            if request.POST.get('lvl4'):
                cat_id = request.POST.get('lvl4')
                cat_lvl = '4'
            if request.POST.get('lvl5'):
                cat_id = request.POST.get('lvl5')
                cat_lvl = '5'

            zip_premium = zip(premium_service_list, premium_service_duration_list, premium_start_date_list,
                              premium_end_date_list)

            # if premium_service_list:
            #     check_premium_service = check_date(zip_premium, cat_id, city_place_id, cat_lvl)
            #     if check_premium_service['success'] == 'false':
            #         data = {'success': 'false', 'message': check_premium_service['msg']}
            #         return HttpResponse(json.dumps(data), content_type='application/json')

            chars = string.digits
            pwdSize = 8
            password = ''.join(random.choice(chars) for _ in range(pwdSize))

            category_obj = Category.objects.get(category_id=category_id)

            business_obj = Business(
                category=category_obj,
                #service_rate_card_id=service_ratecard_obj,
                duration=duration,
                start_date=start_date,
                end_date=end_date,
                supplier=supplier_obj,
                transaction_code="TID" + str(password),
                is_active=0,
                business_created_date=datetime.now(),
                business_created_by=supplier_obj.contact_email,
                country_id = Country.objects.get(country_id=request.POST.get('country1')) if request.POST.get('country1') else None,
                state_id=State.objects.get(state_id=request.POST.get('statec1')) if request.POST.get('statec1') else None,
                city_place_id=City_Place.objects.get(city_place_id=request.POST.get('city1')) if request.POST.get(
                        'city1') else None,
            )

            business_obj.save()
            if request.POST.get('lvl1'):
                business_obj.category_level_1 = CategoryLevel1.objects.get(category_id=request.POST.get('lvl1'))
            if request.POST.get('lvl2'):
                business_obj.category_level_2 = CategoryLevel2.objects.get(category_id=request.POST.get('lvl2'))
            if request.POST.get('lvl3'):
                business_obj.category_level_3 = CategoryLevel3.objects.get(category_id=request.POST.get('lvl3'))
            if request.POST.get('lvl4'):
                business_obj.category_level_4 = CategoryLevel4.objects.get(category_id=request.POST.get('lvl4'))
            if request.POST.get('lvl5'):
                business_obj.category_level_5 = CategoryLevel5.objects.get(category_id=request.POST.get('lvl5'))
            business_obj.save()

            transaction_code = "TID" + str(password)
            if premium_service_list:
                for premium_service, premium_service_duration, premium_start_date, premium_end_date in zip_premium:
                    premium_service_obj = PremiumService(
                        premium_service_name=premium_service,
                        no_of_days=premium_service_duration,
                        category_id=cat_id,
                        category_level=cat_lvl,
                        city_place_id=City_Place.objects.get(city_place_id=city_place_id),
                        start_date=premium_start_date,
                        end_date=premium_end_date,
                        business_id=business_obj,
                        premium_service_status="1",
                        premium_service_created_date=datetime.now(),
                        premium_service_created_by=supplier_obj.contact_email
                    )
                    premium_service_obj.save()

            print enquiry_service_list, enquiry_service_duration_list, enquiry_start_date_list, enquiry_end_date_list
            if enquiry_service_list:
                enquiry_service_obj = EnquiryService(
                    enquiry_service_name=enquiry_service_list,
                    no_of_days=enquiry_service_duration_list,
                    category_id=cat_id,
                    category_level=cat_lvl,
                    city_place_id=City_Place.objects.get(city_place_id=city_place_id),
                    start_date=enquiry_start_date_list[0],
                    end_date=enquiry_end_date_list[0],
                    business_id=business_obj,
                    enquiry_service_status="1",
                    enquiry_service_created_date=datetime.now(),
                    enquiry_service_created_by=supplier_obj.contact_email
                )
                enquiry_service_obj.save()

            send_email(transaction_code, user_email ,contact_person,user_first_name)

            data = {'success': 'true',
                    'message': 'Thank you for the subscription purchase. CityHoopla team will contact you for the payment. Once your payment has been confirmed, you can go ahead and add the advert details.',
                    'business_id': str(business_obj)
                    }
        except Exception as e:
            print e
            data = {'success': 'false', 'message': e}
    return HttpResponse(json.dumps(data), content_type='application/json')


def check_date(zip_premium, category_id, city_place_id, category_level):


    flag_1, flag_2, flag_3, flag_4, flag_5 = 'Yes', 'Yes', 'Yes', 'Yes', 'Yes'
    service_list = ''
    for premium_service, premium_service_duration, premium_start_date, premium_end_date in zip_premium:
        if premium_service == 'No.1 Listing':
            premium_service_obj = PremiumService.objects.filter(
                Q(premium_service_name=premium_service) &
                Q(category_id=str(category_id)) &
                Q(category_level=str(category_level)) &
                Q(city_place_id=str(city_place_id)) &
                Q(start_date__lte=premium_start_date, end_date__gte=premium_end_date) &
                Q(premium_service_status='1')
            ).count()

            if premium_service_obj >= 1:
                flag_1 = 'No'
        if premium_service == 'No.2 Listing':
            premium_service_obj = PremiumService.objects.filter(
                Q(premium_service_name=premium_service) &
                Q(category_id=str(category_id)) &
                Q(category_level=str(category_level)) &
                Q(city_place_id=str(city_place_id)) &
                Q(start_date__lte=premium_start_date, end_date__gte=premium_end_date) &
                Q(premium_service_status='1')
            ).count()

            print premium_service_obj

            if premium_service_obj >= 1:
                flag_2 = 'No'
        if premium_service == 'No.3 Listing':
            premium_service_obj = PremiumService.objects.filter(
                Q(premium_service_name=premium_service) &
                Q(category_id=str(category_id)) &
                Q(category_level=str(category_level)) &
                Q(city_place_id=str(city_place_id)) &
                Q(start_date__lte=premium_start_date, end_date__gte=premium_end_date) &
                Q(premium_service_status='1')
            ).count()
            if premium_service_obj >= 1:
                flag_3 = 'No'
        if premium_service == 'Advert Slider':
            premium_service_obj = PremiumService.objects.filter(
                Q(premium_service_name=premium_service) &
                Q(city_place_id=str(city_place_id)) &
                Q(start_date__lte=premium_start_date, end_date__gte=premium_end_date) &
                Q(premium_service_status='1')
            ).count()
            if premium_service_obj > 10:
                flag_4 = 'No'
        if premium_service == 'Top Advert':
            premium_service_obj = PremiumService.objects.filter(
                Q(premium_service_name=premium_service) &
                Q(city_place_id=str(city_place_id)) &
                Q(start_date__lte=premium_start_date, end_date__gte=premium_end_date) &
                Q(premium_service_status='1')
            ).count()
            if premium_service_obj >= 1:
                flag_5 = 'No'
    if flag_1 == 'No':
        service_list = 'No.1 Listing,'
    if flag_2 == 'No':
        service_list = service_list + 'No.2 Listing,'
    if flag_3 == 'No':
        service_list = service_list + 'No.3 Listing,'
    if flag_4 == 'No':
        service_list = service_list + 'Advert Slider,'
    if flag_5 == 'No':
        service_list = service_list + 'Top Advert'
    if service_list != '':
        msg = service_list + ' already exist for selected date range'
        data = {'success': 'false', 'msg': msg}
    else:
        data = {'success': 'true', 'msg': ''}
    return data


@csrf_exempt
def save_payment_details(request):
    if not request.user.is_authenticated():
        data = {'success':'Expired'}

    else:    
        try:
            chars = string.digits
            pwdSize = 8
            password = ''.join(random.choice(chars) for _ in range(pwdSize))

            business_id = request.POST.get('business_id')
            bank_name = request.POST.get('bank_name')
            cheque_number = request.POST.get('cheque_number')
            total_payable_amount = request.POST.get('total_payable_amount')
            bank_branch_name = request.POST.get('bank_branch_name')
            payment_amount = request.POST.get('payment_amount')
            payment_mode = request.POST.get('payment_mode')
            total_paid_amount = request.POST.get('total_paid_amount')
            payment_note = request.POST.get('payment_note')
            tax_type = request.POST.get('tax_type')
            payment_code = "PMID" + str(password)

            business_obj = Business.objects.get(business_id=business_id)
            tax_obj = Tax.objects.get(tax_rate=tax_type)
            payment_obj = PaymentDetail(
                payment_code=payment_code,
                payment_mode=payment_mode,
                payable_amount=total_payable_amount,
                total_amount=payment_amount,
                note=payment_note,
                tax_type=tax_obj,
                business_id=business_obj
            )
            payment_obj.save()

            if total_paid_amount:
                payment_obj.paid_amount = total_paid_amount
            if payment_mode == 'cheque':
                payment_obj.bank_name = bank_name
                payment_obj.branch_name = bank_branch_name
                payment_obj.cheque_number = cheque_number

            payment_obj.save()

            data = {'success': 'true', 'message': 'Payment done successfully with Payment ID - ' + payment_code}
        except Exception as e:
            print e
            data = {'success': 'true', 'message': e}
        return HttpResponse(json.dumps(data), content_type='application/json')


def get_state(request):
    if not request.user.is_authenticated():
        data = {'success':'Expired'}

    else:    
        country_id = request.GET.get('country_id')
        state_list = []
        try:
            state = State.objects.filter(state_status='1', country_id=country_id)
            currency = Currency.objects.get(country_id=country_id)
            for sta in state:
                options_data = '<option value=' + str(
                    sta.state_id) + '>' + sta.state_name + '</option>'
                state_list.append(options_data)
                print state_list
            data = {'state_list': state_list, 'currency': currency.currency}
        except Exception, e:
            print 'Exception ', e
            data = {'state_list': 'No states available'}
        return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def save_advert(request):
    # pdb.set_trace()
    if not request.user.is_authenticated():
        data = {'success':'Expired'}

    else:
        try:
            if request.method == "POST":
                print '===request=======WWW=', request.POST.get('advert_keywords')

                advert_title = request.POST.get('advert_title')
                advert_title = filter(lambda x: ord(x)<128,advert_title)
                contact_name = request.POST.get('contact_name')
                contact_name = filter(lambda x: ord(x)<128,contact_name)
                phone_no = request.POST.get('phone_no')
                phone_no = filter(lambda x: ord(x)<128,phone_no)                
                website = request.POST.get('website')
                website = filter(lambda x: ord(x)<128,website)
                short_discription = request.POST.get('short_discription')
                short_discription = filter(lambda x: ord(x)<128,short_discription)
                product_discription = request.POST.get('product_discription')
                product_discription = filter(lambda x: ord(x)<128,product_discription)
                discount_discription = request.POST.get('discount_discription')
                discount_discription = filter(lambda x: ord(x)<128,discount_discription)                                                
                email_primary = request.POST.get('email_primary')
                email_primary = filter(lambda x: ord(x)<128,email_primary)
                address_line1 = request.POST.get('address_line1')
                address_line1 = filter(lambda x: ord(x)<128,address_line1) 
                address_line2 = request.POST.get('address_line2')
                address_line2 = filter(lambda x: ord(x)<128,address_line2)                                                                                      
                area = request.POST.get('area')
                area = filter(lambda x: ord(x)<128,area)   
                landmark = request.POST.get('landmark')
                landmark = filter(lambda x: ord(x)<128,landmark)   
                other_projects = request.POST.get('other_projects')
                other_projects = filter(lambda x: ord(x)<128,other_projects)   
                speciality = request.POST.get('speciality')
                speciality = filter(lambda x: ord(x)<128,speciality) 
                affilated = request.POST.get('affilated')
                affilated = filter(lambda x: ord(x)<128,affilated) 
                course_duration = request.POST.get('course_duration')
                course_duration = filter(lambda x: ord(x)<128,course_duration) 
                happy_hour_offer = request.POST.get('happy_hour_offer')
                happy_hour_offer = filter(lambda x: ord(x)<128,happy_hour_offer)                                 
                facility = request.POST.get('facility')
                facility = filter(lambda x: ord(x)<128,facility) 
                advert_keywords = request.POST.get('advert_keywords')
                advert_keywords = filter(lambda x: ord(x)<128,advert_keywords) 
                title = request.POST.get('title')
                title = filter(lambda x: ord(x)<128,title) 
                any_other_amenity = request.POST.get('any_other_amenity')
                any_other_amenity = filter(lambda x: ord(x)<128,any_other_amenity)                 
                advert_obj = Advert(
                    supplier_id=Supplier.objects.get(supplier_id=request.POST.get('supplier_id')),
                    category_id=Category.objects.get(category_id=request.POST.get('categ')),
                    advert_name=advert_title,
                    contact_name=contact_name,
                    contact_no=phone_no,
                    website=website,
                    latitude=request.POST.get('lat'),
                    longitude=request.POST.get('lng'),
                    short_description=short_discription,
                    product_description=product_discription,
                    currency=request.POST.get('currency'),
                    country_id=Country.objects.get(country_id=request.POST.get('country')) if request.POST.get(
                        'country') else None,
                    # product_price=request.POST.get('product_price'),
                    discount_description=discount_discription,
                    email_primary=email_primary,
                    email_secondary=request.POST.get('email_secondary'),
                    address_line_1=address_line1,
                    address_line_2=address_line2,
                    area=area,
                    landmark=landmark,
                    state_id=State.objects.get(state_id=request.POST.get('statec')) if request.POST.get('statec') else None,
                    city_place_id=City_Place.objects.get(city_place_id=request.POST.get('city')) if request.POST.get(
                        'city') else None,
                    pincode_id=Pincode.objects.get(pincode=request.POST.get('pincode')) if request.POST.get(
                        'pincode') else None,
                    property_market_rate=request.POST.get('pro_mark_rate'),
                    possesion_status=request.POST.get('possesion_status'),
                    date_of_delivery=request.POST.get('date_of_delivery'),
                    other_projects=other_projects,
                    distance_frm_railway_station=request.POST.get('dis_rail_stat'),
                    distance_frm_railway_airport=request.POST.get('dis_airport'),
                    speciality=speciality,
                    affilated_to=affilated,
                    course_duration=course_duration,
                    happy_hour_offer=happy_hour_offer,
                    facility=facility,
                    keywords=advert_keywords,
                    image_video_space_used=request.POST.get('image_and_video_space'),
                    other_amenity=any_other_amenity,
                    title=title,
                    created_by=request.session['login_user'],
                    creation_date=datetime.now(),
                    discount_start_date=request.POST.get('startDate'),
                    discount_end_date=request.POST.get('endDate')                    
                );
                advert_obj.save()
                advert_id = advert_obj.advert_id

                any_other_details = request.POST.get('any_other_details')
                any_other_details = filter(lambda x: ord(x)<128,any_other_details) 

                if any_other_details:
                    advert_obj.any_other_details = any_other_details
                    advert_obj.save()
                if request.POST.get('subscription_id'):
                    map_subscription(request.POST.get('subscription_id'), advert_obj)

                sub_cat_list = request.POST.getlist('subcat_list')
                subcat_list = sub_cat_list[0].split(',')
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

                    #save_advert_image(advert_obj)

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
                product_name_list = product_name_list.split(',')
                product_price_list = request.POST.get('product_price_list')
                product_price_list = product_price_list.split(',')
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
                    print "SCHOOL==========>>", request.POST.get('near_schol')
                    near_schol = request.POST.get('near_schol')
                    near_schol = near_schol.split(',')

                    print "SCHOOL DI SORTING-------<<<<", request.POST.get('near_schold')
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
                # advert_add_sms(advert_obj)
            
                supplier_obj = Supplier.objects.get(supplier_id=request.POST.get('supplier_id'))
            
                partner_email = str(supplier_obj.sales_person_name.usre_email_id)
                partner_first_name = supplier_obj.sales_person_name.user_first_name

                print '.............First Name.............',partner_first_name
                contact_person = supplier_obj.contact_person
                print '........Sales Person.........',contact_person
                advert_add_mail(partner_email,partner_first_name,contact_person)
                data = {'success': 'true', 'advert_id': advert_id}

        except Exception, e:
            print 'Exception :', e
            data = {'data': 'none'}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt 
def advert_add_mail(partner_email, partner_first_name,contact_person):
    try:
        print '............IN new mail.................',partner_email
        subject = "New Subscription"
        description = "Dear "+ partner_first_name +","
        description = description + '\n\n' + 'A New Advert with Advert ID 111 has been made by ' + contact_person + '. Please confirm the payment processing so that the Subscriber can proceed with Advert Addition.'

        gmail_user = "donotreply@city-hoopla.com" # "cityhoopla2016"
        gmail_pwd = "Hoopla123#" #"cityhoopla@2016"
        FROM = 'Team CityHoopla<donotreply@city-hoopla.com>' #'CityHoopla Admin: <cityhoopla2016@gmail.com>'
        cc = ['cityhoopla2016@gmail.com']
        TO = [partner_email]
        
        TEXT = description
        SUBJECT = subject
        #server = smtplib.SMTP_SSL()
        #server = smtplib.SMTP("smtp.gmail.com", 587)
        server = smtplib.SMTP("smtpout.asia.secureserver.net", 80)
        server.ehlo()
        #server.starttls()

        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\ncc: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO),", ".join(cc), SUBJECT, TEXT)
        toaddrs = TO + cc 

        server.sendmail(FROM, toaddrs, message)
        server.quit()
    except SMTPException, e:
        print e
    except Exception, e:
        print 'exception', e
    return 1

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
        for product_name, product_price in zipped_product:
            product_name = filter(lambda x: ord(x)<128,product_name)
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


def save_near_attr(near_attr_list, advert_id):
    
    ##    pdb.set_trace()
    print "IN SAVE NEAR ATTRACTION"
    try:
        for ner_attr in near_attr_list:
            ner_attr = filter(lambda x: ord(x)<128,ner_attr)
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
            if shpnml != '':
                shpnml = filter(lambda x: ord(x)<128,shpnml)
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
            if school != '' :
                school = filter(lambda x: ord(x)<128,school)
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
            if hospital != '':
                hospital = filter(lambda x: ord(x)<128,hospital)
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

def edit_subscription(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        # pdb.set_trace()
        business_id = request.GET.get('business_id')
        flag = request.GET.get('flag')
        advert_id = request.GET.get('advert_id')
        tax_list = Tax.objects.all()

        business_obj = Business.objects.get(business_id=business_id)
        supplier_id = str(business_obj.supplier_id)

        supplier_obj = Supplier.objects.get(supplier_id=supplier_id)

        city_place_id = str(supplier_obj.city_place_id)

        telephone_rate_card = TelephoneEnquiryRateCard.objects.filter(city_place_id=city_place_id)

        business_data = {
            'business_id': str(business_obj.business_id),
            'service_rate_card_duration': int(business_obj.duration),
            'start_date': str(business_obj.start_date),
            'end_date': str(business_obj.end_date),
            'country_id': business_obj.country_id.country_id,
            'state_id': business_obj.state_id.state_id,
            'city_place_id': business_obj.city_place_id.city_place_id
        }

        state_list = State.objects.filter(country_id = str(business_obj.country_id.country_id))
        city_list = City_Place.objects.filter(state_id = str(business_obj.state_id.state_id))

        category_lvl1_list = []
        category_lvl2_list = []
        category_lvl3_list = []
        category_lvl4_list = []
        category_lvl5_list = []
        cat_id = ''
        cat_lvl = ''
        category_list = []
        category_id_list = []

        if business_obj.category:
            business_data['category_id'] = business_obj.category.category_id
            cat_id = business_obj.category.category_id
            cat_lvl = ''
            cat_city_map = CategoryCityMap.objects.filter(city_place_id=str(business_obj.city_place_id.city_place_id))
            for cat in cat_city_map:
                category_id_list.append(cat.category_id.category_id)
            category_list = Category.objects.filter(category_status = '1', category_id__in = category_id_list)#.exclude()

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

        rate_obj = CategoryWiseRateCard.objects.get(
                        service_name='Subscription',
                        category_id=cat_id,
                        category_level=cat_lvl,
                        rate_card_status = 1
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
            #print e
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
            print enquiry_service_data
            if enquiry_service_obj.enquiry_service_name == 'Platinum':
                rate_obj = TelephoneEnquiryRateCard.objects.get(
                    service_name=enquiry_service_obj.enquiry_service_name,
                    city_place_id=enquiry_service_obj.city_place_id,
                    rate_card_status = 1
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
                    city_place_id=enquiry_service_obj.city_place_id,
                    rate_card_status = 1
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
                    city_place_id=enquiry_service_obj.city_place_id,
                    rate_card_status = 1
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
                    city_place_id=enquiry_service_obj.city_place_id,
                    rate_card_status = 1
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
                    city_place_id=enquiry_service_obj.city_place_id,
                    rate_card_status = 1
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
                    city_place_id=enquiry_service_obj.city_place_id,
                    rate_card_status = 1
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
        #print "------------------------------------", enquiry_service_data
        total_amount = basic_amount + amount_1 + amount_2 + amount_3 + amount_4 + amount_5 + tel_amount_1 + tel_amount_2 + tel_amount_3 + tel_amount_4 + tel_amount_5 + tel_amount_6
        #total_amount = total_amount

        advert_service_list =[]
        advert_service_lists =[]

        rate_card_obj = CategoryWiseRateCard.objects.filter(
            rate_card_status='1',
            category_id=cat_id,
            category_level=cat_lvl,
            city_place_id = city_place_id
        ).exclude(service_name = 'Subscription')
        advert_service_lists.extend(rate_card_obj)
        rate_card_obj = RateCard.objects.filter(
            rate_card_status='1',
            city_place_id=city_place_id
        )
        advert_service_lists.extend(rate_card_obj)

        for advert_service in advert_service_lists:
            #print advert_service
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


        data = {'tax_list': tax_list, 'advert_service_list': advert_service_list, 'category_list':category_list,
                'username': request.session['login_user'], #'category_list': get_city_category(city_place_id),
                'business_data': business_data, 'telephone_rate_card': telephone_rate_card,
                'premium_service_list': premium_service_list,'enquiry_service_data':enquiry_service_data,
                'total_amount': float(total_amount), 'basic_amount': basic_amount, 'amount_1': amount_1,
                'amount_2': amount_2, 'amount_3': amount_3, 'amount_4': amount_4, 'amount_5': amount_5,
                'tel_amount_1': tel_amount_1, 'tel_amount_2': tel_amount_2, 'tel_amount_3': tel_amount_3,
                'tel_amount_4': tel_amount_4, 'tel_amount_5': tel_amount_5, 'tel_amount_6': tel_amount_6,
                'category_lvl1_list':category_lvl1_list,'city_place_id':city_place_id,
                'category_lvl2_list': category_lvl2_list,'country_list': get_country(request),
                'category_lvl3_list': category_lvl3_list, 'state_list' :state_list,
                'category_lvl4_list': category_lvl4_list, 'city_list' :city_list,
                'category_lvl5_list': category_lvl5_list,'business_id':business_id,
                'cat_id':cat_id,'cat_lvl':cat_lvl,'supplier_id':supplier_id,'flag':flag,'advert_id':advert_id
                }
        return render(request, 'Subscriber/edit_subscription.html', data)

def edit_advert(request):
    if not request.user.is_authenticated():
        logout(request)
        form = CaptchaForm()
        return render_to_response('Subscriber/user_login.html', dict(
            form=form, message_logout='Your session is timed out, Please login again.'
        ), context_instance=RequestContext(request))

    else: 
        advert_id = request.GET.get('advert_id')
        tax_list = Tax.objects.all()
        temp_data = ''
        cat_amenities = []
        pincode_list = []

        advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)
        business_obj = Business.objects.get(business_id=str(advert_sub_obj.business_id))
        start_date = str(business_obj.start_date)
        end_date = str(business_obj.end_date)
        supplier_obj = Supplier.objects.get(supplier_id=str(advert_sub_obj.advert_id.supplier_id))
        supplier_name =supplier_obj.business_name
        city_place_id = str(supplier_obj.city_place_id)
        telephone_rate_card = TelephoneEnquiryRateCard.objects.filter(city_place_id=city_place_id)
        business_data = {
            'business_id': str(business_obj.business_id),
            'service_rate_card_duration': int(business_obj.duration),
            'start_date': str(business_obj.start_date),
            'end_date': str(business_obj.end_date),
            'country_id': business_obj.country_id.country_id,
            'state_id': business_obj.state_id.state_id,
            'city_place_id': business_obj.city_place_id.city_place_id
        }
        state_list = State.objects.filter(country_id = str(business_obj.country_id.country_id))
        city_list = City_Place.objects.filter(state_id = str(business_obj.state_id.state_id))

        city_id1 = City_Place.objects.get(city_place_id=city_place_id)
        city_id2 = City.objects.get(city_id=str(city_id1.city_id.city_id))
        pincode_list1 = Pincode.objects.filter(city_id=city_id2.city_id).order_by('pincode')

        supplier_id = str(advert_sub_obj.advert_id.supplier_id)
        category_lvl1_list = []
        category_lvl2_list = []
        category_lvl3_list = []
        category_lvl4_list = []
        category_lvl5_list = []
        cat_id = ''
        cat_lvl = ''
        category_list = []
        category_id_list = []        

        if business_obj.category:
            business_data['category_id'] = business_obj.category.category_id
            cat_id = business_obj.category.category_id
            cat_lvl = ''
            cat_city_map = CategoryCityMap.objects.filter(city_place_id=str(business_obj.city_place_id.city_place_id))
            for cat in cat_city_map:
                category_id_list.append(cat.category_id.category_id)
            category_list = Category.objects.filter(category_status = '1', category_id__in = category_id_list)#.exclude()


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

            paid_amount1 = 0
            paid_amount2 = 0
            paid_amount3 = 0

            if payment_obj.paid_amount:
                paid_amount1 = round(float(payment_obj.paid_amount), 2)
            if payment_obj.payable_amount:
                paid_amount2 = round(float(payment_obj.payable_amount), 2)
            if payment_obj.total_amount:
                paid_amount3 = round(float(payment_obj.total_amount), 2)             

            payment_details = {
                'payment_mode': payment_obj.payment_mode,
                'paid_amount': paid_amount1,
                'payable_amount': paid_amount2,
                'total_amount': paid_amount3,
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

        discount_flag = ""
        discount_start_date = ""
        discount_end_date = ""
        if advert_obj.discount_start_date:
            discount_start_date = advert_obj.discount_start_date
            discount_end_date = advert_obj.discount_end_date
            if discount_start_date == start_date and discount_end_date == end_date:
                discount_flag = 1
            else:
                discount_flag = 0


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
            'other_amenity':advert_obj.other_amenity,
            'website':advert_obj.website,
            'discount_flag':discount_flag,
            'discount_start_date':discount_start_date,
            'discount_end_date':discount_end_date
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
                    "attraction_id":nr_attr.attraction_id,
                    "attraction": nr_attr.attraction
                }
                nr_attr_list.append(nr_attr_data)

        nr_shop_obj = NearestShopping.objects.filter(advert_id=advert_id)
        nr_shop_list = []
        if nr_shop_obj:
            for nr_shop in nr_shop_obj:
                nr_shop_data = {
                    "shop_id":nr_shop.shopping_id,
                    "shop_name": nr_shop.shop_name,
                    "distance_frm_property": nr_shop.distance_frm_property
                }
                nr_shop_list.append(nr_shop_data)

        nr_shcl_obj = NearestSchool.objects.filter(advert_id=advert_id)
        nr_shcl_list = []
        if nr_shcl_obj:
            for schools in nr_shcl_obj:
                schools_data = {
                    "school_id":schools.school_id,
                    "school_name": schools.school_name,
                    "distance_frm_property": schools.distance_frm_property
                }
                nr_shcl_list.append(schools_data)

        nr_hosp_obj = NearestHospital.objects.filter(advert_id=advert_id)
        nr_hosp_list = []
        if nr_hosp_obj:
            for hospitals in nr_hosp_obj:
                hospital_data = {
                    "hospital_id":hospitals.hospital_id,
                    "hospital_name": hospitals.hospital_name,
                    "distance_frm_property": hospitals.distance_frm_property
                }
                nr_hosp_list.append(hospital_data)
        data = {'tax_list': tax_list, 'advert_service_list': advert_service_list,
                'username': request.session['login_user'], 'category_list':category_list,
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
                'category_l4_list': category_l4_list, 'category_l5_list': category_l5_list,'state_list' :state_list,'city_list' :city_list,'pincode_list1':pincode_list1
                }
                
        return render(request, 'Subscriber/edit_advert.html', data)

def renew_subscription(request):
    if not request.user.is_authenticated():
        logout(request)
        form = CaptchaForm()
        return render_to_response('Subscriber/user_login.html', dict(
            form=form, message_logout='Your session is timed out, Please login again.'
        ), context_instance=RequestContext(request))

    else: 
        advert_id = request.GET.get('advert_id')
        tax_list = Tax.objects.all()
        advert_obj = Advert.objects.get(advert_id=advert_id)
        advert_name = advert_obj.advert_name
        advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)
        business_obj = Business.objects.get(business_id=str(advert_sub_obj.business_id))

        supplier_id = str(advert_obj.supplier_id)
        print 'supplier_id', supplier_id
        supplier_obj = Supplier.objects.get(supplier_id=supplier_id)
        city_place_id = str(supplier_obj.city_place_id)

        telephone_rate_card = TelephoneEnquiryRateCard.objects.filter(city_place_id=city_place_id)

        business_data = {
            'business_id': str(business_obj.business_id),
            'service_rate_card_duration': int(business_obj.duration),
            'start_date': str(business_obj.start_date),
            'end_date': str(business_obj.end_date)
        }

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

        data = {'tax_list': tax_list, 'advert_service_list': advert_service_list,
                'telephone_rate_card': telephone_rate_card,
                'username': request.session['login_user'], 'category_list': get_city_category(city_place_id),
                'country_list': get_country(request), 'city_place_id': city_place_id,
                'state_list': get_states(request), 'business_data': business_data, 'advert_name': advert_name,
                'category_lvl1_list': category_lvl1_list,
                'category_lvl2_list': category_lvl2_list,
                'category_lvl3_list': category_lvl3_list,
                'category_lvl4_list': category_lvl4_list,
                'category_lvl5_list': category_lvl5_list,
                'cat_id': cat_id, 'cat_lvl': cat_lvl, 'supplier_id': supplier_id
                }
        return render(request, 'Subscriber/renew_subscription.html', data)


def update_check_date(zip_premium, category_id, business_id, city_place_id, category_level):
 
    flag_1, flag_2, flag_3, flag_4, flag_5 = 'Yes', 'Yes', 'Yes', 'Yes', 'Yes'
    service_list = ''
    for premium_service, premium_service_duration, premium_start_date, premium_end_date in zip_premium:
        if premium_service == 'No.1 Listing':
            premium_service_obj = PremiumService.objects.filter(
                Q(premium_service_name=premium_service) &
                Q(category_id=str(category_id)) &
                Q(category_level=str(category_level)) &
                Q(city_place_id=str(city_place_id)) &
                Q(start_date__lte=premium_start_date, end_date__gte=premium_end_date) &
                Q(premium_service_status='1')
            ).exclude(business_id=business_id).count()
            if premium_service_obj >= 1:
                flag_1 = 'No'
        if premium_service == 'No.2 Listing':
            premium_service_obj = PremiumService.objects.filter(
                Q(premium_service_name=premium_service) &
                Q(category_id=str(category_id)) &
                Q(category_level=str(category_level)) &
                Q(city_place_id=str(city_place_id)) &
                Q(start_date__lte=premium_start_date, end_date__gte=premium_end_date) &
                Q(premium_service_status='1')
            ).exclude(business_id=business_id).count()

            print premium_service_obj

            if premium_service_obj >= 1:
                flag_2 = 'No'
        if premium_service == 'No.3 Listing':
            premium_service_obj = PremiumService.objects.filter(
                Q(premium_service_name=premium_service) &
                Q(category_id=str(category_id)) &
                Q(category_level=str(category_level)) &
                Q(city_place_id=str(city_place_id)) &
                Q(start_date__lte=premium_start_date, end_date__gte=premium_end_date) &
                Q(premium_service_status='1')
            ).exclude(business_id=business_id).count()
            if premium_service_obj >= 1:
                flag_3 = 'No'
        if premium_service == 'Advert Slider':
            premium_service_obj = PremiumService.objects.filter(
                Q(premium_service_name=premium_service) &
                Q(city_place_id=str(city_place_id)) &
                Q(start_date__lte=premium_start_date, end_date__gte=premium_end_date) &
                Q(premium_service_status='1')
            ).exclude(business_id=business_id).count()
            if premium_service_obj > 10:
                flag_4 = 'No'
        if premium_service == 'Top Advert':
            premium_service_obj = PremiumService.objects.filter(
                Q(premium_service_name=premium_service) &
                Q(city_place_id=str(city_place_id)) &
                Q(start_date__lte=premium_start_date, end_date__gte=premium_end_date) &
                Q(premium_service_status='1')
            ).exclude(business_id=business_id).count()
            if premium_service_obj >= 1:
                flag_5 = 'No'
    if flag_1 == 'No':
        service_list = 'No.1 Listing,'
    if flag_2 == 'No':
        service_list = service_list + 'No.2 Listing,'
    if flag_3 == 'No':
        service_list = service_list + 'No.3 Listing,'
    if flag_4 == 'No':
        service_list = service_list + 'Advert Slider,'
    if flag_5 == 'No':
        service_list = service_list + 'Top Advert'
    if service_list != '':
        msg = service_list + ' already exist for selected date range'
        data = {'success': 'false', 'msg': msg}
    else:
        data = {'success': 'true', 'msg': ''}
    return data


@csrf_exempt
def update_payment_details(request):
    if not request.user.is_authenticated():
        data = {'success':'Expired'}

    else:     
        try:
            chars = string.digits
            pwdSize = 8
            password = ''.join(random.choice(chars) for _ in range(pwdSize))

            business_id = request.POST.get('business_id')
            bank_name = request.POST.get('bank_name')
            cheque_number = request.POST.get('cheque_number')
            total_payable_amount = request.POST.get('total_payable_amount')
            bank_branch_name = request.POST.get('bank_branch_name')
            payment_amount = request.POST.get('payment_amount')
            payment_mode = request.POST.get('payment_mode')
            total_paid_amount = request.POST.get('total_paid_amount')
            payment_note = request.POST.get('payment_note')
            tax_type = request.POST.get('tax_type')
            payment_code = "PMID" + str(password)

            business_obj = Business.objects.get(business_id=business_id)
            tax_obj = Tax.objects.get(tax_rate=tax_type)
            try:
                payment_obj = PaymentDetail.objects.get(business_id=business_id)
            except Exception:
                print "=======new payment==========="
                payment_obj = PaymentDetail()
                payment_obj.save()
                payment_obj.payment_code = payment_code
                payment_obj.business_id = business_obj
                payment_obj.save()

            if total_paid_amount:
                payment_obj.paid_amount = total_paid_amount
            if payment_mode == 'cheque':
                payment_obj.bank_name = bank_name
                payment_obj.branch_name = bank_branch_name
                payment_obj.cheque_number = cheque_number

            payment_obj.payment_mode = payment_mode
            payment_obj.payable_amount = total_payable_amount
            payment_obj.total_amount = payment_amount
            payment_obj.note = payment_note
            payment_obj.tax_type = tax_obj
            payment_obj.save()

            data = {'success': 'true', 'message': 'Payment done successfully with Payment ID - ' + payment_obj.payment_code}
        except Exception as e:
            print e
            data = {'success': 'true', 'message': e}
        return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def update_advert(request):
    # pdb.set_trace()
    if not request.user.is_authenticated():
        logout(request)
        form = CaptchaForm()
        return render_to_response('Subscriber/user_login.html', dict(
            form=form, message_logout='You have successfully logged out.'
        ), context_instance=RequestContext(request))

    else:     
        print "IN SAVE ADVERT METHOD",  # request.POST
        try:
            if request.method == "POST":
                advert_title = request.POST.get('advert_title')
                advert_title = filter(lambda x: ord(x)<128,advert_title)
                contact_name = request.POST.get('contact_name')
                contact_name = filter(lambda x: ord(x)<128,contact_name)
                website = request.POST.get('website')
                website = filter(lambda x: ord(x)<128,website)
                short_discription = request.POST.get('short_discription')
                short_discription = filter(lambda x: ord(x)<128,short_discription)
                product_discription = request.POST.get('product_discription')
                product_discription = filter(lambda x: ord(x)<128,product_discription)
                discount_discription = request.POST.get('discount_discription')
                discount_discription = filter(lambda x: ord(x)<128,discount_discription)                                                
                email_primary = request.POST.get('email_primary')
                email_primary = filter(lambda x: ord(x)<128,email_primary)
                address_line1 = request.POST.get('address_line1')
                address_line1 = filter(lambda x: ord(x)<128,address_line1) 
                address_line2 = request.POST.get('address_line2')
                address_line2 = filter(lambda x: ord(x)<128,address_line2)                                                                                      
                area = request.POST.get('area')
                area = filter(lambda x: ord(x)<128,area)   
                landmark = request.POST.get('landmark')
                landmark = filter(lambda x: ord(x)<128,landmark)   
                other_projects = request.POST.get('other_projects')
                other_projects = filter(lambda x: ord(x)<128,other_projects)   
                speciality = request.POST.get('speciality')
                speciality = filter(lambda x: ord(x)<128,speciality) 
                affilated = request.POST.get('affilated')
                affilated = filter(lambda x: ord(x)<128,affilated) 
                course_duration = request.POST.get('course_duration')
                course_duration = filter(lambda x: ord(x)<128,course_duration) 
                happy_hour_offer = request.POST.get('happy_hour_offer')
                happy_hour_offer = filter(lambda x: ord(x)<128,happy_hour_offer)                                 
                facility = request.POST.get('facility')
                facility = filter(lambda x: ord(x)<128,facility) 
                advert_keywords = request.POST.get('advert_keywords')
                advert_keywords = filter(lambda x: ord(x)<128,advert_keywords) 
                title = request.POST.get('title')
                title = filter(lambda x: ord(x)<128,title)                                                 
                any_other_amenity = request.POST.get('any_other_amenity')
                any_other_amenity = filter(lambda x: ord(x)<128,any_other_amenity)                 

                advert_id = request.POST.get('advert_id')
                advert_obj = Advert.objects.get(advert_id=request.POST.get('advert_id'))
                advert_obj.supplier_id = Supplier.objects.get(supplier_id=request.session['supplier_id'])
                advert_obj.category_id = Category.objects.get(category_id=request.POST.get('categ'))
                advert_obj.advert_name = advert_title
                advert_obj.contact_name = contact_name
                advert_obj.contact_no = request.POST.get('phone_no')
                advert_obj.website = website
                advert_obj.latitude = request.POST.get('lat')
                advert_obj.longitude = request.POST.get('lng')
                advert_obj.short_description = short_discription
                advert_obj.product_description = product_discription
                advert_obj.currency = request.POST.get('currency')
                advert_obj.country_id = Country.objects.get(country_id=request.POST.get('country')) if request.POST.get(
                    'country') else None
                advert_obj.discount_description = discount_discription
                advert_obj.email_primary = email_primary
                advert_obj.email_secondary = request.POST.get('email_secondary')
                advert_obj.address_line_1 = address_line1
                advert_obj.address_line_2 = address_line2
                advert_obj.area = area
                advert_obj.landmark = landmark
                advert_obj.state_id = State.objects.get(state_id=request.POST.get('statec')) if request.POST.get(
                    'statec') else None
                advert_obj.city_place_id = City_Place.objects.get(
                    city_place_id=request.POST.get('city')) if request.POST.get(
                    'city') else None
                advert_obj.pincode_id = Pincode.objects.get(pincode_id=request.POST.get('pincode')) if request.POST.get(
                    'pincode') else None
                advert_obj.property_market_rate = request.POST.get('pro_mark_rate')
                advert_obj.possesion_status = request.POST.get('possesion_status')
                advert_obj.date_of_delivery = request.POST.get('date_of_delivery')
                advert_obj.other_projects = other_projects
                advert_obj.distance_frm_railway_station = request.POST.get('dis_rail_stat')
                advert_obj.distance_frm_railway_airport = request.POST.get('dis_airport')
                advert_obj.speciality = speciality
                advert_obj.affilated_to = affilated
                advert_obj.course_duration = course_duration
                advert_obj.happy_hour_offer = happy_hour_offer
                advert_obj.facility = facility
                advert_obj.keywords = advert_keywords
                advert_obj.image_video_space_used = request.POST.get('image_and_video_space')
                advert_obj.other_amenity = any_other_amenity
                advert_obj.title = title
                advert_obj.save()
                print "advert updated"

                any_other_details = request.POST.get('any_other_details')
                any_other_details = filter(lambda x: ord(x)<128,any_other_details) 

                if any_other_details:
                    advert_obj.any_other_details = any_other_details
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

                if request.POST.get('product_name_list'):
                    Product.objects.filter(advert_id=advert_id).delete()
                if request.POST.get('opening_day_list'):
                    WorkingHours.objects.filter(advert_id=advert_id).delete()
                if request.POST.get('amenity_list'):
                    Amenities.objects.filter(advert_id=advert_id).delete()

                if request.POST.get('near_attraction'):
                    NearByAttraction.objects.filter(advert_id=advert_id).delete()
                if request.POST.get('near_shopnmal'):
                    NearestShopping.objects.filter(advert_id=advert_id).delete()

                product_name_list = request.POST.get('product_name_list')
                product_name_list = product_name_list.split(',')
                product_price_list = request.POST.get('product_price_list')
                product_price_list = product_price_list.split(',')
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

def uploaded_images(request):
    if not request.user.is_authenticated():
        data = {'success':'Expired'}
    else: 
        try:
            advert_id = request.GET.get('advert_id')
            image_list = []
            advert_image = AdvertImage.objects.filter(advert_id=advert_id)
            for images in advert_image:
                image_path = images.advert_image.url
                image_path = image_path.split('/')
                advert_image_data = {
                    "image_path": SERVER_URL + images.advert_image.url,
                    "image_size": "12345",
                    "image_name": image_path[-1]
                }
                image_list.append(advert_image_data)
            data = {'image_list': image_list}
        except Exception, e:
            print 'Exception :', e
            data = {'data': 'none'}
        return HttpResponse(json.dumps(data), content_type='application/json')


def uploaded_videos(request):
    if not request.user.is_authenticated():
        data = {'success':'Expired'}

    else:     
        try:
            advert_id = request.GET.get('advert_id')
            video_list = []
            advert_video = Advert_Video.objects.filter(advert_id=advert_id)
            for videos in advert_video:
                video_path = videos.advert_video_name.url
                video_path = video_path.split('/')
                advert_video_data = {
                    "video_path": SERVER_URL + videos.advert_video_name.url,
                    "video_size": "12345",
                    "video_name": video_path[-1]
                }
                video_list.append(advert_video_data)
            data = {'video_list': video_list}
        except Exception, e:
            print 'Exception :', e
            data = {'data': 'none'}
        return HttpResponse(json.dumps(data), content_type='application/json')

def login_open(request):
    status = request.GET.get('status')
    print '.....In login OPEN STATUS=================',status
    if status:
        message_logout='Your session is timed out, Please login again.'
    else:
        message_logout = ''
    logout(request)        
    form = CaptchaForm()
    return render_to_response('Subscriber/user_login.html', dict(
        form=form,message_logout=message_logout
    ), context_instance=RequestContext(request))


@csrf_exempt
def signin(request):
    data = {}
    try:
        if request.POST:
            form = CaptchaForm(request.POST)
            print 'logs: login request with: ', request.POST
            username = request.POST['username']
            password = request.POST['password']
            request.session['login_user'] = ''

            if form.is_valid():
                try:
                    user_obj = Supplier.objects.get(username=username)

                    user = authenticate(username=username, password=password)
                    print 'valid form befor----->'
                    if user:
                        if user.is_active:
                            print 'valid form after----->', user
                            user_Supplier_obj = Supplier.objects.get(username=username)
                            if user_Supplier_obj.supplier_status == "1":
                                request.session['login_user'] = user_Supplier_obj.username
                                request.session['first_name'] = user_Supplier_obj.contact_person
                                request.session['supplier_id'] = user_Supplier_obj.supplier_id
                                if user_Supplier_obj.logo:
                                    request.session['user_image'] = SERVER_URL + user_Supplier_obj.logo.url
                                else:
                                    request.session['user_image'] = ''
                                login(request, user)

                                supplier_obj_count = Supplier.objects.filter(contact_email=user_Supplier_obj.username).count()
                                if supplier_obj_count == 1:
                                    data = {'success': 'true', 'username': request.session['first_name'],
                                        'supplier_id': user_Supplier_obj.supplier_id}
                                else:
                                    data = {'success': 'redirect', 'username': request.session['first_name'],
                                        'supplier_id': user_Supplier_obj.supplier_id}

                        else:
                            print '.......111......'
                            data = {'success': 'false', 'message': 'User Is Not Active'}
                            return HttpResponse(json.dumps(data), content_type='application/json')
                    else:
                        print '.........222.......'
                        data = {'success': 'Invalid Password', 'message': 'Invalid Password'}
                        print "====USERNAME", data
                        return HttpResponse(json.dumps(data), content_type='application/json')
                except Exception as e:
                    print '........3333......'
                    print e
                    data = {'success': 'false', 'message': 'Invalid Username'}
                    return HttpResponse(json.dumps(data), content_type='application/json')
            else:
                print '.......4444.....'
                form = CaptchaForm()
                data = {'success': 'Invalid Captcha', 'message': 'Invalid Captcha'}
                print "INVALID CAPTCHA"
                return HttpResponse(json.dumps(data), content_type='application/json')
    except MySQLdb.OperationalError, e:
        print '.......5555........'
        print e
        data = {'success': 'false', 'message': 'Internal server'}
        return HttpResponse(json.dumps(data), content_type='application/json')
    except Exception, e:
        print '.......6666........'
        print 'Exception ', e
        data = {'success': 'false', 'message': 'Invalid Username or Password'}
    return HttpResponse(json.dumps(data), content_type='application/json')


def subscriber_profile(request):
    if not request.user.is_authenticated():
        logout(request)
        form = CaptchaForm()
        return render_to_response('Subscriber/user_login.html', dict(
            form=form, message_logout='Your session is timed out, Please login again.'
        ), context_instance=RequestContext(request))

    else:     
        try:
            data = {}
            final_list = []
            final_list1 = []
            final_list2 = []

            try:
                # Item_list = Item.objects.all()

                # for Item_obj in Item_list:
                #     Item_video_id = Item_obj.Item_video_id
                #     video_s = SERVER_URL + Item_obj.Item_video_name.url
                #     # Item_video_name = Item_obj.Item_video_name
                #     print '------$$$---Item_video_name----video_s--', video_s
                #     list2 = {'Item_video_id': Item_video_id, 'video_s': video_s}
                #     final_list2.append(list2)

                supplier_id = request.GET.get('supplier_id')
                print '=======request======first===', supplier_id
                Supplier_obj = Supplier.objects.get(supplier_id=request.GET.get('supplier_id'))
                print "..................Supplier_obj.........", Supplier_obj

                advert_list = Advert.objects.filter(supplier_id=request.GET.get('supplier_id'))
                print "..................advert_list.........", advert_list
                for advert_obj in advert_list:
                    advert_id = advert_obj.advert_id
                    advert_name = advert_obj.advert_name
                    address_line_1 = advert_obj.address_line_1
                    area = advert_obj.area
                    category_name = advert_obj.category_id.category_name
                    #display_image = SERVER_URL + advert_obj.display_image.url
                    count_total = CouponCode.objects.filter(advert_id=advert_id).count()

                    pre_date = datetime.now().strftime("%d/%m/%Y")
                    print '..............pre_date......pre_date........', pre_date
                    pre_date = datetime.strptime(pre_date, "%d/%m/%Y")
                    print '..............pre_date...222...pre_date........', pre_date
                    advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)

                    start_date = advert_sub_obj.business_id.start_date

                    end_date = advert_sub_obj.business_id.end_date
                    end_date = datetime.strptime(end_date, "%d/%m/%Y")

                    date_gap = (end_date - pre_date).days

                    if date_gap > 0:
                        date_gap = date_gap
                    else:
                        date_gap = 0

                    business_id = advert_sub_obj.business_id
                    print business_id
                    premium_ser_list = PremiumService.objects.filter(business_id=business_id)
                    for obj in premium_ser_list:

                        start_date1 = obj.start_date
                        end_date1 = obj.end_date
                        end_date1 = datetime.strptime(end_date1, "%d/%m/%Y")
                        date_gap1 = (end_date1 - pre_date).days

                        if date_gap1 > 0:
                            date_gap1 = date_gap1
                        else:
                            date_gap1 = 0

                        list1 = {'start_date1': start_date1, 'date_gap1': date_gap1}
                        final_list1.append(list1)

                    list = {'advert_id': advert_id, 'advert_name': advert_name, 'address_line_1': address_line_1,
                            'area': area, 'category_name': category_name, 
                            'count_total': count_total, 'start_date': start_date, 'date_gap': date_gap}
                    final_list.append(list)


                sales_person_name_list =[]
                role_name_list = ["Admin","Sales","Super User","Marketing"]
                sales_person_list = UserProfile.objects.filter(user_status='1',user_role__role_name__in=role_name_list)
                for sale in sales_person_list:
                    sales_person_name = sale.user_first_name + ' '+ sale.user_last_name
                    sales_person_name = str(sales_person_name)
                    sales_data={
                    "sales_person_name":sales_person_name,
                    "sales_person_id":sale.user_id
                    }
              
                    sales_person_name_list.append(sales_data)

                user_first_name = Supplier_obj.sales_person_name.user_first_name
                user_last_name = Supplier_obj.sales_person_name.user_last_name
                sales_person_name = user_first_name + ' '+ user_last_name
                sales_person_contact_number = Supplier_obj.sales_person_name.user_contact_no

                if Supplier_obj.logo:
                    logo = SERVER_URL + Supplier_obj.logo.url
                else:
                    logo = SERVER_URL + '/static/assets/layouts/layout2/img/City_Hoopla_Logo.jpg'

                if Supplier_obj.phone_no:
                    phone_no1 = Supplier_obj.phone_no
                else:
                    phone_no1 = "--"

                if Supplier_obj.secondary_phone_no:
                    secondary_phone_no1 = Supplier_obj.secondary_phone_no
                else:
                    secondary_phone_no1 = "--"

                if Supplier_obj.supplier_email:
                    supplier_email1 = Supplier_obj.supplier_email
                else:
                    supplier_email1 = "--"

                phone_no1=phone_no1
                secondary_phone_no1=secondary_phone_no1
                supplier_email1 =supplier_email1
                business_name = Supplier_obj.business_name
                supplier_id = Supplier_obj.supplier_id
                business_details = Supplier_obj.business_details
                business_details_count = Supplier_obj.business_details
                business_details_length = len(business_details_count);
                phone_no = Supplier_obj.phone_no
                secondary_phone_no = Supplier_obj.secondary_phone_no
                supplier_email = Supplier_obj.supplier_email
                secondary_email = Supplier_obj.secondary_email
                address1 = Supplier_obj.address1
                address2 = Supplier_obj.address2
                country_id = Supplier_obj.country_id.country_id
                state_id = Supplier_obj.state.state_id
                city_place_id = Supplier_obj.city_place_id.city_place_id
                pincode_id = Supplier_obj.pincode.pincode_id
                city = Supplier_obj.city_place_id
                pincode = Supplier_obj.pincode

                city_name = Supplier_obj.city_place_id.city_id.city_name
                state_name = Supplier_obj.state.state_name
                country_name = Supplier_obj.country_id.country_name
                pincode_new = Supplier_obj.pincode.pincode


                contact_person = Supplier_obj.contact_person
                contact_no = Supplier_obj.contact_no
                contact_email = Supplier_obj.contact_email
                state_list = State.objects.filter(state_status='1').order_by('state_name')
                city_list = City.objects.filter(city_status='1').order_by('city_name')
                pincode_list = Pincode.objects.filter(pincode_status='1')
                country_list = Country.objects.filter(country_status='1').order_by('country_name')
                notification_status = Supplier_obj.notification_status
                reminders_status = Supplier_obj.reminders_status
                discounts_status = Supplier_obj.discounts_status
                request_call_back_status = Supplier_obj.request_call_back_status
                no_call_status = Supplier_obj.no_call_status


                data = {'sales_person_contact_number':sales_person_contact_number,'phone_no1':phone_no1,'secondary_phone_no1':secondary_phone_no1,'supplier_email1':supplier_email1,'sales_person_name':sales_person_name,'final_list2': final_list2, 'country_list': country_list, 'country_id': country_id,
                        'state_id': state_id, 'city_place_id': city_place_id, 'pincode_id': pincode_id,
                        'business_details_length': business_details_length, 'pincode_list': pincode_list,
                        'city_list': city_list, 'state_list': state_list, 'address2': address2, 'pincode': pincode,
                        'notification_status': notification_status, 'reminders_status': reminders_status,
                        'discounts_status': discounts_status, 'request_call_back_status': request_call_back_status,
                        'no_call_status': no_call_status, 'supplier_id': supplier_id, 'final_list1': final_list1,
                        'final_list': final_list, 'success': 'true', 'logo': logo, 'business_name': business_name,
                        'city': city, 'business_details': business_details, 'phone_no': phone_no,
                        'secondary_phone_no': secondary_phone_no, 'supplier_email': supplier_email,
                        'secondary_email': secondary_email, 'address1': address1, 'contact_person': contact_person,
                        'contact_no': contact_no, 'contact_email': contact_email,'supplier_id':supplier_id,
                        'city_name':city_name,'state_name':state_name,'country_name':country_name,'pincode_new':pincode_new}

            except IntegrityError as e:
                print e
                data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time',
                        'username': request.session['login_user']}
        except MySQLdb.OperationalError, e:
            print e
        except Exception, e:
            print 'Exception ', e
        return render(request, 'Subscriber/subscriber-profile.html', data)

@csrf_exempt
def subscriber_advert(request):
    if not request.user.is_authenticated():
        logout(request)
        form = CaptchaForm()
        return render_to_response('Subscriber/user_login.html', dict(
            form=form, message_logout='Your session is timed out, Please login again.'
        ), context_instance=RequestContext(request))

    else:     
        # last_touch = datetime.now()
        advert_status = ''
        date_gap = ''
        subscription_days = ''
        subscription_text = ''
        subscriber_color = ''
        try:
            data = {}

            advert_list = []
            category_list = []
            pre_date = datetime.now().strftime("%d/%m/%Y")
            pre_date = datetime.strptime(pre_date, "%d/%m/%Y")

            try:
                supplier_id = request.session['supplier_id']
                start_date_var = request.GET.get('start_date_var')
                end_date_var = request.GET.get('end_date_var')
                category_var = request.GET.get('category_var')
                status_var = request.GET.get('status_var')
                sort_by = request.GET.get('sort_by')
                if start_date_var:
                    start_date11 = datetime.strptime(start_date_var, "%d/%m/%Y")
                    
                if end_date_var:
                    end_date11 = datetime.strptime(end_date_var, "%d/%m/%Y") 
                    end_date11 = end_date11.replace(hour=23, minute=59,second = 59)

                Advert_list1 = Advert.objects.all()

                if start_date_var and end_date_var :
                    Advert_list1 = Advert_list1.filter(
                        supplier_id=supplier_id,
                        creation_date__range=[start_date11, end_date11]
                    )

                if category_var:
                    Advert_list1 = Advert_list1.filter(
                        supplier_id=supplier_id,
                        category_id=str(request.GET.get('category_var'))
                    )

                if sort_by == "oldest_first":
                    Advert_list1 = Advert_list1.filter(supplier_id=supplier_id).order_by('-creation_date').reverse()
                
                else:
                    Advert_list1 = Advert_list1.filter(supplier_id=supplier_id).order_by('-creation_date')
                
                advert_id_list = []
                print '......ADVERT LIST...PREVIOUS>>>>>>>>>>..',Advert_list1
                if status_var == '0':
                    for advert in Advert_list1:
                        try:
                            advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id = str(advert.advert_id))
                            end_date3 = advert_sub_obj.business_id.end_date
                            end_date3 = datetime.strptime(end_date3, "%d/%m/%Y")
                            if end_date3 < pre_date:
                                print pre_date, end_date3
                                advert_id_list.append(advert.advert_id)
                        except:
                            pass

                    Advert_list1 = Advert.objects.filter(advert_id__in = advert_id_list)
                
                if status_var == '1':
                    Advert_list1 = Advert_list1.filter(status  = '1')
                    for advert in Advert_list1:
                        end_date3 = ''
                        try:
                            advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id = str(advert.advert_id))
                            print advert_sub_obj.business_id.end_date
                            end_date3 = advert_sub_obj.business_id.end_date
                            end_date3 = datetime.strptime(end_date3, "%d/%m/%Y")
                            print 'MMMMMMMMMMMM.......status==1.......MMMMMMMMMMMMMM',end_date3
                            if end_date3 >= pre_date:
                                print pre_date, end_date3
                                advert_id_list.append(advert.advert_id)
                        except:
                            pass

                    Advert_list1 = Advert.objects.filter(advert_id__in = advert_id_list)                    
                print '......ADVERT LIST...AFTER>>>>>>>>>>..',Advert_list1

                category_objs = Category.objects.all()
                for category_obj in category_objs:
                    category_id = category_obj.category_id
                    category_name = category_obj.category_name
                    cat_data = {'category_name': category_name, 'category_id': category_id}
                    category_list.append(cat_data)

                business_obj = Business.objects.all()

                if start_date_var and end_date_var :
                    business_obj = business_obj.filter(
                        supplier=supplier_id,
                        business_created_date__range=[start_date11, end_date11]
                    )

                if category_var:
                    business_obj = business_obj.filter(
                        supplier=supplier_id,
                        category=request.GET.get('category_var')
                    )

                if sort_by == "oldest_first":
                    business_obj = business_obj.filter(supplier=supplier_id).order_by(
                        '-business_created_date').reverse()
                
                else:
                    business_obj = business_obj.filter(supplier=supplier_id).order_by('-business_created_date')
                
                print 'busines OBJECT>>>>>>PREVOIUS>>>>>>>>>',business_obj

                business_id_list = []
                if status_var == '0':
                    for business in business_obj:
                        try:
                            end_date4 = business.end_date
                            end_date4 = datetime.strptime(end_date4, "%d/%m/%Y")
                            if end_date4 < pre_date:
                                print pre_date, end_date4
                                business_id_list.append(business.business_id)
                        except:
                            pass
                    business_obj = Business.objects.filter(business_id__in = business_id_list)
                
                if status_var == '1':
                    business_obj = business_obj.filter(is_active = '1')
                    for business in business_obj:
                        try:
                            end_date4 = business.end_date
                            end_date4 = datetime.strptime(end_date4, "%d/%m/%Y") 
                            if end_date4 >= pre_date:
                                business_id_list.append(business.business_id)
                        except:
                            pass
                    business_obj = Business.objects.filter(business_id__in = business_id_list)
                print '........business obj......>>AFTER>>>>',business_obj
                for business in business_obj:
                    try:
                        advert_sub_obj = AdvertSubscriptionMap.objects.get(business_id=business.business_id)
                    except:

                        transaction_code = business.transaction_code                        
                        pre_date = datetime.now().strftime("%d/%m/%Y")
                        pre_date = datetime.strptime(pre_date, "%d/%m/%Y")

                        start_date = business.start_date
                        business_created_date = business.business_created_date.strftime("%d %b %y")
                        start_date = datetime.strptime(start_date, "%d/%m/%Y")
                        end_date = business.end_date
                        end_date = datetime.strptime(end_date, "%d/%m/%Y")

                        date_gap = (end_date - pre_date).days

                        if date_gap <= 10 and date_gap >= 0:
                            advert_status = 1
                            subscription_days = "( " + str(date_gap) + " day(s) Remaining )"
                            subscription_text = "Starts on " + start_date.strftime("%d %b %y")
                            subscriber_color = "orange"
                            advert_color = "orange"
                        elif date_gap < 0:
                            advert_status = 0
                            subscription_days = ""
                            subscription_text = "Expired on " + end_date.strftime("%d %b %y")
                            subscriber_color = "red"
                            advert_color = "red"
                        else:
                            advert_status = 2
                            subscription_days = "( " + str(date_gap) + " day(s) Remaining )"
                            subscription_text = "Starts on " + start_date.strftime("%d %b %y")
                            subscriber_color = "#333"
                            advert_color = "green"

                        premium_serv_list = premium_list(business.business_id,request)

                        try:
                            payment_obj = PaymentDetail.objects.get(business_id=business.business_id)
                            has_payment = 'yes'
                            payment_code = payment_obj.payment_code
                        except Exception:
                            has_payment = 'no'
                            payment_code = ''
                            pass

                        advert_data = {
                            'advert_id': '',
                            'transaction_code':transaction_code,
                            'payment_code':payment_code,
                            'business_id': business.business_id,
                            'advert_status': advert_status,
                            'advert_name': 'No Advert is added for this subscription.',
                            'advert_area': '',
                            'advert_creation_date': business_created_date,
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
                            'has_payment': has_payment
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
                    advert_creation_date = advert_obj.creation_date.strftime("%d %b %y")

                    if advert_obj.display_image:
                        display_image = SERVER_URL + advert_obj.display_image.url
                    else:
                        display_image = SERVER_URL + '/static/assets/layouts/layout2/img/City_Hoopla_Logo.jpg'
                    try:
                        advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)
                        transaction_code = advert_sub_obj.business_id.transaction_code
                        
                        business_id_new = advert_sub_obj.business_id
                        
                        payment_obj = PaymentDetail.objects.get(business_id = business_id_new)
                        
                        payment_code = payment_obj.payment_code
                        start_date = advert_sub_obj.business_id.start_date
                        start_date = datetime.strptime(start_date, "%d/%m/%Y")
                        end_date = advert_sub_obj.business_id.end_date
                        end_date = datetime.strptime(end_date, "%d/%m/%Y")
                        date_gap = (end_date - pre_date).days
   
                        if date_gap <= 10 and date_gap >= 0:
                            advert_status = 1
                            subscription_days = "( " + str(date_gap) + " day(s) Remaining )"
                            subscription_text = "Starts on " + start_date.strftime("%d %b %y")
                            subscriber_color = "orange"
                            advert_color = "orange"
                        elif date_gap < 0:
                            advert_status = 0
                            subscription_days = ""
                            subscription_text = "Expired on " + end_date.strftime("%d %b %y")
                            subscriber_color = "red"
                            advert_color = "red"
                        else:
                            advert_status = 2
                            subscription_days = "( " + str(date_gap) + " day(s) Remaining )"
                            subscription_text = "Starts on " + start_date.strftime("%d %b %y")
                            subscriber_color = "#333"
                            advert_color = "green"
                        business_id = advert_sub_obj.business_id
                        premium_service_list = premium_list(business_id,request)
                    except:
                        pass

                    advert_data = {
                        'advert_id': advert_id,
                        'transaction_code':transaction_code,
                        'payment_code':payment_code,                        
                        'advert_status': advert_status,
                        'advert_name': advert_name,
                        'advert_area': advert_area,
                        'advert_creation_date': advert_creation_date,
                        'date_gap': date_gap,
                        'advert_city': advert_city,
                        'category_name': category_name,
                        'display_image': display_image,
                        'advert_views': advert_views,
                        'advert_likes': advert_likes,
                        'advert_shares': advert_shares,
                        'subscription_days': subscription_days,
                        'subscription_text': subscription_text,
                        'subscriber_color': subscriber_color,
                        'premium_service_list': premium_service_list,
                        'advert_bookings': advert_bookings,
                        'advert_color': advert_color,
                        'is_active': str(advert_obj.status)
                    }
                    advert_list.append(advert_data)
                data = {
                   # 'last_touch':last_touch,
                    'advert_list': advert_list,
                    'category_list': category_list,
                    'start_date_var': start_date_var,
                    'end_date_var': end_date_var,
                    'category_var': category_var,
                    'status_var': status_var,
                    'supplier_id': supplier_id,
                    'success': 'true',
                    'sort_by': sort_by
                }

            except IntegrityError as e:
                print e
                data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time',
                        'username': request.session['login_user']}
        except MySQLdb.OperationalError, e:
            print e
        except Exception, e:
            print 'Exception ', e
        return render(request, 'Subscriber/subscriber-advert.html', data)


def premium_list(business_id,request):

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

        if date_gap <= 10 and date_gap >= 1:
            status_advert = 1
            premium_days = "( " + str(date_gap) + " days Remaining )"
            premium_text = "Starts on " + start_date.strftime("%d %b %y")
            premium_color = "orange"
        elif date_gap == 0:
            status_advert = 0
            premium_days = ""
            premium_text = "Expired on " + start_date.strftime("%d %b %y")
            premium_color = "red"
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


def subscriber_booking(request):
    if not request.user.is_authenticated():
        logout(request)
        form = CaptchaForm()
        return render_to_response('Subscriber/user_login.html', dict(
            form=form, message_logout='Your session is timed out, Please login again.'
        ), context_instance=RequestContext(request))

    else:
        try:
            data = {}
            final_list = []
            final_list1 = []
            final_list2 = []

            try:
                supplier_id = request.session['supplier_id']
                start_date_var = request.GET.get('start_date_var')
                print '.......start date ......',start_date_var
                end_date_var = request.GET.get('end_date_var')
                print '.......end date ......',end_date_var
                category_var = request.GET.get('category_var')
                status_var = request.GET.get('status_var')
                sort_by = request.GET.get('sort_by')

                if start_date_var:
                    start_date11 = datetime.strptime(start_date_var, "%d/%m/%Y") - timedelta(days=1)
                    #print '................start date11..........',start_date11
                if end_date_var:
                    end_date11 = datetime.strptime(end_date_var, "%d/%m/%Y") + timedelta(days=1)
                    #print '.........END DATE11......',end_date11

                if category_var:
                    #print '.......category_var.............}}}}'
                    Advert_list1 = Advert.objects.filter(
                        category_id=request.GET.get('category_var'),
                        supplier_id=supplier_id,
                    )
                else:
                    #print '....In ELSE...'
                    Advert_list1 = Advert.objects.filter(supplier_id=supplier_id)

                category_list = Category.objects.filter(category_status='1').exclude(category_name= 'Ticket Resell')
                for category_obj in category_list:
                    category_id = category_obj.category_id
                    category_name = category_obj.category_name
                    list2 = {'category_name': category_name, 'category_id': category_id}
                    final_list2.append(list2)

                for advert_obj in Advert_list1:

                    advert_id = advert_obj.advert_id
                    #print 'advert_id', advert_id
                    if advert_obj.display_image:
                        display_image = SERVER_URL + advert_obj.display_image.url
                    else:
                        display_image = ''

                    if start_date_var and end_date_var:
                        #print 'in .......if'
                        advert_sub_list = CouponCode.objects.filter(advert_id=advert_id,creation_date__range=[start_date11, end_date11]).order_by('id')
                    else:
                        #print '.... in else...'
                        advert_sub_list = CouponCode.objects.filter(advert_id=advert_id).order_by('id')

                    #print 'CCCCCCCCCCCCCCCCCCCCCCCCCCCCCC',advert_sub_list
                    for advert_sub_obj in advert_sub_list:
                        coupon_code = advert_sub_obj.coupon_code
                        # Availed date
                        creation_date1 = (advert_sub_obj.creation_date).strftime('%b %d,%Y')
                        #print '............creation_date..............', creation_date1

                        # consumer personal data
                        user_id = advert_sub_obj.user_id

                        consumer_obj = ConsumerProfile.objects.get(consumer_id=str(user_id))
                        #print 'SAWASW', consumer_obj
                        consumer_full_name = str(consumer_obj.consumer_full_name)

                        consumer_contact_no = consumer_obj.consumer_contact_no
                        consumer_email_id = consumer_obj.consumer_email_id
                        consumer_area = consumer_obj.consumer_area
                        if consumer_obj.consumer_profile_pic:
                            consumer_profile_pic = SERVER_URL + consumer_obj.consumer_profile_pic.url
                        else:
                            consumer_profile_pic = ''

                        # Expiry Date
                        pre_date = datetime.now().strftime("%d/%m/%Y")
                        pre_date = datetime.strptime(pre_date, "%d/%m/%Y")

                        expiry_data_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)
                        business_id = expiry_data_obj.business_id
                        end_date = expiry_data_obj.business_id.end_date
                        end_date = datetime.strptime(end_date, "%d/%m/%Y")
                        date_gap = (end_date - pre_date).days

                        if date_gap > 0:
                            date_gap = date_gap
                            status_advert = 1
                        else:
                            date_gap = 0
                            status_advert = 0

                        end_date = end_date.strftime('%b %d,%Y')
                        # logo

                        list = {'display_image': display_image, 'consumer_full_name': consumer_full_name,
                                'consumer_contact_no': consumer_contact_no, 'consumer_email_id': consumer_email_id,
                                'consumer_area': consumer_area, 'consumer_profile_pic': consumer_profile_pic,
                                'end_date': end_date, 'coupon_code': coupon_code, 'creation_date': creation_date1,
                                'date_gap': date_gap, 'status_advert': status_advert,'coupon_id':int(advert_sub_obj.id),
                                'user_id': str(consumer_obj.consumer_id)
                                }
                        final_list.append(list)
                import operator
                if sort_by == "oldest_first":
                    final_list.sort(key=operator.itemgetter('coupon_id'))
                    #final_list = final_list.reverse()
                else:
                    final_list.sort(key=operator.itemgetter('coupon_id'),reverse=True)
                    
                data = {
                    'final_list': final_list,
                    'success': 'true',
                    'category_list': final_list2,
                    'sort_by': sort_by
                }

            except IntegrityError as e:
                print e
                data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time',
                        'username': request.session['login_user']}
        except MySQLdb.OperationalError, e:
            print e
        except Exception, e:
            print 'Exception ', e
        print data
        return render(request, 'Subscriber/subscriber-booking.html', data)


def get_pincode(request):
    # pdb.set_trace()
    if not request.user.is_authenticated():
        data = {'success':'Expired'}

    else: 
        pincode_list = []
        try:
            city_id = request.GET.get('city_id')
            city_place_obj = City_Place.objects.get(city_place_id=city_id)
            pincode_list1 = Pincode.objects.filter(city_id=str(city_place_obj.city_id.city_id)).order_by('pincode')
            # pincode_objs = pincode_list1.values('pincode').distinct()
            # print pincode_objs
            for pincode in pincode_list1:
                options_data = '<option value="' + str(pincode.pincode_id) + '">' + str(pincode.pincode) + '</option>'
                pincode_list.append(options_data)
                # print pincode_list
            data = {'pincode_list': pincode_list}

        except Exception, ke:
            print ke
            data = {'city_list': 'none', 'message': 'No city available'}
        return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def update_profile(request):
    if not request.user.is_authenticated():
        data = {'success':'Expired'}
        # logout(request)
        # form = CaptchaForm()
        # return render_to_response('Subscriber/user_login.html', dict(
        #     form=form, message_logout='You have successfully logged out.'
        # ), context_instance=RequestContext(request))

    else:     
        try:
            if request.POST:
                supplier_id = request.POST.get('supplier_id')
                print '............supplier_id............', supplier_id
                supplier_obj = Supplier.objects.get(supplier_id=request.POST.get('supplier_id'))
                supplier_obj.business_name = request.POST.get('business_name')
                supplier_obj.phone_no = request.POST.get('phone_no')
                supplier_obj.secondary_phone_no = request.POST.get('sec_phone_no')
                supplier_obj.supplier_email = request.POST.get('email')
                supplier_obj.secondary_email = request.POST.get('sec_email')
                supplier_obj.address1 = request.POST.get('address1')
                supplier_obj.address2 = request.POST.get('address2')
                print supplier_obj.address2
                supplier_obj.city = City_Place.objects.get(city_place_id=request.POST.get('city'))
                print supplier_obj.city
                supplier_obj.country = Country.objects.get(country_id=request.POST.get('country'))
                supplier_obj.state = State.objects.get(state_id=request.POST.get('state'))
                supplier_obj.pincode = Pincode.objects.get(pincode_id=request.POST.get('pincode'))
                supplier_obj.business_details = request.POST.get('business')
                supplier_obj.contact_person = request.POST.get('user_name')
                supplier_obj.contact_email = request.POST.get('user_email')
                supplier_obj.contact_no = request.POST.get('user_contact_no')

                supplier_obj.notification_status = request.POST.get('state1')
                supplier_obj.reminders_status = request.POST.get('state2')
                supplier_obj.discounts_status = request.POST.get('state3')
                supplier_obj.request_call_back_status = request.POST.get('state4')
                supplier_obj.no_call_status = request.POST.get('state5')

                supplier_obj.save()
                try:
                    supplier_obj.logo = request.FILES['logo']
                except:
                    pass

                supplier_obj.save()

                data = {
                    'success': 'true',
                    'message': "Subscriber edited successfully"
                }
        except Exception, e:
            print e
            data = {
                'success': 'false',
                'message': str(e)
            }
    return HttpResponse(json.dumps(data), content_type='application/json')


# @csrf_exempt
# def subscriber_dashboard(request):
#     if not request.user.is_authenticated():
#         logout(request)
#         form = CaptchaForm()
#         return render_to_response('Subscriber/user_login.html', dict(
#             form=form, message_logout='You have successfully logged out.'
#         ), context_instance=RequestContext(request))

#     else:     
#         try:
#             data = {}
#             final_list = []
#             advert_list1 = []
#             try:
#                 #########.............Advert Stats.......For a week..................#####
#                 print '........Advert Stats.......For a week.....'
#                 today_date = str(datetime.now())
#                 one_month_date = str(datetime.now() - timedelta(days=7))
#                 Advert_list = Advert.objects.filter(supplier_id=request.session['supplier_id'])
#                 for ad_obj in Advert_list:
#                     advert_id = ad_obj.advert_id
#                     advert_name = ad_obj.advert_name
#                     advert_list1.append({'advert_id': advert_id, 'advert_name': advert_name})

#                 avail_discount_count = 0
#                 avail_callbacks_count = 0
#                 avail_callsmade_count = 0
#                 avail_shares_count = 0
#                 advert_id_list = []
#                 for advert_obj in Advert_list:
#                     advert_id = advert_obj.advert_id
#                     advert_id_list.append(advert_id)
#                     discount_count = CouponCode.objects.filter(advert_id=advert_id,
#                                                                creation_date__range=[one_month_date,
#                                                                                      today_date]).count()
#                     callbacks_count = AdvertCallbacks.objects.filter(advert_id=advert_id,
#                                                                      creation_date__range=[one_month_date,
#                                                                                            today_date]).count()
#                     callsmade_count = AdvertCallsMade.objects.filter(advert_id=advert_id,
#                                                                      creation_date__range=[one_month_date,
#                                                                                            today_date]).count()
#                     shares_count = AdvertShares.objects.filter(advert_id=advert_id,
#                                                                creation_date__range=[one_month_date,
#                                                                                      today_date]).count()

#                     avail_discount_count = avail_discount_count + discount_count
#                     avail_callbacks_count = avail_callbacks_count + callbacks_count
#                     avail_callsmade_count = avail_callsmade_count + callsmade_count
#                     avail_shares_count = avail_shares_count + shares_count

#                 #######.................Total Bookings Graph....For a week...........########
#                 print '....Total Bookings Graph....For a week....'
#                 current_date = datetime.now()
#                 last_date = (datetime.now() - timedelta(days=7))

#                 list = []
#                 total_view_list = CouponCode.objects.filter(creation_date__range=[last_date, current_date],
#                                                             advert_id__in=advert_id_list)
#                 print 'SSSSSSSSSSSSSSSSSSSSSSS',total_view_list
#                 mon11 = tue11 = wen11 = thus11 = fri11 = sat11 = sun11 = 0
#                 if total_view_list:
#                     for view_obj in total_view_list:
#                         creation_date = view_obj.creation_date
#                         consumer_day = calendar.day_name[creation_date.weekday()]
#                         if consumer_day == 'Monday':
#                             mon11 = mon11 + 1
#                         elif consumer_day == 'Tuesday':
#                             tue11 = tue11 + 1
#                         elif consumer_day == 'Wednesday':
#                             wen11 = wen11 + 1
#                         elif consumer_day == 'Thursday':
#                             thus11 = thus11 + 1
#                         elif consumer_day == 'Friday':
#                             fri11 = fri11 + 1
#                         elif consumer_day == 'Saturday':
#                             sat11 = sat11 + 1
#                         elif consumer_day == 'Sunday':
#                             sun11 = sun11 + 1
#                         else:
#                             pass

#                 print ".........total Bookings Graph....For a week...", mon11, tue11, wen11, thus11, fri11, sat11, sun11

#                 ##########..................Total Views Graph........for a week.............############

#                 current_date = datetime.now()
#                 last_date = (datetime.now() - timedelta(days=7))

#                 list = []
#                 total_view_list = AdvertView.objects.filter(creation_date__range=[last_date, current_date],
#                                                             advert_id__in=advert_id_list)
#                 mon22 = tue22 = wen22 = thus22 = fri22 = sat22 = sun22 = 0
#                 if total_view_list:
#                     for view_obj in total_view_list:
#                         creation_date = view_obj.creation_date
#                         consumer_day = calendar.day_name[creation_date.weekday()]
#                         if consumer_day == 'Monday':
#                             mon22 = mon22 + 1
#                         elif consumer_day == 'Tuesday':
#                             tue22 = tue22 + 1
#                         elif consumer_day == 'Wednesday':
#                             wen22 = wen22 + 1
#                         elif consumer_day == 'Thursday':
#                             thus22 = thus22 + 1
#                         elif consumer_day == 'Friday':
#                             fri22 = fri22 + 1
#                         elif consumer_day == 'Saturday':
#                             sat22 = sat22 + 1
#                         elif consumer_day == 'Sunday':
#                             sun22 = sun22 + 1
#                         else:
#                             pass

#                 data = {'success': 'true', 'avail_callbacks_count': avail_callbacks_count,
#                         'avail_callsmade_count': avail_callsmade_count, 'avail_shares_count': avail_shares_count,
#                         'avail_discount_count': avail_discount_count,
#                         'mon11': mon11, 'tue11': tue11, 'wen11': wen11, 'thus11': thus11, 'fri11': fri11, 'sat11': sat11,
#                         'sun11': sun11, 'mon22': mon22, 'tue22': tue22, 'wen22': wen22, 'thus22': thus22, 'fri22': fri22,
#                         'sat22': sat22, 'sun22': sun22, 'advert_list1': advert_list1}

#             except IntegrityError as e:
#                 print e
#                 data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time',
#                         'username': request.session['login_user']}
#         except MySQLdb.OperationalError, e:
#             print e
#         except Exception, e:
#             print 'Exception ', e

#         print data
#         return render(request, 'Subscriber/subscriber-dashboard.html', data)

@csrf_exempt
def subscriber_dashboard(request):
    if not request.user.is_authenticated():
        logout(request)
        form = CaptchaForm()
        return render_to_response('Subscriber/user_login.html', dict(
            form=form, message_logout='Your session is timed out, Please login again.'
        ), context_instance=RequestContext(request))

    else:     
        try:
            data = {}
            final_list = []
            advert_list1 = []
            try:
                user_Supplier_obj = Supplier.objects.get(supplier_id=request.GET.get('supplier_id'))
                print "-----------------active----------------------",user_Supplier_obj.username
                request.session['login_user'] = user_Supplier_obj.contact_email
                request.session['first_name'] = user_Supplier_obj.contact_person
                request.session['supplier_id'] = user_Supplier_obj.supplier_id

                Advert_list = Advert.objects.filter(supplier_id=request.GET.get('supplier_id'))#request.session['supplier_id']

                for ad_obj in Advert_list:
                    advert_id = ad_obj.advert_id
                    advert_name = ad_obj.advert_name
                    advert_list1.append({'advert_id': advert_id, 'advert_name': advert_name})


                data = {'success': 'true', 'advert_list1': advert_list1}

            except IntegrityError as e:
                print e
                data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time',
                        'username': request.session['login_user']}
        except MySQLdb.OperationalError, e:
            print e
        except Exception, e:
            print 'Exception ', e
        return render(request, 'Subscriber/subscriber-dashboard.html', data)


# TO GET THE CITY
def get_city_places(request):
    city_list = []
    try:
        city_objs = City_Place.objects.filter(city_status='1')
        for city in city_objs:
            city_list.append({'city_place_id': city.city_place_id, 'city': city.city_id.city_name})
            print '............city List..........PPP', city_list
        data = city_list
        return data

    except Exception, ke:
        print ke
        data = {'city_list': 'none', 'message': 'No city available'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def get_admin_filter(request):
    if not request.user.is_authenticated():
        data = {'success':'Expired'}

    else:     
        try:
            data = {}
            final_list = []
            final_list1 = []
            try:
                if request.GET.get('week_var') == 'month':
                    var1 = str(request.GET.get('week_var'))
                    city_front = request.GET.get('citys_var')
                    print '//...........city_front......//', city_front

                    Supplier_obj = Supplier.objects.get(supplier_id=request.GET.get('supplier_id'))

                    if Supplier_obj.logo:
                        logo = SERVER_URL + Supplier_obj.logo.url
                    else:
                        logo = ''

                    #########.............Advert Stats.......For a Month..................#####
                    print '..........Advert Stats.......For a Month.......'
                    today_date = str(datetime.now())
                    one_month_date = str(datetime.now() - timedelta(days=30))
                    Advert_list = Advert.objects.filter(supplier_id=request.GET.get('supplier_id'))

                    avail_discount_count = 0
                    avail_callbacks_count = 0
                    avail_callsmade_count = 0
                    avail_shares_count = 0

                    for advert_obj in Advert_list:
                        advert_id = advert_obj.advert_id
                        discount_count = CouponCode.objects.filter(advert_id=advert_id,
                                                                   creation_date__range=[one_month_date,
                                                                                         today_date]).count()
                        callbacks_count = AdvertCallbacks.objects.filter(advert_id=advert_id,
                                                                         creation_date__range=[one_month_date,
                                                                                               today_date]).count()
                        callsmade_count = AdvertCallsMade.objects.filter(advert_id=advert_id,
                                                                         creation_date__range=[one_month_date,
                                                                                               today_date]).count()
                        shares_count = AdvertShares.objects.filter(advert_id=advert_id,
                                                                   creation_date__range=[one_month_date,
                                                                                         today_date]).count()

                        avail_discount_count = avail_discount_count + discount_count
                        avail_callbacks_count = avail_callbacks_count + callbacks_count
                        avail_callsmade_count = avail_callsmade_count + callsmade_count
                        avail_shares_count = avail_shares_count + shares_count

                    #######.........Total subscription  Graph......(1)...For a Month...........########
                    print '.......Total subscription  Graph......(1)...For a Month....'
                    today = date.today()
                    date_cal = datetime(today.year, today.month, today.day)
                    numb = (date_cal.day - 1) // 7 + 1

                    total_subscription_count1 = 0
                    total_subscription_count2 = 0
                    total_subscription_count3 = 0
                    total_subscription_count4 = 0
                    total_subscription_count5 = 0
                    for i in range(0, numb):
                        if i == 0:
                            start_date = date(today.year, today.month, 01)
                            end_date = date(today.year, today.month, 8)
                            total_subscription_list = Business.objects.filter(
                                business_created_date__range=[start_date, end_date])

                            if total_subscription_list:
                                for consumer_obj in total_subscription_list:

                                    # city_nm1 = consumer_obj.supplier.city.city_name
                                    city_id = consumer_obj.supplier.city_place_id.city_id
                                    print '......................city_id ....11......', city_id

                                    if str(city_front) == str(city_id):
                                        total_subscription_count1 = total_subscription_count1 + 1
                                    else:
                                        pass

                        elif i == 1:
                            start_date = date(today.year, today.month, 8)
                            end_date = date(today.year, today.month, 16)
                            total_subscription_list = Business.objects.filter(
                                business_created_date__range=[start_date, end_date])

                            if total_subscription_list:
                                for consumer_obj in total_subscription_list:

                                    # city_nm1 = consumer_obj.supplier.city.city_name
                                    city_id = consumer_obj.supplier.city_place_id.city_id
                                    print '......................city_id ....11......', city_id

                                    if str(city_front) == str(city_id):
                                        total_subscription_count2 = total_subscription_count2 + 1
                                    else:
                                        pass

                        elif i == 2:
                            start_date = date(today.year, today.month, 16)
                            end_date = date(today.year, today.month, 23)
                            total_subscription_list = Business.objects.filter(
                                business_created_date__range=[start_date, end_date])

                            if total_subscription_list:
                                for consumer_obj in total_subscription_list:

                                    # city_nm1 = consumer_obj.supplier.city.city_name
                                    city_id = consumer_obj.supplier.city_place_id.city_id
                                    print '......................city_id .....11.....', city_id

                                    if str(city_front) == str(city_id):
                                        total_subscription_count3 = total_subscription_count3 + 1
                                    else:
                                        pass

                        elif i == 3:
                            start_date = date(today.year, today.month, 23)
                            end_date = date(today.year, today.month, 30)
                            total_subscription_list = Business.objects.filter(
                                business_created_date__range=[start_date, end_date])

                            if total_subscription_list:
                                for consumer_obj in total_subscription_list:

                                    # city_nm1 = consumer_obj.supplier.city.city_name
                                    city_id = consumer_obj.supplier.city_place_id.city_id
                                    print '......................city_id ....11......', city_id

                                    if str(city_front) == str(city_id):
                                        total_subscription_count4 = total_subscription_count4 + 1
                                    else:
                                        pass

                        elif i == 4:
                            start_date = date(today.year, today.month, 30)
                            end_date = date(today.year, today.month, 31)

                            total_subscription_list = Business.objects.filter(
                                business_created_date__range=[start_date, end_date])

                            if total_subscription_list:
                                for consumer_obj in total_subscription_list:

                                    # city_nm1 = consumer_obj.supplier.city.city_name
                                    city_id = consumer_obj.supplier.city_place_id.city_id
                                    print '......................city_id ...11.......', city_id

                                    if str(city_front) == str(city_id):
                                        total_subscription_count5 = total_subscription_count5 + 1
                                    else:
                                        pass

                    print '//...........total_subscription_count1......//', total_subscription_count1
                    print '//...........total_subscription_count2......//', total_subscription_count2
                    print '//...........total_subscription_count3......//', total_subscription_count3
                    print '//...........total_subscription_count4......//', total_subscription_count4
                    print '//...........total_subscription_count5......//', total_subscription_count5

                    ##########.......Todays Payment received.....(2)....for a month.............############

                    print '........Todays Payment received...(2)....for a month......'
                    today = date.today()
                    date_cal = datetime(today.year, today.month, today.day)
                    numb = (date_cal.day - 1) // 7 + 1

                    payment_count1 = 0
                    payment_count2 = 0
                    payment_count3 = 0
                    payment_count4 = 0
                    payment_count5 = 0

                    for i in range(0, numb):
                        if i == 0:
                            start_date = date(today.year, today.month, 01)
                            end_date = date(today.year, today.month, 8)

                            payment_list = PaymentDetail.objects.filter(payment_created_date__range=[start_date, end_date])

                            if payment_list:
                                for consumer_obj in payment_list:

                                    # city_nm1 = consumer_obj.supplier.city.city_name
                                    city_id = consumer_obj.business_id.supplier.city_place_id.city_id
                                    print '......................city_id ....22......', city_id

                                    if str(city_front) == str(city_id):
                                        payment_count1 = payment_count1 + 1
                                    else:
                                        pass

                        elif i == 1:
                            start_date = date(today.year, today.month, 8)
                            end_date = date(today.year, today.month, 16)
                            payment_list = PaymentDetail.objects.filter(payment_created_date__range=[start_date, end_date])

                            if payment_list:
                                for consumer_obj in payment_list:

                                    # city_nm1 = consumer_obj.supplier.city.city_name
                                    city_id = consumer_obj.business_id.supplier.city_place_id.city_id
                                    print '......................city_id ....22......', city_id

                                    if str(city_front) == str(city_id):
                                        payment_count2 = payment_count2 + 1
                                    else:
                                        pass

                        elif i == 2:
                            start_date = date(today.year, today.month, 16)
                            end_date = date(today.year, today.month, 23)
                            payment_list = PaymentDetail.objects.filter(payment_created_date__range=[start_date, end_date])

                            if payment_list:
                                for consumer_obj in payment_list:

                                    # city_nm1 = consumer_obj.supplier.city.city_name
                                    city_id = consumer_obj.business_id.supplier.city_place_id.city_id
                                    print '......................city_id ....22......', city_id

                                    if str(city_front) == str(city_id):
                                        payment_count3 = payment_count3 + 1
                                    else:
                                        pass

                        elif i == 3:
                            start_date = date(today.year, today.month, 23)
                            end_date = date(today.year, today.month, 30)
                            payment_list = PaymentDetail.objects.filter(payment_created_date__range=[start_date, end_date])

                            if payment_list:
                                for consumer_obj in payment_list:

                                    # city_nm1 = consumer_obj.supplier.city.city_name
                                    city_id = consumer_obj.business_id.supplier.city_place_id.city_id
                                    print '......................city_id ....22......', city_id

                                    if str(city_front) == str(city_id):
                                        payment_count4 = payment_count4 + 1
                                    else:
                                        pass

                        elif i == 4:
                            start_date = date(today.year, today.month, 30)
                            end_date = date(today.year, today.month, 31)
                            payment_list = PaymentDetail.objects.filter(payment_created_date__range=[start_date, end_date])

                            if payment_list:
                                for consumer_obj in payment_list:

                                    # city_nm1 = consumer_obj.supplier.city.city_name
                                    city_id = consumer_obj.business_id.supplier.city_place_id.city_id
                                    print '......................city_id ....22......', city_id

                                    if str(city_front) == str(city_id):
                                        payment_count5 = payment_count5 + 1
                                    else:
                                        pass

                    print '//...........payment_count1......//', payment_count1
                    print '//...........payment_count2......//', payment_count2
                    print '//...........payment_count3......//', payment_count3
                    print '//...........payment_count4......//', payment_count4
                    print '//...........payment_count5......//', payment_count5

                    ##########........Todays Login.(3).....for a month.............############

                    print '.......Todays Login.....(3)......for a month........'
                    today = date.today()
                    date_cal = datetime(today.year, today.month, today.day)
                    numb = (date_cal.day - 1) // 7 + 1

                    login_count1 = 0
                    login_count2 = 0
                    login_count3 = 0
                    login_count4 = 0
                    login_count5 = 0

                    for i in range(0, numb):
                        if i == 0:
                            start_date = date(today.year, today.month, 01)
                            end_date = date(today.year, today.month, 8)
                            login_count1 = ConsumerProfile.objects.filter(
                                last_time_login__range=[start_date, end_date]).count()
                        elif i == 1:
                            start_date = date(today.year, today.month, 8)
                            end_date = date(today.year, today.month, 16)
                            login_count2 = ConsumerProfile.objects.filter(
                                last_time_login__range=[start_date, end_date]).count()
                        elif i == 2:
                            start_date = date(today.year, today.month, 16)
                            end_date = date(today.year, today.month, 23)
                            login_count3 = ConsumerProfile.objects.filter(
                                last_time_login__range=[start_date, end_date]).count()
                        elif i == 3:
                            start_date = date(today.year, today.month, 23)
                            end_date = date(today.year, today.month, 30)
                            login_count4 = ConsumerProfile.objects.filter(
                                last_time_login__range=[start_date, end_date]).count()
                        elif i == 4:
                            start_date = date(today.year, today.month, 30)
                            end_date = date(today.year, today.month, 31)
                            login_count5 = ConsumerProfile.objects.filter(
                                last_time_login__range=[start_date, end_date]).count()

                    print '//...........login_count1......//', login_count1
                    print '//...........login_count2......//', login_count2
                    print '//...........login_count3......//', login_count3
                    print '//...........login_count4......//', login_count4
                    print '//...........login_count5......//', login_count5

                    ##########....... New subscription view...(4).....for a month.............############

                    print '.....New subscription view...(4)......for a month........'
                    today = date.today()
                    date_cal = datetime(today.year, today.month, today.day)
                    numb = (date_cal.day - 1) // 7 + 1

                    subscription_count1 = 0
                    subscription_count2 = 0
                    subscription_count3 = 0
                    subscription_count4 = 0
                    subscription_count5 = 0

                    for i in range(0, numb):
                        if i == 0:
                            start_date = date(today.year, today.month, 01)
                            end_date = date(today.year, today.month, 8)
                            subscription_list = Business.objects.filter(business_created_date__range=[start_date, end_date])

                            if subscription_list:
                                for consumer_obj in subscription_list:

                                    # city_nm1 = consumer_obj.supplier.city.city_name
                                    city_id = consumer_obj.supplier.city_place_id.city_id
                                    print '......................city_id ....44......', city_id

                                    if str(city_front) == str(city_id):
                                        subscription_count1 = subscription_count1 + 1
                                    else:
                                        pass

                        elif i == 1:
                            start_date = date(today.year, today.month, 8)
                            end_date = date(today.year, today.month, 16)
                            subscription_list = Business.objects.filter(business_created_date__range=[start_date, end_date])

                            if subscription_list:
                                for consumer_obj in subscription_list:

                                    # city_nm1 = consumer_obj.supplier.city.city_name
                                    city_id = consumer_obj.supplier.city_place_id.city_id
                                    print '......................city_id ....44......', city_id

                                    if str(city_front) == str(city_id):
                                        subscription_count2 = subscription_count2 + 1
                                    else:
                                        pass

                        elif i == 2:
                            start_date = date(today.year, today.month, 16)
                            end_date = date(today.year, today.month, 23)
                            subscription_list = Business.objects.filter(business_created_date__range=[start_date, end_date])

                            if subscription_list:
                                for consumer_obj in subscription_list:

                                    # city_nm1 = consumer_obj.supplier.city.city_name
                                    city_id = consumer_obj.supplier.city_place_id.city_id
                                    print '......................city_id ....44......', city_id

                                    if str(city_front) == str(city_id):
                                        subscription_count3 = subscription_count3 + 1
                                    else:
                                        pass

                        elif i == 3:
                            start_date = date(today.year, today.month, 23)
                            end_date = date(today.year, today.month, 30)
                            subscription_list = Business.objects.filter(business_created_date__range=[start_date, end_date])

                            if subscription_list:
                                for consumer_obj in subscription_list:

                                    # city_nm1 = consumer_obj.supplier.city.city_name
                                    city_id = consumer_obj.supplier.city_place_id.city_id
                                    print '......................city_id ....44......', city_id

                                    if str(city_front) == str(city_id):
                                        subscription_count4 = subscription_count4 + 1
                                    else:
                                        pass

                        elif i == 4:
                            start_date = date(today.year, today.month, 30)
                            end_date = date(today.year, today.month, 31)
                            subscription_list = Business.objects.filter(business_created_date__range=[start_date, end_date])

                            if subscription_list:
                                for consumer_obj in subscription_list:

                                    # city_nm1 = consumer_obj.supplier.city.city_name
                                    city_id = consumer_obj.supplier.city_place_id.city_id
                                    print '......................city_id ....44......', city_id

                                    if str(city_front) == str(city_id):
                                        subscription_count5 = subscription_count5 + 1
                                    else:
                                        pass

                    print '//...........subscription_count1......//', subscription_count1
                    print '//...........subscription_count2......//', subscription_count2
                    print '//...........subscription_count3......//', subscription_count3
                    print '//...........subscription_count4......//', subscription_count4
                    print '//...........subscription_count5......//', subscription_count5

                    data = {'var1': var1, 'success': 'true', 'logo': logo, 'avail_callbacks_count': avail_callbacks_count,
                            'avail_callsmade_count': avail_callsmade_count, 'avail_shares_count': avail_shares_count,
                            'avail_discount_count': avail_discount_count,
                            'total_subscription_count1': total_subscription_count1,
                            'total_subscription_count2': total_subscription_count2,
                            'total_subscription_count3': total_subscription_count3,
                            'total_subscription_count4': total_subscription_count4,
                            'total_subscription_count5': total_subscription_count5, 'payment_count1': payment_count1,
                            'payment_count2': payment_count2,
                            'payment_count3': payment_count3, 'payment_count4': payment_count4,
                            'payment_count5': payment_count5, 'login_count1': login_count1, 'login_count2': login_count2,
                            'login_count3': login_count3, 'login_count4': login_count4, 'login_count5': login_count5,
                            'subscription_count1': subscription_count1, 'subscription_count2': subscription_count2,
                            'subscription_count3': subscription_count3, 'subscription_count4': subscription_count4,
                            'subscription_count5': subscription_count5}

                if request.GET.get('week_var') == 'week':
                    var1 = str(request.GET.get('week_var'))
                    city_front = request.GET.get('citys_var')

                    Supplier_obj = Supplier.objects.get(supplier_id=request.GET.get('supplier_id'))

                    if Supplier_obj.logo:
                        logo = SERVER_URL + Supplier_obj.logo.url
                    else:
                        logo = ''

                    #########.............Advert Stats.......For a week..................#####
                    print '........Advert Stats.......For a week.....'
                    today_date = str(datetime.now())
                    one_month_date = str(datetime.now() - timedelta(days=7))
                    Advert_list = Advert.objects.filter(supplier_id=request.GET.get('supplier_id'))

                    avail_discount_count = 0
                    avail_callbacks_count = 0
                    avail_callsmade_count = 0
                    avail_shares_count = 0

                    for advert_obj in Advert_list:
                        advert_id = advert_obj.advert_id
                        discount_count = CouponCode.objects.filter(advert_id=advert_id,
                                                                   creation_date__range=[one_month_date,
                                                                                         today_date]).count()
                        callbacks_count = AdvertCallbacks.objects.filter(advert_id=advert_id,
                                                                         creation_date__range=[one_month_date,
                                                                                               today_date]).count()
                        callsmade_count = AdvertCallsMade.objects.filter(advert_id=advert_id,
                                                                         creation_date__range=[one_month_date,
                                                                                               today_date]).count()
                        shares_count = AdvertShares.objects.filter(advert_id=advert_id,
                                                                   creation_date__range=[one_month_date,
                                                                                         today_date]).count()

                        avail_discount_count = avail_discount_count + discount_count
                        avail_callbacks_count = avail_callbacks_count + callbacks_count
                        avail_callsmade_count = avail_callsmade_count + callsmade_count
                        avail_shares_count = avail_shares_count + shares_count

                    #######...........Total subscription  Graph......(1)....For a week...........########
                    print '.....Total subscription  Graph......(1)...For a week....'
                    current_date = datetime.now()
                    last_date = (datetime.now() - timedelta(days=7))

                    list = []
                    total_view_list = Business.objects.filter(business_created_date__range=[last_date, current_date])
                    mon1 = tue1 = wen1 = thus1 = fri1 = sat1 = sun1 = 0
                    if total_view_list:
                        for view_obj in total_view_list:
                            city_nm = view_obj.supplier.city_place_id.city_id
                            business_created_date = view_obj.business_created_date
                            consumer_day = calendar.day_name[business_created_date.weekday()]
                            if consumer_day == 'Monday' and str(city_front) == str(city_nm):
                                mon1 = mon1 + 1
                            elif consumer_day == 'Tuesday' and str(city_front) == str(city_nm):
                                tue1 = tue1 + 1
                            elif consumer_day == 'Wednesday' and str(city_front) == str(city_nm):
                                wen1 = wen1 + 1
                            elif consumer_day == 'Thursday' and str(city_front) == str(city_nm):
                                thus1 = thus1 + 1
                            elif consumer_day == 'Friday' and str(city_front) == str(city_nm):
                                fri1 = fri1 + 1
                            elif consumer_day == 'Saturday' and str(city_front) == str(city_nm):
                                sat1 = sat1 + 1
                            elif consumer_day == 'Sunday' and str(city_front) == str(city_nm):
                                sun1 = sun1 + 1
                            else:
                                pass

                    print "...........Total subscription  Graph......(1)...For a week...", mon1, tue1, wen1, thus1, fri1, sat1, sun1

                    ##########................Todays Payment received.....(2).......for a week.............############

                    current_date = datetime.now()
                    last_date = (datetime.now() - timedelta(days=7))

                    list = []
                    total_view_list = PaymentDetail.objects.filter(payment_created_date__range=[last_date, current_date])
                    mon2 = tue2 = wen2 = thus2 = fri2 = sat2 = sun2 = 0
                    if total_view_list:
                        for view_obj in total_view_list:
                            city_nm = view_obj.business_id.supplier.city_place_id.city_id
                            payment_created_date = view_obj.payment_created_date
                            consumer_day = calendar.day_name[payment_created_date.weekday()]
                            if consumer_day == 'Monday' and str(city_front) == str(city_nm):
                                mon2 = mon2 + 1
                            elif consumer_day == 'Tuesday' and str(city_front) == str(city_nm):
                                tue2 = tue2 + 1
                            elif consumer_day == 'Wednesday' and str(city_front) == str(city_nm):
                                wen2 = wen2 + 1
                            elif consumer_day == 'Thursday' and str(city_front) == str(city_nm):
                                thus2 = thus2 + 1
                            elif consumer_day == 'Friday' and str(city_front) == str(city_nm):
                                fri2 = fri2 + 1
                            elif consumer_day == 'Saturday' and str(city_front) == str(city_nm):
                                sat2 = sat2 + 1
                            elif consumer_day == 'Sunday' and str(city_front) == str(city_nm):
                                sun2 = sun2 + 1
                            else:
                                pass

                    ##########.....Todays Login.(3)... for a week  ##########
                    current_date = datetime.now()
                    last_date = (datetime.now() - timedelta(days=7))

                    list = []
                    total_view_list = ConsumerProfile.objects.filter(last_time_login__range=[last_date, current_date])
                    mon3 = tue3 = wen3 = thus3 = fri3 = sat3 = sun3 = 0
                    if total_view_list:
                        for view_obj in total_view_list:
                            last_time_login = view_obj.last_time_login
                            consumer_day = calendar.day_name[last_time_login.weekday()]
                            if consumer_day == 'Monday':
                                mon3 = mon3 + 1
                            elif consumer_day == 'Tuesday':
                                tue3 = tue3 + 1
                            elif consumer_day == 'Wednesday':
                                wen3 = wen3 + 1
                            elif consumer_day == 'Thursday':
                                thus3 = thus3 + 1
                            elif consumer_day == 'Friday':
                                fri3 = fri3 + 1
                            elif consumer_day == 'Saturday':
                                sat3 = sat3 + 1
                            elif consumer_day == 'Sunday':
                                sun3 = sun3 + 1
                            else:
                                pass

                    ##########..... New subscription view...(4).... for a week  ##########
                    current_date = datetime.now()
                    last_date = (datetime.now() - timedelta(days=7))

                    list = []
                    total_view_list = Business.objects.filter(business_created_date__range=[last_date, current_date])
                    mon4 = tue4 = wen4 = thus4 = fri4 = sat4 = sun4 = 0
                    if total_view_list:
                        for view_obj in total_view_list:
                            city_nm = view_obj.supplier.city_place_id.city_id
                            business_created_date = view_obj.business_created_date
                            consumer_day = calendar.day_name[business_created_date.weekday()]
                            if consumer_day == 'Monday' and str(city_front) == str(city_nm):
                                mon4 = mon4 + 1
                            elif consumer_day == 'Tuesday' and str(city_front) == str(city_nm):
                                tue4 = tue4 + 1
                            elif consumer_day == 'Wednesday' and str(city_front) == str(city_nm):
                                wen4 = wen4 + 1
                            elif consumer_day == 'Thursday' and str(city_front) == str(city_nm):
                                thus4 = thus4 + 1
                            elif consumer_day == 'Friday' and str(city_front) == str(city_nm):
                                fri4 = fri4 + 1
                            elif consumer_day == 'Saturday' and str(city_front) == str(city_nm):
                                sat4 = sat4 + 1
                            elif consumer_day == 'Sunday' and str(city_front) == str(city_nm):
                                sun4 = sun4 + 1
                            else:
                                pass

                    data = {'var1': var1, 'success': 'true', 'logo': logo, 'avail_callbacks_count': avail_callbacks_count,
                            'avail_callsmade_count': avail_callsmade_count, 'avail_shares_count': avail_shares_count,
                            'avail_discount_count': avail_discount_count,
                            'mon1': mon1, 'tue1': tue1, 'wen1': wen1, 'thus1': thus1, 'fri1': fri1, 'sat1': sat1,
                            'sun1': sun1, 'mon2': mon2, 'tue2': tue2, 'wen2': wen2, 'thus2': thus2, 'fri2': fri2,
                            'sat2': sat2, 'sun2': sun2,
                            'mon3': mon3, 'tue3': tue3, 'wen3': wen3, 'thus3': thus3, 'fri3': fri3, 'sat3': sat3,
                            'sun3': sun3,
                            'mon4': mon4, 'tue4': tue4, 'wen4': wen4, 'thus4': thus4, 'fri4': fri4, 'sat4': sat4,
                            'sun4': sun4}


            except IntegrityError as e:
                print e
                data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time',
                        'username': request.session['login_user']}
        except MySQLdb.OperationalError, e:
            print e
        except Exception, e:
            print 'Exception ', e

        print data
        return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def subscriber_advert_stat(request):
    if not request.user.is_authenticated():
        logout(request)
        form = CaptchaForm()
        return render_to_response('Subscriber/user_login.html', dict(
            form=form, message_logout='Your session is timed out, Please login again.'
        ), context_instance=RequestContext(request))

    else:     
        try:
            data = {}
            final_list = []
            final_list1 = []
            final_list2 = []
            print "----------------request--------------", request.GET
            try:
                supplier_id = request.session['supplier_id']
                advert_nm = request.GET.get('advert_nm')

                Advert_list1 = Advert.objects.filter(supplier_id=request.session['supplier_id'])

                Supplier_obj = Supplier.objects.get(supplier_id=request.session['supplier_id'])

                if Supplier_obj.logo:
                    logo = SERVER_URL + Supplier_obj.logo.url
                else:
                    logo = ''

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

                # for advert_obj in Advert_list1:
                advert_obj = Advert.objects.get(advert_id=request.GET.get('advert_id'))
                advert_id = advert_obj.advert_id
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
                start_date = date(today.year, 01, 01)
                end_date = date(today.year, 12, 31)
                monthly_count = []
                # jan,feb,mar,apr,may,jun,jul,aug,sep,octo,nov,dec
                coupon_code_list = AdvertLike.objects.filter(advert_id=advert_id,
                                                             creation_date__range=[start_date, end_date]).extra(
                    select={'month': "EXTRACT(month FROM creation_date)"}).values('month').annotate(
                    count=Count('advert_id'))
                list = {}

                for sub_obj in coupon_code_list:

                    if sub_obj.get('month'):
                        list[sub_obj.get('month')] = sub_obj.get('count') or '0.00'

                for i in FY_MONTH_LIST:
                    try:
                        monthly_count.append(list[i])
                    except:
                        monthly_count.append(0)

                jan2 = jan2 + monthly_count[0]
                feb2 = feb2 + monthly_count[1]
                mar2 = mar2 + monthly_count[2]
                apr2 = apr2 + monthly_count[3]
                may2 = may2 + monthly_count[4]
                jun2 = jun2 + monthly_count[5]
                jul2 = jul2 + monthly_count[6]
                aug2 = aug2 + monthly_count[7]
                sep2 = sep2 + monthly_count[8]
                oct2 = oct2 + monthly_count[9]
                nov2 = nov2 + monthly_count[10]
                dec2 = dec2 + monthly_count[11]

                #######.................Total shares Graph........for a year.......########

                FY_MONTH_LIST = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
                today = date.today()
                start_date = date(today.year, 01, 01)
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
                feb3 = feb3 + monthly_count[1]
                mar3 = mar3 + monthly_count[2]
                apr3 = apr3 + monthly_count[3]
                may3 = may3 + monthly_count[4]
                jun3 = jun3 + monthly_count[5]
                jul3 = jul3 + monthly_count[6]
                aug3 = aug3 + monthly_count[7]
                sep3 = sep3 + monthly_count[8]
                oct3 = oct3 + monthly_count[9]
                nov3 = nov3 + monthly_count[10]
                dec3 = dec3 + monthly_count[11]

                data = {'success': 'true', 'advert_nm': advert_nm, 'supplier_id': supplier_id, 'logo': logo,
                        'advert_views_total': advert_views_total, 'thumbs_count_total': thumbs_count_total,
                        'shares_count_total': shares_count_total, 'jan1': jan1, 'feb1': feb1, 'mar1': mar1, 'apr1': apr1,
                        'may1': may1, 'jun1': jun1, 'jul1': jul1, 'aug1': aug1, 'sep1': sep1, 'oct1': oct1, 'nov1': nov1,
                        'dec1': dec1,
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
        return render(request, 'Subscriber/subscriber-advert-stat.html', data)


# TO GET THE STATE
def get_states(request):
    if not request.user.is_authenticated():
        data = {'success':'Expired'}

    else:     
        country_id = request.GET.get('country_id')
        state_list = []
        try:
            state_objs = State.objects.filter(country_id=country_id, state_status='1').order_by('state_name')
            for state in state_objs:
                options_data = '<option value="' + str(
                    state.state_id) + '">' + state.state_name + '</option>'
                state_list.append(options_data)
            data = {'state_list': state_list}

        except Exception, ke:
            print ke
            data = {'state_list': 'none', 'message': 'No city available'}
        return HttpResponse(json.dumps(data), content_type='application/json')


# TO GET THE CITY
def get_city(request):
    if not request.user.is_authenticated():
        data = {'success':'Expired'}

    else:     
        state_id = request.GET.get('state_id')
        city_list = []
        try:
            city_objs = City_Place.objects.filter(state_id=state_id, city_status='1')
            for city in city_objs:
                options_data = '<option value="' + str(
                    city.city_place_id) + '">' + city.city_id.city_name + '</option>'
                city_list.append(options_data)
                print city_list
            data = {'city_list': city_list}

        except Exception, ke:
            print ke
            data = {'city_list': 'none', 'message': 'No city available'}
        return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def forgot_password(request):
    # pdb.set_trace()
    username = request.POST.get("email")
    try:
        if request.POST:
            user_obj = None
            try:
                user_obj = Supplier.objects.get(username=username)
                new_pass = id_generator()
                user_obj.set_password(new_pass)
            except:
                pass

            if user_obj:
                send_password_email(user_obj.contact_email, new_pass)
                user_obj.save()
                data = {'success': 'true', 'message': 'Login Successfully'}
    except Exception as e:
        print e
        data = {'success': 'false', 'message': 'Invalid Username'}
        return HttpResponse(json.dumps(data), content_type='application/json')
    except Exception, e:
        print 'Exception|view_py|forgot_pwd', e
    return HttpResponse(json.dumps(data), content_type='application/json')


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


@csrf_exempt
def send_email(trans_id, business_name,contact_person,user_first_name):
    try:
        print 'SSSSSSSSSSSSSSSSSSSSSSS....IN new mail...SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS',business_name
        subject = "New Subscription"
        description = "Dear "+ user_first_name +","
        description = description + '\n\n' + 'A New subscription with Transaction ID ' + trans_id + ' has been made by ' + contact_person + '. Please confirm the payment processing so that the Subscriber can proceed with Advert Addition.'

        gmail_user = "donotreply@city-hoopla.com" # "cityhoopla2016"
        gmail_pwd = "Hoopla123#" #"cityhoopla@2016"
        FROM = 'Team CityHoopla<donotreply@city-hoopla.com>' #'CityHoopla Admin: <cityhoopla2016@gmail.com>'
        cc = ['info@city-hoopla.com']
        TO = [business_name]
        
        TEXT = description
        SUBJECT = subject
        #server = smtplib.SMTP_SSL()
        #server = smtplib.SMTP("smtp.gmail.com", 587)
        server = smtplib.SMTP("smtpout.asia.secureserver.net", 80)
        server.ehlo()
        #server.starttls()

        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\ncc: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO),", ".join(cc), SUBJECT, TEXT)
        toaddrs = TO + cc 

        server.sendmail(FROM, toaddrs, message)
        server.quit()
    except SMTPException, e:
        print e
    except Exception, e:
        print 'exception', e
    return 1


@csrf_exempt
def send_email_update(trans_id, business_name):
    try:
        subject = "New subscription"
        description = "Dear Admin,"
        description = description + '\n' + 'A subscription has been updated with Transaction ID ' + trans_id + ' by ' + business_name + '. Please confirm the payment processing so that the Subscriber can proceed with Advert Addition.'

        gmail_user = "cityhoopla2016"
        gmail_pwd = "cityhoopla@2016"
        FROM = 'CityHoopla Admin: <cityhoopla2016@gmail.com>'
        TO = ['cityhoopla2016@gmail.com']

        TEXT = description
        SUBJECT = subject
        server = smtplib.SMTP_SSL()
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()

        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException, e:
        print e
    except Exception, e:
        print 'exception', e
    return 1



@csrf_exempt
def get_booking_graph_data(request):
    if not request.user.is_authenticated():

        data = {'success':'Expired'}

    else:     
        try:
            data = {}
            final_list = []
            final_list1 = []
            try:                
                today_date = datetime.now() #Today date

                current_date = datetime.now() 
                year = current_date.year
                month = current_date.month

                first_day_of_month = datetime(year, month, 1)
                if month == 12:
                    first_day_of_next_month = datetime(year+1, 1, 1)
                else:
                    first_day_of_next_month = datetime(year, month+1, 1)

                #Subtracting 1 day
                last_day_of_month = first_day_of_next_month - timedelta(1)
                #First and Last days of the month
                                        
                if request.GET.get('advert_var') != '':
                    if request.GET.get('week_var') == 'month':
                        var1 = str(request.GET.get('week_var'))

                        #########.............Advert Stats.......For a Month..................#####
                        
                        Advert_list = Advert.objects.filter(supplier_id=request.GET.get('supplier_id'),
                                                            advert_id=request.GET.get('advert_var'))

                        avail_discount_count = 0
                        avail_callbacks_count = 0
                        avail_callsmade_count = 0
                        avail_shares_count = 0
                        advert_id_list = []
                        for advert_obj in Advert_list:
                            advert_id = advert_obj.advert_id
                            advert_id_list.append(advert_id)
                            discount_count = CouponCode.objects.filter(advert_id=advert_id,
                                                                       creation_date__range=[first_day_of_month,
                                                                                             today_date]).count()
                            callbacks_count = AdvertCallbacks.objects.filter(advert_id=advert_id,
                                                                             creation_date__range=[first_day_of_month,
                                                                                                   today_date]).count()
                            callsmade_count = AdvertCallsMade.objects.filter(advert_id=advert_id,
                                                                             creation_date__range=[first_day_of_month,
                                                                                                   today_date]).count()
                            shares_count = AdvertShares.objects.filter(advert_id=advert_id,
                                                                       creation_date__range=[first_day_of_month,
                                                                                             today_date]).count()

                            avail_discount_count = avail_discount_count + discount_count
                            avail_callbacks_count = avail_callbacks_count + callbacks_count
                            avail_callsmade_count = avail_callsmade_count + callsmade_count
                            avail_shares_count = avail_shares_count + shares_count

                        #######.................Total Bookings Graph....For a month...........########

                        #Computing start and end week days
                        first_week_day = first_day_of_month.weekday()+1
                        date_range = [0]*first_week_day + range(first_day_of_month.day,last_day_of_month.day+1)
                        month = []
                        list = []
                        list2 = []
                        list2.append(["",""])
                        while date_range:
                            if len(date_range) >= 7:
                                week = date_range[:7]
                                date_range = date_range[7:]
                            else:
                                week = date_range
                                date_range = None
                            month.append(week)
                        i=1
                        for week in month:
                            start_week, end_week = min(week), max(week)
                            if start_week==0:
                                start_week = 1

                            month = current_date.month
                            first_date_of_current_month = datetime(year, month, start_week)
                            last_date_of_current_month = datetime(year, month, end_week)
                            coupon_code_count = CouponCode.objects.filter(
                                creation_date__range=[first_date_of_current_month, last_date_of_current_month], advert_id=request.GET.get('advert_var')
                            ).count()
                            list.append(["Week"+str(i),coupon_code_count])

                            #########..................Total Views Graph........for a month.............############

                            advert_total_count = AdvertView.objects.filter(
                                creation_date__range=[first_date_of_current_month, last_date_of_current_month], advert_id=request.GET.get('advert_var')
                            ).count()
                            list2.append(["Week"+str(i),advert_total_count])

                            i = i+1

                        data = {'list':list,'list2':list2,'var1': var1, 'success': 'true', 'avail_callbacks_count': avail_callbacks_count,
                                'avail_callsmade_count': avail_callsmade_count, 'avail_shares_count': avail_shares_count,
                                'avail_discount_count': avail_discount_count
                            }

                    if request.GET.get('week_var') == 'week':
                        var1 = str(request.GET.get('week_var'))

                        #########.............Advert Stats.......For a week..................#####
                        today_date = datetime.now()
                        start =  today_date - timedelta(days = today_date.weekday())- timedelta(days=1)
                        end = start + timedelta(days=6)
                        start = start.strftime("%Y-%m-%d")
                        
                        Advert_list = Advert.objects.filter(supplier_id=request.GET.get('supplier_id'),
                                                            advert_id=request.GET.get('advert_var'))

                        avail_discount_count = 0
                        avail_callbacks_count = 0
                        avail_callsmade_count = 0
                        avail_shares_count = 0
                        advert_id_list = []
                        for advert_obj in Advert_list:
                            advert_id = advert_obj.advert_id
                            advert_id_list.append(advert_id)
                            discount_count = CouponCode.objects.filter(advert_id=advert_id,
                                                                       creation_date__range=[start,
                                                                                             today_date]).count()
                            callbacks_count = AdvertCallbacks.objects.filter(advert_id=advert_id,
                                                                             creation_date__range=[start,
                                                                                                   today_date]).count()
                            callsmade_count = AdvertCallsMade.objects.filter(advert_id=advert_id,
                                                                             creation_date__range=[start,
                                                                                                   today_date]).count()
                            shares_count = AdvertShares.objects.filter(advert_id=advert_id,
                                                                       creation_date__range=[start,
                                                                                             today_date]).count()

                            avail_discount_count = avail_discount_count + discount_count
                            avail_callbacks_count = avail_callbacks_count + callbacks_count
                            avail_callsmade_count = avail_callsmade_count + callsmade_count
                            avail_shares_count = avail_shares_count + shares_count

                        #######.................Total Bookings Graph....For a week...........########

                        list = []
                        total_view_list = CouponCode.objects.filter(creation_date__range=[start, today_date],
                                                                    advert_id=request.GET.get('advert_var'))
                        mon1 = tue1 = wen1 = thus1 = fri1 = sat1 = sun1 = 0
                        if total_view_list:
                            for view_obj in total_view_list:
                                creation_date = view_obj.creation_date
                                consumer_day = calendar.day_name[creation_date.weekday()]
                                if consumer_day == 'Monday':
                                    mon1 = mon1 + 1
                                elif consumer_day == 'Tuesday':
                                    tue1 = tue1 + 1
                                elif consumer_day == 'Wednesday':
                                    wen1 = wen1 + 1
                                elif consumer_day == 'Thursday':
                                    thus1 = thus1 + 1
                                elif consumer_day == 'Friday':
                                    fri1 = fri1 + 1
                                elif consumer_day == 'Saturday':
                                    sat1 = sat1 + 1
                                elif consumer_day == 'Sunday':
                                    sun1 = sun1 + 1
                                else:
                                    pass
                        list.append(["MON",mon1])
                        list.append(["TUE",tue1])
                        list.append(["WED",wen1])
                        list.append(["THU",thus1])
                        list.append(["FRI",fri1])
                        list.append(["SAT",sat1])
                        list.append(["SUN",sun1])


                        ##########..................Total Views Graph........for a week.............############

                        total_view_list = AdvertView.objects.filter(creation_date__range=[start, today_date],
                                                                   advert_id=request.GET.get('advert_var'))
                        list2 = [] 
                        mon2 = tue2 = wen2 = thus2 = fri2 = sat2 = sun2 = 0
                        if total_view_list:
                            for view_obj in total_view_list:
                                creation_date = view_obj.creation_date
                                consumer_day = calendar.day_name[creation_date.weekday()]
                                if consumer_day == 'Monday':
                                    mon2 = mon2 + 1
                                elif consumer_day == 'Tuesday':
                                    tue2 = tue2 + 1
                                elif consumer_day == 'Wednesday':
                                    wen2 = wen2 + 1
                                elif consumer_day == 'Thursday':
                                    thus2 = thus2 + 1
                                elif consumer_day == 'Friday':
                                    fri2 = fri2 + 1
                                elif consumer_day == 'Saturday':
                                    sat2 = sat2 + 1
                                elif consumer_day == 'Sunday':
                                    sun2 = sun2 + 1
                                else:
                                    pass

                        list2.append(["",""])                                    
                        list2.append(["MON",mon2])
                        list2.append(["TUE",tue2])
                        list2.append(["WED",wen2])
                        list2.append(["THU",thus2])
                        list2.append(["FRI",fri2])
                        list2.append(["SAT",sat2])
                        list2.append(["SUN",sun2]) 


                        data = {'list':list,'list2':list2,'var1': var1, 'success': 'true', 'avail_callbacks_count': avail_callbacks_count,
                                'avail_callsmade_count': avail_callsmade_count, 'avail_shares_count': avail_shares_count,
                                'avail_discount_count': avail_discount_count
                            }

                else:
                    if request.GET.get('week_var') == 'month':
                        var1 = str(request.GET.get('week_var'))

                        #########.............Advert Stats.......For a Month..................#####
                        today_date = str(datetime.now())
                        Advert_list = Advert.objects.filter(supplier_id=request.GET.get('supplier_id'))

                        avail_discount_count = 0
                        avail_callbacks_count = 0
                        avail_callsmade_count = 0
                        avail_shares_count = 0
                        advert_id_list = []
                        for advert_obj in Advert_list:
                            advert_id = advert_obj.advert_id
                            advert_id_list.append(advert_id)
                            discount_count = CouponCode.objects.filter(advert_id=advert_id,
                                                                       creation_date__range=[first_day_of_month,
                                                                                             today_date]).count()
                            callbacks_count = AdvertCallbacks.objects.filter(advert_id=advert_id,
                                                                             creation_date__range=[first_day_of_month,
                                                                                                   today_date]).count()
                            callsmade_count = AdvertCallsMade.objects.filter(advert_id=advert_id,
                                                                             creation_date__range=[first_day_of_month,
                                                                                                   today_date]).count()
                            shares_count = AdvertShares.objects.filter(advert_id=advert_id,
                                                                       creation_date__range=[first_day_of_month,
                                                                                             today_date]).count()

                            avail_discount_count = avail_discount_count + discount_count
                            avail_callbacks_count = avail_callbacks_count + callbacks_count
                            avail_callsmade_count = avail_callsmade_count + callsmade_count
                            avail_shares_count = avail_shares_count + shares_count

                        #######.................Total Bookings Graph....For a month...........########

                        #Computing start and end week days
                        first_week_day = first_day_of_month.weekday()+1
                        date_range = [0]*first_week_day + range(first_day_of_month.day,last_day_of_month.day+1)
                        month = []
                        list = []
                        list2 = []
                        list2.append(["",""])
                        while date_range:
                            if len(date_range) >= 7:
                                week = date_range[:7]
                                date_range = date_range[7:]
                            else:
                                week = date_range
                                date_range = None
                            month.append(week)
                        i=1
                        for week in month:
                            start_week, end_week = min(week), max(week)
                            if start_week==0:
                                start_week = 1

                            month = current_date.month
                            first_date_of_current_month = datetime(year, month, start_week)
                            last_date_of_current_month = datetime(year, month, end_week)

                            coupon_code_count = CouponCode.objects.filter(
                                creation_date__range=[first_date_of_current_month, last_date_of_current_month], advert_id__in=advert_id_list
                            ).count()
                            list.append(["Week"+str(i),coupon_code_count])

                            advert_total_count = AdvertView.objects.filter(
                                creation_date__range=[first_date_of_current_month, last_date_of_current_month], advert_id__in=advert_id_list
                            ).count()
                            list2.append(["Week"+str(i),advert_total_count])

                            i = i+1

                        data = {'list':list,'list2':list2,'var1': var1, 'success': 'true', 'avail_callbacks_count': avail_callbacks_count,
                                'avail_callsmade_count': avail_callsmade_count, 'avail_shares_count': avail_shares_count,
                                'avail_discount_count': avail_discount_count
                            }

                    if request.GET.get('week_var') == 'week':
                        var1 = str(request.GET.get('week_var'))

                        #########.............Advert Stats.......For a week..................#####
                        Advert_list = Advert.objects.filter(supplier_id=request.GET.get('supplier_id'))

                        today_date = datetime.now()
                        start =  today_date - timedelta(days = today_date.weekday())- timedelta(days=1)
                        end = start + timedelta(days=6)
                        start = start.strftime("%Y-%m-%d")

                        avail_discount_count = 0
                        avail_callbacks_count = 0
                        avail_callsmade_count = 0
                        avail_shares_count = 0
                        advert_id_list = []
                        for advert_obj in Advert_list:
                            advert_id = advert_obj.advert_id
                            advert_id_list.append(advert_id)
                            discount_count = CouponCode.objects.filter(advert_id=advert_id,
                                                                       creation_date__range=[start,
                                                                                             today_date]).count()
                            callbacks_count = AdvertCallbacks.objects.filter(advert_id=advert_id,
                                                                             creation_date__range=[start,
                                                                                                   today_date]).count()
                            callsmade_count = AdvertCallsMade.objects.filter(advert_id=advert_id,
                                                                             creation_date__range=[start,
                                                                                                   today_date]).count()
                            shares_count = AdvertShares.objects.filter(advert_id=advert_id,
                                                                       creation_date__range=[start,
                                                                                             today_date]).count()

                            avail_discount_count = avail_discount_count + discount_count
                            avail_callbacks_count = avail_callbacks_count + callbacks_count
                            avail_callsmade_count = avail_callsmade_count + callsmade_count
                            avail_shares_count = avail_shares_count + shares_count

                        #######.................Total Bookings Graph....For a week...........########
                        list = []
                        total_view_list = CouponCode.objects.filter(creation_date__range=[start, today_date],
                                                                    advert_id__in=advert_id_list)
                        mon1 = tue1 = wen1 = thus1 = fri1 = sat1 = sun1 = 0
                        if total_view_list:
                            for view_obj in total_view_list:
                                creation_date = view_obj.creation_date
                                consumer_day = calendar.day_name[creation_date.weekday()]
                                if consumer_day == 'Monday':
                                    mon1 = mon1 + 1
                                elif consumer_day == 'Tuesday':
                                    tue1 = tue1 + 1
                                elif consumer_day == 'Wednesday':
                                    wen1 = wen1 + 1
                                elif consumer_day == 'Thursday':
                                    thus1 = thus1 + 1
                                elif consumer_day == 'Friday':
                                    fri1 = fri1 + 1
                                elif consumer_day == 'Saturday':
                                    sat1 = sat1 + 1
                                elif consumer_day == 'Sunday':
                                    sun1 = sun1 + 1
                                else:
                                    pass
                        list.append(["MON",mon1])
                        list.append(["TUE",tue1])
                        list.append(["WED",wen1])
                        list.append(["THU",thus1])
                        list.append(["FRI",fri1])
                        list.append(["SAT",sat1])
                        list.append(["SUN",sun1])

                        ##########..................Total Views Graph........for a week.............############

                        list2 = []
                        total_view_list = AdvertView.objects.filter(creation_date__range=[start, today_date],
                                                                    advert_id__in=advert_id_list)
                        mon2 = tue2 = wen2 = thus2 = fri2 = sat2 = sun2 = 0
                        if total_view_list:
                            for view_obj in total_view_list:
                                creation_date = view_obj.creation_date
                                consumer_day = calendar.day_name[creation_date.weekday()]
                                if consumer_day == 'Monday':
                                    mon2 = mon2 + 1
                                elif consumer_day == 'Tuesday':
                                    tue2 = tue2 + 1
                                elif consumer_day == 'Wednesday':
                                    wen2 = wen2 + 1
                                elif consumer_day == 'Thursday':
                                    thus2 = thus2 + 1
                                elif consumer_day == 'Friday':
                                    fri2 = fri2 + 1
                                elif consumer_day == 'Saturday':
                                    sat2 = sat2 + 1
                                elif consumer_day == 'Sunday':
                                    sun2 = sun2 + 1
                                else:
                                    pass
                        list2.append(["",""])                                    
                        list2.append(["MON",mon2])
                        list2.append(["TUE",tue2])
                        list2.append(["WED",wen2])
                        list2.append(["THU",thus2])
                        list2.append(["FRI",fri2])
                        list2.append(["SAT",sat2])
                        list2.append(["SUN",sun2]) 

                        data = {'list':list,'list2':list2,'var1': var1, 'success': 'true', 'avail_callbacks_count': avail_callbacks_count,
                                'avail_callsmade_count': avail_callsmade_count, 'avail_shares_count': avail_shares_count,
                                'avail_discount_count': avail_discount_count
                            }

            except IntegrityError as e:
                print e
                data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time',
                        'username': request.session['login_user']}
        except MySQLdb.OperationalError, e:
            print e
        except Exception, e:
            print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def check_category(request):
    # pdb.set_trace()
    if not request.user.is_authenticated():
        data = {'success':'Expired'}

    else:
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
            cat_list = []
            if cat_obj:
                for cat in cat_obj:
                    options_data = '<option value=' + str(cat.category_id) + '>' + cat.category_name + '</option>'
                    cat_list.append(options_data)
                data = {'success': 'true','category_list': cat_list}
            else:
                data = {'success': 'false'}
        except Exception, e:
            data = {'success': 'false'}
            print e
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def check_category_supplier(request):
    # pdb.set_trace()
    if not request.user.is_authenticated():
        data = {'success':'Expired'}

    else:
        print "IN CHECK NEW CATEGORY",request.POST
        has_rate_card = 'false'
        try:
            temp_data = ''
            cat_amenities = []
            if request.POST.get('cat_level') != '6':
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
                cat_list = []
                if cat_obj:
                    for cat in cat_obj:
                        options_data = '<option value=' + str(cat.category_id) + '>' + cat.category_name + '</option>'
                        cat_list.append(options_data)
                    data = { 'success': 'true','category_list': cat_list}
                else:
                    cat_level = int(request.POST.get('cat_level')) - 1
                    print "main_category_id",request.POST.get('main_category_id')
                    xyz = []
                    amenity_list = CategorywiseAmenity.objects.filter(status="1",category=request.POST.get('main_category_id'))
                    if amenity_list:
                        xyz = amenity_list
                    if cat_level == 1:
                        amenity_list = CategorywiseAmenity.objects.filter(status="1",category_level_1=request.POST.get('category_id'),category=request.POST.get('main_category_id'))
                        if amenity_list:
                            xyz = amenity_list
                    if cat_level == 2:
                        print "in cate 2"
                        amenity_list = CategorywiseAmenity.objects.filter(status="1",category_level_2=request.POST.get('category_id'),category=request.POST.get('main_category_id'))
                        if amenity_list:
                            xyz = amenity_list
                    if cat_level == 3:
                        amenity_list = CategorywiseAmenity.objects.filter(status="1",category_level_3=request.POST.get('category_id'),category=request.POST.get('main_category_id'))
                        if amenity_list:
                            xyz = amenity_list

                    if cat_level == 4:
                        amenity_list = CategorywiseAmenity.objects.filter(status="1",category_level_4=request.POST.get('category_id'),category=request.POST.get('main_category_id'))
                        if amenity_list:
                            xyz = amenity_list
                    if cat_level == 5:
                        amenity_list = CategorywiseAmenity.objects.filter(status="1",category_level_5=request.POST.get('category_id'),category=request.POST.get('main_category_id'))
                        if amenity_list:
                            xyz = amenity_list

                    for amnenity in xyz:

                        temp_data ={
                        'id':str(amnenity.categorywise_amenity_id),
                        'amenity':str(amnenity.amenity)
                        }
                        cat_amenities.append(temp_data)

                    supplier_obj = Supplier.objects.get(supplier_id = request.POST.get('supplier_id'))
                    rate_card = RateCard.objects.filter(city_place_id=request.POST.get('city_place_id'))
                    service_rate_card = CategoryWiseRateCard.objects.filter(city_place_id=request.POST.get('city_place_id'),
                                                                            category_id=request.POST.get('category_id'),
                                                                            category_level=cat_level,
                                                                            rate_card_status = '1')
                    if rate_card and service_rate_card:
                        has_rate_card = 'true'
                    data = {
                        'success': 'false','has_rate_card':has_rate_card,'cat_amenities':cat_amenities
                    }
            else:
                cat_level = int(request.POST.get('cat_level')) - 1
                supplier_obj = Supplier.objects.get(supplier_id=request.session['supplier_id'])
                rate_card = RateCard.objects.filter(city_place_id=request.POST.get('city_place_id'))
                service_rate_card = CategoryWiseRateCard.objects.filter(city_place_id=request.POST.get('city_place_id'),
                                                                        category_id=request.POST.get('category_id'),
                                                                        category_level=cat_level,
                                                                        rate_card_status = '1')
                if rate_card and service_rate_card:
                    has_rate_card = 'true'
                data = {'success': 'false', 'has_rate_card': has_rate_card}
        except Exception, e:
            print e
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def get_telephone_service_slots(request):
    if not request.user.is_authenticated():
        data = {'success':'Expired'}

    else:    
        has_platinum = 'false'
        has_diamond = 'false'
        has_gold = 'false'
        has_silver = 'false'
        has_bronze = 'false'
        has_value = 'false'
        try:
            print request.POST
            start_date = request.POST.get('start_date')
            cat_level = int(request.POST.get('cat_lvl'))
            enquiry_service_obj = EnquiryService.objects.filter(
                category_id=request.POST.get('cat_id'),
                category_level=cat_level,
                city_place_id=request.POST.get('city_place_id'),
                enquiry_service_status=1,
                enquiry_service_name='Platinum'
            )
            for enquiry_service in enquiry_service_obj:
                date1 = datetime.strptime(enquiry_service.start_date, "%d/%m/%Y")
                date2 = datetime.strptime(enquiry_service.end_date, "%d/%m/%Y")
                date3 = datetime.strptime(start_date, "%d/%m/%Y")
                if date1 <= date3 <= date2:
                    has_platinum = 'true'

            enquiry_service_obj = EnquiryService.objects.filter(
                category_id=request.POST.get('cat_id'),
                category_level=cat_level,
                city_place_id=request.POST.get('city_place_id'),
                enquiry_service_status=1,
                enquiry_service_name='Diamond'
            )
            for enquiry_service in enquiry_service_obj:
                date1 = datetime.strptime(enquiry_service.start_date, "%d/%m/%Y")
                date2 = datetime.strptime(enquiry_service.end_date, "%d/%m/%Y")
                date3 = datetime.strptime(start_date, "%d/%m/%Y")
                if date1 <= date3 <= date2:
                    has_diamond = 'true'


            enquiry_service_obj = EnquiryService.objects.filter(
                category_id=request.POST.get('cat_id'),
                category_level=cat_level,
                city_place_id=request.POST.get('city_place_id'),
                enquiry_service_status=1,
                enquiry_service_name='Gold'
            )
            for enquiry_service in enquiry_service_obj:
                date1 = datetime.strptime(enquiry_service.start_date, "%d/%m/%Y")
                date2 = datetime.strptime(enquiry_service.end_date, "%d/%m/%Y")
                date3 = datetime.strptime(start_date, "%d/%m/%Y")
                if date1 <= date3 <= date2:
                    has_gold = 'true'

            enquiry_service_obj = EnquiryService.objects.filter(
                category_id=request.POST.get('cat_id'),
                category_level=cat_level,
                city_place_id=request.POST.get('city_place_id'),
                enquiry_service_status=1,
                enquiry_service_name='Silver'
            )
            i = 0
            for enquiry_service in enquiry_service_obj:
                date1 = datetime.strptime(enquiry_service.start_date, "%d/%m/%Y")
                date2 = datetime.strptime(enquiry_service.end_date, "%d/%m/%Y")
                date3 = datetime.strptime(start_date, "%d/%m/%Y")
                if date1 <= date3 <= date2:
                    i = i + 1
            if i >= 2:
                has_silver = 'true'

            enquiry_service_obj = EnquiryService.objects.filter(
                category_id=request.POST.get('cat_id'),
                category_level=cat_level,
                city_place_id=request.POST.get('city_place_id'),
                enquiry_service_status=1,
                enquiry_service_name='Bronze'
            )
            i = 0
            for enquiry_service in enquiry_service_obj:
                date1 = datetime.strptime(enquiry_service.start_date, "%d/%m/%Y")
                date2 = datetime.strptime(enquiry_service.end_date, "%d/%m/%Y")
                date3 = datetime.strptime(start_date, "%d/%m/%Y")
                if date1 <= date3 <= date2:
                    i = i + 1
            if i >= 3:
                has_bronze = 'true'

            enquiry_service_obj = EnquiryService.objects.filter(
                category_id=request.POST.get('cat_id'),
                category_level=cat_level,
                city_place_id=request.POST.get('city_place_id'),
                enquiry_service_status=1,
                enquiry_service_name='Value'
            )
            i = 0
            for enquiry_service in enquiry_service_obj:
                date1 = datetime.strptime(enquiry_service.start_date, "%d/%m/%Y")
                date2 = datetime.strptime(enquiry_service.end_date, "%d/%m/%Y")
                date3 = datetime.strptime(start_date, "%d/%m/%Y")
                if date1 <= date3 <= date2:
                    i = i + 1
            if i >= 2:
                has_value = 'true'

            data = {
                'success': 'true',
                'has_platinum': has_platinum, 'has_diamond': has_diamond,
                'has_gold': has_gold, 'has_silver': has_silver,
                'has_bronze': has_bronze, 'has_value': has_value,
            }
        except Exception, e:
            print e
            data = {'success': 'true'}
    return HttpResponse(json.dumps(data), content_type='application/json')    

@csrf_exempt
def get_premium_subscription_amount(request):
    if not request.user.is_authenticated():
        data = {'success':'Expired'}

    else:    
        try:
            duration = request.POST.get('duration')
            service_name = request.POST.get('service_name')
            cat_lvl = request.POST.get('cat_lvl')
            cat_id = request.POST.get('cat_id')
            user_id = request.POST.get('supplier_id')
            supplier_obj = Supplier.objects.get(supplier_id=user_id)
            city_place_id = request.POST.get('city_place_id')
            if not city_place_id:
                city_place_id = str(supplier_obj.city_place_id)

            if service_name == "Subscription" or service_name == "No.1 Listing" or service_name == "No.2 Listing" or service_name == "No.3 Listing":
                rate_card_obj = CategoryWiseRateCard.objects.get(service_name=service_name,category_id=cat_id,rate_card_status = '1',
                                                                 category_level=cat_lvl,city_place_id = city_place_id)
            else:
                rate_card_obj = RateCard.objects.get(service_name=service_name,rate_card_status = '1',city_place_id = city_place_id)
            if duration == '3':
                amount = str(rate_card_obj.cost_for_3_days)
            if duration == '7':
                amount = str(rate_card_obj.cost_for_7_days)
            if duration == '30':
                amount = str(rate_card_obj.cost_for_30_days)
            if duration == '90':
                amount = str(rate_card_obj.cost_for_90_days)
            if duration == '180':
                amount = str(rate_card_obj.cost_for_180_days)
            data = {'success': 'true', 'amount': amount}
        except:
            data = {'success': 'true', 'amount': "0.00"}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def get_booked_slots(request):
    if not request.user.is_authenticated():
        data = {'success':'Expired'}

    else:    
        date_list = []
        slider_date_list = []
        duration_date_list = []
        booked_date_list = []
        try:
            print request.POST
            if request.POST.get('service_name') == 'Advert Slider':
                premium_service_obj = PremiumService.objects.filter(
                    city_place_id = request.POST.get('city_place_id'),
                    premium_service_name = request.POST.get('service_name'),
                    premium_service_status = 1
                )
                for premium_service in premium_service_obj:
                    if str(premium_service.business_id.business_id) != str(request.POST.get('business_id')):
                        start_date = datetime.strptime(premium_service.start_date, "%d/%m/%Y")
                        end_date = datetime.strptime(premium_service.end_date, "%d/%m/%Y")
                        date_data = {
                            'start_date': str(start_date.strftime("%m/%d/%Y")),
                            'end_date': str(end_date.strftime("%m/%d/%Y"))
                        }
                        slider_date_list.append(date_data)
                slider_start_date = datetime.strptime(request.POST.get('start_date'), "%d/%m/%Y")
                slider_end_date = datetime.strptime(request.POST.get('end_date'), "%d/%m/%Y")
                date_diff = slider_end_date - slider_start_date
                for i in range(date_diff.days + 1):
                    duration_date_list.append(slider_start_date + timedelta(i))
                for dates in duration_date_list:
                    i = 0
                    for slider_date in slider_date_list:
                        date1 = datetime.strptime(slider_date['start_date'], "%m/%d/%Y")
                        date2 = datetime.strptime(slider_date['end_date'], "%m/%d/%Y")
                        if date1 <= dates <= date2:
                            i = i + 1
                    if i >= 10:
                        booked_date_list.append(dates.strftime("%m/%d/%Y"))
            elif request.POST.get('service_name') == 'Top Advert':
                # print '...........TOP ADVERT..................'
                premium_service_obj = PremiumService.objects.filter(
                    city_place_id = request.POST.get('city_place_id'),
                    premium_service_name = request.POST.get('service_name'),
                    premium_service_status = 1
                )

                for premium_service in premium_service_obj:
                    if str(premium_service.business_id.business_id) != str(request.POST.get('business_id')):
                        start_date = datetime.strptime(premium_service.start_date, "%d/%m/%Y")
                        end_date = datetime.strptime(premium_service.end_date, "%d/%m/%Y")
                        date_data = {
                            'start_date': str(start_date.strftime("%m/%d/%Y")),
                            'end_date': str(end_date.strftime("%m/%d/%Y"))
                        }
                        slider_date_list.append(date_data)
                slider_start_date = datetime.strptime(request.POST.get('start_date'), "%d/%m/%Y")
                slider_end_date = datetime.strptime(request.POST.get('end_date'), "%d/%m/%Y")
                date_diff = slider_end_date - slider_start_date
                for i in range(date_diff.days + 1):
                    duration_date_list.append(slider_start_date + timedelta(i))
                for dates in duration_date_list:
                    i = 0
                    for slider_date in slider_date_list:
                        date1 = datetime.strptime(slider_date['start_date'], "%m/%d/%Y")
                        date2 = datetime.strptime(slider_date['end_date'], "%m/%d/%Y")
                        if date1 <= dates <= date2:
                            i = i + 1
                    if i >= 15:
                        booked_date_list.append(dates.strftime("%m/%d/%Y"))
                # print 'SSSSSSSSSSSSSSS',booked_date_list

            else:
                premium_service_obj = PremiumService.objects.filter(
                    category_level=request.POST.get('cat_lvl'),
                    category_id=request.POST.get('cat_id'),
                    city_place_id=request.POST.get('city_place_id'),
                    premium_service_name=request.POST.get('service_name'),
                    premium_service_status=1
                )
            for premium_service in premium_service_obj:
                if str(premium_service.business_id.business_id) != str(request.POST.get('business_id')):
                    start_date = datetime.strptime(premium_service.start_date, "%d/%m/%Y")
                    end_date = datetime.strptime(premium_service.end_date, "%d/%m/%Y")
                    date_data ={
                        'start_date':str(start_date.strftime("%m/%d/%Y")),
                        'end_date':str(end_date.strftime("%m/%d/%Y"))
                    }
                    date_list.append(date_data)
            if request.POST.get('service_name') == 'Advert Slider':
                date_list = []
            if request.POST.get('service_name') == 'Top Advert':
                date_list = []
            # print '........booked_date_list....',booked_date_list
            data = {'success': 'true','date_list':date_list,'booked_date_list':booked_date_list}
        except Exception, e:
            print e
            data = {'success': 'true', 'date_list': date_list,'booked_date_list':booked_date_list}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def get_telephone_subscription_amount(request):
    if not request.user.is_authenticated():
        data = {'success':'Expired'}

    else:
        print "--------------------------------", request.POST
        duration = request.POST.get('duration')
        service_name = request.POST.get('service_name')
        if request.POST.get('city_place_id'):
            city_place_id = request.POST.get('city_place_id')
        elif request.POST.get('supplier_id'):
            city_place_id = Supplier.objects.get(supplier_id = request.POST.get('supplier_id')).city_place_id.city_place_id
        try:
            rate_card_obj = TelephoneEnquiryRateCard.objects.get(service_name=service_name,rate_card_status = '1',city_place_id = city_place_id)
            if duration == '3':
                amount = str(rate_card_obj.cost_for_3_days)
            if duration == '7':
                amount = str(rate_card_obj.cost_for_7_days)
            if duration == '30':
                amount = str(rate_card_obj.cost_for_30_days)
            if duration == '90':
                amount = str(rate_card_obj.cost_for_90_days)
            if duration == '180':
                amount = str(rate_card_obj.cost_for_180_days)
            data = {'success': 'true', 'amount': amount}
        except Exception as e:
            print e
            data = {'success': 'true', 'amount': '0'}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def get_edit_booked_slots(request):
    if not request.user.is_authenticated():
        data = {'success':'Expired'}

    else:    
        date_list = []
        city_place_id = request.POST.get('city_place_id')
        business_id = request.POST.get('business_id')
        cat_lvl = request.POST.get('cat_lvl')
        cat_id = request.POST.get('cat_id')
        try:
            no1_ranges = []
            no2_ranges = []
            no3_ranges = []
            no4_ranges = []
            no5_ranges = []
            slider_date_list=[]
            duration_date_list=[]
            no1_start_date,no1_end_date = '', ''
            no2_start_date,no2_end_date = '', ''
            no3_start_date,no3_end_date = '', ''
            no4_start_date,no4_end_date = '', ''
            no5_start_date,no5_end_date = '', ''
            has_platinum = 'false'
            has_diamond = 'false'
            has_gold = 'false'
            has_silver = 'false'
            has_bronze = 'false'
            has_value = 'false'

            service_name_list = ['Advert Slider', 'Top Advert', 'No.1 Listing', 'No.2 Listing', 'No.3 Listing']
            for service_name in service_name_list:
                if service_name == 'Advert Slider':
                    premium_service_obj = PremiumService.objects.filter(
                        city_place_id=city_place_id,
                        premium_service_name=service_name,
                        premium_service_status=1
                    )
                    for premium_service in premium_service_obj:
                        if str(premium_service.business_id.business_id) == str(business_id):
                            no4_start_date, no4_end_date = premium_service.start_date, premium_service.end_date
                    for premium_service in premium_service_obj:
                        if str(premium_service.business_id.business_id) != str(business_id):
                            start_date = datetime.strptime(premium_service.start_date, "%d/%m/%Y")
                            end_date = datetime.strptime(premium_service.end_date, "%d/%m/%Y")
                            date_data = {
                                'start_date': str(start_date.strftime("%m/%d/%Y")),
                                'end_date': str(end_date.strftime("%m/%d/%Y"))
                            }
                            slider_date_list.append(date_data)
                        slider_start_date = datetime.strptime(request.POST.get('start_date'), "%d/%m/%Y")
                        slider_end_date = datetime.strptime(request.POST.get('end_date'), "%d/%m/%Y")
                        date_diff = slider_end_date - slider_start_date
                        for i in range(date_diff.days + 1):
                            duration_date_list.append(slider_start_date + timedelta(i))
                        for dates in duration_date_list:
                            i = 0
                            for slider_date in slider_date_list:
                                date1 = datetime.strptime(slider_date['start_date'], "%m/%d/%Y")
                                date2 = datetime.strptime(slider_date['end_date'], "%m/%d/%Y")
                                if date1 <= dates <= date2:
                                    i = i + 1
                            if i >= 10:
                                no4_ranges.append(dates.strftime("%m/%d/%Y"))
                no4_ranges = set(no4_ranges)
                no4_ranges = list(no4_ranges)
                if service_name == 'Top Advert':
                    date_list = []
                    premium_service_obj = PremiumService.objects.filter(
                        city_place_id=city_place_id,
                        premium_service_name=service_name,
                        premium_service_status=1
                    )
                    for premium_service in premium_service_obj:
                        if str(premium_service.business_id.business_id) != str(business_id):
                            start_date = datetime.strptime(premium_service.start_date, "%d/%m/%Y")
                            end_date = datetime.strptime(premium_service.end_date, "%d/%m/%Y")
                            date_data = {
                                'start_date': str(start_date.strftime("%m/%d/%y")),
                                'end_date': str(end_date.strftime("%m/%d/%y"))
                            }
                            date_list.append(date_data)
                        else:
                            no5_start_date, no5_end_date = premium_service.start_date, premium_service.end_date
                    no5_ranges = date_list
                if service_name == 'No.1 Listing':
                    date_list = []
                    premium_service_obj = PremiumService.objects.filter(
                        category_level=cat_lvl,
                        category_id=cat_id,
                        city_place_id=city_place_id,
                        premium_service_name=service_name,
                        premium_service_status=1
                    )
                    print "premium_service_obj", premium_service_obj
                    for premium_service in premium_service_obj:
                        if str(premium_service.business_id.business_id) != str(business_id):
                            start_date = datetime.strptime(premium_service.start_date, "%d/%m/%Y")
                            end_date = datetime.strptime(premium_service.end_date, "%d/%m/%Y")
                            date_data = {
                                'start_date': str(start_date.strftime("%m/%d/%y")),
                                'end_date': str(end_date.strftime("%m/%d/%y"))
                            }
                            date_list.append(date_data)
                        else:
                            no1_start_date, no1_end_date = premium_service.start_date, premium_service.end_date
                    no1_ranges = date_list
                if service_name == 'No.2 Listing':
                    date_list = []
                    premium_service_obj = PremiumService.objects.filter(
                        category_level=cat_lvl,
                        category_id=cat_id,
                        city_place_id=city_place_id,
                        premium_service_name=service_name,
                        premium_service_status=1
                    )
                    for premium_service in premium_service_obj:
                        if str(premium_service.business_id.business_id) != str(business_id):
                            start_date = datetime.strptime(premium_service.start_date, "%d/%m/%Y")
                            end_date = datetime.strptime(premium_service.end_date, "%d/%m/%Y")
                            date_data = {
                                'start_date': str(start_date.strftime("%m/%d/%y")),
                                'end_date': str(end_date.strftime("%m/%d/%y"))
                            }
                            date_list.append(date_data)
                        else:
                            no2_start_date, no2_end_date = premium_service.start_date, premium_service.end_date
                    no2_ranges = date_list
                if service_name == 'No.3 Listing':
                    date_list = []
                    premium_service_obj = PremiumService.objects.filter(
                        category_level=cat_lvl,
                        category_id=cat_id,
                        city_place_id=city_place_id,
                        premium_service_name=service_name,
                        premium_service_status=1
                    )
                    for premium_service in premium_service_obj:
                        if str(premium_service.business_id.business_id) != str(business_id):
                            start_date = datetime.strptime(premium_service.start_date, "%d/%m/%Y")
                            end_date = datetime.strptime(premium_service.end_date, "%d/%m/%Y")
                            date_data = {
                                'start_date': str(start_date.strftime("%m/%d/%y")),
                                'end_date': str(end_date.strftime("%m/%d/%y"))
                            }
                            date_list.append(date_data)
                        else:
                            no3_start_date, no3_end_date = premium_service.start_date, premium_service.end_date
                    no3_ranges = date_list

            start_date = request.POST.get('start_date')
            cat_level = int(request.POST.get('cat_lvl'))
            enquiry_service_obj = EnquiryService.objects.filter(
                category_id=request.POST.get('cat_id'),
                category_level=cat_level,
                city_place_id=request.POST.get('city_place_id'),
                enquiry_service_status=1,
                enquiry_service_name='Platinum'
            )
            for enquiry_service in enquiry_service_obj:
                if str(enquiry_service.business_id.business_id) != str(business_id):
                    date1 = datetime.strptime(enquiry_service.start_date, "%d/%m/%Y")
                    date2 = datetime.strptime(enquiry_service.end_date, "%d/%m/%Y")
                    date3 = datetime.strptime(start_date, "%d/%m/%Y")
                    if date1 <= date3 <= date2:
                        has_platinum = 'true'

            enquiry_service_obj = EnquiryService.objects.filter(
                category_id=request.POST.get('cat_id'),
                category_level=cat_level,
                city_place_id=request.POST.get('city_place_id'),
                enquiry_service_status=1,
                enquiry_service_name='Diamond'
            )
            for enquiry_service in enquiry_service_obj:
                if str(enquiry_service.business_id.business_id) != str(business_id):
                    date1 = datetime.strptime(enquiry_service.start_date, "%d/%m/%Y")
                    date2 = datetime.strptime(enquiry_service.end_date, "%d/%m/%Y")
                    date3 = datetime.strptime(start_date, "%d/%m/%Y")
                    if date1 <= date3 <= date2:
                        has_diamond = 'true'

            enquiry_service_obj = EnquiryService.objects.filter(
                category_id=request.POST.get('cat_id'),
                category_level=cat_level,
                city_place_id=request.POST.get('city_place_id'),
                enquiry_service_status=1,
                enquiry_service_name='Gold'
            )
            for enquiry_service in enquiry_service_obj:
                if str(enquiry_service.business_id.business_id) != str(business_id):
                    date1 = datetime.strptime(enquiry_service.start_date, "%d/%m/%Y")
                    date2 = datetime.strptime(enquiry_service.end_date, "%d/%m/%Y")
                    date3 = datetime.strptime(start_date, "%d/%m/%Y")
                    if date1 <= date3 <= date2:
                        has_gold = 'true'

            enquiry_service_obj = EnquiryService.objects.filter(
                category_id=request.POST.get('cat_id'),
                category_level=cat_level,
                city_place_id=request.POST.get('city_place_id'),
                enquiry_service_status=1,
                enquiry_service_name='Silver'
            )
            i = 0
            for enquiry_service in enquiry_service_obj:
                if str(enquiry_service.business_id.business_id) != str(business_id):
                    date1 = datetime.strptime(enquiry_service.start_date, "%d/%m/%Y")
                    date2 = datetime.strptime(enquiry_service.end_date, "%d/%m/%Y")
                    date3 = datetime.strptime(start_date, "%d/%m/%Y")
                    if date1 <= date3 <= date2:
                        i = i + 1
            if i >= 2:
                has_silver = 'true'

            enquiry_service_obj = EnquiryService.objects.filter(
                category_id=request.POST.get('cat_id'),
                category_level=cat_level,
                city_place_id=request.POST.get('city_place_id'),
                enquiry_service_status=1,
                enquiry_service_name='Bronze'
            )
            i = 0
            for enquiry_service in enquiry_service_obj:
                if str(enquiry_service.business_id.business_id) != str(business_id):
                    date1 = datetime.strptime(enquiry_service.start_date, "%d/%m/%Y")
                    date2 = datetime.strptime(enquiry_service.end_date, "%d/%m/%Y")
                    date3 = datetime.strptime(start_date, "%d/%m/%Y")
                    if date1 <= date3 <= date2:
                        i = i + 1
            if i >= 3:
                has_bronze = 'true'

            enquiry_service_obj = EnquiryService.objects.filter(
                category_id=request.POST.get('cat_id'),
                category_level=cat_level,
                city_place_id=request.POST.get('city_place_id'),
                enquiry_service_status=1,
                enquiry_service_name='Value'
            )
            i = 0
            for enquiry_service in enquiry_service_obj:
                if str(enquiry_service.business_id.business_id) != str(business_id):
                    date1 = datetime.strptime(enquiry_service.start_date, "%d/%m/%Y")
                    date2 = datetime.strptime(enquiry_service.end_date, "%d/%m/%Y")
                    date3 = datetime.strptime(start_date, "%d/%m/%Y")
                    if date1 <= date3 <= date2:
                        i = i + 1
            if i >= 2:
                has_value = 'true'

            data = {
                'success': 'true','no1_ranges':no1_ranges,
                'no2_ranges':no2_ranges,'no3_ranges':no3_ranges,
                'no4_ranges':no4_ranges,'no5_ranges':no5_ranges,
                'no1_start_date': no1_start_date,
                'no2_start_date': no2_start_date,
                'no3_start_date': no3_start_date,
                'no4_start_date': no4_start_date,
                'no5_start_date': no5_start_date,
                'no1_end_date': no1_end_date,
                'no2_end_date': no2_end_date,
                'no3_end_date': no3_end_date,
                'no4_end_date': no4_end_date,
                'no5_end_date': no5_end_date,
                'has_platinum': has_platinum, 'has_diamond': has_diamond,
                'has_gold': has_gold, 'has_silver': has_silver,
                'has_bronze': has_bronze, 'has_value': has_value,
            }
        except Exception, e:
            print e
            data = {'success': 'true'}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def get_edit_telephone_service_slots(request):
    if not request.user.is_authenticated():
        data = {'success':'Expired'}

    else:    
        has_platinum = 'false'
        has_diamond = 'false'
        has_gold = 'false'
        has_silver = 'false'
        has_bronze = 'false'
        has_value = 'false'
        try:
            print request.POST
            start_date = request.POST.get('start_date')
            cat_level = int(request.POST.get('cat_lvl'))
            enquiry_service_obj = EnquiryService.objects.filter(
                category_id=request.POST.get('cat_id'),
                category_level=cat_level,
                city_place_id=request.POST.get('city_place_id'),
                enquiry_service_status=1,
                enquiry_service_name='Platinum'
            )
            for enquiry_service in enquiry_service_obj:
                if str(enquiry_service.business_id.business_id) != str(request.POST.get('business_id')):
                    date1 = datetime.strptime(enquiry_service.start_date, "%d/%m/%Y")
                    date2 = datetime.strptime(enquiry_service.end_date, "%d/%m/%Y")
                    date3 = datetime.strptime(start_date, "%d/%m/%Y")
                    if date1 <= date3 <= date2:
                        has_platinum = 'true'

            enquiry_service_obj = EnquiryService.objects.filter(
                category_id=request.POST.get('cat_id'),
                category_level=cat_level,
                city_place_id=request.POST.get('city_place_id'),
                enquiry_service_status=1,
                enquiry_service_name='Diamond'
            )
            for enquiry_service in enquiry_service_obj:
                if str(enquiry_service.business_id.business_id) != str(request.POST.get('business_id')):
                    date1 = datetime.strptime(enquiry_service.start_date, "%d/%m/%Y")
                    date2 = datetime.strptime(enquiry_service.end_date, "%d/%m/%Y")
                    date3 = datetime.strptime(start_date, "%d/%m/%Y")
                    if date1 <= date3 <= date2:
                        has_diamond = 'true'


            enquiry_service_obj = EnquiryService.objects.filter(
                category_id=request.POST.get('cat_id'),
                category_level=cat_level,
                city_place_id=request.POST.get('city_place_id'),
                enquiry_service_status=1,
                enquiry_service_name='Gold'
            )
            for enquiry_service in enquiry_service_obj:
                if str(enquiry_service.business_id.business_id) != str(request.POST.get('business_id')):
                    date1 = datetime.strptime(enquiry_service.start_date, "%d/%m/%Y")
                    date2 = datetime.strptime(enquiry_service.end_date, "%d/%m/%Y")
                    date3 = datetime.strptime(start_date, "%d/%m/%Y")
                    if date1 <= date3 <= date2:
                        has_gold = 'true'

            enquiry_service_obj = EnquiryService.objects.filter(
                category_id=request.POST.get('cat_id'),
                category_level=cat_level,
                city_place_id=request.POST.get('city_place_id'),
                enquiry_service_status=1,
                enquiry_service_name='Silver'
            )
            i = 0
            for enquiry_service in enquiry_service_obj:
                if str(enquiry_service.business_id.business_id) != str(request.POST.get('business_id')):
                    date1 = datetime.strptime(enquiry_service.start_date, "%d/%m/%Y")
                    date2 = datetime.strptime(enquiry_service.end_date, "%d/%m/%Y")
                    date3 = datetime.strptime(start_date, "%d/%m/%Y")
                    if date1 <= date3 <= date2:
                        i = i + 1
            if i >= 2:
                has_silver = 'true'

            enquiry_service_obj = EnquiryService.objects.filter(
                category_id=request.POST.get('cat_id'),
                category_level=cat_level,
                city_place_id=request.POST.get('city_place_id'),
                enquiry_service_status=1,
                enquiry_service_name='Bronze'
            )
            i = 0
            for enquiry_service in enquiry_service_obj:
                if str(enquiry_service.business_id.business_id) != str(request.POST.get('business_id')):
                    date1 = datetime.strptime(enquiry_service.start_date, "%d/%m/%Y")
                    date2 = datetime.strptime(enquiry_service.end_date, "%d/%m/%Y")
                    date3 = datetime.strptime(start_date, "%d/%m/%Y")
                    if date1 <= date3 <= date2:
                        i = i + 1
            if i >= 3:
                has_bronze = 'true'

            enquiry_service_obj = EnquiryService.objects.filter(
                category_id=request.POST.get('cat_id'),
                category_level=cat_level,
                city_place_id=request.POST.get('city_place_id'),
                enquiry_service_status=1,
                enquiry_service_name='Value'
            )
            i = 0
            for enquiry_service in enquiry_service_obj:
                if str(enquiry_service.business_id.business_id) != str(request.POST.get('business_id')):
                    date1 = datetime.strptime(enquiry_service.start_date, "%d/%m/%Y")
                    date2 = datetime.strptime(enquiry_service.end_date, "%d/%m/%Y")
                    date3 = datetime.strptime(start_date, "%d/%m/%Y")
                    if date1 <= date3 <= date2:
                        i = i + 1
            if i >= 2:
                has_value = 'true'

            data = {
                'success': 'true',
                'has_platinum': has_platinum, 'has_diamond': has_diamond,
                'has_gold': has_gold, 'has_silver': has_silver,
                'has_bronze': has_bronze, 'has_value': has_value,
            }
        except Exception, e:
            print e
            data = {'success': 'true'}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def delete_product(request):
    if not request.user.is_authenticated():
        data = {'success':'Expired'}

    else:
        try:
            request.POST.get('product_id')
            pro_obj = Product.objects.filter(product_id=request.POST.get('product_id'))
            pro_obj.delete()

            data = {'message': 'Product Deleted Successfully', 'success': 'true','del_flag':'3'}
        except IntegrityError as e:
            print e
        except Exception, e:
            print e
    return HttpResponse(json.dumps(data), content_type='application/json')  

@csrf_exempt
def delete_nearbyatt(request):
    if not request.user.is_authenticated():
        data = {'success':'Expired'}

    else:
        try:
            request.POST.get('product_id')
            pro_obj = NearByAttraction.objects.filter(attraction_id=request.POST.get('product_id'))
            pro_obj.delete()

            data = {'message': 'Attraction Deleted Successfully', 'success': 'true','del_flag':'3'}
        except IntegrityError as e:
            print e
        except Exception, e:
            print e
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def delete_shopping(request):
    if not request.user.is_authenticated():
        data = {'success':'Expired'}

    else:
        try:
            request.POST.get('product_id')
            pro_obj = NearestShopping.objects.filter(shopping_id=request.POST.get('product_id'))
            pro_obj.delete()

            data = {'message': 'Shopping Deleted Successfully', 'success': 'true','del_flag':'3'}
        except IntegrityError as e:
            print e
        except Exception, e:
            print e
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def delete_school(request):
    if not request.user.is_authenticated():
        data = {'success':'Expired'}

    else:
        try:
            request.POST.get('product_id')
            pro_obj = NearestSchool.objects.filter(school_id=request.POST.get('product_id'))
            pro_obj.delete()

            data = {'message': 'School Deleted Successfully', 'success': 'true','del_flag':'3'}
        except IntegrityError as e:
            print e
        except Exception, e:
            print e
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def delete_hospital(request):
    if not request.user.is_authenticated():
        data = {'success':'Expired'}

    else:
        try:
            request.POST.get('product_id')
            pro_obj = NearestHospital.objects.filter(hospital_id=request.POST.get('product_id'))
            pro_obj.delete()

            data = {'message': 'Hospital Deleted Successfully', 'success': 'true','del_flag':'3'}
        except IntegrityError as e:
            print e
        except Exception, e:
            print e
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def update_subscription_plan(request):
    if not request.user.is_authenticated():
        data = {'success':'Expired'}

    else:    
        advert_flag = 'false'
        try:
            #pdb.set_trace()
            supplier_id = request.POST.get('supplier_id')
            supplier_obj = Supplier.objects.get(supplier_id=supplier_id)
            city_place_id = str(supplier_obj.city_place_id)
            category_id = request.POST.get('sub_category')
            business_id = request.POST.get('business_id')

            duration = request.POST.get('duration_list')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')

            premium_service_list = request.POST.getlist('premium_service')
            premium_service_duration_list = request.POST.getlist('premium_ser_duration')
            premium_start_date_list = request.POST.getlist('premium_start_date')
            premium_end_date_list = request.POST.getlist('premium_end_date')
            premium_end_date_list = filter(None, premium_end_date_list)
            enquiry_service_list = request.POST.get('tel_service_name')
            enquiry_service_duration_list = request.POST.get('tel_ser_duration')
            enquiry_start_date_list = request.POST.getlist('tel_start_date')
            enquiry_end_date_list = request.POST.getlist('tel_end_date')
            enquiry_start_date_list = filter(None, enquiry_start_date_list)
            enquiry_end_date_list = filter(None, enquiry_end_date_list)


            cat_id = ''
            cat_lvl = ''
            if request.POST.get('lvl1'):
                cat_id = request.POST.get('lvl1')
                cat_lvl = '1'
            if request.POST.get('lvl2'):
                cat_id = request.POST.get('lvl2')
                cat_lvl = '2'
            if request.POST.get('lvl3'):
                cat_id = request.POST.get('lvl3')
                cat_lvl = '3'
            if request.POST.get('lvl4'):
                cat_id = request.POST.get('lvl4')
                cat_lvl = '4'
            if request.POST.get('lvl5'):
                cat_id = request.POST.get('lvl5')
                cat_lvl = '5'

            premium_end_date_list = filter(None, premium_end_date_list)
            zip_premium = zip(premium_service_list, premium_service_duration_list, premium_start_date_list,
                              premium_end_date_list)
            # if premium_service_list:
            #     check_premium_service = update_check_date(zip_premium, cat_id, business_id, city_place_id, cat_lvl)
            #     if check_premium_service['success'] == 'false':
            #         data = {'success': 'false', 'message': check_premium_service['msg']}
            #         return HttpResponse(json.dumps(data), content_type='application/json')

            supplier_obj = Supplier.objects.get(supplier_id=supplier_id)
            category_obj = Category.objects.get(category_id=category_id)

            business_obj = Business.objects.get(business_id=business_id)
            business_obj.category = category_obj
            business_obj.duration = duration
            business_obj.start_date = start_date
            business_obj.end_date = end_date
            business_obj.supplier = supplier_obj
            business_obj.business_created_date = datetime.now()
            business_obj.business_created_by = supplier_obj.contact_email
            business_obj.country_id=Country.objects.get(country_id=request.POST.get('country1')) if request.POST.get(
                'country1') else None
            business_obj.state_id=State.objects.get(state_id=request.POST.get('statec1')) if request.POST.get('statec1') else None
            business_obj.city_place_id=City_Place.objects.get(city_place_id=request.POST.get('city1')) if request.POST.get(
                'city1') else None

            business_obj.save()
            if request.POST.get('lvl1'):
                business_obj.category_level_1 = CategoryLevel1.objects.get(category_id=request.POST.get('lvl1'))
            if request.POST.get('lvl2'):
                business_obj.category_level_2 = CategoryLevel2.objects.get(category_id=request.POST.get('lvl2'))
            if request.POST.get('lvl3'):
                business_obj.category_level_3 = CategoryLevel3.objects.get(category_id=request.POST.get('lvl3'))
            if request.POST.get('lvl4'):
                business_obj.category_level_4 = CategoryLevel4.objects.get(category_id=request.POST.get('lvl4'))
            if request.POST.get('lvl5'):
                business_obj.category_level_5 = CategoryLevel5.objects.get(category_id=request.POST.get('lvl5'))
            business_obj.save()
            #
            transaction_code = business_obj.transaction_code
            if premium_end_date_list:
                print "premium_service_list", premium_service_list, premium_end_date_list
                PremiumService.objects.filter(business_id=business_id).delete()
                for premium_service, premium_service_duration, premium_start_date, premium_end_date in zip_premium:
                    if premium_service == "Top Advert":
                        advert_flag = "true"
                    elif premium_service == "Advert Slider":
                        advert_flag = "true"
                    premium_service_obj = PremiumService(
                        premium_service_name=premium_service,
                        no_of_days=premium_service_duration,
                        category_id=cat_id,
                        category_level=cat_lvl,
                        city_place_id=City_Place.objects.get(city_place_id=city_place_id),
                        start_date=premium_start_date,
                        end_date=premium_end_date,
                        business_id=business_obj,
                        premium_service_status="1",
                        premium_service_created_date=datetime.now(),
                        premium_service_created_by=supplier_obj.contact_email
                    )
                    premium_service_obj.save()
            else:
                PremiumService.objects.filter(business_id=business_id).delete()
            if enquiry_service_list:
                EnquiryService.objects.filter(business_id=business_id).delete()
                enquiry_service_obj = EnquiryService(
                    enquiry_service_name=enquiry_service_list,
                    no_of_days=enquiry_service_duration_list,
                    category_id=cat_id,
                    category_level=cat_lvl,
                    city_place_id=City_Place.objects.get(city_place_id=city_place_id),
                    start_date=enquiry_start_date_list[0],
                    end_date=enquiry_end_date_list[0],
                    business_id=business_obj,
                    enquiry_service_status="1",
                    enquiry_service_created_date=datetime.now(),
                    enquiry_service_created_by=supplier_obj.contact_email
                )
                enquiry_service_obj.save()
            else:
                EnquiryService.objects.filter(business_id=business_id).delete()
            
            data = {'success': 'true','advert_flag':advert_flag,
                    'message': 'The subscription is updated successfully with transaction ID :' + transaction_code + '. Please proceed with the payment .',
                    'business_id': str(business_obj)
                    }
        except Exception as e:
            print e
            data = {'success': 'false', 'message': e}
    return HttpResponse(json.dumps(data), content_type='application/json')    

@csrf_exempt
def select_subscriber(request):
    if not request.user.is_authenticated():
        logout(request)
        form = CaptchaForm()
        return render_to_response('Subscriber/user_login.html', dict(
            form=form, message_logout='Your session is timed out, Please login again.'
        ), context_instance=RequestContext(request))

    else:     
        try:
            data = {}
            supplier_list1 = []
            try:
                supplier_list = Supplier.objects.filter(contact_email=request.session['login_user'])
                for sub_obj in supplier_list:
                    supplier_id     = sub_obj.supplier_id
                    contact_person  = sub_obj.contact_person
                    business_name   = sub_obj.business_name
                    user_city       = sub_obj.city_place_id.city_id.city_name
                    user_contact_no = sub_obj.contact_no
                    user_email_id   = sub_obj.contact_email
                    supplier_status = sub_obj.supplier_status
                    if sub_obj.title:
                        user_title =sub_obj.title
                    else:
                        user_title=""
                    user_name = str(user_title + " " +sub_obj.contact_person) 

                    if sub_obj.logo:
                        logo = SERVER_URL + sub_obj.logo.url
                    else:
                        logo = SERVER_URL + '/static/assets/layouts/layout2/img/City_Hoopla_Logo.png'

                    supplier_list1.append({
                        'supplier_id': supplier_id, 'contact_person': contact_person,
                        'business_name':business_name,'user_city':user_city,
                        'user_contact_no':user_contact_no,
                        'user_email_id':user_email_id,'user_name':user_name,
                        'logo':logo,'status':supplier_status
                     })
                data = {'success': 'true', 'supplier_list1': supplier_list1}

            except IntegrityError as e:
                print e
                data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time',
                        'username': request.session['login_user']}
        except MySQLdb.OperationalError, e:
            print e
        except Exception, e:
            print 'Exception ', e
        return render(request, 'Subscriber/select_subscriber.html', data)