from django.shortcuts import render
import math
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
import time
from smtplib import SMTPException
# from captcha_form import CaptchaForm
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

# for random generation of string and numbers
import string
import random
import urllib  # Python URL functions
import urllib2

# HTTP Response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.files.base import ContentFile

# Push Notifications
from push_notifications.models import APNSDevice, GCMDevice

from helper import dd2dms
import geocoder

from geopy.distance import vincenty

import operator

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import textwrap
import StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile

# SERVER_URL = "http://192.168.0.151:9090"
SERVER_URL = "http://52.66.133.35"

# Constants
earth_radius = 6371.0
degrees_to_radians = math.pi / 180.0
radians_to_degrees = 180.0 / math.pi


@csrf_exempt
def get_about_city(request):
    json_obj = json.loads(request.body)
    city_id = json_obj['city_id']
    try:
        advert_list = []
        # where_to_shop
        # reputed_hospitals
        # college_and_universities
        # point_of_interest

        city_obj = City_Place.objects.get(city_place_id=city_id)
        city_name = city_obj.city_id.city_name
        state_county_name = city_obj.city_id.state_id.state_name + ', ' + city_obj.city_id.state_id.country_id.country_name
        city_image = city_obj.city_image.url
        about_city = ''
        if city_obj.about_city:
            about_city = city_obj.about_city
            
        city_add = city_name + ', ' + state_county_name
        location = geocoder.google(city_add)
        latitude = location.lat
        longitude = location.lng
        long_degrees, lat_degrees = dd2dms(longitude, latitude)

        point_of_interest_list = []
        colleges_list = []
        shopping_hub_list = []
        hospital_list = []

        point_of_interest_obj = Places.objects.filter(city_place_id=city_id, place_type='point_of_interest')
        for point_of_interest in point_of_interest_obj:
            if point_of_interest.place_image:
                poi_data = {
                    'place_details': point_of_interest.place_name,
                    'place_image': point_of_interest.place_image.url
                }
                point_of_interest_list.append(poi_data)

        college_obj = Places.objects.filter(city_place_id=city_id, place_type='college_and_universities')
        for college in college_obj:
            if college.place_image:
                college_data = {
                    'place_details': college.place_name,
                    'place_image': college.place_image.url
                }
                colleges_list.append(college_data)

        shopping_obj = Places.objects.filter(city_place_id=city_id, place_type='where_to_shop')
        for shopping in shopping_obj:
            if shopping.place_image:
                shopping_data = {
                    'place_details': shopping.place_name,
                    'place_image': shopping.place_image.url
                }
                shopping_hub_list.append(shopping_data)

        hospital_obj = Places.objects.filter(city_place_id=city_id, place_type='reputed_hospitals')
        for hospital in hospital_obj:
            if hospital.place_image:
                hospital_data = {
                    'place_details': hospital.place_name,
                    'place_image': hospital.place_image.url
                }
                hospital_list.append(hospital_data)

        data = {
            'success': 'true', 'message': '',
            'city_name': city_name,
            'state_county_name': state_county_name,
            'city_image': city_image,
            'about_city': about_city,
            'longitude': long_degrees,
            'latitude': lat_degrees,
            'point_of_interest': point_of_interest_list,
            'colleges': colleges_list,
            'shopping_hub': shopping_hub_list,
            'hospitals': hospital_list
        }
    except Exception, ke:
        print ke
        data = {'success': 'false', 'message': 'Something went wrong', 'advert_list': []}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def consumer_signup(request):
    try:
        json_obj = json.loads(request.body)
        consumer_obj = ConsumerProfile(
            username=json_obj['phone'],
            consumer_full_name=json_obj['full_name'],
            consumer_contact_no=json_obj['phone'],
            sign_up_source=json_obj['sign_up_source'],
            device_token=json_obj['device_token'],
            consumer_created_date=datetime.now(),
            consumer_status='1',
            consumer_created_by=json_obj['full_name'],
            consumer_updated_by=json_obj['full_name'],
            consumer_updated_date=datetime.now(),
            user_verified='false'
        );
        consumer_obj.save()
        consumer_obj.set_password(json_obj['password']);
        if json_obj['email_id']:
            consumer_obj.consumer_email_id=json_obj['email_id']
        consumer_obj.save()
        device_id = json_obj['device_token']
        device_status = add_update_consumer_device_id(consumer_obj, device_id)
        print "=======device_status=======", device_status
        ret = u''
        ret = ''.join(random.choice('0123456789') for i in range(6))
        OTP = ret
        consumer_obj.consumer_otp = str(OTP)
        consumer_obj.save()
        # request.session["OTP"] = str(OTP)
        # print request.session["OTP"]
        sms_otp(consumer_obj, OTP)
        try:
            filename = "IMG_%s_%s.png" % (consumer_obj.username, str(datetime.now()).replace('.', '_'))
            resource = urllib.urlopen(json_obj['user_profile_image'])

            consumer_obj.consumer_profile_pic = ContentFile(resource.read(), filename)  # assign image to model
            consumer_obj.save()
        except:
            pass

        data = {
            'success': 'true',
            'message': 'User Created Successfully',
            'user_info': get_profile_info(consumer_obj.consumer_id)
        }
    except Exception, e:
        print '=e===========', e
        data = {
            'success': 'false',
            'message': 'User with same username already exists'
        }
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def guest_login(request):
    try:
        json_obj = json.loads(request.body)
        consumer_list = ConsumerProfile.objects.filter(consumer_type = "guest")
        if consumer_list:
            i = consumer_list.count() - 1
            last_consumer = consumer_list[i].username
            last_consumer = last_consumer.split("_")
            user_name = "guest_user_"+str(int(last_consumer[2]) + 1)
        else:
            user_name = "guest_user_1"
        consumer_obj = ConsumerProfile(
            username=user_name,
            consumer_created_date=datetime.now(),
            user_verified='false',
            consumer_type = "guest"
        );
        consumer_obj.save()
        if json_obj['consumer_latitude']:
            consumer_obj.latitude = json_obj['consumer_latitude']
            consumer_obj.longitude = json_obj['consumer_longitude']
        data = {'success': 'true', 'user_id': str(consumer_obj.consumer_id), 'message': ''}
    except User.DoesNotExist as err:
        print 'usr NOt Exist'
        data = {'success': 'false', 'message': 'User Not Exists'}
    except Exception, e:
        print e
        data = {'success': 'false', 'message': 'Internal Server Error '}
    return HttpResponse(json.dumps(data), content_type='application/json')

def add_update_consumer_device_id(consumer_obj, device_id):
    try:
        user_obj = User.objects.get(username=consumer_obj.consumer_email_id)
        check_device = GCMDevice.objects.get(user=user_obj)
        check_device.registration_id = device_id
        check_device.save()
        send_notification(user_obj)
        return True
    except GCMDevice.DoesNotExist as err:
        print 'app_push_notifications.py | user_obj | Exception ', err
        user_obj = User.objects.get(username=consumer_obj.consumer_email_id)
        device = GCMDevice(registration_id=device_id, user=user_obj)
        device.save()
        send_notification(user_obj)
        return True
    except Exception as err:
        print 'app_push_notifications.py | user_obj | Exception ', err
        return False


@csrf_exempt
def send_notification(user_obj):
    try:
        devices = GCMDevice.objects.get(user=user_obj)
        status = devices.send_message(None,
                                      extra={"message": "Hello from City Hoopla", "badge": "1", "sound": "default",
                                             "title": "City Hoopla"})
        print 'Status : ', status
        return True
    except Exception, e:
        print e
        return False


def sms_otp(consumer_obj, OTP):
    authkey = "118994AIG5vJOpg157989f23"
    mobiles = str(consumer_obj.consumer_contact_no)

    message = "Dear User,\n"
    message = message + str(OTP) + " is your One Time Password(OTP) for CityHoopla."
    print message
    sender = "CTHPLA"
    route = "4"
    country = "91"

    values = {
        'authkey': authkey,
        'mobiles': mobiles,
        'message': message,
        'sender': sender,
        'route': route,
        'country': country
    }

    url = "http://api.msg91.com/api/sendhttp.php"
    postdata = urllib.urlencode(values)
    req = urllib2.Request(url, postdata)
    response = urllib2.urlopen(req)
    output = response.read()
    print output


@csrf_exempt
def resend_otp(request):
    json_obj = json.loads(request.body)
    user_id = json_obj['user_id']
    contact_no = json_obj['contact_no']
    ret = u''
    ret = ''.join(random.choice('0123456789') for i in range(6))
    OTP = ret
    # request.session["OTP"] = str(OTP)
    consumer_obj = ConsumerProfile.objects.get(consumer_id=str(user_id))
    consumer_obj.consumer_contact_no = str(contact_no)
    consumer_obj.consumer_otp = str(OTP)
    consumer_obj.save()
    sms_otp(consumer_obj, OTP)
    data = {'success': 'true', 'message': 'OPT send to user'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def check_otp(request):
    json_obj = json.loads(request.body)
    # print request.session["OTP"]
    # session_otp = request.session['OTP']
    user_id = json_obj['user_id']
    #contact_no = json_obj['contact_no']
    msg_otp = json_obj['OTP']
    consumer_obj = ConsumerProfile.objects.get(consumer_id=str(user_id))
    session_otp = str(consumer_obj.consumer_otp)
    if session_otp == msg_otp:
        consumer_obj.user_verified = 'true'
        #consumer_obj.consumer_contact_no = str(contact_no)
        consumer_obj.save()
        data = {'success': 'true', 'message': 'OPT match'}
    else:
        data = {'success': 'false', 'message': "OPT doesn't match"}
    return HttpResponse(json.dumps(data), content_type='application/json')


# Sign Up via Gmail and Facebook
@csrf_exempt
def social_signup(request):
    try:
        # pdb.set_trace()
        json_obj = json.loads(request.body)
        print 'JSON OBJECT : ', json_obj
        consumer_obj = ConsumerProfile(
            username=json_obj['email_id'],
            consumer_full_name=json_obj['full_name'],
            consumer_email_id=json_obj['email_id'],
            device_token=json_obj['device_token'],
            sign_up_source=json_obj['sign_up_source'],
            consumer_profile_pic=json_obj['user_profile_image'],
            consumer_contact_no=json_obj['phone'],
            consumer_created_date=datetime.now(),
            consumer_status='1',
            consumer_created_by=json_obj['full_name'],
            consumer_updated_by=json_obj['full_name'],
            consumer_updated_date=datetime.now()
        )
        consumer_obj.save()

        filename = "IMG_%s_%s.jpg" % (
            consumer_obj.username, str(datetime.now()).replace('.', '_'))  # For giving filename to Image
        resource = urllib.urlopen(json_obj['user_profile_image'])

        consumer_obj.consumer_profile_pic = ContentFile(resource.read(), filename)  # assign image to model
        consumer_obj.save()

        if consumer_obj:
            data = {'success': 'true', 'message': 'Successful Sign Up',
                    'user_info': get_profile_info(consumer_obj.consumer_id)}
            email = consumer_obj.username
        else:
            data = {'success': 'false', 'message': 'Sign Up not Successful'}
    except ConsumerProfile.DoesNotExist, e:
        data = {'success': 'false', 'message': str(e)}
    except IntegrityError as err:
        json_obj = json.loads(request.body)
        consumer_obj = ConsumerProfile.objects.get(username=json_obj['email_id'])
        data = {'success': 'true', 'message': 'Login Successful',
                'user_info': get_profile_info(consumer_obj.consumer_id)}
        return HttpResponse(json.dumps(data), content_type='application/json')
    except Exception, e:
        json_obj = json.loads(request.body)
        email_id = json_obj['email_id']
        data = {'success': 'false', 'message': 'Server Error'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def set_notification_settings(request):
    try:
        json_obj = json.loads(request.body)
        print json_obj

        customer_object = ConsumerProfile.objects.get(consumer_id=json_obj['user_id'])
        customer_object.notification_status = json_obj['all_notification_status']
        customer_object.push_review_status = json_obj['push_my_reviews_status']
        customer_object.push_post_status = json_obj['push_my_posts_status']
        customer_object.push_social_status = json_obj['push_social_notifications_status']
        customer_object.email_review_status = json_obj['email_my_reviews_status']
        customer_object.newsletter_status = json_obj['email_weekly_newsletter_status']
        customer_object.email_social_status = json_obj['email_social_notifications_status']
        customer_object.save()

        data = {'success': 'true', 'message': 'Notification setting updated successfully',
                'user_info': get_profile_info(customer_object.consumer_id)}
    except Exception, e:
        print e
        data = {'success': 'false', 'message': "Server Error, Please try again!"}
    return HttpResponse(json.dumps(data), content_type='application/json')


def get_profile_info(user_id):
    print "ID--", user_id

    consumer_object = ConsumerProfile.objects.get(consumer_id=user_id)
    if consumer_object.consumer_profile_pic:
        user_profile_image = consumer_object.consumer_profile_pic.url
    else:
        user_profile_image = ''
    data = {
        'user_id': str(consumer_object.consumer_id),
        'full_name': consumer_object.consumer_full_name,
        'phone': consumer_object.consumer_contact_no,
        'user_profile_image': user_profile_image,
        'email_id': consumer_object.consumer_email_id if consumer_object.consumer_email_id else '',
        'active_status': consumer_object.online,
        'created_date': consumer_object.consumer_created_date.strftime('%d/%m/%Y'),
        'user_verified': consumer_object.user_verified,
        'all_notification': consumer_object.notification_status,
        'push_my_reviews': consumer_object.push_review_status,
        'push_my_posts': consumer_object.push_post_status,
        'push_social_notifications': consumer_object.push_social_status,
        'email_my_reviews': consumer_object.email_review_status,
        'email_weekly_newsletter': consumer_object.newsletter_status,
        'email_social_notifications': consumer_object.email_social_status
    }
    return data


@csrf_exempt
def consumer_login(request):
    try:
        print request.body
        if request.method == 'POST':
            json_obj = json.loads(request.body)
            try:
                consumer_obj = ConsumerProfile.objects.get(username=json_obj['username'])
                user = authenticate(username=json_obj['username'], password=json_obj['password'])

                print "info", user
                if user:
                    consumer = ConsumerProfile.objects.get(username=json_obj['username'])
                    if user.is_active:
                        if consumer.no_of_login:
                            count = int(consumer.no_of_login) + 1
                        else:
                            count = 1
                        consumer.no_of_login = count
                        consumer.save()

                        data = {'success': 'true', 'message': 'Login Successful',
                                'user_info': get_profile_info(consumer.consumer_id)}

                    else:
                        data = {'success': 'false', 'message': 'User Is Not Active'}
                else:
                    data = {'success': 'false', 'message': 'Please enter valid Password'}
            except:
                data = {'success': 'false', 'message': 'Invalid Username'}
        else:
            data = {'success': 'false', 'message': 'Invalid Request'}
    except User.DoesNotExist as err:
        print 'usr NOt Exist'
        data = {'success': 'false', 'message': 'User Not Exists'}
    except Exception, e:
        print e
        data = {'success': 'false', 'message': 'Internal Server Error '}
    return HttpResponse(json.dumps(data), content_type='application/json')


# API for forgot password
@csrf_exempt
def forgot_password(request):
    json_obj = json.loads(request.body)
    user_name = json_obj['contact_no']
    try:
        if request.method == 'POST':
            customer_obj = ConsumerProfile.objects.get(username=user_name)
            authkey = "118994AIG5vJOpg157989f23"
            mobiles = str(customer_obj.consumer_contact_no)
            pwdSize = 6
            chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
            password = ''.join((random.choice(chars)) for x in range(pwdSize))
            print "PASSWORD", password
            customer_obj.set_password(password)
            customer_obj.save()
            message = " Dear "+customer_obj.consumer_full_name+",\nYour password has been set to " + str(password)
            message = message + " .\n\nBest Wishes," + "\nTeam CityHoopla"
            print message
            sender = "CTHPLA"
            route = "4"
            country = "91"

            values = {
                'authkey': authkey,
                'mobiles': mobiles,
                'message': message,
                'sender': sender,
                'route': route,
                'country': country
            }

            url = "http://api.msg91.com/api/sendhttp.php"
            postdata = urllib.urlencode(values)
            req = urllib2.Request(url, postdata)
            response = urllib2.urlopen(req)
            output = response.read()
            data = {'success': 'true', 'message': " Password Sent Successfully"}

    except User.DoesNotExist, e:
        data = {'success': 'false', 'message': "Username does not exists"}
        print "failed to send mail", e
    except Exception, e:
        print e
        data = {'success': 'false', 'message': "Server Error, Please try again!"}
    print '=====data=============', data
    return HttpResponse(json.dumps(data), content_type='application/json')


def get_city_list(request):
    ##    pdb.set_trace()
    city_list = []

    try:
        city_objs = City_Place.objects.filter(city_status=1)

        for city in city_objs:
            city_id = str(city.city_place_id)
            city_name = str(city.city_id.city_name)
            city_list1 = {'city_id': city_id, 'city_name': city_name}

            city_list.append(city_list1)
        data = {'city_list': city_list, 'success': 'true'}
    except Exception, ke:
        print ke
        data = {'city_list': city_list, 'success': 'true'}
    return HttpResponse(json.dumps(data), content_type='application/json')


def save_advert_slider_image(advert_obj):
    try:
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
        
        font = ImageFont.truetype("/home/ec2-user/DigiSpace/static/Khula-SemiBold.ttf", 15)
        bold_font = ImageFont.truetype("/home/ec2-user/DigiSpace/static/Khula-Bold.ttf", 18)
        #semi_bold_font = ImageFont.truetype("/home/ec2-user/DigiSpace/static/Khula-SemiBold.ttf", 20)
        if advert_obj.display_image:
            display_image = advert_obj.display_image.url
        else:
            display_image = "/static/assets/layouts/layout2/img/City_Hoopla_Logo.png"


        dis_img = Image.open(os_path + display_image)

        dis_img = dis_img.resize((200, 100), Image.ANTIALIAS)

        title_txt = Image.new('RGBA', (400,100), (255,255,255,255))
        draw = ImageDraw.Draw(title_txt)

        current_h, pad = 0, 4
        MAX_W, MAX_H = 355, 100
        for line in textwrap.wrap(advert_tilte, width=30):
            w, h = draw.textsize(line, font=font)   
            draw.text(((MAX_W - w) / 2, current_h), line, font=bold_font, fill="#00448b")
            current_h += h + pad

        current_h, pad = 40, 2
        MAX_W, MAX_H = 400, 100
        for line in textwrap.wrap(advert_address, width=35):
            w, h = draw.textsize(line, font=font)   
            draw.text(((MAX_W - w) / 2, current_h), line, font=font, fill="#00448b")
            current_h += h + pad


        image_name = "new_advert_slider_" + str(advert_obj.advert_id) + ".jpg"
        blank_image = Image.new('RGBA', (600,100), (255,255,255,255))
        draw = ImageDraw.Draw(blank_image)
        blank_image.paste(dis_img, (0,0))
        blank_image.paste(title_txt, (200,0))
        tempfile = blank_image
        tempfile_io = StringIO.StringIO()
        tempfile.save(tempfile_io, format='JPEG')
        image_file = InMemoryUploadedFile(tempfile_io, None, image_name, 'image/jpeg', tempfile_io.len, None)
        advert_obj.advert_slider_image.save(image_name, image_file)
        advert_obj.save()
    except Exception as e:
        print "advert slider image", e
    return 1

@csrf_exempt
def get_bottom_advert_list(request):
    json_obj = json.loads(request.body)
    city_id = json_obj['city_id']
    user_id = json_obj['user_id']
    try:
        advert_list = []
        advert_obj_list = Advert.objects.filter(city_place_id=city_id,status =1)
        for advert_obj in advert_obj_list:
            save_advert_slider_image(advert_obj)
            advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=str(advert_obj.advert_id))
            pre_ser_obj_list = PremiumService.objects.filter(business_id=str(advert_sub_obj.business_id))
            pre_date = datetime.now().strftime("%d/%m/%Y")
            pre_date = datetime.strptime(pre_date, "%d/%m/%Y")
            end_date = advert_sub_obj.business_id.end_date
            start_date = datetime.strptime(advert_sub_obj.business_id.start_date, "%d/%m/%Y")
            if start_date <= pre_date:
                end_date = datetime.strptime(end_date, "%d/%m/%Y")
                date_gap = end_date - pre_date
                if int(date_gap.days) >= 0:
                    for pre_ser_obj in pre_ser_obj_list:
                        if pre_ser_obj.premium_service_name == "Advert Slider":
                            if advert_obj.advert_slider_image:
                                advert_image = advert_obj.advert_slider_image.url
                            else:
                                advert_image = "/static/assets/layouts/layout2/img/City_Hoopla_Logo.png"
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
                            advert_data = {
                                "advert_id": str(advert_obj.advert_id),
                                "advert_image": advert_image,
                                "user_id": str(user_id),
                                "category_id": "0",
                                "level": "0",
                                "discount_description":discount_description,
                                "advert_tilte":advert_tilte,
                                "advert_address":advert_address
                            }
                            advert_list.append(advert_data)
        data = {'success': 'true', 'message': '', 'advert_list': advert_list}
    except Exception, ke:
        print ke
        data = {'success': 'false', 'message': 'Something went wrong', 'advert_list': []}
    return HttpResponse(json.dumps(data), content_type='application/json')

def save_advert_image(advert_obj):
    os_path = '/home/ec2-user/DigiSpace'

    discount_description = advert_obj.discount_description
    advert_tilte = advert_obj.advert_name.strip()
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

    font = ImageFont.truetype("/home/ec2-user/DigiSpace/static/Khula-Regular.ttf",  24)
    bold_font = ImageFont.truetype("/home/ec2-user/DigiSpace/static/Khula-Bold.ttf", 30)
    semi_bold_font = ImageFont.truetype("/home/ec2-user/DigiSpace/static/Khula-SemiBold.ttf", 28)

    imageA = Image.open(os_path + advert_obj.display_image.url)
    image_width = imageA.size[0]
    image_height = imageA.size[1]
    width = 556
    offset = 0
    height = 810
    margin = 0

    if image_width < 556:
        width = image_width
        offset = 556 - int(image_width)
        offset = offset/2

    if image_height < 810:
        height = image_height
        margin = 810 - int(image_height)
        margin = margin/2

    crop_width = 556
    crop_height = 810

    if image_width < 556:
        crop_width = image_width

    if image_height < 810:
        crop_height = image_height

    image = imageA.crop((0, 0, crop_width, crop_height))
    imageA = Image.open(os_path + "/static/Ad_background-image2.png")
    imageA = imageA.resize((556, 810), Image.ANTIALIAS)
    imageA.paste(image, (offset,margin))

    imageB = Image.open (os_path + "/static/Black-gradient.png")
    imageB = imageB.resize((556, 810), Image.ANTIALIAS)
    imageA.paste(imageB, (0, 0), imageB.convert('RGBA'))

    imgsize = (566, 820) #The size of the image
    image = Image.open (os_path + "/static/Ad_background-image2.png")
    image = image.resize((566, 820), Image.ANTIALIAS)

    image.paste(imageA, (5,5))
    draw = ImageDraw.Draw(image)

    margin = 20
    offset = 20
    i = 0
    for line in textwrap.wrap(advert_tilte, width=25):
        draw.text((margin, offset), line, font=bold_font, fill="#ffffff")
        offset += font.getsize(line)[1] + 15
        i = i + 1

    i = 0
    offset = offset + 15
    for line in textwrap.wrap(discount_description, width=50):
        draw.text((margin, offset), line, font=font, fill="#ffffff")
        offset += font.getsize(line)[1] + 5
        i = i + 1

    margin = 20
    offset = 700
    i = 0
    for line in textwrap.wrap(advert_address, width=30):
        draw.text((margin, offset), line, font=semi_bold_font, fill="#ffffff")
        offset += font.getsize(line)[1] + 10
        i = i + 1

    image_name = "new_top_advert_" + str(advert_obj.advert_id) + ".jpg"
    tempfile = image
    tempfile_io = StringIO.StringIO()
    tempfile.save(tempfile_io, format='JPEG')
    image_file = InMemoryUploadedFile(tempfile_io, None, image_name, 'image/jpeg', tempfile_io.len, None)
    advert_obj.advert_image.save(image_name, image_file)
    advert_obj.save()
    return 1

@csrf_exempt
def get_top_advert(request):
    json_obj = json.loads(request.body)
    city_id = json_obj['city_id']
    user_id = json_obj['user_id']
    try:
        advert_list = []
        advert_data = ''
        advert_obj_list = Advert.objects.filter(city_place_id=city_id,status = 1)
        if advert_obj_list:
            for advert_obj in advert_obj_list:

                advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=str(advert_obj.advert_id))
                pre_ser_obj_list = PremiumService.objects.filter(business_id=str(advert_sub_obj.business_id))
                for pre_ser_obj in pre_ser_obj_list:
                    if pre_ser_obj.premium_service_name == "Top Advert":
                        pre_date = datetime.now().strftime("%d/%m/%Y")
                        pre_date = datetime.strptime(pre_date, "%d/%m/%Y")
                        end_date = pre_ser_obj.end_date
                        start_date = datetime.strptime(pre_ser_obj.start_date, "%d/%m/%Y")
                        if start_date <= pre_date:
                            end_date = datetime.strptime(end_date, "%d/%m/%Y")
                            date_gap = end_date - pre_date
                            print pre_date,end_date,date_gap
                            if int(date_gap.days) >= 0:
                        
                                save_advert_image(advert_obj)
                                if advert_obj.advert_image:
                                    advert_image = advert_obj.advert_image.url
                                else:
                                    advert_image = "/static/assets/layouts/layout2/img/City_Hoopla_Logo.png"
                                advert_data = {
                                    "advert_id": str(advert_obj.advert_id),
                                    "advert_image": advert_image,
                                    "user_id": str(user_id),
                                    "category_id": "0",
                                    "level": "0"
                                }
        else:
            advert_data = {
                "advert_id": "",
                "advert_image": "",
                "user_id": "",
                "category_id": "",
                "level": ""
            }
        data = {'success': 'true', 'message': '', 'advert_data': advert_data}
    except Exception, ke:
        print ke
        data = {'success': 'false', 'message': 'Something went wrong', 'advert_data': ''}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def get_category_subcategory_list(request):
    ##    pdb.set_trace()
    json_obj = json.loads(request.body)
    city_id = json_obj['city_id']
    level = json_obj['level']
    category_list = []
    category_id_list = []
    color = ''
    city_image = ''
    try:
        city_obj = City_Place.objects.get(city_place_id=city_id)
        if json_obj['user_id']:
            print json_obj['user_id']
            consumer_obj = ConsumerProfile.objects.get(consumer_id = json_obj['user_id'])
            consumer_obj.city_place_id = city_obj
            consumer_obj.save()
        if city_obj.city_image:
            city_image = city_obj.city_image.url
        else:
            city_image = "/static/assets/layouts/layout2/img/City_Hoopla_Logo.png"

        cat_objs = Category.objects.filter(category_status='1')
        x = 0
        for cat in cat_objs:
            cat_city_obj = CategoryCityMap.objects.filter(category_id=str(cat.category_id))
            if cat_city_obj:
                for cat_city in cat_city_obj:
                    if int(cat_city.city_place_id.city_place_id) == int(city_id):
                        print cat_city.sequence
                        category_id_list.append(str(cat.category_id))
            else:
                category_id_list.append(str(cat.category_id))
        for cat_city in category_id_list:
            category_id = str(cat_city)
            cat_objs = Category.objects.filter(category_id=category_id, category_status='1')
            i = 0
            for cat_obj in cat_objs:
                i = i + 1
                if cat_obj.category_name != "Ticket Resell":
                    cat_id = str(cat_obj.category_id)
                    advert_count, like_count, subcat_list = get_cat_data(cat_id, city_id)
                    try:
                        category_sequence = CategoryCityMap.objects.get(category_id = str(cat_id)).sequence
                    except:
                        category_sequence = i
                    cat_obj_data = {
                        "category_id": str(cat_id),
                        "category_name": cat_obj.category_name,
                        "category_img": cat_obj.category_image.url,
                        "total_adverts_count": str(advert_count),
                        "total_likes": str(like_count),
                        "favorite": "0",
                        "category": subcat_list,
                        "category_color": str(cat_obj.category_color) or '#000000',
                        "category_sequence": int(category_sequence)
                    }
                    category_list.append(cat_obj_data)

            for cat_obj in cat_objs:
                i = i + 1
                if cat_obj.category_name == "Ticket Resell":
                    cat_id = str(cat_obj.category_id)
                    #advert_count, like_count, subcat_list = get_cat_data(cat_id, city_id)
                    status = ["unread","appropriate"]
                    sell_ticket_obj = SellTicket.objects.filter(city_id=json_obj['city_id'], status__in=status)#.count()

                    sellticket_id_list = []
                    if sell_ticket_obj:
                        for ticket in sell_ticket_obj:
                            pre_date = datetime.now().strftime("%d/%m/%Y")
                            pre_date = datetime.strptime(pre_date, "%d/%m/%Y")
                            if ticket.start_date:
                                try:
                                    event_start_date = datetime.strptime(ticket.start_date, "%Y-%m-%d")
                                except:
                                    try:
                                        event_start_date = datetime.strptime(ticket.start_date, "%d %b %Y")
                                    except:
                                        event_start_date = datetime.strptime(ticket.start_date, "%d-%m-%Y")
                                if event_start_date >= pre_date:
                                    sellticket_id_list.append(ticket.sellticket_id)

                            if ticket.select_activation_date:
                                try:
                                    event_activation_date = datetime.strptime(ticket.select_activation_date, "%Y-%m-%d")
                                except:
                                    try:
                                        event_activation_date = datetime.strptime(ticket.select_activation_date, "%d %b %Y")
                                    except:
                                        event_activation_date = datetime.strptime(ticket.select_activation_date, "%d-%m-%Y")
                                if event_activation_date >= pre_date:                
                                    sellticket_id_list.append(ticket.sellticket_id)

                        selltckt_id_list = set(sellticket_id_list)
                        sellticket_id_list = list(selltckt_id_list)

                    like_count = SellTicketLike.objects.filter(sellticket_id__in = sellticket_id_list).count()

                    cat_obj_data = {
                        "category_id": str(cat_id),
                        "category_name": cat_obj.category_name,
                        "category_img": cat_obj.category_image.url,
                        "total_adverts_count": str(len(sellticket_id_list)),
                        "total_likes": str(like_count),
                        "favorite": "0",
                        "category": [],
                        "category_color": str(cat_obj.category_color) or '#000000',
                        "category_sequence": 1000
                    }
                    category_list.append(cat_obj_data)
        category_list.sort(key=operator.itemgetter('category_sequence'))
        data = {'success': 'true', 'message': '', 'category_list': category_list, 'level': level,
                'city_image': city_image}
    except Exception, ke:
        print ke
        data = {'success': 'false', 'message': 'Something went wrong', 'category_list': [], 'level': ''}
    return HttpResponse(json.dumps(data), content_type='application/json')


def get_cat_data(cat_id, city_id):
    advert_count = 0
    like_count = 0
    sub_cat_obj = CategoryLevel1.objects.filter(parent_category_id=cat_id, category_status='1')
    subcat_list = []
    for sub_cat in sub_cat_obj:
        i = 0
        advert_obj = Advert.objects.filter(category_level_1=str(sub_cat.category_id), status='1')
        for adverts in advert_obj:
            advert_id = adverts.advert_id
            if adverts.city_place_id:
                try:
                    pre_date = datetime.now().strftime("%d/%m/%Y")
                    pre_date = datetime.strptime(pre_date, "%d/%m/%Y")
                    advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)
                    end_date = advert_sub_obj.business_id.end_date
                    start_date = datetime.strptime(advert_sub_obj.business_id.start_date, "%d/%m/%Y")
                    if start_date <= pre_date:
                        end_date = datetime.strptime(end_date, "%d/%m/%Y")
                        date_gap = end_date - pre_date
                        if int(date_gap.days) >= 0:
                            i = i + 1
                except Exception:
                    print ""
                advert_like_obj = AdvertLike.objects.filter(advert_id=advert_id)
                like_count = like_count + advert_like_obj.count()
            # else:
            #         i = i + 1
        cat_id = str(sub_cat.category_id)
        subcat2_list = get_cat2_data(cat_id, city_id)

        sub_cat_data = {
            "category_id": str(sub_cat.category_id),
            "category_name": sub_cat.category_name,
            "total_adverts_count": str(i),
            "level": "1",
            "category": subcat2_list,
        }
        advert_count = advert_count + int(i) 
        subcat_list.append(sub_cat_data)
    return advert_count, like_count, subcat_list


def get_cat2_data(cat_id, city_id):
    advert_count = 0
    like_count = 0
    sub_cat_obj = CategoryLevel2.objects.filter(parent_category_id=cat_id, category_status='1')
    subcat_list = []
    for sub_cat in sub_cat_obj:
        i = 0
        advert_obj = Advert.objects.filter(category_level_2=str(sub_cat.category_id), status='1')
        for adverts in advert_obj:
            advert_id = adverts.advert_id
            if adverts.city_place_id:
                # if int(adverts.city_place_id.city_place_id) == int(city_id):
                try:
                    pre_date = datetime.now().strftime("%d/%m/%Y")
                    pre_date = datetime.strptime(pre_date, "%d/%m/%Y")
                    advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)
                    end_date = advert_sub_obj.business_id.end_date
                    start_date = datetime.strptime(advert_sub_obj.business_id.start_date, "%d/%m/%Y")
                    if start_date <= pre_date:
                        end_date = datetime.strptime(end_date, "%d/%m/%Y")
                        date_gap = end_date - pre_date
                        if int(date_gap.days) >= 0:
                            i = i + 1
                except Exception:
                    pass
                # else:
                #     i = i + 1
        cat_id = str(sub_cat.category_id)
        subcat3_list = get_cat3_data(cat_id, city_id)

        sub_cat_data = {
            "category_id": str(sub_cat.category_id),
            "category_name": sub_cat.category_name,
            "total_adverts_count": str(i),
            "level": "2",
            "category": subcat3_list
        }
        # advert_count = advert_count + int(advert_obj.count()) - i
        subcat_list.append(sub_cat_data)
    return subcat_list


def get_cat3_data(cat_id, city_id):
    advert_count = 0
    like_count = 0
    sub_cat_obj = CategoryLevel3.objects.filter(parent_category_id=cat_id, category_status='1')
    subcat_list = []
    for sub_cat in sub_cat_obj:
        i = 0
        advert_obj = Advert.objects.filter(category_level_3=str(sub_cat.category_id), status='1')
        for adverts in advert_obj:
            advert_id = adverts.advert_id
            if adverts.city_place_id:
                #if int(adverts.city_place_id.city_place_id) == int(city_id):
                try:
                    pre_date = datetime.now().strftime("%d/%m/%Y")
                    pre_date = datetime.strptime(pre_date, "%d/%m/%Y")
                    advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)
                    end_date = advert_sub_obj.business_id.end_date
                    start_date = datetime.strptime(advert_sub_obj.business_id.start_date, "%d/%m/%Y")
                    if start_date <= pre_date:
                        end_date = datetime.strptime(end_date, "%d/%m/%Y")
                        date_gap = end_date - pre_date
                        if int(date_gap.days) >= 0:
                            i = i + 1
                except Exception:
                    pass
                # else:
                #     i = i + 1
        cat_id = str(sub_cat.category_id)
        subcat4_list = get_cat4_data(cat_id, city_id)

        sub_cat_data = {
            "category_id": str(sub_cat.category_id),
            "category_name": sub_cat.category_name,
            "total_adverts_count": str(i),
            "level": "3",
            "category": subcat4_list
        }
        # advert_count = advert_count + int(advert_obj.count()) - i
        subcat_list.append(sub_cat_data)
    return subcat_list


def get_cat4_data(cat_id, city_id):
    advert_count = 0
    like_count = 0
    sub_cat_obj = CategoryLevel4.objects.filter(parent_category_id=cat_id, category_status='1')
    subcat_list = []
    for sub_cat in sub_cat_obj:
        i = 0
        advert_obj = Advert.objects.filter(category_level_4=str(sub_cat.category_id), status='1')
        for adverts in advert_obj:
            advert_id = adverts.advert_id
            if adverts.city_place_id:
                # if int(adverts.city_place_id.city_place_id) == int(city_id):
                try:
                    pre_date = datetime.now().strftime("%d/%m/%Y")
                    pre_date = datetime.strptime(pre_date, "%d/%m/%Y")
                    advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)
                    end_date = advert_sub_obj.business_id.end_date
                    start_date = datetime.strptime(advert_sub_obj.business_id.start_date, "%d/%m/%Y")
                    if start_date <= pre_date:
                        end_date = datetime.strptime(end_date, "%d/%m/%Y")
                        date_gap = end_date - pre_date
                        if int(date_gap.days) >= 0:
                            i = i + 1
                except Exception:
                    pass
                # else:
                #     i = i + 1
        cat_id = str(sub_cat.category_id)
        subcat5_list = get_cat5_data(cat_id, city_id)

        sub_cat_data = {
            "category_id": str(sub_cat.category_id),
            "category_name": sub_cat.category_name,
            "total_adverts_count": str(i),
            "level": "4",
            "category": subcat5_list
        }
        # advert_count = advert_count + int(advert_obj.count()) - i
        subcat_list.append(sub_cat_data)
    return subcat_list


def get_cat5_data(cat_id, city_id):
    advert_count = 0
    like_count = 0
    sub_cat_obj = CategoryLevel5.objects.filter(parent_category_id=cat_id, category_status='1')
    subcat_list = []
    for sub_cat in sub_cat_obj:
        i = 0
        advert_obj = Advert.objects.filter(category_level_5=str(sub_cat.category_id), status='1')
        for adverts in advert_obj:
            advert_id = adverts.advert_id
            if adverts.city_place_id:
                #if int(adverts.city_place_id.city_place_id) == int(city_id):
                try:
                    pre_date = datetime.now().strftime("%d/%m/%Y")
                    pre_date = datetime.strptime(pre_date, "%d/%m/%Y")
                    advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)
                    end_date = advert_sub_obj.business_id.end_date
                    start_date = datetime.strptime(advert_sub_obj.business_id.start_date, "%d/%m/%Y")
                    if start_date <= pre_date:
                        end_date = datetime.strptime(end_date, "%d/%m/%Y")
                        date_gap = end_date - pre_date
                        if int(date_gap.days) >= 0:
                            i = i + 1
                except Exception:
                    pass
                # else:
                #     i = i + 1
        sub_cat_data = {
            "category_id": str(sub_cat.category_id),
            "category_name": sub_cat.category_name,
            "total_adverts_count": str(i),
            "level": "5"
        }
        # advert_count = advert_count + int(advert_obj.count()) - i
        subcat_list.append(sub_cat_data)
    return subcat_list


@csrf_exempt
def get_category_list(request):
    ##    pdb.set_trace()
    json_obj = json.loads(request.body)
    city_id = json_obj['city_id']
    level = json_obj['level']
    category_list = []
    category_id_list = []
    color = ''
    try:
        if json_obj['category_id'] == "0":
            cat_objs = Category.objects.filter(category_status='1')
            x = 0
            for cat in cat_objs:
                cat_city_obj = CategoryCityMap.objects.filter(category_id=str(cat.category_id))
                if cat_city_obj:
                    for cat_city in cat_city_obj:
                        if int(cat_city.city_place_id.city_place_id) == int(city_id):
                            category_id_list.append(str(cat.category_id))
                else:
                    category_id_list.append(str(cat.category_id))
            print category_id_list
            for cat_city in category_id_list:
                category_id = str(cat_city)
                # print category_id
                cat_objs = Category.objects.filter(category_id=category_id, category_status='1')
                for cat_obj in cat_objs:
                    cat_id = str(cat_obj.category_id)
                    advert_count = 0
                    like_count = 0
                    sub_cat_obj = CategoryLevel1.objects.filter(parent_category_id=cat_id, category_status='1')
                    subcat_list = []
                    for sub_cat in sub_cat_obj:
                        i = 0
                        advert_obj = Advert.objects.filter(category_level_1=str(sub_cat.category_id))
                        for adverts in advert_obj:
                            advert_id = adverts.advert_id
                            if adverts.city_place_id:
                                if int(adverts.city_place_id.city_place_id) == int(city_id):
                                    try:
                                        pre_date = datetime.now().strftime("%d/%m/%Y")
                                        pre_date = datetime.strptime(pre_date, "%d/%m/%Y")
                                        advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)
                                        end_date = advert_sub_obj.business_id.end_date
                                        end_date = datetime.strptime(end_date, "%d/%m/%Y")
                                        date_gap = end_date - pre_date
                                        if int(date_gap.days) < 0:
                                            i = i + 1
                                    except Exception:
                                        print ""

                                    advert_like_obj = AdvertLike.objects.filter(advert_id=advert_id)
                                    for advert_like in advert_like_obj:
                                        like_count = like_count + 1

                                else:
                                    i = i + 1
                        sub_cat_data = {
                            "id": sub_cat.category_id,
                            "name": sub_cat.category_name,
                            "count": int(advert_obj.count()) - i,
                        }
                        advert_count = advert_count + int(advert_obj.count()) - i
                        subcat_list.append(sub_cat_data)
                    cat_obj_data = {
                        "category_id": cat_id,
                        "category_name": cat_obj.category_name,
                        "category_img": cat_obj.category_image.url,
                        "total_adverts_count": advert_count,
                        "total_likes": like_count,
                        "favorite": "0",
                        "subcategories": subcat_list,
                        "category_color": str(cat_obj.category_color) or '#000000'
                    }
                    category_list.append(cat_obj_data)
        else:
            if level == '1':
                cat_objs = CategoryLevel1.objects.filter(category_id=json_obj['category_id'],
                                                         category_status='1')
            if level == '2':
                cat_objs = CategoryLevel2.objects.filter(category_id=json_obj['category_id'],
                                                         category_status='1')
            if level == '3':
                cat_objs = CategoryLevel3.objects.filter(category_id=json_obj['category_id'],
                                                         category_status='1')
            if level == '4':
                cat_objs = CategoryLevel4.objects.filter(category_id=json_obj['category_id'],
                                                         category_status='1')
            if level == '5':
                cat_objs = CategoryLevel5.objects.filter(category_id=json_obj['category_id'],
                                                         category_status='1')
            print cat_objs
            for cat_obj in cat_objs:
                cat_id = str(cat_obj.category_id)
                advert_count = 0
                like_count = 0
                if level == '1':
                    sub_cat_obj = CategoryLevel2.objects.filter(parent_category_id=cat_id, category_status='1')
                if level == '2':
                    sub_cat_obj = CategoryLevel3.objects.filter(parent_category_id=cat_id, category_status='1')
                if level == '3':
                    sub_cat_obj = CategoryLevel4.objects.filter(parent_category_id=cat_id, category_status='1')
                if level == '4':
                    sub_cat_obj = CategoryLevel5.objects.filter(parent_category_id=cat_id, category_status='1')
                subcat_list = []
                for sub_cat in sub_cat_obj:
                    i = 0
                    if level == '1':
                        advert_obj = Advert.objects.filter(category_level_2=str(sub_cat.category_id))
                    if level == '2':
                        advert_obj = Advert.objects.filter(category_level_3=str(sub_cat.category_id))
                    if level == '3':
                        advert_obj = Advert.objects.filter(category_level_4=str(sub_cat.category_id))
                    if level == '4':
                        advert_obj = Advert.objects.filter(category_level_5=str(sub_cat.category_id))
                    for adverts in advert_obj:
                        advert_id = adverts.advert_id
                        if adverts.city_place_id:
                            if int(adverts.city_place_id.city_place_id) == int(city_id):
                                try:
                                    pre_date = datetime.now().strftime("%d/%m/%Y")
                                    pre_date = datetime.strptime(pre_date, "%d/%m/%Y")
                                    advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)
                                    end_date = advert_sub_obj.business_id.end_date
                                    end_date = datetime.strptime(end_date, "%d/%m/%Y")
                                    date_gap = end_date - pre_date
                                    if int(date_gap.days) < 0:
                                        i = i + 1
                                except Exception:
                                    print ""

                                advert_like_obj = AdvertLike.objects.filter(advert_id=advert_id)

                                for advert_like in advert_like_obj:
                                    like_count = like_count + 1

                            else:
                                i = i + 1
                    sub_cat_data = {
                        "id": sub_cat.category_id,
                        "name": sub_cat.category_name,
                        "count": int(advert_obj.count()) - i,
                    }
                    advert_count = advert_count + int(advert_obj.count()) - i
                    subcat_list.append(sub_cat_data)
                cat_obj_data = {
                    "category_id": str(cat_obj.category_id),
                    "category_name": cat_obj.category_name,
                    "category_img": "",
                    "total_adverts_count": advert_count,
                    "total_likes": like_count,
                    "favorite": "0",
                    "subcategories": subcat_list,
                    "category_color": color
                }
                category_list.append(cat_obj_data)
        data = {'success': 'true', 'message': '', 'category_list': category_list, 'level': level}
    except Exception, ke:
        print ke
        data = {'success': 'false', 'message': 'Something went wrong', 'category_list': [], 'level': ''}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def get_advert_list(request):
    json_obj = json.loads(request.body)
    category_id = json_obj['category_id']
    city_id = json_obj['city_id']
    user_id = json_obj['user_id']
    level = json_obj['level']
    advert_list = []
    consumer_latitude = json_obj['sort_parameter']['consumer_latitude']
    consumer_longitude = json_obj['sort_parameter']['consumer_longitude']
    sort_by = json_obj['sort_parameter']['sort_by']
    rating_range = json_obj['filter_parameter']['rating_range']
    radius = json_obj['filter_parameter']['radius']
    try:
        if level == '1':
            advert_map_obj = Advert.objects.filter(category_level_1=category_id, status='1')

        if level == '2':
            advert_map_obj = Advert.objects.filter(category_level_2=CategoryLevel2.objects.get(category_id=category_id),
                                                   status='1')
            print advert_map_obj
        if level == '3':
            advert_map_obj = Advert.objects.filter(category_level_3=category_id, status='1')
        if level == '4':
            advert_map_obj = Advert.objects.filter(category_level_4=category_id, status='1')
        if level == '5':
            advert_map_obj = Advert.objects.filter(category_level_5=category_id, status='1')
        if level == '0':
            advert_map_obj = Advert.objects.filter(category_id=category_id, status='1')

        if radius:
            if int(radius) < 15:
                lon_max, lon_min, lat_max, lat_min = bounding_box(
                    float(consumer_latitude),
                    float(consumer_longitude),
                    int(radius)
                )
                advert_map_obj = advert_map_obj.filter(
                    latitude__range=[lat_min, lat_max],
                    longitude__range=[lon_min, lon_max],
                    status='1'
                )
                print advert_map_obj

        sequence_advert_list = []
        other_advert_list = []

        for advert in advert_map_obj:
            advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=advert.advert_id)
            premium_obj = PremiumService.objects.filter(business_id=advert_sub_obj.business_id.business_id,
                                                        category_id=category_id)
            if premium_obj:
                for premium in premium_obj:
                    if premium.premium_service_name == "No.1 Listing":
                        sequence_advert_list.append(advert)
                        break
                    elif premium.premium_service_name == "No.2 Listing":
                        sequence_advert_list.append(advert)
                        break
                    elif premium.premium_service_name == "No.3 Listing":
                        sequence_advert_list.append(advert)
                        break
                    elif premium.premium_service_name == "Top Advert":
                        other_advert_list.append(advert)
                        break
                    elif premium.premium_service_name == "Advert Slider":
                        other_advert_list.append(advert)
                        break
            else:
                other_advert_list.append(advert)

        advert_list1 = advert_premium_list(sequence_advert_list, city_id, category_id, user_id, level, consumer_latitude, consumer_longitude)
        advert_list2 = advert_sorted_list(other_advert_list, city_id, category_id, user_id, level, consumer_latitude, consumer_longitude)
        
        abc=advert_list1
        advert_list1.sort(key=operator.itemgetter('advert_sequence'))

        for dic in advert_list2:
            print dic['advert_name']

        advert_list2.sort(key=operator.itemgetter("advert_name"))
        

        if sort_by == "location":
            advert_list2.sort(key=operator.itemgetter('distance'))
            
        advert_list.extend(advert_list1)
        advert_list.extend(advert_list2)

        if radius:
            if int(radius) < 15:
                advert_list = [d for d in advert_list if d['distance'] < int(radius)]
            else:
                advert_list = [d for d in advert_list if d['distance'] > 10]

        top_advert_list = [d for d in advert_list if d['ratings'] >= 4.5]
        top_count = len(top_advert_list)
        good_advert_list = [d for d in advert_list if d['ratings'] >= 3.0 and d['ratings'] < 4.5]
        good_count = len(good_advert_list)
        avg_advert_list = [d for d in advert_list if d['ratings'] >= 1.5 and d['ratings'] < 3.0]
        avg_count = len(avg_advert_list)
        poor_advert_list = [d for d in advert_list if d['ratings'] > 0 and d['ratings'] < 1.5]
        poor_count = len(poor_advert_list)
        nry_advert_list = [d for d in advert_list if d['ratings'] == 0]
        nry_count = len(nry_advert_list)

        if rating_range:
            new_list = []
            for ranges in rating_range:
                if ranges == "Top":
                    new_list.extend(top_advert_list)
                if ranges == "Good":
                    new_list.extend(good_advert_list)
                if ranges == "Average":
                    new_list.extend(avg_advert_list)
                if ranges == "Poor":
                    new_list.extend(poor_advert_list)
                if ranges == "Not Rated Yet":
                    new_list.extend(nry_advert_list)
            new_list.sort(key=operator.itemgetter("ratings"))
            advert_list = new_list

        data = {
            'success': 'true', 
            'message': '', 
            'advert_list': advert_list, 
            'category_id': category_id,
            'top_count':str(top_count),
            'good_count':str(good_count),
            'avg_count':str(avg_count),
            'poor_count':str(poor_count),
            'nry_count':str(nry_count),
            }
    except Exception, ke:
        print ke
        data = {'success': 'false', 'message': 'Something went wrong', 'advert_list': [], 'category_id': category_id}
    return HttpResponse(json.dumps(data), content_type='application/json')

def advert_premium_list(advert_map_obj, city_id, category_id, user_id, level,consumer_latitude,consumer_longitude):
    advert_list = []
    for advert_map in advert_map_obj:
        if advert_map.city_place_id:
            phone_list = []
            email_list = []
            advert_id = str(advert_map.advert_id)
            pre_date = datetime.now().strftime("%d/%m/%Y")
            pre_date = datetime.strptime(pre_date, "%d/%m/%Y")
            advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)
            advert_sequence = ''
            premium_service_name_list = ["Advert Slider","Top Advert"]
            premium_obj = PremiumService.objects.filter(business_id=advert_sub_obj.business_id.business_id,
                                                        category_id=category_id).exclude(premium_service_name__in = premium_service_name_list)
            if premium_obj:
                for premium in premium_obj:
                    if premium.premium_service_name == "No.1 Listing":
                        advert_sequence = 1
                    if premium.premium_service_name == "No.2 Listing":
                        advert_sequence = 2
                    if premium.premium_service_name == "No.3 Listing":
                        advert_sequence = 3

            advert_data = get_advert_data(advert_sub_obj, advert_sequence, pre_date, advert_id, user_id, level,
                                          consumer_latitude, consumer_longitude)
            if advert_data:
                advert_list.append(advert_data)
    return advert_list

def advert_sorted_list(advert_map_obj, city_id, category_id, user_id, level,consumer_latitude,consumer_longitude):
    advert_list = []
    for advert_map in advert_map_obj:
        if advert_map.city_place_id:
            phone_list = []
            email_list = []
            advert_id = str(advert_map.advert_id)
            pre_date = datetime.now().strftime("%d/%m/%Y")
            pre_date = datetime.strptime(pre_date, "%d/%m/%Y")
            advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)
            advert_sequence = 0
            advert_data = get_advert_data(advert_sub_obj,advert_sequence,pre_date,advert_id,user_id, level,consumer_latitude,consumer_longitude)
            if advert_data:
                advert_list.append(advert_data)
    return advert_list

def get_advert_data(advert_sub_obj,advert_sequence,pre_date,advert_id,user_id, level,consumer_latitude,consumer_longitude):
    phone_list = []
    email_list = []
    advert_data = ''
    end_date = advert_sub_obj.business_id.end_date
    start_date = datetime.strptime(advert_sub_obj.business_id.start_date, "%d/%m/%Y")
    if start_date <= pre_date:
        end_date = datetime.strptime(end_date, "%d/%m/%Y")
        date_gap = end_date - pre_date
        print pre_date,end_date,date_gap
        if int(date_gap.days) >= 0:
            advert_obj = Advert.objects.get(advert_id=advert_id)
            advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)
            start_date = advert_sub_obj.business_id.start_date
            end_date = advert_sub_obj.business_id.end_date
            start_date = datetime.strptime(start_date, "%d/%m/%Y")
            end_date = datetime.strptime(end_date, "%d/%m/%Y")
            address = ''
            if advert_obj.area:
                address = advert_obj.area
            if advert_obj.city_place_id:
                address = address + ' ' + advert_obj.city_place_id.city_id.city_name
            phone_list.append(advert_obj.contact_no)
            email_list.append(advert_obj.email_primary)
            if advert_obj.email_secondary:
                email_list.append(advert_obj.email_secondary)
            if advert_obj.display_image:
                image_url = advert_obj.display_image.url
            else:
                image_url = ''
            try:
                advert_like_obj = AdvertLike.objects.get(advert_id=advert_id, user_id=str(user_id))
                is_like = "true"
            except Exception:
                is_like = "false"
            try:
                advert_like_obj = AdvertFavourite.objects.get(advert_id=advert_id,
                                                              user_id=str(user_id))
                is_favourite = "true"
            except Exception:
                is_favourite = "false"
            
            rating_count = 0
            review_obj = AdvertReview.objects.filter(advert_id=advert_id)
            ratings_total = 0
            rating_count = 0
            for review in review_obj:
                if float(review.ratings) > 0:
                    ratings_total = ratings_total + float(review.ratings)
                    rating_count = rating_count + 1
            if rating_count > 0:
                ratings = round(float(ratings_total) / rating_count,1)
            else:
                ratings = 0.0

            if consumer_latitude:
                newport_ri = (consumer_latitude, consumer_longitude)
                cleveland_oh = (advert_obj.latitude, advert_obj.longitude)
                distance = round(float(vincenty(newport_ri, cleveland_oh).kilometers), 2)
            else:
                distance = 0.0
            time_list = []
            hours_obj = WorkingHours.objects.filter(advert_id=advert_id)
            for hours in hours_obj:
                timing = hours.day + ', ' + hours.start_time.lower() + ' to ' + hours.end_time.lower()
                time_list.append(timing)
            advert_address = advert_obj.address_line_1
            if advert_obj.address_line_2:
                advert_address = address + ', ' + advert_obj.address_line_2
            if advert_obj.area:
                advert_address = address + ', ' + advert_obj.area
                landmark = advert_obj.area
            if advert_obj.city_place_id:
                advert_address = address + ', ' + advert_obj.city_place_id.city_id.city_name
                landmark = landmark + ', ' + advert_obj.city_place_id.city_id.city_name
            if advert_obj.state_id:
                advert_address = address + ', ' + advert_obj.state_id.state_name
            if advert_obj.pincode_id:
                advert_address = address + '-' + advert_obj.pincode_id.pincode
            if advert_obj.product_description:
                product_description = advert_obj.product_description
            else:
                product_description = ''
            try:
                coupon_obj = CouponCode.objects.get(advert_id=advert_id, user_id=user_id)
                coupon_flag = 'true'
            except Exception, ke:
                coupon_flag = 'false'

            if advert_obj.discount_description:
                start_date = start_date.strftime("%d %b %Y")
                end_date = end_date.strftime("%d %b %Y")
            else:
                start_date = ''
                end_date = ''

            discount_start_date = ''
            discount_end_date = ''
            if advert_obj.discount_description:
                discount_description = advert_obj.discount_description
                if advert_obj.discount_start_date:
                    discount_start_date = datetime.strptime(advert_obj.discount_start_date, "%d/%m/%Y")
                    discount_start_date = discount_start_date.strftime("%d %b %Y")
                if advert_obj.discount_end_date:
                    discount_end_date = datetime.strptime(advert_obj.discount_end_date, "%d/%m/%Y")
                    discount_end_date = discount_end_date.strftime("%d %b %Y")
            else:
                discount_description = ''

            advert_data = {
                "advert_id": str(advert_obj.advert_id),
                "advert_img": image_url,
                "name": advert_obj.advert_name.strip(),
                "advert_name": str(advert_obj.advert_name.strip().lower()),
                "location": address,
                "offer_start_date": start_date,
                "offer_end_date": end_date,
                "likes": str(AdvertLike.objects.filter(advert_id=advert_id).count()),
                "is_like": is_like,
                "is_favourite": is_favourite,
                "views": str(AdvertView.objects.filter(advert_id=advert_id).count()),
                "reviews": str(review_obj.count()),
                "phone": phone_list,
                "email": email_list,
                "ratings": ratings,
                "level": level,
                "advert_sequence": advert_sequence,
                "distance": distance,
                "advert_address": advert_address,
                "product_description": product_description,
                "coupon_flag": coupon_flag,
                "opening_closing_time": time_list,
                "category_color": str(advert_obj.category_id.category_color),
                "category_name": advert_obj.category_id.category_name,
                "discount_end_date":discount_end_date,
                "discount_start_date":discount_start_date
            }
            #print "=============11==============",advert_data['name']
    return advert_data

@csrf_exempt
def get_advert_details(request):
    json_obj = json.loads(request.body)
    advert_id = json_obj['advert_id']
    user_id = json_obj['user_id']
    category_id = json_obj['category_id']
    level = json_obj['level']
    advert_list = []
    try:
        mobile_list = []
        landline_list = []
        email_list = []
        image_list = []
        video_list = []
        time_list = []
        advert_id = str(advert_id)
        advert_obj = Advert.objects.get(advert_id=advert_id)

        if user_id:
            try:
                advet_view_obj = AdvertView.objects.get(advert_id=advert_id, user_id=user_id)
            except:
                advet_view_obj = AdvertView()
                advet_view_obj.advert_id = advert_obj
                advet_view_obj.user_id = ConsumerProfile.objects.get(consumer_id=user_id)
                advet_view_obj.creation_date = datetime.now()
                advet_view_obj.save()

        try:
            coupon_obj = CouponCode.objects.get(advert_id=advert_id, user_id=json_obj['user_id'])
            coupon_flag = 'true'
        except Exception, ke:
            coupon_flag = 'false'

        try:
            advert_like_obj = AdvertLike.objects.get(advert_id=advert_id, user_id=str(user_id))
            is_like = "true"
        except Exception:
            is_like = "false"

        try:
            advert_like_obj = AdvertFavourite.objects.get(advert_id=advert_id, user_id=str(user_id))
            is_favourite = "true"
        except Exception:
            is_favourite = "false"

        advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)
        start_date = advert_sub_obj.business_id.start_date
        end_date = advert_sub_obj.business_id.end_date
        start_date = datetime.strptime(start_date, "%d/%m/%Y")
        end_date = datetime.strptime(end_date, "%d/%m/%Y")
        landmark = ''
        address_landmark = ''
        address = advert_obj.address_line_1
        if advert_obj.address_line_2:
            address = address + ', ' + advert_obj.address_line_2
        if advert_obj.area:
            address = address + ', ' + advert_obj.area
            landmark = advert_obj.area
        if advert_obj.landmark:
            #address = address + ', ' + advert_obj.landmark
            address_landmark = advert_obj.landmark
        if advert_obj.city_place_id:
            address = address + ', ' + advert_obj.city_place_id.city_id.city_name
            landmark = landmark + ' ' + advert_obj.city_place_id.city_id.city_name
        if advert_obj.state_id:
            address = address + ', ' + advert_obj.state_id.state_name
        if advert_obj.pincode_id:
            address = address + '-' + advert_obj.pincode_id.pincode

        phone_obj = PhoneNo.objects.filter(advert_id=advert_id)
        advert_img_obj = AdvertImage.objects.filter(advert_id=advert_id)
        advert_video_obj = Advert_Video.objects.filter(advert_id=advert_id)
        if advert_obj.display_image:
            image_list.append(advert_obj.display_image.url)
        for advert_img in advert_img_obj:
            image_url = advert_img.advert_image.url
            image_list.append(image_url)

        for advert_video in advert_video_obj:
            video_url = advert_video.advert_video_name.url
            video_list.append(video_url)

        for phone in phone_obj:
            phone_no = phone.phone_no
            phone_name = phone.phone_category_id.phone_category_name
            if phone_name == 'Mobile':
                mobile_list.append(phone_no)
            else:
                landline_list.append(phone_no)
        mobile_list.append(advert_obj.contact_no)
        email_list.append(advert_obj.email_primary)
        if advert_obj.email_secondary:
            email_list.append(advert_obj.email_secondary)

        if advert_obj.display_image:
            image_url = advert_obj.display_image.url
        else:
            image_url = ''

        if advert_obj.any_other_details:
            other_details = advert_obj.any_other_details
        else:
            other_details = ''

        if advert_obj.product_description:
            product_description = advert_obj.product_description
        else:
            product_description = ''

        discount_start_date = ''
        discount_end_date = ''
        if advert_obj.discount_description:
            discount_description = advert_obj.discount_description
            if advert_obj.discount_start_date:
                discount_start_date = datetime.strptime(advert_obj.discount_start_date, "%d/%m/%Y")
                discount_start_date = discount_start_date.strftime("%d %b %Y")
            if advert_obj.discount_end_date:
                discount_end_date = datetime.strptime(advert_obj.discount_end_date, "%d/%m/%Y")
                discount_end_date = discount_end_date.strftime("%d %b %Y")
        else:
            discount_description = ''     

        hours_obj = WorkingHours.objects.filter(advert_id=advert_id)
        for hours in hours_obj:
            if hours.day == "All":
                hours_day = "All Days"
            else:
                hours_day = hours.day
            timing = hours_day + ', ' + hours.start_time.lower() + ' to ' + hours.end_time.lower()
            time_list.append(timing)

        advert_like_obj = AdvertLike.objects.filter(advert_id=advert_id)

        like_count = 0
        for advert_like in advert_like_obj:
            like_count = like_count + 1

        if advert_obj.speciality:
            speciality = advert_obj.speciality
        else:
            speciality = ''

        if advert_obj.short_description:
            short_description = advert_obj.short_description
        else:
            short_description = ''

        if json_obj['consumer_latitude']:
            newport_ri = (json_obj['consumer_latitude'], json_obj['consumer_longitude'])
            cleveland_oh = (advert_obj.latitude, advert_obj.longitude)
            distance = round(float(vincenty(newport_ri, cleveland_oh).kilometers),2)
        else:
            distance = ''

        review_list = []
        review_obj = AdvertReview.objects.filter(advert_id=advert_id)
        ratings_total = 0
        rating_count = 0
        for review in review_obj:
            if review.user_id.consumer_profile_pic:
                consumer_img = review.user_id.consumer_profile_pic.url
            else:
                consumer_img = "/static/assets/layouts/layout2/img/City_Hoopla_Logo.png"
            review_data = {
                "reviewer_name": review.user_id.consumer_full_name,
                "reviewer_image": consumer_img,
                "review_date": review.creation_date.strftime("%d %b %Y"),
                "review": review.review,
                "review_rating": str(review.ratings)
            }
            review_list.append(review_data)
            if float(review.ratings) > 0:
                rating_count = rating_count + 1
                ratings_total = ratings_total + float(review.ratings)
        if rating_count > 0:
            ratings = round(float(ratings_total) / rating_count,1)
        else:
            ratings = "0.0"

        amenity_list = []
        try:
            aminity_obj = Amenities.objects.filter(advert_id = advert_id)
            for aminity in aminity_obj:
                amenity_list.append(aminity.categorywise_amenity_id.amenity.strip())
        except:
            pass

        other_amenity = ''
        if advert_obj.other_amenity:
            other_amenity = advert_obj.other_amenity

        if advert_obj.date_of_delivery:
            try:
                date_of_delivery = datetime.strptime(advert_obj.date_of_delivery,'%d/%m/%Y')
            except:
                date_of_delivery = datetime.strptime(advert_obj.date_of_delivery,'%m/%d/%Y')
            date_of_delivery = date_of_delivery.strftime("%d %b %Y")
        else:
            date_of_delivery = ''

        any_other_details = ''
        if advert_obj.any_other_details:
            any_other_details = advert_obj.any_other_details

        if advert_obj.website:
            website = advert_obj.website
        else:
            website = ''

        advert_data = {
            "advert_id": str(advert_obj.advert_id),
            "advert_img": image_url,
            "name": advert_obj.advert_name,
            "location": address,
            "offer_start_date": start_date.strftime("%d %b %Y"),
            "offer_end_date": end_date.strftime("%d %b %Y"),
            "likes": str(like_count),
            "is_like": is_like,
            "is_favourite": is_favourite,
            "views": str(AdvertView.objects.filter(advert_id=advert_id).count()),
            "reviews": str(review_obj.count()),
            "ratings": str(ratings),
            "email": email_list,
            "discount_description": discount_description,
            "product_description": product_description,
            "other_details": other_details,
            "short_description": short_description,
            "latitude": advert_obj.latitude,
            "longitude": advert_obj.longitude,
            "opening_closing_time": time_list,
            "phone_no": mobile_list,
            "image_list": image_list,
            "video_list": video_list,
            "landmark": landmark,
            "address_landmark" : address_landmark,
            "coupon_flag": coupon_flag,
            "review_list": review_list,
            "level": level,
            'other_amenity':other_amenity,
            "distance":distance,
            "amenity_list":amenity_list,
            'speciality':speciality,
            'property_market_rate':advert_obj.property_market_rate,
            'possesion_status':advert_obj.possesion_status,
            'other_projects':advert_obj.other_projects,
            'date_of_delivery':date_of_delivery,
            'any_other_details':any_other_details,
            'happy_hour_offer':advert_obj.happy_hour_offer,
            'course_duration':advert_obj.course_duration,
            'affilated_to':advert_obj.affilated_to,
            'facility':advert_obj.facility,
            'distance_from_railway_station':advert_obj.distance_frm_railway_station,
            'distance_from_airport':advert_obj.distance_frm_railway_airport,
            "category_color":str(advert_obj.category_id.category_color),
            "category_name":advert_obj.category_id.category_name,
            "website":website,
            "discount_end_date":discount_end_date,
            "discount_start_date":discount_start_date
        }
        advert_list.append(advert_data)
        product_list = []
        product_obj = Product.objects.filter(advert_id = advert_id)
        if product_obj:
            for product in product_obj:
                if product.product_name:
                    product_data = {
                        'product_name':product.product_name,
                        'product_price':product.product_price
                    }
                    product_list.append(product_data)


        attraction_list = []
        attraction_obj = NearByAttraction.objects.filter(advert_id = advert_id)
        if attraction_obj:
            for attraction in attraction_obj:
                if attraction.attraction:
                    attraction_data = {
                        'name':attraction.attraction
                    }
                    attraction_list.append(attraction_data)
        shopping_list = []
        #NearestShopping
        shopping_obj = NearestShopping.objects.filter(advert_id = advert_id)
        if shopping_obj:
            for shopping in shopping_obj:
                if shopping.shop_name:
                    shopping_data = {
                        'name':shopping.shop_name,
                        'distance':shopping.distance_frm_property,
                    }
                    shopping_list.append(shopping_data)
        school_list = []
        school_obj = NearestSchool.objects.filter(advert_id = advert_id)
        if school_obj:
            for school in school_obj:
                if school.school_name:
                    school_data = {
                        'name':school.school_name,
                        'distance':school.distance_frm_property,
                    }
                    school_list.append(school_data)
        hospital_list = []
        hospital_obj = NearestHospital.objects.filter(advert_id = advert_id)
        if hospital_obj:
            for hospital in hospital_obj:
                if hospital.hospital_name:
                    hospital_data = {
                        'name':hospital.hospital_name,
                        'distance':hospital.distance_frm_property,
                    }
                    hospital_list.append(hospital_data)

        data = {
                    'success': 'true', 'message': '', 
                    'advert_list': advert_list, 
                    'product_list':product_list,
                    'category_id': category_id,
                    'level': level,
                    'hospital_list':hospital_list,
                    'school_list':school_list,
                    'shopping_list':shopping_list,
                    'attraction_list':attraction_list
                }
    except Exception, ke:
        print ke
        data = {
                    'success': 'false', 'message': 'Something went wrong', 
                    'advert_list': [], 
                    'product_list':[],
                    'category_id': [],
                    'level': [],
                    'hospital_list':[],
                    'school_list':[],
                    'shopping_list':[],
                    'attraction_list':[]
                }
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def get_coupon_code(request):
    json_obj = json.loads(request.body)
    advert_id = json_obj['advert_id']
    user_id = json_obj['user_id']
    try:
        advert_id = str(advert_id)
        advert_obj = Advert.objects.get(advert_id=advert_id)
        advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)
        category_name = advert_sub_obj.business_id.category.category_name
        city_name = advert_obj.city_place_id.city_id.city_name
        random_no = u''
        random_no = random_no.join(random.choice('0123456789') for i in range(4))
        coupon_code = 'CH' + city_name[:3].upper() + category_name[:2].upper() + str(random_no)

        coupon_obj = CouponCode.objects.create()
        coupon_obj.coupon_code = coupon_code
        coupon_obj.user_id = ConsumerProfile.objects.get(consumer_id=json_obj['user_id'])
        coupon_obj.advert_id = advert_obj
        coupon_obj.creation_date = datetime.now()
        coupon_obj.save()

        data = {'success': 'true', 'message': '', 'coupon_code': coupon_code}
    except Exception, ke:
        print ke
        data = {'success': 'false', 'message': '', 'coupon_code': ''}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def like_advert(request):
    json_obj = json.loads(request.body)
    try:
        if json_obj['like_status'] == 'true':
            advert_like_obj = AdvertLike.objects.create()
            advert_like_obj.user_id = ConsumerProfile.objects.get(consumer_id=json_obj['user_id'])
            advert_like_obj.advert_id = Advert.objects.get(advert_id=json_obj['advert_id'])
            advert_like_obj.creation_date = datetime.now()
            advert_like_obj.save()
        else:
            advert_like_obj = AdvertLike.objects.get(advert_id=json_obj['advert_id'], user_id=json_obj['user_id'])
            advert_like_obj.delete()
        data = {'success': 'true', 'message': ''}
    except Exception, ke:
        print ke
        data = {'success': 'false', 'message': 'Oops! Something went wrong'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def favourite_advert(request):
    json_obj = json.loads(request.body)
    try:
        advert_fav_obj = AdvertFavourite.objects.filter(advert_id=json_obj['advert_id'], user_id=json_obj['user_id'])
        advert_fav_obj.delete()
        if json_obj['favourite_status'] == 'true':
            advert_fav_obj = AdvertFavourite.objects.create()
            advert_fav_obj.user_id = ConsumerProfile.objects.get(consumer_id=json_obj['user_id'])
            advert_fav_obj.advert_id = Advert.objects.get(advert_id=json_obj['advert_id'])
            advert_fav_obj.creation_date = datetime.now()
            advert_fav_obj.save()
            
        data = {'success': 'true', 'message': ''}
    except Exception, ke:
        print ke
        data = {'success': 'false', 'message': 'Oops! Something went wrong'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def get_discount_details(request):
    json_obj = json.loads(request.body)
    user_id = json_obj['user_id']
    discount_detail = []
    try:
        coupon_obj = CouponCode.objects.filter(user_id=user_id)
        for coupons in coupon_obj:
            advert_obj = Advert.objects.get(advert_id=str(coupons.advert_id))
            advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=str(coupons.advert_id))
            start_date = advert_sub_obj.business_id.start_date
            end_date = advert_sub_obj.business_id.end_date
            start_date = datetime.strptime(start_date, "%d/%m/%Y")
            end_date = datetime.strptime(end_date, "%d/%m/%Y")
            pre_date = datetime.now().strftime("%d/%m/%Y")
            pre_date = datetime.strptime(pre_date, "%d/%m/%Y")

            coupon_code = coupons.coupon_code
            discount_description = ''

            date_gap = end_date - pre_date
            if int(date_gap.days) >= 0:
                status = 'Active'
            else:
                status = 'Inactive'

            if advert_obj.discount_description:
                start_date = start_date.strftime("%d %b %Y")
                end_date = end_date.strftime("%d %b %Y")
                discount_description = advert_obj.discount_description
            else:
                start_date = ''
                end_date = ''

            discount_start_date = ''
            discount_end_date = ''
            if advert_obj.discount_description:
                discount_description = advert_obj.discount_description
                if advert_obj.discount_start_date:
                    discount_start_date = datetime.strptime(advert_obj.discount_start_date, "%d/%m/%Y")
                    discount_start_date = discount_start_date.strftime("%d %b %Y")
                if advert_obj.discount_end_date:
                    discount_end_date = datetime.strptime(advert_obj.discount_end_date, "%d/%m/%Y")
                    discount_end_date = discount_end_date.strftime("%d %b %Y")
            else:
                discount_description = ''

            address = ''
            if advert_obj.area:
                address = advert_obj.area
            if advert_obj.city_place_id:
                address = address + ' ' + advert_obj.city_place_id.city_id.city_name

            try:
                advert_like_obj = AdvertFavourite.objects.get(advert_id=str(coupons.advert_id), user_id=str(user_id))
                is_favourite = "true"
            except Exception:
                is_favourite = "false"

            try:
                advert_like_obj = AdvertLike.objects.get(advert_id=str(coupons.advert_id), user_id=str(user_id))
                is_like = "true"
            except Exception:
                is_like = "false"

            advert_like_obj = AdvertLike.objects.filter(advert_id=str(coupons.advert_id))

            like_count = 0
            for advert_like in advert_like_obj:
                like_count = like_count + 1

            if advert_obj.advert_views:
                advert_views = str(advert_obj.advert_views)
            else:
                advert_views = '0'

            review_obj = AdvertReview.objects.filter(advert_id=str(coupons.advert_id))
            ratings_total = 0
            rating_count = 0
            for review in review_obj:
                if float(review.ratings) > 0:
                    ratings_total = ratings_total + float(review.ratings)
                    rating_count = rating_count + 1
            if rating_count > 0:
                ratings = round(float(ratings_total) / rating_count,1)
            else:
                ratings = "0.0"

            phone_list = []
            phone_list.append(advert_obj.contact_no)
            email_list = []
            email_list.append(advert_obj.email_primary)

            if json_obj['consumer_latitude']:
                newport_ri = (json_obj['consumer_latitude'], json_obj['consumer_longitude'])
                cleveland_oh = (advert_obj.latitude, advert_obj.longitude)
                distance = round(float(vincenty(newport_ri, cleveland_oh).kilometers), 2)
            else:
                distance = ''

            advert_data = {
                "advert_id": str(advert_obj.advert_id),
                "name": advert_obj.advert_name,
                "location": address,
                "offer_start_date": start_date,
                "offer_end_date": end_date,
                "likes": str(like_count),
                "views": str(AdvertView.objects.filter(advert_id=str(coupons.advert_id)).count()),
                "reviews": str(review_obj.count()),
                "ratings": str(ratings),
                "is_favourite": is_favourite,
                "is_like": is_like,
                "coupon_avail_date": coupons.creation_date.strftime("%d %b %Y"),
                "status": status,
                'phone_list':phone_list,
                'email_list':email_list,
                'distance':distance,
                "category_color":str(advert_obj.category_id.category_color),
                "category_name":advert_obj.category_id.category_name,
                "coupon_code":coupon_code,
                "discount_description":discount_description,
                "discount_end_date":discount_end_date,
                "discount_start_date":discount_start_date
            }
            discount_detail.append(advert_data)
        data = {'success': 'true', 'message': '', 'count': len(discount_detail), 'discount_detail': discount_detail}
    except Exception, ke:
        print ke
        data = {'success': 'false', 'message': 'Something went wrong', 'count': '', 'discount_detail': []}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def get_favourite_details(request):
    json_obj = json.loads(request.body)
    user_id = json_obj['user_id']
    discount_detail = []
    try:
        advert_fav_obj = AdvertFavourite.objects.filter(user_id=user_id)
        for advert_fav in advert_fav_obj:
            advert_obj = Advert.objects.get(advert_id=str(advert_fav.advert_id))
            advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=str(advert_fav.advert_id))
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
            address = ''
            if advert_obj.area:
                address = advert_obj.area
            if advert_obj.city_place_id:
                address = address + ' ' + advert_obj.city_place_id.city_id.city_name

            try:
                advert_like_obj = AdvertLike.objects.get(advert_id=str(advert_fav.advert_id), user_id=str(user_id))
                is_like = "true"
            except Exception:
                is_like = "false"

            advert_like_obj = AdvertLike.objects.filter(advert_id=str(advert_fav.advert_id))

            if advert_obj.display_image:
                image_path = advert_obj.display_image.url
            else:
                image_path = ''
            if advert_obj.advert_views:
                views = advert_obj.advert_views
            else:
                views = 0

            review_obj = AdvertReview.objects.filter(advert_id=str(advert_fav.advert_id))
            ratings_total = 0
            rating_count = 0
            for review in review_obj:
                if float(review.ratings) > 0:
                    ratings_total = ratings_total + float(review.ratings)
                    rating_count = rating_count + 1
            if rating_count > 0:
                ratings = round(float(ratings_total) / rating_count,1)
            else:
                ratings = "0.0"

            phone_list = []
            phone_list.append(advert_obj.contact_no)
            email_list = []
            email_list.append(advert_obj.email_primary)

            if advert_obj.category_id:
                category_id = str(advert_obj.category_id.category_id)
                level = '0'
            if advert_obj.category_level_1:
                category_id = str(advert_obj.category_level_1.category_id)
                level = '1'
            if advert_obj.category_level_2:
                category_id = str(advert_obj.category_level_2.category_id)
                level = '2'
            if advert_obj.category_level_3:
                category_id = str(advert_obj.category_level_3.category_id)
                level = '3'
            if advert_obj.category_level_4:
                category_id = str(advert_obj.category_level_4.category_id)
                level = '4'
            if advert_obj.category_level_5:
                category_id = str(advert_obj.category_level_5.category_id)
                level = '5'

            time_list = []

            hours_obj = WorkingHours.objects.filter(advert_id=str(advert_fav.advert_id))
            for hours in hours_obj:
                timing = hours.day + ', ' + hours.start_time.lower() + ' to ' + hours.end_time.lower()
                time_list.append(timing)

            advert_address = advert_obj.address_line_1
            if advert_obj.address_line_2:
                advert_address = address + ', ' + advert_obj.address_line_2
            if advert_obj.area:
                advert_address = address + ', ' + advert_obj.area
                landmark = advert_obj.area
            if advert_obj.city_place_id:
                advert_address = address + ', ' + advert_obj.city_place_id.city_id.city_name
                landmark = landmark + ', ' + advert_obj.city_place_id.city_id.city_name
            if advert_obj.state_id:
                advert_address = address + ', ' + advert_obj.state_id.state_name
            if advert_obj.pincode_id:
                advert_address = address + '-' + advert_obj.pincode_id.pincode

            if advert_obj.product_description:
                product_description = advert_obj.product_description
            else:
                product_description = ''

            try:
                coupon_obj = CouponCode.objects.get(advert_id=str(advert_fav.advert_id), user_id=user_id)
                coupon_flag = 'true'
            except Exception, ke:
                coupon_flag = 'false'

            if json_obj['consumer_latitude']:
                newport_ri = (json_obj['consumer_latitude'], json_obj['consumer_longitude'])
                cleveland_oh = (advert_obj.latitude, advert_obj.longitude)
                distance = round(float(vincenty(newport_ri, cleveland_oh).kilometers), 2)
            else:
                distance = ''

            if advert_obj.discount_description:
                start_date = start_date.strftime("%d %b %Y")
                end_date = end_date.strftime("%d %b %Y")
            else:
                start_date = ''
                end_date = ''

            discount_start_date = ''
            discount_end_date = ''
            if advert_obj.discount_description:
                discount_description = advert_obj.discount_description
                if advert_obj.discount_start_date:
                    discount_start_date = datetime.strptime(advert_obj.discount_start_date, "%d/%m/%Y")
                    discount_start_date = discount_start_date.strftime("%d %b %Y")
                if advert_obj.discount_end_date:
                    discount_end_date = datetime.strptime(advert_obj.discount_end_date, "%d/%m/%Y")
                    discount_end_date = discount_end_date.strftime("%d %b %Y")
            else:
                discount_description = ''

            advert_data = {
                "advert_id": str(advert_obj.advert_id),
                "name": advert_obj.advert_name,
                "category_id": str(advert_obj.category_id.category_id),
                "category_name": advert_obj.category_id.category_name,
                "advert_image": image_path,
                "location": address,
                "offer_start_date": start_date,
                "offer_end_date": end_date,
                "likes": str(advert_like_obj.count()),
                "views": str(AdvertView.objects.filter(advert_id=str(advert_fav.advert_id)).count()),
                "reviews": str(review_obj.count()),
                "ratings": str(ratings),
                "is_favourite": "true",
                "is_like": is_like,
                "phone": phone_list,
                "email": email_list,
                "level": level,
                "coupon_flag":coupon_flag,
                'distance':distance,
                'product_description':product_description,
                'advert_address':advert_address,
                "opening_closing_time": time_list,
                "category_color":str(advert_obj.category_id.category_color),
                "category_name":advert_obj.category_id.category_name,
                "discount_end_date":discount_end_date,
                "discount_start_date":discount_start_date
            }
            discount_detail.append(advert_data)
        data = {'success': 'true', 'message': '', 'count': len(discount_detail), 'favourite_detail': discount_detail}
    except Exception, ke:
        print ke
        data = {'success': 'false', 'count': '', 'message': 'Something went wrong', 'favourite_detail': []}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def user_advert_activity(request):
    json_obj = json.loads(request.body)
    try:

        if json_obj['activity_type'] == 'share':
            advert_activity_obj = AdvertShares.objects.create()
        if json_obj['activity_type'] == 'call':
            advert_activity_obj = AdvertCallsMade.objects.create()
        if json_obj['activity_type'] == 'callback':
            advert_activity_obj = AdvertCallbacks.objects.create()

        advert_activity_obj.user_id = ConsumerProfile.objects.get(consumer_id=json_obj['user_id'])
        advert_activity_obj.advert_id = Advert.objects.get(advert_id=json_obj['advert_id'])
        advert_activity_obj.creation_date = datetime.now()
        advert_activity_obj.save()

        data = {'success': 'true', 'message': ''}
    except Exception, ke:
        print ke
        data = {'success': 'false', 'message': 'Oops! Something went wrong'}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def get_active_discount_details(request):
    json_obj = json.loads(request.body)
    user_id = json_obj['user_id']
    discount_detail = []
    try:
        coupon_obj = CouponCode.objects.filter(user_id=user_id)
        for coupons in coupon_obj:
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
                address = ''
                if advert_obj.area:
                    address = advert_obj.area
                if advert_obj.city_place_id:
                    address = address + ' ' + advert_obj.city_place_id.city_id.city_name

                try:
                    advert_like_obj = AdvertFavourite.objects.get(advert_id=str(coupons.advert_id),
                                                                  user_id=str(user_id))
                    is_favourite = "true"
                except Exception:
                    is_favourite = "false"

                try:
                    advert_like_obj = AdvertLike.objects.get(advert_id=str(coupons.advert_id), user_id=str(user_id))
                    is_like = "true"
                except Exception:
                    is_like = "false"

                advert_like_obj = AdvertLike.objects.filter(advert_id=str(coupons.advert_id))

                like_count = 0
                for advert_like in advert_like_obj:
                    like_count = like_count + 1

                if advert_obj.advert_views:
                    advert_views = str(advert_obj.advert_views)
                else:
                    advert_views = '0'

                review_obj = AdvertReview.objects.filter(advert_id=str(coupons.advert_id))
                ratings_total = 0
                rating_count = 0
                for review in review_obj:
                    if float(review.ratings) > 0:
                        ratings_total = ratings_total + float(review.ratings)
                        rating_count = rating_count + 1
                if rating_count > 0:
                    ratings = round(float(ratings_total) / rating_count,1)
                else:
                    ratings = "0.0"

                phone_list = []
                phone_list.append(advert_obj.contact_no)
                email_list = []
                email_list.append(advert_obj.email_primary)

                if json_obj['consumer_latitude']:
                    newport_ri = (json_obj['consumer_latitude'], json_obj['consumer_longitude'])
                    cleveland_oh = (advert_obj.latitude, advert_obj.longitude)
                    distance = round(float(vincenty(newport_ri, cleveland_oh).kilometers), 2)
                else:
                    distance = ''

                coupon_code = coupons.coupon_code
                discount_description = ''

                if advert_obj.discount_description:
                    start_date = start_date.strftime("%d %b %Y")
                    end_date = end_date.strftime("%d %b %Y")
                    discount_description = advert_obj.discount_description
                else:
                    start_date = ''
                    end_date = ''

                discount_start_date = ''
                discount_end_date = ''
                if advert_obj.discount_description:
                    discount_description = advert_obj.discount_description
                    if advert_obj.discount_start_date:
                        discount_start_date = datetime.strptime(advert_obj.discount_start_date, "%d/%m/%Y")
                        discount_start_date = discount_start_date.strftime("%d %b %Y")
                    if advert_obj.discount_end_date:
                        discount_end_date = datetime.strptime(advert_obj.discount_end_date, "%d/%m/%Y")
                        discount_end_date = discount_end_date.strftime("%d %b %Y")
                else:
                    discount_description = ''

                advert_data = {
                    "advert_id": str(advert_obj.advert_id),
                    "name": advert_obj.advert_name,
                    "location": address,
                    "offer_start_date": start_date,
                    "offer_end_date": end_date,
                    "likes": str(like_count),
                    "views": str(AdvertView.objects.filter(advert_id=str(coupons.advert_id)).count()),
                    "reviews": str(review_obj.count()),
                    "ratings": str(ratings),
                    "is_like": is_like,
                    "is_favourite": is_favourite,
                    "coupon_avail_date": coupons.creation_date.strftime("%d %b %Y"),
                    "status": status,
                    'phone_list':phone_list,
                    'email_list':email_list,
                    'distance':distance,
                    "category_color":str(advert_obj.category_id.category_color),
                    "category_name":advert_obj.category_id.category_name,
                    "discount_description":discount_description,
                    "coupon_code":coupon_code,
                    "discount_end_date":discount_end_date,
                    "discount_start_date":discount_start_date
                }
                discount_detail.append(advert_data)
        data = {'success': 'true', 'message': '', 'count': len(discount_detail), 'discount_detail': discount_detail}
    except Exception, ke:
        print ke
        data = {'success': 'false', 'message': 'Something went wrong', 'count': '', 'discount_detail': []}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def edit_customer_profile(request):
    print "REQUEST", request.body
    try:
        json_obj = json.loads(request.body)
        print 'JSON OBJECT : ', json_obj
        if request.method == 'POST':
            customer_object = ConsumerProfile.objects.get(consumer_id=json_obj['user_id'])
            customer_object.consumer_full_name = json_obj['full_name']
            #customer_object.consumer_contact_no = json_obj['phone']
            customer_object.consumer_updated_by = json_obj['full_name']
            if json_obj['email_id']:
                customer_object.consumer_email_id = json_obj['email_id']
            customer_object.device_token = json_obj['device_token']
            customer_object.consumer_area = json_obj['consumer_area']
            customer_object.consumer_updated_date = datetime.now()
            customer_object.save()

            # try:
            #    filename = "IMG_%s_%s.png" % (customer_object.username, str(datetime.now()).replace('.', '_'))
            #    resource = urllib.urlopen(json_obj['user_profile_image'])

            #    customer_object.consumer_profile_pic = ContentFile(resource.read(), filename)  # assign image to model
            #    customer_object.save()
            # except:
            #    pass

            data = {'success': 'true', 'message': 'Profile Updated Successfully',
                    'user_info': get_profile_info(customer_object.consumer_id)}
        else:
            data = {'success': 'false', 'message': 'Profile Update Failed'}
    except ConsumerProfile.DoesNotExist, e:
        print e
        data = {'success': 'false', 'message': 'User does not exists'}
    except Exception, e:
        print e
        data = {'success': 'false', 'message': 'Invalid request'}
    return HttpResponse(json.dumps(data), content_type='application/json')


# save consumer feedback
@csrf_exempt
def consumer_feedback(request):
    try:
        json_obj = json.loads(request.body)
        print 'JSON OBJECT : ', json_obj
        if request.method == 'POST':
            user_id = json_obj['user_id']
            consumer_feedback = Consumer_Feedback(
                consumer_id=ConsumerProfile.objects.get(consumer_id=user_id),
                consumer_feedback=json_obj['feedback']
            );
            consumer_feedback.save()
            data = {'success': 'true', 'message': "Feedback Sent Successfully"}

    except Consumer_Feedback.DoesNotExist, e:
        data = {'success': 'false', 'message': "Feedback not Send"}
        print "failed to send mail", e
    except Exception, e:
        print e
        data = {'success': 'false', 'message': "Server Error, Please try again!"}
    return HttpResponse(json.dumps(data), content_type='application/json')


# update device_token
@csrf_exempt
def update_device_token(request):
    print "REQUEST", request.body
    try:
        ##        pdb.set_trace()
        json_obj = json.loads(request.body)

        if request.method == 'POST':
            customer_object = ConsumerProfile.objects.get(consumer_id=json_obj['user_id'])
            customer_object.device_token = json_obj['device_token']
            customer_object.save()
            data = {'success': 'true', 'message': 'Device Token Updated Successfully'}
    except ConsumerProfile.DoesNotExist, e:
        data = {'success': 'false', 'message': "Device token is not update"}
        print "Exception in Update Token", e
    except Exception, e:
        print e
        data = {'success': 'false', 'message': "Server Error, Please try again!"}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def update_profile_photo(request):
    try:
        json_obj = json.loads(request.body)
        if request.method == 'POST':
            try:
                customer_object = ConsumerProfile.objects.get(consumer_id=json_obj['user_id'])
                customer_object.consumer_profile_pic = save_image(
                    json_obj['user_profile_image'])
                customer_object.save()
            except:
                pass
            data = {'success': 'true', 'message': 'Profile Picture Updated Successfully',
                    'user_info': get_profile_info(customer_object.consumer_id)}
    except ConsumerProfile.DoesNotExist, e:
        data = {'success': 'false', 'message': "Profile Picture is not update"}
        print "Exception in Update Token", e
    except Exception, e:
        print e
        data = {'success': 'false', 'message': "Server Error, Please try again!"}
    return HttpResponse(json.dumps(data), content_type='application/json')


def save_image(imgdata):
    import os
    print "save_image"
    # pdb.set_trace()
    try:
        filename = "uploaded_image%s.png" % str(datetime.now()).replace('.', '_')
        decoded_image = imgdata.decode('base64')
        return ContentFile(decoded_image, filename)
    except Exception, e:
        print e
        data = {'data': None}
        return False


@csrf_exempt
def search_advert(request):
    try:
        json_obj = json.loads(request.body)
        search_keyword = json_obj['search_keyword']
        list = []
        advert_list = []

        supplier_obj = Supplier.objects.filter(business_name__icontains = search_keyword)
        for supplier in supplier_obj:
            advert_obj = Advert.objects.filter(supplier_id = str(supplier.supplier_id))
            list.extend(advert_obj)

        category_obj = Category.objects.filter(category_name__icontains = search_keyword)
        for category in category_obj:
            advert_obj = Advert.objects.filter(category_id=str(category.category_id))
            list.extend(advert_obj)

        category_obj_1 = CategoryLevel1.objects.filter(category_name__icontains=search_keyword)
        for category_1 in category_obj_1:
            advert_obj = Advert.objects.filter(category_level_1=str(category_1.category_id))
            list.extend(advert_obj)

        category_obj_2 = CategoryLevel2.objects.filter(category_name__icontains=search_keyword)
        for category_2 in category_obj_2:
            advert_obj = Advert.objects.filter(category_level_2=str(category_2.category_id))
            list.extend(advert_obj)

        category_obj_3 = CategoryLevel3.objects.filter(category_name__icontains=search_keyword)
        for category_3 in category_obj_3:
            advert_obj = Advert.objects.filter(category_level_3=str(category_3.category_id))
            list.extend(advert_obj)

        category_obj_4 = CategoryLevel4.objects.filter(category_name__icontains=search_keyword)
        for category_4 in category_obj_4:
            advert_obj = Advert.objects.filter(category_level_4=str(category_4.category_id))
            list.extend(advert_obj)

        category_obj_5 = CategoryLevel5.objects.filter(category_name__icontains=search_keyword)
        for category_5 in category_obj_5:
            advert_obj = Advert.objects.filter(category_level_5=str(category_5.category_id))
            list.extend(advert_obj)

        city_obj = City.objects.filter(city_name__icontains=search_keyword)
        for city in city_obj:
            try:
                city_place_obj = City_Place.objects.get(city_id = str(city.city_id))
                advert_obj = Advert.objects.filter(city_place_id=str(city_place_obj.city_place_id))
                list.extend(advert_obj)
            except:
                pass

        advert_obj = Advert.objects.filter(advert_name__icontains=search_keyword)
        list.extend(advert_obj)

        advert_obj = Advert.objects.filter(keywords__icontains=search_keyword)
        list.extend(advert_obj)

        advert_obj = Advert.objects.filter(area__icontains=search_keyword)
        list.extend(advert_obj)

        list = set(list)
        for advert in list:
            phone_list = []
            email_list = []
            advert_id = str(advert.advert_id)
            pre_date = datetime.now().strftime("%d/%m/%Y")
            pre_date = datetime.strptime(pre_date, "%d/%m/%Y")
            advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)
            end_date = advert_sub_obj.business_id.end_date
            start_date = datetime.strptime(advert_sub_obj.business_id.start_date, "%d/%m/%Y")
            if start_date <= pre_date:
                end_date = datetime.strptime(end_date, "%d/%m/%Y")
                date_gap = end_date - pre_date
                if int(date_gap.days) >= 0:
                    advert_obj = Advert.objects.get(advert_id=advert_id)
                    advert_data = {
                        "advert_id": str(advert_obj.advert_id),
                        "advert_name": str(advert_obj.advert_name),
                        "category_name": str(advert_obj.category_id.category_name)
                    }
                    advert_list.append(advert_data)

        data = {'success': 'true', 'advert_list': advert_list, 'count':str(len(advert_list))}
    except Exception, e:
        print e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')


def bounding_box(latitude, longitude, distance):
    lat_change = change_in_latitude(distance)
    lat_max = latitude + lat_change
    lat_min = latitude - lat_change
    lon_change = change_in_longitude(latitude, distance)
    lon_max = longitude + lon_change
    lon_min = longitude - lon_change
    return (lon_max, lon_min, lat_max, lat_min)


def change_in_latitude(distance):
    "Given a distance north, return the change in latitude."
    return (distance / earth_radius) * radians_to_degrees


def change_in_longitude(latitude, distance):
    r = earth_radius * math.cos(latitude * degrees_to_radians)
    return (distance / r) * radians_to_degrees


@csrf_exempt
def get_category(request):
    print "REQUEST", request.body
    try:
        cat_id_list = []
        json_obj = json.loads(request.body)
        cat_obj_list = CategoryCityMap.objects.filter(city_id=City.objects.get(city_id=json_obj['city_id']))
        for cat in cat_obj_list:
            cat_id_list.append(str(cat.category_id))
        if cat_id_list:
            category_obj_list = Category.objects.filter(category_id__in=cat_id_list)
            if category_obj_list:
                for category in category_obj_list:
                    category_id = str(category.category_id)
                    category_name = category.category_name
                    category_image = ''
                    category_advert = Advert.objects.filter(category_id=category)
                    category_advert_count = len(category_advert)
                    category_like = ''
                    category_favourite = ''
                    sub_category = Category.objects.filter(has_category=category)
                    if sub_category:
                        sub_category_list = []
                        for sub_cat in sub_category:
                            id = str(sub_cat.category_id)
                            name = sub_cat.category_name
                            count = ''
                            sub_category_list = {'id': id, 'name': name, 'count': count}

                    list = {'sub_category_list': sub_category_list, 'category_favourite': category_favourite,
                            'category_like': category_like, 'category_advert_count': category_advert_count,
                            'category_image': category_image, 'category_id': category_id,
                            'category_name': category_name}

        data = {'success': 'true', 'list': list}

    except Exception, e:
        print e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def user_logout(request):
    json_obj = json.loads(request.body)
    user_obj = ConsumerProfile.objects.get(consumer_id=json_obj['user_id'])
    user_obj.online = '0'
    user_obj.save()
    data = {'success': 'true'}
    return HttpResponse(json.dumps(data), content_type='application/json')


# Save Sell Ticket
@csrf_exempt
def save_sellticket(request):
    try:
        # pdb.set_trace()
        json_obj = json.loads(request.body)
        print 'JSON OBJECT : ', json_obj['start_date']

        user_id = json_obj['user_id']
        city_id = json_obj['city_id']
        sellticket_obj = SellTicket(
            user_id=ConsumerProfile.objects.get(consumer_id=user_id),
            event_name=json_obj['event_name'],
            event_venue=json_obj['event_venue'],
            start_date=json_obj['start_date'],
            start_time=json_obj['start_time'],
            select_activation_date=json_obj['select_activation_date'],
            other_comments=json_obj['other_comments'],
            contact_number=json_obj['contact_number'],
            sellticket_views = 0,
            city_id = City_Place.objects.get(city_place_id = city_id)
        )
        sellticket_obj.save()
        if json_obj['image_one']:
            sellticket_obj.image_one = save_image(json_obj['image_one'])
        if json_obj['image_two']:
            sellticket_obj.image_two = save_image(json_obj['image_two'])
        if json_obj['image_three']:
            sellticket_obj.image_three = save_image(json_obj['image_three'])
        if json_obj['image_four']:
            sellticket_obj.image_four = save_image(json_obj['image_four'])
        sellticket_obj.save()

        for i in range(len(json_obj['ticket_details'])):
            sell_datail_obj = SellTicketDetails()
            sell_datail_obj.sellticket_id = sellticket_obj
            sell_datail_obj.ticket_class = json_obj['ticket_details'][i]['ticket_class']
            sell_datail_obj.no_of_tickets = json_obj['ticket_details'][i]['no_of_tickets']
            sell_datail_obj.original_price = json_obj['ticket_details'][i]['original_price']
            sell_datail_obj.asking_price = json_obj['ticket_details'][i]['asking_price']
            sell_datail_obj.created_date = datetime.now()
            sell_datail_obj.save()

        data = {'success': 'true', 'message': 'Sell Ticket Saved Successfully'}

    except Exception, e:
        print "Exception", e
        data = {'success': 'false', 'message': 'Sell Ticket not Save'}
    return HttpResponse(json.dumps(data), content_type='application/json')


# Sell Ticket List
@csrf_exempt
def view_list_sellticket(request):
    try:
        # pdb.set_trace()
        json_obj = json.loads(request.body)
        user_id = json_obj['user_id']
        city_id = json_obj['city_id']
        sell_ticket_list = []
        status = ["unread","appropriate"]
        sell_ticket_obj = SellTicket.objects.filter(city_id = city_id,status__in=status)
        ratings = ''

        sellticket_id_list = []

        if sell_ticket_obj:
            for ticket in sell_ticket_obj:
                pre_date = datetime.now().strftime("%d/%m/%Y")
                pre_date = datetime.strptime(pre_date, "%d/%m/%Y")
                if ticket.start_date:
                    try:
                        event_start_date = datetime.strptime(ticket.start_date, "%Y-%m-%d")
                    except:
                        try:
                            event_start_date = datetime.strptime(ticket.start_date, "%d %b %Y")
                        except:
                            event_start_date = datetime.strptime(ticket.start_date, "%d-%m-%Y")
                    if event_start_date >= pre_date:
                        sellticket_id_list.append(ticket.sellticket_id)

                if ticket.select_activation_date:
                    try:
                        event_activation_date = datetime.strptime(ticket.select_activation_date, "%Y-%m-%d")
                    except:
                        try:
                            event_activation_date = datetime.strptime(ticket.select_activation_date, "%d %b %Y")
                        except:
                            event_activation_date = datetime.strptime(ticket.select_activation_date, "%d-%m-%Y")
                    if event_activation_date >= pre_date:                
                        sellticket_id_list.append(ticket.sellticket_id)

        selltckt_id_list = set(sellticket_id_list)


        sell_ticket_obj = SellTicket.objects.filter(sellticket_id__in = list(selltckt_id_list))
        if sell_ticket_obj:
            for ticket in sell_ticket_obj:
                user_id1 = str(ticket.user_id)
                consumer_object = ConsumerProfile.objects.get(consumer_id=user_id1)
                phone_no = consumer_object.consumer_contact_no
                email = consumer_object.consumer_email_id
                sellticket_id = str(ticket.sellticket_id)
                if ticket.image_one:
                    image_one = ticket.image_one.url
                else:
                    try:
                        cat_city_map = CategoryCityMap.objects.filter(city_place_id = city_id)
                        for cat in cat_city_map:
                            if cat.category_id.category_name == "Ticket Resell":
                                image_one = cat.category_id.category_image.url
                    except:
                        image_one = ''
                        pass

                sellticket_review_count = str(SellTicketReview.objects.filter(sellticket_id=sellticket_id).count())

                rating_count = 0
                sellticket_rating = SellTicketReview.objects.filter(sellticket_id=sellticket_id)
                sum_rating = 0
                for sellticket in sellticket_rating:
                    if sellticket.ratings > 0:
                        ratings = sellticket.ratings
                        rating_count = rating_count + 1
                    else:
                        ratings = 0
                    sum_rating = float(ratings) + float(sum_rating)

                if rating_count > 0:
                    avg_rating = sum_rating / rating_count
                    avg_rating = str(round(avg_rating, 1))
                else:
                    avg_rating = "0.0"
                

                try:
                    sellticket_like_obj = SellTicketLike.objects.get(sellticket_id=sellticket_id, user_id=str(user_id))
                    is_like = "true"
                except Exception:
                    is_like = "false"

                try:
                    sellticket_fav_obj = SellTicketFavourite.objects.get(sellticket_id=sellticket_id,
                                                                         user_id=str(user_id))
                    is_favourite = "true"
                except Exception:
                    is_favourite = "false"

                if ticket.sellticket_views:
                    views_count = str(SellTicketView.objects.filter(sellticket_id=sellticket_id).count())
                else:
                    views_count = "0"

                like_count = str(SellTicketLike.objects.filter(sellticket_id=sellticket_id).count())

                if ticket.contact_number:
                    phone_no = ticket.contact_number
                    
                tkt_data = {
                    "sellticket_id": str(ticket.sellticket_id),
                    "event_name": ticket.event_name,
                    "event_venue": ticket.event_venue,
                    "start_date": ticket.start_date,
                    "start_time": ticket.start_time,
                    "image_one": image_one,
                    "phone_no": phone_no,
                    "email": email,
                    "likes": str(like_count),
                    "is_like": is_like,
                    "is_favourite": is_favourite,
                    "views": str(views_count),
                    "reviews": sellticket_review_count,
                    "ratings": avg_rating
                }
                sell_ticket_list.append(tkt_data)
            sell_ticket_list. reverse()
            data = {"success": "true", "sell_ticket_list": sell_ticket_list}
        else:
            tkt_data = {
                "": ""
            }
            sell_ticket_list.append(tkt_data)
            data = {"success": "false", 'message': "Sell Ticket not Availabel"}

    except Exception, e:
        print "Exception", e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def favourite_sellticket(request):
    json_obj = json.loads(request.body)
    try:
        if json_obj['favourite_status'] == 'true':
            sellticket_fav_obj = SellTicketFavourite.objects.create()
            sellticket_fav_obj.user_id = ConsumerProfile.objects.get(consumer_id=json_obj['user_id'])
            sellticket_fav_obj.sellticket_id = SellTicket.objects.get(sellticket_id=json_obj['sellticket_id'])
            sellticket_fav_obj.creation_date = datetime.now()
            sellticket_fav_obj.save()
        else:
            sellticket_fav_obj = SellTicketFavourite.objects.get(sellticket_id=json_obj['sellticket_id'],
                                                                 user_id=json_obj['user_id'])
            sellticket_fav_obj.delete()
        data = {'success': 'true', 'message': ''}
    except Exception, ke:
        print ke
        data = {'success': 'false', 'message': 'Oops! Something went wrong'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def like_sellticket(request):
    json_obj = json.loads(request.body)
    try:
        if json_obj['like_status'] == 'true':
            sellticket_like_obj = SellTicketLike.objects.create()
            sellticket_like_obj.user_id = ConsumerProfile.objects.get(consumer_id=json_obj['user_id'])
            sellticket_like_obj.sellticket_id = SellTicket.objects.get(sellticket_id=json_obj['sellticket_id'])
            sellticket_like_obj.creation_date = datetime.now()
            sellticket_like_obj.save()
        else:
            sellticket_like_obj = SellTicketLike.objects.get(sellticket_id=json_obj['sellticket_id'],
                                                             user_id=json_obj['user_id'])
            sellticket_like_obj.delete()
        data = {'success': 'true', 'message': ''}
    except Exception, ke:
        print ke
        data = {'success': 'false', 'message': 'Oops! Something went wrong'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def post_sellticket_review(request):
    json_obj = json.loads(request.body)
    user_id = json_obj['user_id']
    sellticket_id = json_obj['sellticket_id']
    review = json_obj['review']
    ratings = json_obj['ratings']
    try:
        review_obj = SellTicketReview()
        review_obj.user_id = ConsumerProfile.objects.get(consumer_id=user_id)
        review_obj.sellticket_id = SellTicket.objects.get(sellticket_id=sellticket_id)
        review_obj.review = review
        review_obj.ratings = ratings
        review_obj.creation_date = datetime.now()
        review_obj.save()
        data = {"success": "true", "message": "Review published successfully."}

    except Exception, e:
        print "Exception", e
        data = {"success": "false", "message": "Something went wrong"}
    return HttpResponse(json.dumps(data), content_type='application/json')


# Sell Ticket Detail
@csrf_exempt
def view_sellticket_detail(request):
    try:
        # pdb.set_trace()
        json_obj = json.loads(request.body)
        user_id = json_obj['user_id']
        city_id = json_obj['city_id']
        sellticket_id = json_obj['sellticket_id']
        sell_ticket_detail = []
        review_list = []
        image_list = []
        ratings = ''
        avg_rating = 0
        sum_rating = 0
        count = 0
        if request.method == 'POST':
            sellticket_id = json_obj['sellticket_id']
            tkt_obj = SellTicket.objects.filter(sellticket_id=sellticket_id)
            for ticket_object in tkt_obj:
                user_id1 = str(ticket_object.user_id)
                consumer_object = ConsumerProfile.objects.get(consumer_id=user_id1)
                phone_no = consumer_object.consumer_contact_no
                email = consumer_object.consumer_email_id

                #SellTicketView
                if user_id:
                    try:
                        st_view_obj = SellTicketView.objects.get(sellticket_id=sellticket_id, user_id=user_id)
                    except:
                        st_view_obj = SellTicketView()
                        st_view_obj.sellticket_id = ticket_object
                        st_view_obj.user_id = ConsumerProfile.objects.get(consumer_id=user_id)
                        st_view_obj.creation_date = datetime.now()
                        st_view_obj.save()

                
                views_count = 0
                views_count = SellTicketView.objects.filter(sellticket_id=sellticket_id).count()
                #ticket_object.save()

                sellticket_review_count = SellTicketReview.objects.filter(sellticket_id=sellticket_id).count()

                rating_count = 0
                sellticket_rating = SellTicketReview.objects.filter(sellticket_id=sellticket_id)
                sum_rating = 0
                for sellticket in sellticket_rating:
                    if sellticket.ratings > 0:
                        ratings = sellticket.ratings
                        rating_count = rating_count + 1
                    else:
                        ratings = 0
                    sum_rating = float(ratings) + float(sum_rating)

                if rating_count > 0:
                    avg_rating = sum_rating / rating_count
                    avg_rating = str(round(avg_rating, 1))
                else:
                    avg_rating = "0.0"

                try:
                    sellticket_like_obj = SellTicketLike.objects.get(sellticket_id=sellticket_id, user_id=str(user_id))
                    is_like = "true"
                except Exception:
                    is_like = "false"

                try:
                    sellticket_fav_obj = SellTicketFavourite.objects.get(sellticket_id=sellticket_id,
                                                                         user_id=str(user_id))
                    is_favourite = "true"
                except Exception:
                    is_favourite = "false"

                like_count = SellTicketLike.objects.filter(sellticket_id=sellticket_id).count()

                if ticket_object.image_one:
                    image_one = ticket_object.image_one.url
                    image_list.append(image_one)
                else:
                    image_one = ''
                if ticket_object.image_two:
                    image_two = ticket_object.image_two.url
                    image_list.append(image_two)
                else:
                    image_two = ''
                if ticket_object.image_three:
                    image_three = ticket_object.image_three.url
                    image_list.append(image_three)
                else:
                    image_three = ''
                if ticket_object.image_four:
                    image_four = ticket_object.image_four.url
                    image_list.append(image_four)
                else:
                    image_four = ''

                if not image_list:
                    try:
                        cat_city_map = CategoryCityMap.objects.filter(city_place_id = city_id)
                        for cat in cat_city_map:
                            if cat.category_id.category_name == "Ticket Resell":
                                image_one = cat.category_id.category_image.url
                        image_list.append(image_one)
                    except:
                        pass

                review_obj = SellTicketReview.objects.filter(sellticket_id=sellticket_id)

                for review in review_obj:
                    user_id2 = str(review.user_id)
                    consumer_object = ConsumerProfile.objects.get(consumer_id=user_id2)
                    name = consumer_object.consumer_full_name
                    if consumer_object.consumer_profile_pic:
                        image = consumer_object.consumer_profile_pic.url
                    else:
                        image = ''

                    review_data = {
                        "reviewer_name": name,
                        "reviewer_image": image,
                        "review_date": review.creation_date.strftime("%d/%m/%Y"),
                        "review": review.review,
                        "review_rating": review.ratings
                    }
                    review_list.append(review_data)

                sellticket_detail_obj = SellTicketDetails.objects.filter(sellticket_id=sellticket_id)
                ticket_details =[]
                for sell_detail in sellticket_detail_obj:
                    sell_ticket_data = {
                        'original_price': sell_detail.original_price,
                        'no_of_tickets': sell_detail.no_of_tickets,
                        'ticket_class': sell_detail.ticket_class,
                        'asking_price': sell_detail.asking_price
                    }
                    ticket_details.append(sell_ticket_data)

                if ticket_object.contact_number:
                    phone_no = ticket_object.contact_number
                ticket_data = {
                    'event_name': ticket_object.event_name,
                    'event_venue': ticket_object.event_venue,
                    'start_date': ticket_object.start_date,
                    'start_time': ticket_object.start_time,
                    'ticket_details':ticket_details,
                    'phone_no': phone_no,
                    'email': email,
                    'other_comments': ticket_object.other_comments,
                    'likes': str(like_count),
                    'is_like': is_like,
                    'is_favourite': is_favourite,
                    'views': str(views_count),
                    'review_list': review_list,
                    'reviews': sellticket_review_count,
                    'avg_rating': avg_rating
                }
                sell_ticket_detail.append(ticket_data)

        data = {"success": "true", "sell_ticket_detail": sell_ticket_detail, 'image_list': image_list}

    except Exception, e:
        print "Exception", e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def share_sell_ticket(request):
    json_obj = json.loads(request.body)
    try:
        sell_ticket_obj = SellTicket.objects.get(sellticket_id=json_obj['sellticket_id'])
        user_obj  = ConsumerProfile.objects.get(consumer_id=json_obj['user_id'])
        share_obj = SellTicketShares()
        share_obj.sellticket_id = sell_ticket_obj
        share_obj.user_id = user_obj
        share_obj.creation_date = datetime.now()
        share_obj.save()
        data = {'success': 'true', 'message': ''}
    except Exception, ke:
        print ke
        data = {'success': 'false', 'message': 'Oops! Something went wrong'}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def get_map_advert_list(request):
    json_obj = json.loads(request.body)
    user_id = json_obj['user_id']
    city_id = json_obj['city_id']
    consumer_latitude = json_obj['consumer_latitude']
    consumer_longitude = json_obj['consumer_longitude']
    rating_range = json_obj['filter_parameter']['rating_range']
    radius = ''
    if not city_id:
        radius = 10
        lon_max, lon_min, lat_max, lat_min = bounding_box(
            float(json_obj['consumer_latitude']),
            float(json_obj['consumer_longitude']),
            float(radius)
        )
    if json_obj['filter_parameter']['radius']:
        radius = json_obj['filter_parameter']['radius']
        lon_max, lon_min, lat_max, lat_min = bounding_box(
            float(json_obj['consumer_latitude']),
            float(json_obj['consumer_longitude']),
            float(radius)
        )
    advert_list = []
    try:
        if city_id:
            advert_map_obj = Advert.objects.filter(
                city_place_id=city_id,
                status='1'
            )
        if city_id and json_obj['filter_parameter']['radius'] and int(radius) < 15:
            advert_map_obj = advert_map_obj.filter(
                latitude__range=[lat_min, lat_max],
                longitude__range=[lon_min, lon_max],
            )
        if not city_id:
            advert_map_obj = Advert.objects.filter(
                latitude__range=[lat_min, lat_max],
                longitude__range=[lon_min, lon_max],
                status='1'
            )
        for advert_map in advert_map_obj:
            phone_list = []
            email_list = []
            advert_id = str(advert_map.advert_id)
            pre_date = datetime.now().strftime("%d/%m/%Y")
            pre_date = datetime.strptime(pre_date, "%d/%m/%Y")
            advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)
            end_date = advert_sub_obj.business_id.end_date
            start_date = datetime.strptime(advert_sub_obj.business_id.start_date, "%d/%m/%Y")
            if start_date <= pre_date:
                end_date = datetime.strptime(end_date, "%d/%m/%Y")
                date_gap = end_date - pre_date
                if int(date_gap.days) >= 0:
                    advert_obj = Advert.objects.get(advert_id=advert_id)
                    advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)
                    start_date = advert_sub_obj.business_id.start_date
                    end_date = advert_sub_obj.business_id.end_date
                    start_date = datetime.strptime(start_date, "%d/%m/%Y")
                    end_date = datetime.strptime(end_date, "%d/%m/%Y")
                    address = ''
                    if advert_obj.area:
                        address = advert_obj.area
                    if advert_obj.city_place_id:
                        address = address + ' ' + advert_obj.city_place_id.city_id.city_name

                    phone_list.append(advert_obj.contact_no)

                    category_color = advert_obj.category_id.category_color
                    category_name = advert_obj.category_id.category_name

                    email_list.append(advert_obj.email_primary)
                    if advert_obj.email_secondary:
                        email_list.append(advert_obj.email_secondary)
                    if advert_obj.display_image:
                        image_url = advert_obj.display_image.url
                    else:
                        image_url = ''

                    try:
                        advert_like_obj = AdvertLike.objects.get(advert_id=advert_id, user_id=str(user_id))
                        is_like = "true"
                    except Exception:
                        is_like = "false"

                    try:
                        advert_like_obj = AdvertFavourite.objects.get(advert_id=advert_id, user_id=str(user_id))
                        is_favourite = "true"
                    except Exception:
                        is_favourite = "false"

                    views_count = AdvertView.objects.filter(advert_id=advert_id).count()
                    like_count = AdvertLike.objects.filter(advert_id=advert_id).count()

                    review_obj = AdvertReview.objects.filter(advert_id=str(advert_id))
                    ratings_total = 0
                    rating_count = 0
                    for review in review_obj:
                        if float(review.ratings) > 0:
                            ratings_total = ratings_total + float(review.ratings)
                            rating_count = rating_count + 1
                    if rating_count > 0:
                        ratings = round(float(ratings_total) / rating_count,1)
                    else:
                        ratings = 0.0

                    if consumer_latitude:
                        newport_ri = (consumer_latitude, consumer_longitude)
                        cleveland_oh = (advert_obj.latitude, advert_obj.longitude)
                        distance = round(float(vincenty(newport_ri, cleveland_oh).kilometers), 2)
                    else:
                        distance = ''

                    time_list = []

                    hours_obj = WorkingHours.objects.filter(advert_id=advert_id)
                    for hours in hours_obj:
                        timing = hours.day + ', ' + hours.start_time.lower() + ' to ' + hours.end_time.lower()
                        time_list.append(timing)

                    advert_address = advert_obj.address_line_1
                    if advert_obj.address_line_2:
                        advert_address = address + ', ' + advert_obj.address_line_2
                    if advert_obj.area:
                        advert_address = address + ', ' + advert_obj.area
                        landmark = advert_obj.area
                    if advert_obj.city_place_id:
                        advert_address = address + ', ' + advert_obj.city_place_id.city_id.city_name
                        landmark = landmark + ', ' + advert_obj.city_place_id.city_id.city_name
                    if advert_obj.state_id:
                        advert_address = address + ', ' + advert_obj.state_id.state_name
                    if advert_obj.pincode_id:
                        advert_address = address + '-' + advert_obj.pincode_id.pincode

                    if advert_obj.product_description:
                        product_description = advert_obj.product_description
                    else:
                        product_description = ''

                    try:
                        coupon_obj = CouponCode.objects.get(advert_id=advert_id, user_id=user_id)
                        coupon_flag = 'true'
                    except Exception, ke:
                        coupon_flag = 'false'

                    if advert_obj.discount_description:
                        start_date = start_date.strftime("%d %b %Y")
                        end_date = end_date.strftime("%d %b %Y")
                    else:
                        start_date = ''
                        end_date = ''

                    discount_start_date = ''
                    discount_end_date = ''
                    if advert_obj.discount_description:
                        discount_description = advert_obj.discount_description
                        if advert_obj.discount_start_date:
                            discount_start_date = datetime.strptime(advert_obj.discount_start_date, "%d/%m/%Y")
                            discount_start_date = discount_start_date.strftime("%d %b %Y")
                        if advert_obj.discount_end_date:
                            discount_end_date = datetime.strptime(advert_obj.discount_end_date, "%d/%m/%Y")
                            discount_end_date = discount_end_date.strftime("%d %b %Y")
                    else:
                        discount_description = ''

                    advert_data = {
                        "advert_id": str(advert_obj.advert_id),
                        "advert_img": image_url,
                        "name": advert_obj.advert_name,
                        "location": address,
                        "offer_start_date": start_date,
                        "offer_end_date": end_date,
                        "likes": str(like_count),
                        "is_like": is_like,
                        "is_favourite": is_favourite,
                        "views": str(views_count),
                        "reviews": str(review_obj.count()),
                        "phone": phone_list,
                        "email": email_list,
                        "ratings": ratings,
                        "latitude": str(advert_obj.latitude),
                        "longitude": str(advert_obj.longitude),
                        "coupon_flag":coupon_flag,
                        "product_description":product_description,
                        "advert_address":advert_address,
                        "opening_closing_time":time_list,
                        "distance":str(distance),
                        "category_color":str(category_color),
                        "category_name":category_name,
                        "discount_end_date":discount_end_date,
                        "discount_start_date":discount_start_date
                    }
                    advert_list.append(advert_data)
        if radius:
            if int(radius) < 15:
                advert_list = [d for d in advert_list if float(d['distance']) < int(radius)]
            else:
                advert_list = [d for d in advert_list if float(d['distance']) > 10]
        
        top_advert_list = [d for d in advert_list if d['ratings'] >= 4.5]
        top_count = len(top_advert_list)
        good_advert_list = [d for d in advert_list if d['ratings'] >= 3.0 and d['ratings'] < 4.5]
        good_count = len(good_advert_list)
        avg_advert_list = [d for d in advert_list if d['ratings'] >= 1.5 and d['ratings'] < 3.0]
        avg_count = len(avg_advert_list)
        poor_advert_list = [d for d in advert_list if d['ratings'] > 0 and d['ratings'] < 1.5]
        poor_count = len(poor_advert_list)
        nry_advert_list = [d for d in advert_list if d['ratings'] == 0]
        nry_count = len(nry_advert_list)

        if rating_range:
            new_list = []
            for ranges in rating_range:
                if ranges == "Top":
                    new_list.extend(top_advert_list)
                if ranges == "Good":
                    new_list.extend(good_advert_list)
                if ranges == "Average":
                    new_list.extend(avg_advert_list)
                if ranges == "Poor":
                    new_list.extend(poor_advert_list)
                if ranges == "Not Rated Yet":
                    new_list.extend(nry_advert_list)
            new_list.sort(key=operator.itemgetter("ratings"))
            advert_list = new_list

        data = {
            'success': 'true', 
            'message': '', 
            'advert_list': advert_list, 
            #'category_id': category_id,
            'top_count':str(top_count),
            'good_count':str(good_count),
            'avg_count':str(avg_count),
            'poor_count':str(poor_count),
            'nry_count':str(nry_count),
            }

    except Exception, e:
        print "Exception", e
        data = {"success": "false", "message": "Something went wrong", "advert_list": advert_list}
    return HttpResponse(json.dumps(data), content_type='application/json')


def change_in_latitude(distance):
    "Given a distance north, return the change in latitude."
    return (distance / earth_radius) * radians_to_degrees


def change_in_longitude(latitude, distance):
    "Given a latitude and a distance west, return the change in longitude."
    # Find the radius of a circle around the earth at given latitude.
    r = earth_radius * math.cos(latitude * degrees_to_radians)
    return (distance / r) * radians_to_degrees


def bounding_box(latitude, longitude, distance):
    lat_change = change_in_latitude(distance)
    lat_max = latitude + lat_change
    lat_min = latitude - lat_change
    lon_change = change_in_longitude(latitude, distance)
    lon_max = longitude + lon_change
    lon_min = longitude - lon_change
    return (lon_max, lon_min, lat_max, lat_min)


@csrf_exempt
def post_advert_review(request):
    json_obj = json.loads(request.body)
    user_id = json_obj['user_id']
    advert_id = json_obj['advert_id']
    ratings = json_obj['ratings']
    review = json_obj['review']
    try:
        review_obj = AdvertReview()
        review_obj.user_id = ConsumerProfile.objects.get(consumer_id=user_id)
        review_obj.advert_id = Advert.objects.get(advert_id=advert_id)
        review_obj.ratings = ratings
        review_obj.review = review
        review_obj.creation_date = datetime.now()
        review_obj.save()
        data = {"success": "true", "message": "Review published successfully."}

    except Exception, e:
        print "Exception", e
        data = {"success": "false", "message": "Something went wrong"}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def get_city_star(request):
    json_obj = json.loads(request.body)
    user_id = json_obj['user_id']
    city_id = json_obj['city_id']
    city_star_list = []
    try:
        try:
            city_star_obj = CityStarDetails.objects.get(city=city_id, status='current')
        except:
            try:
                city_star_obj = CityStarDetails.objects.get(city=city_id, status='default')
            except:
                city_star_obj = ''
                pass
            pass
        if city_star_obj:
            consumer_obj = ConsumerProfile.objects.get(consumer_id=user_id)
            try:
                like_obj = CityStar_Like.objects.get(user_id=consumer_obj, citystarID=city_star_obj.citystarID)
                is_like = 'true'
            except:
                is_like = 'false'
                pass
            try:
                view_obj = CityStar_View.objects.get(user_id=consumer_obj, citystarID=city_star_obj.citystarID)
            except:
                view_obj = CityStar_View()
                view_obj.user_id = consumer_obj
                view_obj.citystarID = city_star_obj
                view_obj.creation_date = datetime.now()
                view_obj.save()
                pass

            if city_star_obj.title:
                name = city_star_obj.title + ' ' + city_star_obj.name
            else:
                name = city_star_obj.name

            address = ''
            if city_star_obj.address1:
                address = address + city_star_obj.address1
            if city_star_obj.address2:
                address = address + ' ,' + city_star_obj.address2

            phone_number = ''
            if city_star_obj.phone:
                phone_number = city_star_obj.phone

            email = ''
            if city_star_obj.email:
                email = city_star_obj.email

            age = ''
            if city_star_obj.age:
                age = city_star_obj.age

            experience = ''
            if city_star_obj.experience:
                experience = city_star_obj.experience

            education = ''
            if city_star_obj.education:
                education = city_star_obj.education

            summary = ''
            if city_star_obj.summary:
                summary = city_star_obj.summary

            occupation = ''
            if city_star_obj.occupation:
                occupation = city_star_obj.occupation

            achievements = ''
            if city_star_obj.achievements:
                achievements = city_star_obj.achievements

            description = ''
            if city_star_obj.description:
                description = city_star_obj.description

            image = ''
            if city_star_obj.image:
                image = city_star_obj.image.url

            image_list = []
            star_image_obj = StarImage.objects.filter(star_id = city_star_obj.citystarID)
            for star_image in star_image_obj:
                if star_image.star_image:
                    image_list.append(star_image.star_image.url)

            city_star_data = {
                'name': name,
                'address': address,
                'phone_number': phone_number,
                'email': email,
                'education': education,
                'age': age,
                'experience': experience,
                'summary': summary,
                'occupation': occupation,
                'description': description,
                'achievements': achievements,
                'image': image,
                'background_image': image_list,
                'like': str(CityStar_Like.objects.filter(citystarID=city_star_obj.citystarID).count()),
                'share': str(city_star_obj.shares),
                'view': str(CityStar_View.objects.filter(citystarID=city_star_obj.citystarID).count()),
                'is_like': is_like,
                'city_star_id':str(city_star_obj.citystarID)
            }
            city_star_list.append(city_star_data)
        else:
            city_star_data = ''
        data = {"success": "true", "city_star_details": city_star_list}
    except Exception, e:
        print "Exception", e
        data = {"success": "false", "message": "Something went wrong"}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def like_city_star(request):
    json_obj = json.loads(request.body)
    try:
        if json_obj['like_status'] == 'true':
            like_obj = CityStar_Like.objects.create()
            like_obj.user_id = ConsumerProfile.objects.get(consumer_id=json_obj['user_id'])
            like_obj.citystarID = CityStarDetails.objects.get(citystarID=json_obj['city_star_id'])
            like_obj.creation_date = datetime.now()
            like_obj.save()
        else:
            like_obj = CityStar_Like.objects.get(citystarID=json_obj['city_star_id'], user_id=json_obj['user_id'])
            like_obj.delete()
        data = {'success': 'true', 'message': ''}
    except Exception, ke:
        print ke
        data = {'success': 'false', 'message': 'Oops! Something went wrong'}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def share_city_star(request):
    json_obj = json.loads(request.body)
    try:
        citystar_obj = CityStarDetails.objects.get(citystarID=json_obj['city_star_id'])
        share_count = int(citystar_obj.shares) + 1
        citystar_obj.shares = share_count
        citystar_obj.save()
        data = {'success': 'true', 'message': '','share_count':str(citystar_obj.shares)}
    except Exception, ke:
        print ke
        data = {'success': 'false', 'message': 'Oops! Something went wrong'}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def search_sellticket(request):
    try:
        json_obj = json.loads(request.body)
        search_keyword = json_obj['search_keyword']
        list = []
        sellticket_list = []
        status = ["unread","appropriate"]
        sellticket_obj = SellTicket.objects.filter(event_name__icontains=search_keyword, status__in =status)
        list.extend(sellticket_obj)

        sellticket_obj = SellTicket.objects.filter(event_venue__icontains=search_keyword, status__in =status)
        list.extend(sellticket_obj)

        list = set(list)
        for sellticket in list:
            print sellticket
            sellticket_obj = SellTicket.objects.get(sellticket_id=str(sellticket.sellticket_id))
            sellticket_data = {
                "sellticket_id": str(sellticket_obj.sellticket_id),
                "event_name": str(sellticket_obj.event_name),
                "event_venue": str(sellticket_obj.event_venue),
                "start_date": str(sellticket_obj.start_date)
            }
            sellticket_list.append(sellticket_data)

        data = {'success': 'true', 'sellticket_list': sellticket_list, 'count':str(len(sellticket_list))}
    except Exception, e:
        print e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def get_citylife_category_list(request):
    ##    pdb.set_trace()
    category_list = []
    json_obj = json.loads(request.body)
    try:
        category_objs = citylife_category.objects.filter(status=1,city_id=json_obj['city_id'])
        for category in category_objs:
            category_id = str(category.category_id)
            category_name = str(category.category_name)
            category_data = {'category_id': category_id, 'category_name': category_name}
            category_list.append(category_data)
        data = {'category_list': category_list, 'success': 'true'}
    except Exception, ke:
        print ke
        data = {'category_list': category_list, 'success': 'true'}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def save_citylife_post(request):
    json_obj = json.loads(request.body)
    try:
        category_obj = citylife_category.objects.get(category_id=json_obj['category_id'])
        city_obj = City_Place.objects.get(city_place_id=json_obj['city_id'])
        country_id = city_obj.city_id.state_id.country_id
        consumer_obj = ConsumerProfile.objects.get(consumer_id=json_obj['user_id'])
        post_obj = PostDetails()
        post_obj.city_id = city_obj
        post_obj.country_id = country_id
        post_obj.citylife_category = category_obj
        post_obj.user_id = consumer_obj
        post_obj.creation_date = datetime.now()
        post_obj.mood = json_obj['mood']
        post_obj.area = json_obj['area']
        post_obj.title = json_obj['title']
        post_obj.description = json_obj['description']
        post_obj.status = "unread"
        post_obj.save()
        #post_add_mail(category_obj.category_name,consumer_obj.consumer_full_name,city_obj.city_id.city_name)

        # if consumer_obj.consumer_contact_no:
        #     sms_post(consumer_obj.consumer_contact_no,consumer_obj.consumer_full_name)
        # if consumer_obj.consumer_email_id:
        #     post_user_mail(consumer_obj.consumer_full_name, str(consumer_obj.consumer_email_id))

        data = {'message': "Post saved successfully", 'success': 'true','post_id' : str(post_obj.post_id)}
    except Exception, ke:
        print ke
        data = {'message': "Oops! Something went wrong.", 'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def save_citylife_files(request):
    try:
        post_obj = PostDetails.objects.get(post_id = request.POST['post_id'])
        post_file_obj = PostFile()
        post_file_obj.creation_date = datetime.now()
        post_file_obj.post_file = request.FILES['file']
        post_file_obj.post_id = post_obj
        post_file_obj.save()

        if request.POST['file_width']:
            post_file_obj.file_width = request.POST['file_width']
        if request.POST['file_height']:
            post_file_obj.file_height = request.POST['file_height']
        post_file_obj.save()

        data = {'message': "Post file saved successfully", 'success': 'true'}
    except Exception, ke:
        print ke
        data = {'message': "Oops! Something went wrong.", 'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def view_citylife_post(request):
    post_list = []
    json_obj = json.loads(request.body)
    try:
        status = ["unread","appropriate"]
        post_obj = PostDetails.objects.filter(city_id=json_obj['city_id'],status__in=status).order_by('-post_id')

        if json_obj['filter_parameter']['day_range'] == 'today':
            dt = datetime.now()
            start = dt
            start = start.strftime("%Y-%m-%d")
            start = datetime.strptime(start,"%Y-%m-%d")
            end = dt
            # print "\n\n\n\n\n\n===========\n\n\n\n\n\n"
            # print start,end
            # print "\n\n\n\n\n\n===========\n\n\n\n\n\n"
            post_obj = post_obj.filter(creation_date__range=[start, end])

        if json_obj['filter_parameter']['day_range'] == 'week':
            dt = datetime.now()
            start = dt - timedelta(days=dt.weekday()) - timedelta(days=1)
            end = start + timedelta(days=6)
            start = start.strftime("%Y-%m-%d")
            start = datetime.strptime(start,"%Y-%m-%d")
            
            post_obj = post_obj.filter(creation_date__range=[start, end])

        if json_obj['filter_parameter']['day_range'] == 'month':
            import calendar
            dt = datetime.now()
            month = dt.month
            year = dt.year
            _, num_days = calendar.monthrange(year, month)
            first_day = date(year, month, 1) - timedelta(days=1)
            last_day = date(year, month, num_days) + timedelta(days=1)
            post_obj = post_obj.filter(creation_date__range=[first_day, last_day])

        if json_obj['filter_parameter']['category']:
            post_obj = post_obj.filter(citylife_category__in = json_obj['filter_parameter']['category'])

        os_path = '/home/ec2-user/DigiSpace'
        #os_path = '/home/admin1/Prod_backup/DigiSpace_25/'
        for post in post_obj:
            post_file_obj = PostFile.objects.filter(post_id=post.post_id)
            post_image = ''
            file_width = ''
            file_height = ''
            if post_file_obj:
                for files in post_file_obj:
                    #Image.open
                    try:
                        image = Image.open(os_path + files.post_file.url)
                        post_image = files.post_file.url
                        file_width = files.file_width
                        file_height = files.file_height
                        break
                    except Exception as e:
                        print e
                        pass

            post_like_count = PostMood.objects.filter(status = "like",post_id=post.post_id).count()
            post_dislike_count = PostMood.objects.filter(status = "dislike",post_id=post.post_id).count()
            if post_dislike_count == 0 and post_like_count == 0:
                dislike_like_percentage = 50
            else:
                dislike_like_percentage = (float(post_like_count)/float(PostMood.objects.filter(post_id=post.post_id).count()))*100

            mood = ""
            if dislike_like_percentage >= 0 and dislike_like_percentage < 20:
                mood = "Miserable"
            elif dislike_like_percentage > 20 and dislike_like_percentage < 50:
                mood = "Heartbroken"
            elif dislike_like_percentage == 50:
                mood = "Neutral"
            elif dislike_like_percentage > 50 and dislike_like_percentage < 80:
                mood = "Thrilled"
            elif dislike_like_percentage > 80:
                mood = "Awesome"

            if post_dislike_count == 0 and post_like_count == 0:
                mood = "NA"
            posted_time = post.creation_date


            pre_date = datetime.now().strftime("%d/%m/%Y")
            pre_date = datetime.strptime(pre_date, "%d/%m/%Y")
            start_date = posted_time.strftime("%d/%m/%Y")
            start_date = datetime.strptime(start_date, "%d/%m/%Y")

            if start_date == pre_date:
                posted_time = posted_time.strftime("%I.%M%P") + " - Today"
            else:
                posted_time = posted_time.strftime("%I.%M%P - %d %b.%y")

            is_like = 'false'
            is_dislike = 'false'
            is_favorite = 'false'

            try:
                post_mood_obj = PostMood.objects.get(user_id = json_obj['user_id'],post_id=post.post_id)
                if post_mood_obj.status == "like":
                    is_like = "true"
                if post_mood_obj.status == "dislike":
                    is_dislike = "true"
            except:
                pass

            try:
                post_fav_obj = PostFavourite.objects.get(user_id=json_obj['user_id'],post_id=post.post_id)
                is_favorite = "true"
            except:
                pass

            post_data = {
                'post_id': post.post_id,
                'description':post.description,
                'category_name':post.citylife_category.category_name,
                'posted_date':posted_time,
                'mood':mood,
                'dislike_like_percentage':str(float(dislike_like_percentage)),
                'like_count':str(PostMood.objects.filter(status = "like",post_id=post.post_id).count()),
                'dislike_count':str(PostMood.objects.filter(status = "dislike",post_id=post.post_id).count()),
                'view_count':str(PostView.objects.filter(post_id=post.post_id).count()),
                'comment_count': str(PostComments.objects.filter(post_id=post.post_id, status='1').count()),
                'post_image':post_image,
                'is_like':is_like,
                'is_dislike':is_dislike,
                'is_favorite':is_favorite,
                'file_width':file_width,
                'file_height':file_height,
                'share_count':str(post.share)
            }
            post_list.append(post_data)
        if json_obj['filter_parameter']['mood_ranges']:
            new_list = []
            for ranges in json_obj['filter_parameter']['mood_ranges']:
                new_post_list = []
                if ranges == "0":
                    new_post_list = [d for d in post_list if float(d['dislike_like_percentage']) >= 0 and float(d['dislike_like_percentage']) <= 20]
                if ranges == "20":
                    new_post_list = [d for d in post_list if float(d['dislike_like_percentage']) > 20 and float(d['dislike_like_percentage']) < 50]
                if ranges == "50":
                    new_post_list = [d for d in post_list if float(d['dislike_like_percentage']) == 50 and float(d['dislike_count']) > 0 and float(d['like_count']) > 0]
                if ranges == "na":
                    new_post_list = [d for d in post_list if float(d['dislike_like_percentage']) == 50 and float(d['dislike_count']) == 0 and float(d['like_count']) == 0]
                if ranges == "80":
                    new_post_list = [d for d in post_list if float(d['dislike_like_percentage']) > 50 and float(d['dislike_like_percentage']) <= 80]
                if ranges == "100":
                    new_post_list = [d for d in post_list if float(d['dislike_like_percentage']) > 80]
                new_list.extend(new_post_list)
            post_list = new_list
        data = {'post_list': post_list, 'success': 'true'}
    except Exception, ke:
        print ke
        data = {'message': "Oops! Something went wrong.", 'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def view_citylife_post_details(request):
    ##    pdb.set_trace()
    post_file_list = []
    json_obj = json.loads(request.body)
    try:
        post = PostDetails.objects.get(post_id=json_obj['post_id'])
        user_id = ConsumerProfile.objects.get(consumer_id=json_obj['user_id'])

        try:
            view_obj = PostView.objects.get(user_id=json_obj['user_id'],post_id=json_obj['post_id'])
        except:
            view_obj = PostView()
            view_obj.user_id = user_id
            view_obj.post_id = post
            view_obj.creation_date = datetime.now()
            view_obj.save()
            pass

        print "view_obj",view_obj

        post_file_obj = PostFile.objects.filter(post_id=post.post_id)
        for file in post_file_obj:
            image_data = {
                'file_url' : file.post_file.url,
                'file_id' : str(file.post_file_id),
                'file_width' : str(file.file_width),
                'file_height' : str(file.file_height)
            }
            post_file_list.append(image_data)
        post_like_count = PostMood.objects.filter(status = "like",post_id=post.post_id).count()
        post_dislike_count = PostMood.objects.filter(status = "dislike",post_id=post.post_id).count()
        if post_dislike_count == 0 and post_like_count == 0:
            dislike_like_percentage = 50
        else:
            dislike_like_percentage = (float(post_like_count)/float(PostMood.objects.filter(post_id=post.post_id).count()))*100
        mood = ""
        if dislike_like_percentage >= 0 and dislike_like_percentage < 20:
            mood = "Miserable"
        elif dislike_like_percentage > 20 and dislike_like_percentage < 50:
            mood = "Heartbroken"
        elif dislike_like_percentage == 50:
            mood = "Neutral"
        elif dislike_like_percentage > 50 and dislike_like_percentage < 80:
            mood = "Thrilled"
        elif dislike_like_percentage > 80:
            mood = "Awesome"

        if post_dislike_count == 0 and post_like_count == 0:
            mood = "NA"

        
        posted_time = post.creation_date
        pre_date = datetime.now().strftime("%d/%m/%Y")
        pre_date = datetime.strptime(pre_date, "%d/%m/%Y")
        start_date = posted_time.strftime("%d/%m/%Y")
        start_date = datetime.strptime(start_date, "%d/%m/%Y")

        if start_date == pre_date:
            posted_time = posted_time.strftime("%I.%M%P") + " - Today"
        else:
            posted_time = posted_time.strftime("%I.%M%P - %d %b.%y")

        is_like = 'false'
        is_dislike = 'false'
        is_favorite = 'false'

        try:
            post_mood_obj = PostMood.objects.get(user_id=json_obj['user_id'],post_id=post.post_id)
            if post_mood_obj.status == "like":
                is_like = "true"
            if post_mood_obj.status == "dislike":
                is_dislike = "true"
        except:
            pass

        try:
            post_fav_obj = PostFavourite.objects.get(user_id=json_obj['user_id'],post_id=post.post_id)
            is_favorite = "true"
        except:
            pass

        comment_list = []
        post_comment_obj = PostComments.objects.filter(post_id=post.post_id,status='1')
        for comments in post_comment_obj:
            post_reply_obj = PostReplys.objects.filter(comment_id=str(comments.comment_id), status='1')

            com_like = "false"
            com_dislike = "false"
            try:
                post_mood_obj = LikeDislikeComment.objects.get(user_id=json_obj['user_id'], comment_id=comments.comment_id)
                if post_mood_obj.status == "like":
                    com_like = "true"
                if post_mood_obj.status == "dislike":
                    com_dislike = "true"
            except:
                pass

            profile_pic = ''
            if comments.user_id.consumer_profile_pic:
                profile_pic = comments.user_id.consumer_profile_pic.url

            comment_time = comments.creation_date
            pre_date = datetime.now().strftime("%d/%m/%Y")
            pre_date = datetime.strptime(pre_date, "%d/%m/%Y")
            start_date = comment_time.strftime("%d/%m/%Y")
            start_date = datetime.strptime(start_date, "%d/%m/%Y")

            if start_date == pre_date:
                comment_time = comment_time.strftime("%I.%M%P") + " - Today"
            else:
                comment_time = comment_time.strftime("%I.%M%P - %d %b.%y")

            reply_list = []
            for reply in post_reply_obj:
                re_like = "false"
                re_dislike = "false"
                try:
                    post_mood_obj = LikeDislikeReply.objects.get(user_id=json_obj['user_id'],reply_id=reply.reply_id)
                    if post_mood_obj.status == "like":
                        re_like = "true"
                    if post_mood_obj.status == "dislike":
                        re_dislike = "true"
                except:
                    pass

                profile_pic = ''
                if reply.user_id.consumer_profile_pic:
                    profile_pic = reply.user_id.consumer_profile_pic.url

                reply_time = reply.creation_date
                pre_date = datetime.now().strftime("%d/%m/%Y")
                pre_date = datetime.strptime(pre_date, "%d/%m/%Y")
                start_date = reply_time.strftime("%d/%m/%Y")
                start_date = datetime.strptime(start_date, "%d/%m/%Y")

                if start_date == pre_date:
                    reply_time = reply_time.strftime("%I.%M%P") + " - Today"
                else:
                    reply_time = reply_time.strftime("%I.%M%P - %d %b.%y")

                reply_data = {
                    "name":reply.user_id.consumer_full_name,
                    "reply_id":str(reply.reply_id),
                    "user_id":reply.user_id.consumer_id,
                    "profile_pic":profile_pic,
                    "date":reply_time,
                    "comment":reply.reply,
                    "is_like":re_like,
                    "is_dislike":re_dislike,
                    "like_count":str(LikeDislikeReply.objects.filter(reply_id=reply.reply_id,status ="like").count()),
                    "dislike_count":str(LikeDislikeReply.objects.filter(reply_id=reply.reply_id,status ="dislike").count()),
                }
                reply_list.append(reply_data)
            comment_data = {
                "name":comments.user_id.consumer_full_name,
                "comment_id":str(comments.comment_id),
                "user_id":comments.user_id.consumer_id,
                "profile_pic":profile_pic,
                "date":comment_time,
                "comment":comments.comment,
                "is_like": com_like,
                "is_dislike": com_dislike,
                "like_count":str(LikeDislikeComment.objects.filter(comment_id=comments.comment_id,status ="like").count()),
                "dislike_count":str(LikeDislikeComment.objects.filter(comment_id=comments.comment_id,status ="dislike").count()),
                'reply_list':reply_list
            }
            comment_list.append(comment_data)
        user_image = ''
        if post.user_id.consumer_profile_pic:
            user_image = post.user_id.consumer_profile_pic.url
        post_data = {
            'post_id': post.post_id,
            'description':post.description,
            'title':post.title if post.title else '',
            'category_name':post.citylife_category.category_name,
            'posted_date':posted_time,
            'mood':mood,
            #'posted_by':user_id.consumer_full_name,
            'dislike_like_percentage':str(float(dislike_like_percentage)),
            'like_count':str(PostMood.objects.filter(status = "like",post_id=post.post_id).count()),
            'dislike_count':str(PostMood.objects.filter(status = "dislike",post_id=post.post_id).count()),
            'view_count':str(PostView.objects.filter(post_id=post.post_id).count()),
            'comment_count':str(PostComments.objects.filter(post_id=post.post_id,status='1').count()),
            'post_file_list':post_file_list,
            'is_like': is_like,
            'is_dislike': is_dislike,
            'is_favorite': is_favorite,
            'comment_list':comment_list,
            'user_id': post.user_id.consumer_id,
            'user_image':user_image,
            'posted_by':post.user_id.consumer_full_name
        }
        data = {'post_data': post_data, 'success': 'true'}
    except Exception, ke:
        print ke
        data = {'message': "Oops! Something went wrong.", 'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def like_dislike_post(request):
    json_obj = json.loads(request.body)
    try:

        if json_obj['mood_status'] == 'like':
            post_like_obj = PostMood.objects.filter(post_id=json_obj['post_id'], user_id=json_obj['user_id'], status = "like")
            if post_like_obj:
                PostMood.objects.filter(post_id=json_obj['post_id'], user_id=json_obj['user_id']).delete()
            else:
                PostMood.objects.filter(post_id=json_obj['post_id'], user_id=json_obj['user_id'], status = "dislike").delete()
                post_like_obj = PostMood.objects.create()
                post_like_obj.user_id = ConsumerProfile.objects.get(consumer_id=json_obj['user_id'])
                post_like_obj.post_id = PostDetails.objects.get(post_id=json_obj['post_id'])
                post_like_obj.creation_date = datetime.now()
                post_like_obj.status = "like"
                post_like_obj.save()
        elif json_obj['mood_status'] == 'dislike':
            post_like_obj = PostMood.objects.filter(post_id=json_obj['post_id'], user_id=json_obj['user_id'],
                                                    status="dislike")
            if post_like_obj:
                PostMood.objects.filter(post_id=json_obj['post_id'], user_id=json_obj['user_id']).delete()
            else:
                PostMood.objects.filter(post_id=json_obj['post_id'], user_id=json_obj['user_id'],
                                        status="like").delete()
                post_like_obj = PostMood.objects.create()
                post_like_obj.user_id = ConsumerProfile.objects.get(consumer_id=json_obj['user_id'])
                post_like_obj.post_id = PostDetails.objects.get(post_id=json_obj['post_id'])
                post_like_obj.creation_date = datetime.now()
                post_like_obj.status = "dislike"
                post_like_obj.save()
        data = {
            'success': 'true', 
            'message': '', 
            'like_count': str(PostMood.objects.filter(post_id=json_obj['post_id'], status = "like").count()),
            'dislike_count': str(PostMood.objects.filter(post_id=json_obj['post_id'], status = "dislike").count())
            }
    except Exception, ke:
        print ke
        data = {'success': 'false', 'message': 'Oops! Something went wrong'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def favourite_post(request):
    json_obj = json.loads(request.body)
    try:
        post_fav_obj = PostFavourite.objects.filter(post_id=json_obj['post_id'], user_id=json_obj['user_id'])
        if json_obj['status'] == "unfavorite":
            post_fav_obj.delete()
        if json_obj['status'] == "favorite":
            if post_fav_obj:
                post_fav_obj.delete()
            post_fav_obj = PostFavourite.objects.create()
            post_fav_obj.user_id = ConsumerProfile.objects.get(consumer_id=json_obj['user_id'])
            post_fav_obj.post_id = PostDetails.objects.get(post_id=json_obj['post_id'])
            post_fav_obj.creation_date = datetime.now()
            post_fav_obj.save()
        data = {'success': 'true', 'message': ''}
    except Exception, ke:
        print ke
        data = {'success': 'false', 'message': 'Oops! Something went wrong'}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def post_comment(request):
    json_obj = json.loads(request.body)
    user_id = json_obj['user_id']
    post_id = json_obj['post_id']
    comment = json_obj['comment']
    try:
        post_comment_obj = PostComments()
        post_comment_obj.user_id = ConsumerProfile.objects.get(consumer_id=user_id)
        post_comment_obj.post_id = PostDetails.objects.get(post_id=post_id)
        post_comment_obj.comment = comment
        post_comment_obj.comment_status = "unread"
        post_comment_obj.status = "1"
        post_comment_obj.creation_date = datetime.now()
        post_comment_obj.save()
        post = post_comment_obj.post_id.description
        cat_name = post_comment_obj.post_id.citylife_category.category_name
        username = post_comment_obj.user_id.consumer_full_name
        city = post_comment_obj.post_id.city_id.city_id.city_name
        #comment_add_mail(post, cat_name, username,city)
        data = {"success": "true", "message": "Comment posted successfully."}
    except Exception, e:
        print "Exception", e
        data = {"success": "false", "message": "Something went wrong"}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def edit_comment(request):
    json_obj = json.loads(request.body)
    comment = json_obj['comment']
    comment_id = json_obj['comment_id']
    try:
        post_comment_obj = PostComments.objects.get(comment_id=comment_id)
        post_comment_obj.comment = comment
        post_comment_obj.updated_date = datetime.now()
        post_comment_obj.comment_status = "unread"
        post_comment_obj.status = "1"
        post_comment_obj.save()
        post = post_comment_obj.post_id.description
        cat_name = post_comment_obj.post_id.citylife_category.category_name
        username = post_comment_obj.user_id.consumer_full_name
        city = post_comment_obj.post_id.city_id.city_id.city_name
        #comment_update_mail(post, cat_name, username,city)
        data = {"success": "true", "message": "Comment updated successfully."}
    except Exception, e:
        print "Exception", e
        data = {"success": "false", "message": "Something went wrong"}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def delete_comment(request):
    json_obj = json.loads(request.body)
    comment_id = json_obj['comment_id']
    try:
        post_comment_obj = PostComments.objects.get(comment_id=comment_id)
        post_comment_obj.status = '0'
        post_comment_obj.deleted_date = datetime.now()
        post_comment_obj.save()
        data = {"success": "true", "message": "Comment deleted successfully."}
    except Exception, e:
        print "Exception", e
        data = {"success": "false", "message": "Something went wrong"}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def like_dislike_comment(request):
    json_obj = json.loads(request.body)
    try:

        if json_obj['mood_status'] == 'like':
            post_like_obj = LikeDislikeComment.objects.filter(comment_id=json_obj['comment_id'], user_id=json_obj['user_id'], status = "like")
            if post_like_obj:
                LikeDislikeComment.objects.filter(comment_id=json_obj['comment_id'], user_id=json_obj['user_id']).delete()
            else:
                LikeDislikeComment.objects.filter(comment_id=json_obj['comment_id'], user_id=json_obj['user_id'], status = "dislike").delete()
                post_like_obj = LikeDislikeComment.objects.create()
                post_like_obj.user_id = ConsumerProfile.objects.get(consumer_id=json_obj['user_id'])
                post_like_obj.comment_id = PostComments.objects.get(comment_id=json_obj['comment_id'])
                post_like_obj.creation_date = datetime.now()
                post_like_obj.status = "like"
                post_like_obj.save()
        elif json_obj['mood_status'] == 'dislike':
            post_like_obj = LikeDislikeComment.objects.filter(comment_id=json_obj['comment_id'], user_id=json_obj['user_id'],
                                                    status="dislike")
            if post_like_obj:
                LikeDislikeComment.objects.filter(comment_id=json_obj['comment_id'], user_id=json_obj['user_id']).delete()
            else:
                LikeDislikeComment.objects.filter(comment_id=json_obj['comment_id'], user_id=json_obj['user_id'],
                                        status="like").delete()
                post_like_obj = LikeDislikeComment.objects.create()
                post_like_obj.user_id = ConsumerProfile.objects.get(consumer_id=json_obj['user_id'])
                post_like_obj.comment_id = PostComments.objects.get(comment_id=json_obj['comment_id'])
                post_like_obj.creation_date = datetime.now()
                post_like_obj.status = "dislike"
                post_like_obj.save()
        data = {'success': 'true', 'message': ''}
    except Exception, ke:
        print ke
        data = {'success': 'false', 'message': 'Oops! Something went wrong'}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def post_reply(request):
    json_obj = json.loads(request.body)
    user_id = json_obj['user_id']
    comment_id = json_obj['comment_id']
    reply = json_obj['reply']
    try:
        post_reply_obj = PostReplys()
        post_reply_obj.user_id = ConsumerProfile.objects.get(consumer_id=user_id)
        post_reply_obj.comment_id = PostComments.objects.get(comment_id=comment_id)
        post_reply_obj.reply = reply
        post_reply_obj.status = "1"
        post_reply_obj.creation_date = datetime.now()
        post_reply_obj.save()

        post = post_reply_obj.comment_id.post_id.description
        cat_name = post_reply_obj.comment_id.post_id.citylife_category.category_name
        username = post_reply_obj.user_id.consumer_full_name
        city = post_reply_obj.comment_id.post_id.city_id.city_id.city_name
        
        #reply_add_mail(post, cat_name, username,city)
        data = {"success": "true", "message": "Reply posted successfully."}
    except Exception, e:
        print "Exception", e
        data = {"success": "false", "message": "Something went wrong"}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def edit_reply(request):
    json_obj = json.loads(request.body)
    reply = json_obj['reply']
    reply_id = json_obj['reply_id']
    try:
        post_reply_obj = PostReplys.objects.get(reply_id=reply_id)
        post_reply_obj.reply = reply
        post_reply_obj.updated_date = datetime.now()
        post_reply_obj.save()
        data = {"success": "true", "message": "Reply updated successfully."}
    except Exception, e:
        print "Exception", e
        data = {"success": "false", "message": "Something went wrong"}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def delete_reply(request):
    json_obj = json.loads(request.body)
    reply_id = json_obj['reply_id']
    try:
        post_reply_obj = PostReplys.objects.get(reply_id=reply_id)
        post_reply_obj.status = '0'
        post_reply_obj.deleted_date = datetime.now()
        post_reply_obj.save()
        data = {"success": "true", "message": "Reply deleted successfully."}
    except Exception, e:
        print "Exception", e
        data = {"success": "false", "message": "Something went wrong"}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def like_dislike_reply(request):
    json_obj = json.loads(request.body)
    try:

        if json_obj['mood_status'] == 'like':
            post_like_obj = LikeDislikeReply.objects.filter(reply_id=json_obj['reply_id'], user_id=json_obj['user_id'], status = "like")
            if post_like_obj:
                LikeDislikeReply.objects.filter(reply_id=json_obj['reply_id'], user_id=json_obj['user_id']).delete()
            else:
                LikeDislikeReply.objects.filter(reply_id=json_obj['reply_id'], user_id=json_obj['user_id'], status = "dislike").delete()
                post_like_obj = LikeDislikeReply.objects.create()
                post_like_obj.user_id = ConsumerProfile.objects.get(consumer_id=json_obj['user_id'])
                post_like_obj.reply_id = PostReplys.objects.get(reply_id=json_obj['reply_id'])
                post_like_obj.creation_date = datetime.now()
                post_like_obj.status = "like"
                post_like_obj.save()
        elif json_obj['mood_status'] == 'dislike':
            post_like_obj = LikeDislikeReply.objects.filter(reply_id=json_obj['reply_id'], user_id=json_obj['user_id'],
                                                    status="dislike")
            if post_like_obj:
                LikeDislikeReply.objects.filter(reply_id=json_obj['reply_id'], user_id=json_obj['user_id']).delete()
            else:
                LikeDislikeReply.objects.filter(reply_id=json_obj['reply_id'], user_id=json_obj['user_id'],
                                        status="like").delete()
                post_like_obj = LikeDislikeReply.objects.create()
                post_like_obj.user_id = ConsumerProfile.objects.get(consumer_id=json_obj['user_id'])
                post_like_obj.reply_id = PostReplys.objects.get(reply_id=json_obj['reply_id'])
                post_like_obj.creation_date = datetime.now()
                post_like_obj.status = "dislike"
                post_like_obj.save()
        data = {'success': 'true', 'message': ''}
    except Exception, ke:
        print ke
        data = {'success': 'false', 'message': 'Oops! Something went wrong'}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def share_citylife(request):
    json_obj = json.loads(request.body)
    try:
        post_obj = PostDetails.objects.get(post_id=json_obj['post_id'])
        share_count = int(post_obj.share) + 1
        post_obj.share = share_count
        post_obj.save()
        data = {'success': 'true', 'message': '','share_count':str(post_obj.share)}
    except Exception, ke:
        print ke
        data = {'success': 'false', 'message': 'Oops! Something went wrong'}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def update_post(request):
    json_obj = json.loads(request.body)
    try:
        category_obj = citylife_category.objects.get(category_id=json_obj['category_id'])
        post_obj = PostDetails.objects.get(post_id=json_obj['post_id'])
        post_obj.citylife_category = category_obj
        post_obj.updation_date = datetime.now()
        post_obj.mood = json_obj['mood']
        post_obj.area = json_obj['area']
        post_obj.title = json_obj['title']
        post_obj.description = json_obj['description']
        post_obj.status = "unread"
        post_obj.save()
        #post_update_mail(category_obj.category_name,post_obj.user_id.consumer_full_name,post_obj.city_id.city_id.city_name)
        #PostFile.objects.filter(post_id=json_obj['post_id']).delete()
        data = {'message': "Post updated successfully", 'success': 'true','post_id' : str(post_obj.post_id)}
    except Exception, ke:
        print ke
        data = {'message': "Oops! Something went wrong.", 'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def delete_post(request):
    json_obj = json.loads(request.body)
    post_id = json_obj['post_id']
    try:
        post_obj = PostDetails.objects.get(post_id=post_id)
        post_obj.status = 'deleted'
        post_obj.deleted_date = datetime.now()
        post_obj.save()
        data = {"success": "true", "message": "Post deleted successfully."}
    except Exception, e:
        print "Exception", e
        data = {"success": "false", "message": "Something went wrong"}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def view_favorite_post(request):
    post_list = []
    json_obj = json.loads(request.body)
    try:
        favourite_post_obj = PostFavourite.objects.filter(user_id = json_obj['user_id'])#.order_by('-id')
        post_id_list = []
        for favourite_post in favourite_post_obj:
            post_id_list.append(str(favourite_post.post_id.post_id))
        post_obj = PostDetails.objects.filter(post_id__in = post_id_list,status__in=["unread","appropriate"])

        os_path = '/home/ec2-user/DigiSpace'
        #os_path = '/home/admin1/Prod_backup/DigiSpace_25/'
        for post in post_obj:
            post_file_obj = PostFile.objects.filter(post_id=post.post_id)
            post_image = ''
            file_width = ''
            file_height = ''
            if post_file_obj:
                for files in post_file_obj:
                    #Image.open
                    try:
                        image = Image.open(os_path + files.post_file.url)
                        post_image = files.post_file.url
                        file_width = files.file_width
                        file_height = files.file_height
                        break
                    except Exception as e:
                        print e
                        pass

            post_like_count = PostMood.objects.filter(status = "like",post_id=post.post_id).count()
            post_dislike_count = PostMood.objects.filter(status = "dislike",post_id=post.post_id).count()
            if post_dislike_count == 0 and post_like_count == 0:
                dislike_like_percentage = 50
            else:
                dislike_like_percentage = (float(post_like_count)/float(PostMood.objects.filter(post_id=post.post_id).count()))*100

            mood = ""
            if dislike_like_percentage >= 0 and dislike_like_percentage < 20:
                mood = "Miserable"
            elif dislike_like_percentage > 20 and dislike_like_percentage < 50:
                mood = "Heartbroken"
            elif dislike_like_percentage == 50:
                mood = "Neutral"
            elif dislike_like_percentage > 50 and dislike_like_percentage < 80:
                mood = "Thrilled"
            elif dislike_like_percentage > 80:
                mood = "Awesome"

            if post_dislike_count == 0 and post_like_count == 0:
                mood = "NA"

            
            posted_time = post.creation_date


            pre_date = datetime.now().strftime("%d/%m/%Y")
            pre_date = datetime.strptime(pre_date, "%d/%m/%Y")
            start_date = posted_time.strftime("%d/%m/%Y")
            start_date = datetime.strptime(start_date, "%d/%m/%Y")

            if start_date == pre_date:
                posted_time = posted_time.strftime("%I.%M%P") + " - Today"
            else:
                posted_time = posted_time.strftime("%I.%M%P - %d %b.%y")

            is_like = 'false'
            is_dislike = 'false'
            is_favorite = 'false'

            try:
                post_mood_obj = PostMood.objects.get(user_id = json_obj['user_id'],post_id=post.post_id)
                if post_mood_obj.status == "like":
                    is_like = "true"
                if post_mood_obj.status == "dislike":
                    is_dislike = "true"
            except:
                pass

            try:
                post_fav_obj = PostFavourite.objects.get(user_id=json_obj['user_id'],post_id=post.post_id)
                is_favorite = "true"
            except:
                pass

            post_data = {
                'post_id': str(post.post_id),
                'description':post.description,
                'category_name':post.citylife_category.category_name,
                'posted_date':posted_time,
                'mood':mood,
                'dislike_like_percentage':str(float(dislike_like_percentage)),
                'like_count':str(PostMood.objects.filter(status = "like",post_id=post.post_id).count()),
                'dislike_count':str(PostMood.objects.filter(status = "dislike",post_id=post.post_id).count()),
                'view_count':str(PostView.objects.filter(post_id=post.post_id).count()),
                'comment_count': str(PostComments.objects.filter(post_id=post.post_id, status='1').count()),
                'post_image':post_image,
                'is_like':is_like,
                'is_dislike':is_dislike,
                'is_favorite':is_favorite,
                'file_width':file_width,
                'file_height':file_height,
                'share_count':str(post.share)
            }
            post_list.append(post_data)
        data = {'post_list': post_list, 'success': 'true'}
    except Exception, ke:
        print ke
        data = {'message': "Oops! Something went wrong.", 'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def view_active_post(request):
    post_list = []
    json_obj = json.loads(request.body)
    try:
        status = ["unread","appropriate"]
        post_obj = PostDetails.objects.filter(user_id = json_obj['user_id'],status__in=status).order_by('-post_id')

        os_path = '/home/ec2-user/DigiSpace'
        #os_path = '/home/admin1/Prod_backup/DigiSpace_25/'
        for post in post_obj:
            post_file_obj = PostFile.objects.filter(post_id=post.post_id)
            post_image = ''
            file_width = ''
            file_height = ''
            if post_file_obj:
                for files in post_file_obj:
                    #Image.open
                    try:
                        image = Image.open(os_path + files.post_file.url)
                        post_image = files.post_file.url
                        file_width = files.file_width
                        file_height = files.file_height
                        break
                    except Exception as e:
                        print e
                        pass

            post_like_count = PostMood.objects.filter(status = "like",post_id=post.post_id).count()
            post_dislike_count = PostMood.objects.filter(status = "dislike",post_id=post.post_id).count()
            if post_dislike_count == 0 and post_like_count == 0:
                dislike_like_percentage = 50
            else:
                dislike_like_percentage = (float(post_like_count)/float(PostMood.objects.filter(post_id=post.post_id).count()))*100

            mood = ""
            if dislike_like_percentage >= 0 and dislike_like_percentage < 20:
                mood = "Miserable"
            elif dislike_like_percentage > 20 and dislike_like_percentage < 50:
                mood = "Heartbroken"
            elif dislike_like_percentage == 50:
                mood = "Neutral"
            elif dislike_like_percentage > 50 and dislike_like_percentage < 80:
                mood = "Thrilled"
            elif dislike_like_percentage > 80:
                mood = "Awesome"

            if post_dislike_count == 0 and post_like_count == 0:
                mood = "NA"

            
            posted_time = post.creation_date


            pre_date = datetime.now().strftime("%d/%m/%Y")
            pre_date = datetime.strptime(pre_date, "%d/%m/%Y")
            start_date = posted_time.strftime("%d/%m/%Y")
            start_date = datetime.strptime(start_date, "%d/%m/%Y")

            if start_date == pre_date:
                posted_time = posted_time.strftime("%I.%M%P") + " - Today"
            else:
                posted_time = posted_time.strftime("%I.%M%P - %d %b.%y")

            is_like = 'false'
            is_dislike = 'false'
            is_favorite = 'false'

            try:
                post_mood_obj = PostMood.objects.get(user_id = json_obj['user_id'],post_id=post.post_id)
                if post_mood_obj.status == "like":
                    is_like = "true"
                if post_mood_obj.status == "dislike":
                    is_dislike = "true"
            except:
                pass

            try:
                post_fav_obj = PostFavourite.objects.get(user_id=json_obj['user_id'],post_id=post.post_id)
                is_favorite = "true"
            except:
                pass

            post_data = {
                'post_id': post.post_id,
                'description':post.description,
                'category_name':post.citylife_category.category_name,
                'posted_date':posted_time,
                'mood':mood,
                'dislike_like_percentage':str(float(dislike_like_percentage)),
                'like_count':str(PostMood.objects.filter(status = "like",post_id=post.post_id).count()),
                'dislike_count':str(PostMood.objects.filter(status = "dislike",post_id=post.post_id).count()),
                'view_count':str(PostView.objects.filter(post_id=post.post_id).count()),
                'comment_count': str(PostComments.objects.filter(post_id=post.post_id, status='1').count()),
                'post_image':post_image,
                'is_like':is_like,
                'is_dislike':is_dislike,
                'is_favorite':is_favorite,
                'file_width':file_width,
                'file_height':file_height,
                'share_count':str(post.share)
            }
            post_list.append(post_data)
        data = {'post_list': post_list, 'success': 'true'}
    except Exception, ke:
        print ke
        data = {'message': "Oops! Something went wrong.", 'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def view_all_post(request):
    post_list = []
    json_obj = json.loads(request.body)
    try:
        post_obj = PostDetails.objects.filter(user_id = json_obj['user_id']).order_by('-post_id')

        os_path = '/home/ec2-user/DigiSpace'
        #os_path = '/home/admin1/Prod_backup/DigiSpace_25/'
        for post in post_obj:
            post_file_obj = PostFile.objects.filter(post_id=post.post_id)
            post_image = ''
            file_width = ''
            file_height = ''
            if post_file_obj:
                for files in post_file_obj:
                    #Image.open
                    try:
                        image = Image.open(os_path + files.post_file.url)
                        post_image = files.post_file.url
                        file_width = files.file_width
                        file_height = files.file_height
                        break
                    except Exception as e:
                        print e
                        pass

            post_like_count = PostMood.objects.filter(status = "like",post_id=post.post_id).count()
            post_dislike_count = PostMood.objects.filter(status = "dislike",post_id=post.post_id).count()
            if post_dislike_count == 0 and post_like_count == 0:
                dislike_like_percentage = 50
            else:
                dislike_like_percentage = (float(post_like_count)/float(PostMood.objects.filter(post_id=post.post_id).count()))*100

            mood = ""
            if dislike_like_percentage >= 0 and dislike_like_percentage < 20:
                mood = "Miserable"
            elif dislike_like_percentage > 20 and dislike_like_percentage < 50:
                mood = "Heartbroken"
            elif dislike_like_percentage == 50:
                mood = "Neutral"
            elif dislike_like_percentage > 50 and dislike_like_percentage < 80:
                mood = "Thrilled"
            elif dislike_like_percentage > 80:
                mood = "Awesome"

            if post_dislike_count == 0 and post_like_count == 0:
                mood = "NA"

            
            posted_time = post.creation_date


            pre_date = datetime.now().strftime("%d/%m/%Y")
            pre_date = datetime.strptime(pre_date, "%d/%m/%Y")
            start_date = posted_time.strftime("%d/%m/%Y")
            start_date = datetime.strptime(start_date, "%d/%m/%Y")

            if start_date == pre_date:
                posted_time = posted_time.strftime("%I.%M%P") + " - Today"
            else:
                posted_time = posted_time.strftime("%I.%M%P - %d %b.%y")

            is_like = 'false'
            is_dislike = 'false'
            is_favorite = 'false'

            try:
                post_mood_obj = PostMood.objects.get(user_id = json_obj['user_id'],post_id=post.post_id)
                if post_mood_obj.status == "like":
                    is_like = "true"
                if post_mood_obj.status == "dislike":
                    is_dislike = "true"
            except:
                pass

            try:
                post_fav_obj = PostFavourite.objects.get(user_id=json_obj['user_id'],post_id=post.post_id)
                is_favorite = "true"
            except:
                pass

            post_data = {
                'post_id': post.post_id,
                'description':post.description,
                'category_name':post.citylife_category.category_name,
                'posted_date':posted_time,
                'mood':mood,
                'dislike_like_percentage':str(float(dislike_like_percentage)),
                'like_count':str(PostMood.objects.filter(status = "like",post_id=post.post_id).count()),
                'dislike_count':str(PostMood.objects.filter(status = "dislike",post_id=post.post_id).count()),
                'view_count':str(PostView.objects.filter(post_id=post.post_id).count()),
                'comment_count': str(PostComments.objects.filter(post_id=post.post_id, status='1').count()),
                'post_image':post_image,
                'is_like':is_like,
                'is_dislike':is_dislike,
                'is_favorite':is_favorite,
                'file_width':file_width,
                'file_height':file_height,
                'share_count':str(post.share),
                'post_status':post.status
            }
            post_list.append(post_data)
        data = {'post_list': post_list, 'success': 'true'}
    except Exception, ke:
        print ke
        data = {'message': "Oops! Something went wrong.", 'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def search_post(request):
    post_id_list = []
    post_list = []
    json_obj = json.loads(request.body)
    try:
        search_keyword = json_obj['search_keyword']
        status = ["unread","appropriate"]
        category_obj = citylife_category.objects.filter(category_name__icontains = search_keyword)
        post_obj = PostDetails.objects.filter(status__in=status).order_by('-post_id')
        post_new_list = []
        for post in post_obj:

            post_like_count = PostMood.objects.filter(status = "like",post_id=post.post_id).count()
            post_dislike_count = PostMood.objects.filter(status = "dislike",post_id=post.post_id).count()
            if post_dislike_count == 0 and post_like_count == 0:
                dislike_like_percentage = 50
            else:
                dislike_like_percentage = (float(post_like_count)/float(PostMood.objects.filter(post_id=post.post_id).count()))*100

            if dislike_like_percentage >= 0 and dislike_like_percentage < 20:
                mood = "miserable"
            elif dislike_like_percentage > 20 and dislike_like_percentage < 50:
                mood = "heartbroken"
            elif dislike_like_percentage == 50:
                mood = "neutral"
            elif dislike_like_percentage > 50 and dislike_like_percentage < 80:
                mood = "thrilled"
            elif dislike_like_percentage > 80:
                mood = "awesome"
            if post_dislike_count == 0 and post_like_count == 0:
                mood = "NA"
            post_data = {
                'post_id': str(post.post_id),
                'description':post.description,
                'category_name':post.citylife_category.category_name,
                'mood':mood
            }
            post_new_list.append(post_data)

        
        post_new_list = [d for d in post_new_list if search_keyword.lower() in d['mood']]

        for post in post_new_list:
            post_id_list.append(post['post_id'])

        post_obj = post_obj.filter(citylife_category__in = category_obj)
        for post in post_obj:
            post_id_list.append(post.post_id)
        
        post_obj = PostDetails.objects.filter(status__in=status).order_by('-post_id')
        post_obj = post_obj.filter(description__icontains = search_keyword)

        for post in post_obj:
            post_id_list.append(post.post_id)

        unique_list = set(post_id_list)        
        unique_list = list(unique_list)

        post_obj = PostDetails.objects.filter(post_id__in = unique_list)

        for post in post_obj:

            post_like_count = PostMood.objects.filter(status = "like",post_id=post.post_id).count()
            post_dislike_count = PostMood.objects.filter(status = "dislike",post_id=post.post_id).count()
            if post_dislike_count == 0 and post_like_count == 0:
                dislike_like_percentage = 50
            else:
                dislike_like_percentage = (float(post_like_count)/float(PostMood.objects.filter(post_id=post.post_id).count()))*100

            mood = ""
            if dislike_like_percentage >= 0 and dislike_like_percentage < 20:
                mood = "Miserable"
            elif dislike_like_percentage > 20 and dislike_like_percentage < 50:
                mood = "Heartbroken"
            elif dislike_like_percentage == 50:
                mood = "Neutral"
            elif dislike_like_percentage > 50 and dislike_like_percentage < 80:
                mood = "Thrilled"
            elif dislike_like_percentage > 80:
                mood = "Awesome"

            if post_dislike_count == 0 and post_like_count == 0:
                mood = "NA"

            post_data = {
                'post_id': str(post.post_id),
                'description':post.description,
                'category_name':post.citylife_category.category_name,
                'mood':mood
            }
            post_list.append(post_data)

            #avg_advert_list = [d for d in advert_list if d['ratings'] >= 1.5 and d['ratings'] < 3.0]

        data = {'post_list': post_list, 'success': 'true','result_count':len(post_list)}
    except Exception, ke:
        print ke
        data = {'message': "Oops! Something went wrong.", 'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def remove_post_file(request):
    json_obj = json.loads(request.body)
    try:
        PostFile.objects.get(post_file_id = json_obj['file_id']).delete()
        data = {'message':'File removed successfully','success': 'true'}
    except Exception, ke:
        print ke
        data = {'message': "Oops! Something went wrong.", 'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt 
def post_add_mail(category_name, username, city):
    try:
        subject = "New CityLife Post"
        description = "Dear Admin,"
        description = description + '\n\n' + 'A new post under the category of ' + category_name + ' has been added by the user ' + username + ' for the city ' + city
        description = description + ' in the CityLife feature of the CityHoopla mobile application. Kindly review the same and if it violates the Listing policy, please mark it as inappropriate.'
        description = description + '\n\n' + 'Best Wishes,\nTeam CityHoopla'

        gmail_user = "donotreply@city-hoopla.com" # "cityhoopla2016"
        gmail_pwd = "Hoopla123#" #"cityhoopla@2016"
        FROM = 'Team CityHoopla<donotreply@city-hoopla.com>' #'CityHoopla Admin: <cityhoopla2016@gmail.com>'
        cc = ['cityhoopla2016@gmail.com']
        TO = ["info@city-hoopla.com"]
        
        TEXT = description
        SUBJECT = subject
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
def post_update_mail(category_name, username, city):
    try:
        subject = "CityLife Post Updated"
        description = "Dear Admin,"
        description = description + '\n\n' + 'A post under the category of ' + category_name + ' has been updated by the user ' + username + ' for the city ' + city
        description = description + ' in the CityLife feature of the CityHoopla mobile application. Kindly review the same and if it violates the Listing policy, please mark it as inappropriate.'
        description = description + '\n\n' + 'Best Wishes,\nTeam CityHoopla'

        gmail_user = "donotreply@city-hoopla.com" # "cityhoopla2016"
        gmail_pwd = "Hoopla123#" #"cityhoopla@2016"
        FROM = 'Team CityHoopla<donotreply@city-hoopla.com>' #'CityHoopla Admin: <cityhoopla2016@gmail.com>'
        cc = ['cityhoopla2016@gmail.com']
        TO = ["info@city-hoopla.com"]
        
        TEXT = description
        SUBJECT = subject
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
def comment_add_mail(post, category_name, username, city):
    try:
        subject = "New CityLife Comment"
        description = "Dear Admin,"
        description = description + '\n\n' + 'A new comment for the post \"'+ post +'\" under the category of ' + category_name + ' has been added by the user ' + username + ' for the city ' + city
        description = description + ' in the CityLife feature of the CityHoopla mobile application. Kindly review the same and if it violates the Listing policy, please mark it as inappropriate.'
        description = description + '\n\n' + 'Best Wishes,\nTeam CityHoopla'

        gmail_user = "donotreply@city-hoopla.com" # "cityhoopla2016"
        gmail_pwd = "Hoopla123#" #"cityhoopla@2016"
        FROM = 'Team CityHoopla<donotreply@city-hoopla.com>' #'CityHoopla Admin: <cityhoopla2016@gmail.com>'
        cc = ['cityhoopla2016@gmail.com']
        TO = ["info@city-hoopla.com"]
        #TO = ["vikas@bynry.com"]
        
        TEXT = description
        SUBJECT = subject
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
def comment_update_mail(post, category_name, username, city):
    try:
        subject = "CityLife Comment Updated"
        description = "Dear Admin,"
        description = description + '\n\n' + 'A comment for the post \"'+ post +'\" under the category of ' + category_name + ' has been updated by the user ' + username + ' for the city ' + city
        description = description + ' in the CityLife feature of the CityHoopla mobile application. Kindly review the same and if it violates the Listing policy, please mark it as inappropriate.'
        description = description + '\n\n' + 'Best Wishes,\nTeam CityHoopla'

        gmail_user = "donotreply@city-hoopla.com" # "cityhoopla2016"
        gmail_pwd = "Hoopla123#" #"cityhoopla@2016"
        FROM = 'Team CityHoopla<donotreply@city-hoopla.com>' #'CityHoopla Admin: <cityhoopla2016@gmail.com>'
        cc = ['cityhoopla2016@gmail.com']
        TO = ["info@city-hoopla.com"]
        #TO = ["vikas@bynry.com"]
        
        TEXT = description
        SUBJECT = subject
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
def reply_add_mail(post, category_name, username, city):
    try:
        subject = "New CityLife Reply"
        description = "Dear Admin,"
        description = description + '\n\n' + 'A new reply for the post \"'+ post +'\" under the category of ' + category_name + ' has been added by the user ' + username + ' for the city ' + city
        description = description + ' in the CityLife feature of the CityHoopla mobile application. Kindly review the same and if it violates the Listing policy, please mark it as inappropriate.'
        description = description + '\n\n' + 'Best Wishes,\nTeam CityHoopla'

        gmail_user = "donotreply@city-hoopla.com" # "cityhoopla2016"
        gmail_pwd = "Hoopla123#" #"cityhoopla@2016"
        FROM = 'Team CityHoopla<donotreply@city-hoopla.com>' #'CityHoopla Admin: <cityhoopla2016@gmail.com>'
        cc = ['cityhoopla2016@gmail.com']
        TO = ["info@city-hoopla.com"]
        #TO = ["vikas@bynry.com"]
        
        TEXT = description
        SUBJECT = subject
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
def reply_update_mail(post, category_name, username, city):
    try:
        subject = "CityLife Reply Updated"
        description = "Dear Admin,"
        description = description + '\n\n' + 'A reply for the post \"'+ post +'\" under the category of ' + category_name + ' has been updated by the user ' + username + ' for the city ' + city
        description = description + ' in the CityLife feature of the CityHoopla mobile application. Kindly review the same and if it violates the Listing policy, please mark it as inappropriate.'
        description = description + '\n\n' + 'Best Wishes,\nTeam CityHoopla'

        gmail_user = "donotreply@city-hoopla.com" # "cityhoopla2016"
        gmail_pwd = "Hoopla123#" #"cityhoopla@2016"
        FROM = 'Team CityHoopla<donotreply@city-hoopla.com>' #'CityHoopla Admin: <cityhoopla2016@gmail.com>'
        cc = ['cityhoopla2016@gmail.com']
        TO = ["info@city-hoopla.com"]
        #TO = ["vikas@bynry.com"]
        
        TEXT = description
        SUBJECT = subject
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
def post_user_mail(username, email_id):
    try:
        subject = "CityLife Post"
        description = "Dear "+username+","
        description = description + '\n\n' + 'Thank you for posting in our CityLife feature. As per our listing policy, the post will be reviewed by our internal team and if deemed inappropriate, will be deleted from the feed.'
        description = description + '\n' + 'The CityHoopla listing policy can be viewed under the settings, MyProfile section of the CityHoopla mobile app.'
        description = description + '\n' + 'Please write to us at info@city-hoopla.com in case you would like to discuss further.'
        description = description + '\n\n' + 'Best Wishes,\nTeam CityHoopla'

        gmail_user = "donotreply@city-hoopla.com" # "cityhoopla2016"
        gmail_pwd = "Hoopla123#" #"cityhoopla@2016"
        FROM = 'Team CityHoopla<donotreply@city-hoopla.com>' #'CityHoopla Admin: <cityhoopla2016@gmail.com>'
        cc = ['cityhoopla2016@gmail.com']
        TO = [email_id]
        #TO = ["vikas@bynry.com"]
        
        TEXT = description
        SUBJECT = subject
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

def sms_post(consumer_number,username):
    authkey = "118994AIG5vJOpg157989f23"
    mobiles = str(consumer_number)

    message = "Dear "+username+","
    message = message + '\n\n' + 'Thank you for posting in our CityLife feature. As per our listing policy, the post will be reviewed by our internal team and if deemed inappropriate, will be deleted from the feed.'
    message = message + '\n' + 'The CityHoopla listing policy can be viewed under the settings, MyProfile section of the CityHoopla mobile app.'
    message = message + '\n' + 'Please write to us at info@city-hoopla.com in case you would like to discuss further.'
    message = message + '\n\n' + 'Best Wishes,\nTeam CityHoopla'
    print message
    sender = "CTHPLA"
    route = "4"
    country = "91"

    values = {
        'authkey': authkey,
        'mobiles': mobiles,
        'message': message,
        'sender': sender,
        'route': route,
        'country': country
    }

    url = "http://api.msg91.com/api/sendhttp.php"
    postdata = urllib.urlencode(values)
    req = urllib2.Request(url, postdata)
    response = urllib2.urlopen(req)
    output = response.read()
    print output