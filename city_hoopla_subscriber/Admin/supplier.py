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
import urllib2

SERVER_URL = "http://52.40.205.128"


# SERVER_URL = "http://127.0.0.1:8000" 

def get_city_category(city_place_id):
    ##    pdb.set_trace()
    cat_list = []
    try:
        cat_city_map = CategoryCityMap.objects.filter(city_place_id=city_place_id)
        for cat in cat_city_map:
            category = Category.objects.get(category_id=str(cat.category_id))
            if category.category_name != "Event Ticket Resale":
                cat_list.append(
                    {'category_id': category.category_id, 'category': category.category_name})
    except Exception, e:
        print 'Exception ', e
    return cat_list

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_subscriber(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        state_list = State.objects.filter(state_status='1').order_by('state_name')
        tax_list = Tax.objects.all()
        category_list = Category.objects.filter(category_status='1').order_by('category_name')

        sales_person_name_list =[]

        sales_person_list = UserProfile.objects.filter(user_status='1',user_role__role_name='Sales')
        for sale in sales_person_list:
            sales_person_name = sale.user_first_name + ' '+ sale.user_last_name
            sales_person_name = str(sales_person_name)
            sales_data={
            "sales_person_name":sales_person_name,
            "sales_person_id":sale.user_id
            }
      
            sales_person_name_list.append(sales_data)

        service_list = ServiceRateCard.objects.filter(service_rate_card_status='1').values('service_name').distinct()
        advert_service_list, item_ids = [], []
        for item in AdvertRateCard.objects.filter(advert_rate_card_status='1'):
            if item.advert_service_name not in item_ids:
                advert_service_list.append(str(item.advert_rate_card_id))
                item_ids.append(item.advert_service_name)

        advert_service_list = AdvertRateCard.objects.filter(advert_rate_card_id__in=advert_service_list,
                                                            advert_rate_card_status='1')

        data = {'sales_person_list':sales_person_name_list,'country_list': get_country(request), 'username': request.session['login_user'],
                'advert_service_list': advert_service_list, 'service_list': service_list, 'tax_list': tax_list,
                'state_list': state_list, 'category_list': get_category(request)}
        return render(request, 'Admin/add_supplier.html', data)


@csrf_exempt
def check_category(request):
    # pdb.set_trace()
    print "IN CHECK NEW CATEGORY"
    has_rate_card = 'false'
    try:
        if request.POST.get('cat_level') != '6':
            if request.POST.get('cat_level') == '1':
                cat_obj = CategoryLevel1.objects.filter(parent_category_id=request.POST.get('category_id'))
                category_color = cat_obj.parent_category_id.category_color
            if request.POST.get('cat_level') == '2':
                cat_obj = CategoryLevel2.objects.filter(parent_category_id=request.POST.get('category_id'))
                category_color = cat_obj.parent_category_id.parent_category_id.category_color
            if request.POST.get('cat_level') == '3':
                cat_obj = CategoryLevel3.objects.filter(parent_category_id=request.POST.get('category_id'))
                category_color = cat_obj.parent_category_id.parent_category_id.parent_category_id.category_color
            if request.POST.get('cat_level') == '4':
                cat_obj = CategoryLevel4.objects.filter(parent_category_id=request.POST.get('category_id'))
                category_color = cat_obj.parent_category_id.parent_category_id.parent_category_id.parent_category_id.category_color
            if request.POST.get('cat_level') == '5':
                cat_obj = CategoryLevel5.objects.filter(parent_category_id=request.POST.get('category_id'))
                category_color = cat_obj.parent_category_id.parent_category_id.parent_category_id.parent_category_id.parent_category_id.category_color
            cat_list = []
            if cat_obj:
                for cat in cat_obj:
                    options_data = '<option value=' + str(cat.category_id) + '>' + cat.category_name + '</option>'

                    cat_list.append(options_data)
                data = {'category_list': cat_list,'category_color':category_color}
            else:
                supplier_obj = Supplier.objects.get(supplier_id = request.POST.get('supplier_id'))
                rate_card = RateCard.objects.filter(city_place_id = str(supplier_obj.city_place_id))
                service_rate_card = CategoryWiseRateCard.objects.filter(city_place_id = str(supplier_obj.city_place_id),
                                                                   category_id=request.POST.get('category_id'))
                if rate_card and service_rate_card:
                    has_rate_card = 'true'
                data = {'success': 'false','has_rate_card':has_rate_card}
        else:
            cat_level = int(request.POST.get('cat_level')) - 1
            supplier_obj = Supplier.objects.get(supplier_id=request.session['supplier_id'])
            rate_card = RateCard.objects.filter(city_place_id=str(supplier_obj.city_place_id))
            service_rate_card = CategoryWiseRateCard.objects.filter(city_place_id=str(supplier_obj.city_place_id),
                                                                    category_id=request.POST.get('category_id'),
                                                                    category_level=cat_level,
                                                                    rate_card_status = '1')
            if rate_card and service_rate_card:
                has_rate_card = 'true'
            data = {'success': 'false', 'has_rate_card': has_rate_card}
    except Exception, e:
        print e
    return HttpResponse(json.dumps(data), content_type='application/json')


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


@csrf_exempt
def save_supplier(request):
    try:
        # pdb.set_trace()
        supplier_obj = Supplier(
            business_name=request.POST.get('business_name'),
            phone_no=request.POST.get('phone_no'),
            secondary_phone_no=request.POST.get('sec_phone_no'),
            supplier_email=request.POST.get('email'),
            secondary_email=request.POST.get('sec_email'),
            address1=request.POST.get('address1'),
            address2=request.POST.get('address2'),
            city_place_id=City_Place.objects.get(city_place_id=request.POST.get('city')),
            country_id=Country.objects.get(country_id=request.POST.get('country')),
            state=State.objects.get(state_id=request.POST.get('state')),
            pincode=Pincode.objects.get(pincode=request.POST.get('pincode')),
            business_details=request.POST.get('business'),
            contact_person=request.POST.get('user_name'),
            contact_email=request.POST.get('user_email'),
            contact_no=request.POST.get('user_contact_no'),
            username=request.POST.get('user_email'),
            sales_person_name=UserProfile.objects.get(user_id=request.POST.get('sale_person_name')),
            sales_person_email=request.POST.get('sale_person_email'),
            sales_person_contact_number=request.POST.get('sale_person_contact_no'),
            title=request.POST.get('title'),
            supplier_status='1'
        )
        supplier_obj.save()
        email = str(supplier_obj.contact_email)
        supplier_id=str(supplier_obj.supplier_id)
        try:
            supplier_add_mail(supplier_obj)
        except:
            pass

        try:
            supplier_obj.logo = request.FILES['logo']
            supplier_obj.save()
        except:
            pass
        data = {
            'success': 'true',
            'message': "Supplier added successfully",
            'email': email,
            'supplier_id':supplier_id
        }
    except Exception, e:
        data = {
            'success': 'false',
            'message': str(e)
        }
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def save_service(request):
    try:
        # pdb.set_trace()
        supplier_id = request.POST.get('supplier_id')
        print "supplier_id", supplier_id
        supplier_obj = Supplier.objects.get(supplier_id=supplier_id)
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

        if premium_service_list:
            check_premium_service = check_date(zip_premium, cat_id, city_place_id, cat_lvl)
            if check_premium_service['success'] == 'false':
                data = {'success': 'false', 'message': check_premium_service['msg']}
                return HttpResponse(json.dumps(data), content_type='application/json')

        chars = string.digits
        pwdSize = 8
        password = ''.join(random.choice(chars) for _ in range(pwdSize))


        category_obj = Category.objects.get(category_id=category_id)
        #service_ratecard_obj = ServiceRateCard.objects.get(duration=duration, service_name='Basic Subscription Plan')

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
            business_created_by=supplier_obj.contact_email
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
                    city_place_id = City_Place.objects.get(city_place_id=city_place_id),
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

        
        data = {'success': 'true',
                'message': 'The subscription is created successfully with transaction ID :' + transaction_code + '. Please proceed with the payment .',
                'business_id': str(business_obj, )
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


def add_subscription_sms(business_obj):
    authkey = "118994AIG5vJOpg157989f23"
    # user_obj = Supplier.objects.get(supplier_id=su_id)
    #    contact_no = user_obj.contact_no
    #    print '---------contact_no------',contact_no

    mobiles = "+919403884595"
    message = "New/Renew subscription activity performed on \t" + str(business_obj.business_id) + "\t" + str(
        business_obj.supplier.business_name) + "\t with \t" + str(business_obj.transaction_code)
    sender = "DGSPCE"
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
def edit_service(request):
    try:
        serv_obj = ServiceRateCard.objects.get(service_name=request.POST.get('service'),
                                               duration=request.POST.get('selected_duration'))
        try:
            supplier_obj = Supplier.objects.get(username=request.POST.get('user_email'))
            try:
                business_obj = Business.objects.get(supplier_id=str(supplier_obj))
            except:
                business_obj = ''
            premium_service_list = request.POST.get('premium_service')
            no_of_days_list = request.POST.get('premium_day_list')
            if (premium_service_list):
                final_data = check_subscription(premium_service_list, no_of_days_list)
                if final_data['success'] == 'true':
                    category_obj = Category.objects.get(category_name=request.POST.get('category'))

                    date_validation = check_date(premium_service_list, request.POST.get('premium_start_date'),
                                                 request.POST.get('premium_end_date'), category_obj, business_obj)
                    if date_validation['success'] == 'true':
                        try:
                            business_obj = Business.objects.get(supplier=supplier_obj)
                            business_obj.category = Category.objects.get(category_name=request.POST.get('category'))
                            business_obj.service_rate_card_id = ServiceRateCard.objects.get(
                                service_name=request.POST.get('service'),
                                duration=request.POST.get('selected_duration'))
                            business_obj.duration = request.POST.get('selected_duration')
                            business_obj.start_date = request.POST.get('duration_start_date')
                            business_obj.end_date = request.POST.get('duration_end_date')
                            business_obj.save()
                        except:
                            chars = string.digits
                            pwdSize = 8
                            password = ''.join(random.choice(chars) for _ in range(pwdSize))
                            business_obj = Business(
                                category=Category.objects.get(category_name=request.POST.get('category')),
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
                        save_working_hours(zipped_wk, business_obj)
                        data = {
                            'success': 'true',
                            'message': "Supplier profile edited successfully",
                            'transaction_code': str(business_obj.transaction_code),
                            'subscriber_id': str(supplier_obj.supplier_id)
                        }
                        try:
                            supplier_edit_service_mail(business_obj)
                        except:
                            pass
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
                premium_service_obj = PremiumService.objects.filter(business_id=business_obj).delete()
                try:
                    business_obj = Business.objects.get(supplier=supplier_obj)
                    business_obj.category = Category.objects.get(category_name=request.POST.get('category'))
                    business_obj.service_rate_card_id = ServiceRateCard.objects.get(
                        service_name=request.POST.get('service'), duration=request.POST.get('selected_duration'))
                    business_obj.duration = request.POST.get('selected_duration')
                    business_obj.start_date = request.POST.get('duration_start_date')
                    business_obj.end_date = request.POST.get('duration_end_date')
                    business_obj.save()
                except:
                    chars = string.digits
                    pwdSize = 8
                    password = ''.join(random.choice(chars) for _ in range(pwdSize))
                    business_obj = Business(
                        category=Category.objects.get(category_name=request.POST.get('category')),
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
                data = {
                    'success': 'true',
                    'message': "Supplier profile edited successfully",
                    'transaction_code': str(business_obj.transaction_code),
                    'subscriber_id': str(supplier_obj.supplier_id)
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


def save_working_hours(zipped_wk, business_obj):
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
def register_supplier(request):
    try:
        # pdb.set_trace()
        print "Taxtype", request.POST.get('selected_tax_type')
        business_id = request.POST.get('business_id')
        chars = string.digits
        pwdSize = 8
        password = ''.join(random.choice(chars) for _ in range(pwdSize))
        business_obj = Business.objects.get(business_id=business_id)

        payment_obj = PaymentDetail(
            business_id=business_obj,
            note=request.POST.get('note'),
            payment_mode=request.POST.get('payment_mode'),
            bank_name=request.POST.get('bank_name'),
            branch_name=request.POST.get('bank_branch_name'),
            cheque_number=request.POST.get('cheque_number'),
            paid_amount=request.POST.get('paid_amount'),
            payable_amount=request.POST.get('payable_amount'),
            total_amount=request.POST.get('generated_amount'),
            tax_type=Tax.objects.get(tax_type=request.POST.get('selected_tax_type')),
            payment_code="PMID" + str(password)
        )
        payment_obj.save()
        payment_code = payment_obj.payment_code

        subscriber_info=[]
        subscriber_id=business_obj.supplier.supplier_id
        subscriber_obj = Supplier.objects.get(supplier_id=subscriber_id)
        business_name = subscriber_obj.business_name
        print '----business_name----',business_name
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


        temp_data ={
        'business_name':subscriber_obj.business_name,
        'subscriber_id':subscriber_obj.supplier_id,
        'subscriber_city':subscriber_obj.city_place_id.city_id.city_name,
        'business_details' :subscriber_obj.business_details,
        'phone_no':subscriber_obj.phone_no,
        'secondary_phone_no':secondary_phone_no,
        'supplier_email':subscriber_obj.supplier_email,
        'secondary_email': secondary_email,
        'contact_person':subscriber_obj.contact_person,
        'contact_no':subscriber_obj.contact_no,
        'contact_email':subscriber_obj.contact_email,
        'address1':subscriber_obj.address1,
        'logo':logo,
        
        }
        subscriber_info.append(temp_data)

        supplier_add_payment_mail(payment_obj)
        payment_sms(payment_obj)


        data = {
            'success': 'true',
            'message': "Supplier added successfully", 'business_id': business_id,
            'message': 'Payment done successfully with Payment ID - ' + payment_code
        }


    except Exception, e:
        data = {
            'success': 'false',
            'message': str(e)
        }
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def register_supplier_review(request):
    try:
        # pdb.set_trace()
        print "Taxtype", request.POST.get('selected_tax_type')
        business_id = request.POST.get('business_id')
        chars = string.digits
        pwdSize = 8
        password = ''.join(random.choice(chars) for _ in range(pwdSize))
        business_obj = Business.objects.get(business_id=business_id)

        payment_obj = PaymentDetail(
            business_id=business_obj,
            note=request.POST.get('note'),
            payment_mode=request.POST.get('payment_mode'),
            bank_name=request.POST.get('bank_name'),
            branch_name=request.POST.get('bank_branch_name'),
            cheque_number=request.POST.get('cheque_number'),
            paid_amount=request.POST.get('paid_amount'),
            payable_amount=request.POST.get('payable_amount'),
            total_amount=request.POST.get('generated_amount'),
            tax_type=Tax.objects.get(tax_type=request.POST.get('selected_tax_type')),
            payment_code="PMID" + str(password)
        )
        payment_obj.save()
        payment_code = payment_obj.payment_code

        subscriber_info=[]
        subscriber_id=business_obj.supplier.supplier_id
        subscriber_obj = Supplier.objects.get(supplier_id=subscriber_id)
        business_name = subscriber_obj.business_name
        print '----business_name----',business_name
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




        business_obj = Business.objects.get(business_id=business_id)
        supplier_id = business_obj.supplier_id
        start_date = business_obj.start_date
        start_date = datetime.strptime(start_date, "%d/%m/%Y")
        end_date = business_obj.start_date
        end_date = datetime.strptime(end_date, "%d/%m/%Y")

        business_data = {
            'business_id': str(business_obj.business_id),
            'category_name': str(business_obj.category.category_name),
            'service_rate_card_duration': int(business_obj.service_rate_card_id.duration),
            'start_date': str(start_date.strftime("%d %b %y")),
            'end_date': str(end_date.strftime("%d %b %y")),
            'flag':"1"
        }

        basic_amount = int(business_obj.service_rate_card_id.cost)
        amount_1 = 0
        amount_2 = 0
        amount_3 = 0
        amount_4 = 0
        amount_5 = 0

        premium_service_list = []

        premium_service_obj = PremiumService.objects.filter(business_id=str(business_obj.business_id))
        for premium_service in premium_service_obj:
            advert_rate_obj = AdvertRateCard.objects.get(advert_service_name=premium_service.premium_service_name,
                                                         duration=premium_service.no_of_days
                                                         )
            if premium_service.premium_service_name == 'No.1 Listing':
                amount_1 = int(advert_rate_obj.cost)
            if premium_service.premium_service_name == 'No.2 Listing':
                amount_2 = int(advert_rate_obj.cost)
            if premium_service.premium_service_name == 'No.3 Listing':
                amount_3 = int(advert_rate_obj.cost)
            if premium_service.premium_service_name == 'Advert Slider':
                amount_4 = int(advert_rate_obj.cost)
            if premium_service.premium_service_name == 'Top Advert':
                amount_5 = int(advert_rate_obj.cost)

            start_date = premium_service.start_date
            start_date = datetime.strptime(start_date, "%d/%m/%Y")
            end_date = premium_service.start_date
            end_date = datetime.strptime(end_date, "%d/%m/%Y")
           

            premium_service_data = {
                'premium_service_name': premium_service.premium_service_name,
                'premium_service_duration': premium_service.no_of_days,
                'premium_service_start_date': str(start_date.strftime("%d %b %y")),
                'premium_service_end_date': str(end_date.strftime("%d %b %y"))
            }
            premium_service_list.append(premium_service_data)

        total_amount = basic_amount + amount_1 + amount_2 + amount_3 + amount_4 + amount_5
        # service_list = ServiceRateCard.objects.filter(service_rate_card_status='1').values('service_name').distinct()
        # advert_service_list, item_ids = [], []
        # for item in AdvertRateCard.objects.filter(advert_rate_card_status='1'):
        #     if item.advert_service_name not in item_ids:
        #         advert_service_list.append(str(item.advert_rate_card_id))
        #         item_ids.append(item.advert_service_name)

        # advert_services_list = []
        # advert_service_list = AdvertRateCard.objects.filter(advert_rate_card_id__in=advert_service_list)
        # print advert_service_list
        # for advert_service in advert_service_list:
        #     try:
        #         premium_obj = PremiumService.objects.get(premium_service_name=advert_service.advert_service_name,
        #                                                  business_id=str(business_obj.business_id),
        #                                                  category_id=str(business_obj.category.category_id)
        #                                                  )
        #         advert_service_data = {
        #             'service_name': advert_service.advert_service_name,
        #             'advert_rate_card_id': advert_service.advert_rate_card_id,
        #             'checked': 'true',
        #             'service_duration': int(premium_obj.no_of_days),
        #             'service_start_date': premium_obj.start_date,
        #             'service_end_date': premium_obj.end_date
        #         }
        #         advert_services_list.append(advert_service_data)
        #     except Exception as e:
        #         advert_service_data = {
        #             'service_name': advert_service.advert_service_name,
        #             'advert_rate_card_id': advert_service.advert_rate_card_id,
        #             'checked': 'false',
        #             'service_duration': 0,
        #             'service_start_date': '',
        #             'service_end_date': ''
        #         }
        #         advert_services_list.append(advert_service_data)
        #         pass

        try:
            payment_obj = PaymentDetail.objects.get(business_id=str(business_obj.business_id))
            tax=round(float(payment_obj.payable_amount), 2)-round(float(payment_obj.total_amount), 2)
            payment_details = {

                'payment_mode': payment_obj.payment_mode,
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

        temp_data ={
        'business_name':subscriber_obj.business_name,
        'subscriber_id':subscriber_obj.supplier_id,
        'subscriber_city':subscriber_obj.city_place_id.city_id.city_name,
        'business_details' :subscriber_obj.business_details,
        'phone_no':subscriber_obj.phone_no,
        'secondary_phone_no':secondary_phone_no,
        'supplier_email':subscriber_obj.supplier_email,
        'secondary_email': secondary_email,
        'contact_person':subscriber_obj.contact_person,
        'contact_no':subscriber_obj.contact_no,
        'contact_email':subscriber_obj.contact_email,
        'address1':subscriber_obj.address1,
        'logo':logo,
        'premium_service_list': premium_service_list,
        'payment_details': payment_details,
        'business_data': business_data,
        'flag':"1"
        }
        subscriber_info.append(temp_data)

        supplier_add_payment_mail(payment_obj)
        payment_sms(payment_obj)


        data = {
            'success': 'true',
            'message': "Supplier added successfully", 'business_id': business_id,
            'message': 'Payment done successfully with Payment ID - ' + payment_code,
            'subscriber_info':subscriber_info,

        }

        print "=====DATA====",data


        data = render(request,'Admin/review_demo.html',data)

        print "=====DATA====",data

    except Exception, e:
        data = {
            'success': 'false',
            'message': str(e)
        }
    return HttpResponse(data)


def payment_sms(payment_obj):
    # pdb.set_trace()
    business_obj = Business.objects.get(business_id=str(payment_obj.business_id.business_id))

    authkey = "118994AIG5vJOpg157989f23"

    mobiles = "+919403884595"
    message = "Payment made by \t" + str(business_obj.business_id) + "\t" + str(
        business_obj.supplier.business_name) + "\t via \t" + str(payment_obj.payment_mode) + "\t mode with \t" + str(
        payment_obj.payment_id) + "\t for the amount \t" + str(payment_obj.payable_amount)
    sender = "DGSPCE"
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
def get_amount(request):
    try:
        premium_service_list = request.POST.get('premium_service_list')
        premium_service_list = str(premium_service_list).split(',')

        premium_day = request.POST.get('premium_day')
        premium_day = str(premium_day).split(',')

        zipped_wk = zip(premium_service_list, premium_day)
        rate_card_obj = ServiceRateCard.objects.get(service_name=request.POST.get('service'),
                                                    duration=request.POST.get('duration'))
        final_cost = int(rate_card_obj.cost)
        if zipped_wk != [('', '')]:

            for serv, day in zipped_wk:
                service_rate_card_obj = AdvertRateCard.objects.get(advert_service_name=serv, duration=day)
                final_cost = int(final_cost) + int(service_rate_card_obj.cost)

        data = {
            'success': 'true',
            'cost': str(final_cost)
        }
    except Exception, e:
        data = {
            'success': 'false',
            'message': str(e)
        }
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def get_basic_subscription_amount(request):
    print "--------------------------------"
    try:
        duration = request.POST.get('duration')
        service_obj = ServiceRateCard.objects.get(duration=duration)
        data = {'success': 'true', 'amount': str(service_obj.cost)}
    except:
        data = {'success': 'true', 'amount': "0.00"}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def get_premium_subscription_amount(request):
    try:
        print "--------------------------------", request.POST
        duration = request.POST.get('duration')
        service_name = request.POST.get('service_name')
        cat_lvl = request.POST.get('cat_lvl')
        cat_id = request.POST.get('cat_id')
        user_id = request.POST.get('supplier_id')
        supplier_obj = Supplier.objects.get(supplier_id=user_id)
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
def get_telephone_subscription_amount(request):
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


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def view_subscriber_list(request):
    try:

        final_list = []
        pre_date = datetime.now().strftime("%d/%m/%Y")
        pre_date = datetime.strptime(pre_date, "%d/%m/%Y")
        date_gap = ''
        advert_count = ''
        sort_by = request.GET.get('sort_by')
        status_var = request.GET.get('status_var')
        start_date_var = request.GET.get('start_date_var')
        end_date_var = request.GET.get('end_date_var')
        city_var = request.GET.get('city_var')
        try:
            if start_date_var:
                start_date = datetime.strptime(start_date_var, "%d/%m/%Y")- timedelta(days=1)
            if end_date_var:
                end_date = datetime.strptime(end_date_var, "%d/%m/%Y")+ timedelta(days=1)
            if start_date_var and end_date_var and status_var and city_var:
                user_list = Supplier.objects.filter(
                    city_place_id=request.GET.get('city_var'),
                    supplier_created_date__range=[start_date, end_date],
                    supplier_status=request.GET.get('status_var')
                )
            elif start_date_var and end_date_var and city_var:
                user_list = Supplier.objects.filter(
                    city_place_id=request.GET.get('city_var'),
                    supplier_created_date__range=[start_date, end_date]
                )
            elif start_date_var and end_date_var and status_var:
                user_list = Supplier.objects.filter(
                    supplier_created_date__range=[start_date, end_date],
                    supplier_status=request.GET.get('status_var')
                )
            elif start_date_var and end_date_var:
                user_list = Supplier.objects.filter(
                    supplier_created_date__range=[start_date, end_date]
                )
            elif city_var :
                print "In CITY Filter"
                user_list = Supplier.objects.filter(
                    city_place_id=request.GET.get('city_var')
                )
                print "user_list",user_list
            elif status_var:
                print "In status "
                user_list = Supplier.objects.filter(
                    supplier_status=request.GET.get('status_var')
                )
            elif sort_by == "oldest_first":
                print "In sort"
                user_list = Supplier.objects.all().order_by('-supplier_created_date').reverse()
            else:
                print "In else"
                user_list = Supplier.objects.all().order_by('-supplier_created_date')

            for user_obj in user_list:
                user_id = str(user_obj.supplier_id)
                business_name = user_obj.business_name
                user_name = user_obj.contact_person
                user_email_id = user_obj.contact_email
                user_contact_no = user_obj.contact_no
                user_city = user_obj.city_place_id.city_id.city_name
                subscription = '---'
                category = '---'
                if user_obj.title:
                    user_title =user_obj.title
                else:
                    user_title=""
                user_name = str(user_title + " " +user_obj.contact_person) 

                if user_obj.logo:
                    logo = SERVER_URL + user_obj.logo.url
                else:
                    logo = SERVER_URL + '/static/assets/layouts/layout2/img/City_Hoopla_Logo.png'

                # subscription_start_date = '---'
                subscription_end_date = '---'

                advert_count = Advert.objects.filter(supplier_id=user_obj, status="1").count()

                subscription_obj = Business.objects.filter(supplier=user_obj)
                # for business in subscription_obj:
                #   start_date=business.start_date
                #   subscription_start_date = datetime.strptime(start_date, "%m/%d/%Y")
                #   subscription_start_date=subscription_start_date.strftime("%d %b %y")
                #   end_date1 = business.end_date
                #                   end_date2 = datetime.strptime(end_date1, "%m/%d/%Y")
                #                   date_gap = (end_date2 - pre_date).days

                print '=========len==========', len(subscription_obj)
                if len(subscription_obj) <= 1:
                    edit = '<a  id="' + str(
                        user_id) + '" title="Edit" class="edit" style="padding: 8px;" data-toggle="modal;" href="/edit-subscriber/?user_id=' + str(
                        user_id) + '"><i class="fa fa-pencil"></i></a>'
                else:
                    edit = '<a  id="' + str(
                        user_id) + '" title="Edit" class="edit" style="padding: 8px;" data-toggle="modal;" href="/edit-subscriber-detail/?user_id=' + str(
                        user_id) + '"><i class="fa fa-pencil"></i></a>'

                # if user_obj.supplier_status == '1':
                #   status= 'Active'
                #   advert = '<a  id="'+str(user_id)+'"  style="text-align: center; padding: 8px;" title="Advert" class="edit" data-toggle="modal" onclick="check_advert(this.id)" ><i class="fa fa-shopping-cart"></i></a>'
                #   #edit = '<a  id="'+str(user_id)+'" title="Edit" class="edit" style="padding: 8px;" data-toggle="modal;" href="/edit-subscriber/?user_id='+str(user_id)+'"><i class="fa fa-pencil"></i></a>'
                #   delete = '<a  id="'+str(user_id)+'" onclick="delete_user_detail(this.id)" style="padding: 8px;"  title="Delete"  ><i class="fa fa-trash"></i></a>'
                #   actions =  advert + edit + delete
                # else:
                #   status = 'Inactive'
                #   active = '<a  id="'+str(user_id)+'" onclick="active_subscriber(this.id);" style="text-align: center;letter-spacing: 5px;width:15%;" title="Activate" class="edit" data-toggle="modal" ><i class="fa fa-repeat"></i></a>'
                #   actions =  active

                list = {'subscriber_category': category,
                        'subscription_end_date': '',
                        'subscription_start_date': '',
                        'subscriber_subscription': subscription,
                        'subscriber_city': user_city,
                        'subscriber_id': user_id,
                        'business_name': business_name,
                        'subscriber_name': user_name,
                        'user_email_id': user_email_id,
                        'user_contact_no': user_contact_no,
                        'logo': logo,
                        'advert_count': advert_count,
                        'status': user_obj.supplier_status
                        }
                final_list.append(list)
            data = {'username': request.session['login_user'],'sort_by':sort_by, 'success': 'true', 'city_list': get_cities(request),
                    'subscriber_list': final_list}
        except IntegrityError as e:
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception, e:
        print 'Exception ', e
    return render(request, 'Admin/supplier_list.html', data)


# TO GET THE STATE
def get_cities(request):
    ##    pdb.set_trace()
    print "IN cities"
    city_list = []
    try:
        city = City_Place.objects.filter(city_status='1')
        for cit in city:
            options_data = {
                'city_id': str(cit.city_place_id),
                'city_name': str(cit.city_id.city_name)

            }
            city_list.append(options_data)
            print city_list
        return city_list
    except Exception, e:
        print 'Exception ', e
        data = {'state_list': 'No states available'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def delete_subscriber(request):
    try:
        user_obj = Supplier.objects.get(supplier_id=request.POST.get('user_id'))
        user_obj.supplier_status = '0'
        user_obj.save()
        supplier_inactive_mail(user_obj)
        supplier_inactive_sms(user_obj)
        data = {'message': 'User Inactivated Successfully', 'success': 'true'}

    except IntegrityError as e:
        print e
    except Exception, e:
        print e
    print "Final Data: ", data
    return HttpResponse(json.dumps(data), content_type='application/json')


def supplier_inactive_sms(user_obj):
    authkey = "118994AIG5vJOpg157989f23"

    contact_no = user_obj.contact_no
    print '---------contact_no------', contact_no

    mobiles = "+919403884595"
    message = "Your profile with CityHoopla has been de-activated, To re-activate, please contact 9028527219 or write us to at info@city-hoopla.com"
    sender = "DGSPCE"
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


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_subscriber(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        # pdb.set_trace()
        flag=request.GET.get("flag")
        print "flag",flag
        business_id=request.GET.get("business_id")
        print "business_id",business_id

        sales_person_name_list =[]

        sales_person_list = UserProfile.objects.filter(user_status='1',user_role__role_name='Sales')
        for sale in sales_person_list:
            sales_person_name = sale.user_first_name + ' '+ sale.user_last_name
            sales_person_name = str(sales_person_name)
            sales_data={
            "sales_person_name":sales_person_name,
            "sales_person_id":sale.user_id
            }
      
            sales_person_name_list.append(sales_data)

        business_obj = Business.objects.filter(supplier=request.GET.get('subscriber_id'))
        print 'business_obj', business_obj

        state_list = State.objects.filter(state_status='1').order_by('state_name')
        subscriber_obj = Supplier.objects.get(supplier_id=request.GET.get('subscriber_id'))
        business_name = subscriber_obj.business_name
        phone_no = subscriber_obj.phone_no
        secondary_phone_no = subscriber_obj.secondary_phone_no
        supplier_email = subscriber_obj.supplier_email
        secondary_email = subscriber_obj.secondary_email
        try:
            display_image = SERVER_URL + subscriber_obj.logo.url
            file_name = str(subscriber_obj.logo)[19:]
        except:
            display_image = ''
            file_name = ''

        address1 = subscriber_obj.address1
        address2 = subscriber_obj.address2
        country_list = Country.objects.filter(country_status='1').order_by('country_name')
        country = subscriber_obj.country_id.country_id
        state = subscriber_obj.state.state_id
        city_list = City_Place.objects.filter(state_id=state, city_status='1')
        city = subscriber_obj.city_place_id
        city_name = subscriber_obj.city_place_id.city_id.city_name
        city_id = subscriber_obj.city_place_id.city_id.city_id
        pincode_list = Pincode.objects.filter(city_id=city_id, pincode_status='1')
        pincode = subscriber_obj.pincode
        business_details = subscriber_obj.business_details
        supplier_id = subscriber_obj.supplier_id
        contact_person = subscriber_obj.contact_person
        contact_no = subscriber_obj.contact_no
        contact_email = subscriber_obj.contact_email
        sales_person_name = subscriber_obj.sales_person_name.user_id
        sales_person_contact_number = subscriber_obj.sales_person_contact_number
        sales_person_email = subscriber_obj.sales_person_email
        title =subscriber_obj.title

        state_list = State.objects.filter(state_status='1').order_by('state_name')
        tax_list = Tax.objects.all()
        category_list = Category.objects.filter(category_status='1').order_by('category_name')

        service_list = ServiceRateCard.objects.filter(service_rate_card_status='1').values('service_name').distinct()
        advert_service_list, item_ids = [], []
        for item in AdvertRateCard.objects.filter(advert_rate_card_status='1'):
            if item.advert_service_name not in item_ids:
                advert_service_list.append(str(item.advert_rate_card_id))
                item_ids.append(item.advert_service_name)

        advert_service_list = AdvertRateCard.objects.filter(advert_rate_card_id__in=advert_service_list,
                                                            advert_rate_card_status='1')

        data = {'title':title,'sales_person_list':sales_person_name_list,'username': request.session['login_user'], 'country_list': country_list, 'country': country,
                'state_list': state_list, 'supplier_email': supplier_email, 'contact_no': contact_no,
                'contact_person': contact_person, 'secondary_email': secondary_email,
                'city_list': city_list, 'state': state, 'city': city, 'pincode_list': pincode_list,
                'business_name': business_name, 'business_details': business_details, 'address2': address2,
                'address1': address1,
                'file_name': file_name, 'display_image': display_image, 'phone_no': phone_no,
                'secondary_phone_no': secondary_phone_no, 'contact_email': contact_email, 'user_pincode': pincode,
                'supplier_id': supplier_id,'flag':flag,'business_id':business_id,
                'sales_person_name': sales_person_name, 'sales_person_contact_number': sales_person_contact_number,
                'sales_person_email': sales_person_email
                }
        if business_obj:
            return render(request, 'Admin/edit_supplier.html', data)
        else:
            data = {'title':title,'sales_person_list':sales_person_name_list,'username': request.session['login_user'], 'country_list': country_list, 'country': country,
                    'state_list': state_list, 'supplier_email': supplier_email, 'contact_no': contact_no,
                    'contact_person': contact_person, 'secondary_email': secondary_email,
                    'city_list': city_list, 'state': state, 'city': city, 'pincode_list': pincode_list,
                    'business_name': business_name, 'business_details': business_details, 'address2': address2,
                    'address1': address1,
                    'file_name': file_name, 'display_image': display_image, 'phone_no': phone_no,
                    'secondary_phone_no': secondary_phone_no, 'contact_email': contact_email, 'user_pincode': pincode,
                    'supplier_id': supplier_id,
                    'sales_person_name': sales_person_name, 'sales_person_contact_number': sales_person_contact_number,
                    'sales_person_email': sales_person_email,'flag':flag,'business_id':business_id,
                    'country_list': get_country(request), 'username': request.session['login_user'],
                    'advert_service_list': advert_service_list, 'service_list': service_list, 'tax_list': tax_list,
                    'state_list': state_list,'category_list': get_category(request)
                    }
            return render(request, 'Admin/edit_supplier_detail.html', data)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_subscriber_detail(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        status = ""
        state_list = State.objects.filter(state_status='1').order_by('state_name')
        country_list = Country.objects.filter(country_status='1').order_by('country_name')
        category_list = Category.objects.filter(category_status='1').order_by('category_name')
        tax_list = Tax.objects.all()
        subscriber_obj = Supplier.objects.get(supplier_id=request.GET.get('user_id'))
        business_name = subscriber_obj.business_name
        phone_no = subscriber_obj.phone_no
        supplier_id = subscriber_obj.supplier_id
        secondary_phone_no = subscriber_obj.secondary_phone_no
        supplier_email = subscriber_obj.supplier_email
        secondary_email = subscriber_obj.secondary_email
        try:
            display_image = SERVER_URL + subscriber_obj.logo.url
            file_name = str(subscriber_obj.logo)[19:]
        except:
            display_image = ''
            file_name = ''

        address1 = subscriber_obj.address1
        address2 = subscriber_obj.address2
        country = subscriber_obj.country_id.country_id
        state = subscriber_obj.state
        city_list = City_Place.objects.filter(state_id=state, city_status='1')
        city = subscriber_obj.city_place_id
        city_id = subscriber_obj.city_place_id.city_id.city_id
        print "CITY", city
        pincode_list = Pincode.objects.filter(city_id=city_id, pincode_status='1')
        pincode = subscriber_obj.pincode
        business_details = subscriber_obj.business_details
        contact_person = subscriber_obj.contact_person
        contact_no = subscriber_obj.contact_no
        contact_email = subscriber_obj.contact_email

        subscription_list = Business.objects.filter(supplier_id=str(subscriber_obj))
        final_subscription_details = []
        print subscription_list
        for subscription in subscription_list:
            rate_card_obj = ServiceRateCard.objects.get(service_rate_card_id=str(subscription.service_rate_card_id),
                                                        duration=subscription.duration)
            final_cost = int(rate_card_obj.cost)
            final_service_list = []
            premium_service_list = PremiumService.objects.filter(business_id=str(subscription))
            if premium_service_list:

                for premium_service in premium_service_list:
                    service_rate_card_obj = AdvertRateCard.objects.get(
                        advert_service_name=premium_service.premium_service_name, duration=premium_service.no_of_days)
                    final_cost = int(final_cost) + int(service_rate_card_obj.cost)

                    service_name = premium_service.premium_service_name
                    start_date = premium_service.start_date
                    end_date = premium_service.end_date
                    service_list = {'service_name': service_name, 'start_date': start_date, 'end_date': end_date}
                    final_service_list.append(service_list)
            else:
                service_list = {'service_name': '---', 'start_date': '---', 'end_date': '---'}
                final_service_list.append(service_list)

            print "=================================", str(subscription)
            check_status = datetime.now()
            check_status = check_status.strftime('%d/%m/%Y')
            try:
                advert_obj = AdvertSubscriptionMap.objects.get(business_id=str(subscription))
                business_obj = Business.objects.get(business_id=str(advert_obj.business_id))
                end_date1 = business_obj.end_date
                if check_status < end_date1:
                    status = "Active"
                else:
                    status = "Inactive"
                advert_id = str(advert_obj.advert_id)
                advert_name = advert_obj.advert_id.advert_name
            except Exception as e:
                advert_id = ''
                advert_name = 'N/A'
                status = 'N/A'

            subscription_details = {'status': status, 'final_cost': final_cost,
                                    'final_service_list': final_service_list, 'advert_id': advert_id,
                                    'advert_name': advert_name}
            final_subscription_details.append(subscription_details)
        data = {'country': country, 'state_list': state_list, 'country_list': country_list, 'supplier_id': supplier_id,
                'final_subscription_details': final_subscription_details, 'username': request.session['login_user'],
                'user_pincode': pincode, 'file_name': file_name, 'display_image': display_image,
                'pincode_list': pincode_list, 'city_list': city_list, 'state': state, 'city': city,
                'state_list': state_list, 'contact_email': contact_email, 'contact_no': contact_no,
                'contact_person': contact_person, 'business_details': business_details, 'address2': address2,
                'address1': address1, 'secondary_email': secondary_email, 'supplier_email': supplier_email,
                'business_name': business_name, 'phone_no': phone_no, 'secondary_phone_no': secondary_phone_no}
        return render(request, 'Admin/edit-subscriber-detail.html', data)


@csrf_exempt
def update_subscriber(request):
    try:
        # pdb.set_trace()
        print "USER", request.POST.get('user_email')
        if request.POST.get('user_email'):
            try:
                supplier_obj = Supplier.objects.get(supplier_id=request.POST.get('supplier_id'))
                supplier_obj.username = request.POST.get('user_email')
                supplier_obj.save()
            except IntegrityError, e:
                print "Exception", e
                data = {'success': 'false', 'message': 'User already exist.'}
                return HttpResponse(json.dumps(data), content_type='application/json')
        print "=======Country", request.POST.get('country')
        supplier_obj = Supplier.objects.get(supplier_id=request.POST.get('supplier_id'))
        supplier_obj.business_name = request.POST.get('business_name')
        supplier_obj.phone_no = request.POST.get('phone_no')
        supplier_obj.secondary_phone_no = request.POST.get('sec_phone_no')
        supplier_obj.country_id = Country.objects.get(country_id=request.POST.get('country'))
        supplier_obj.supplier_email = request.POST.get('email')
        supplier_obj.secondary_email = request.POST.get('sec_email')
        supplier_obj.address1 = request.POST.get('address1')
        supplier_obj.address2 = request.POST.get('address2')
        supplier_obj.city_place_id = City_Place.objects.get(city_place_id=request.POST.get('city'))
        supplier_obj.state = State.objects.get(state_id=request.POST.get('state'))
        supplier_obj.pincode = Pincode.objects.get(pincode=request.POST.get('pincode'))
        supplier_obj.business_details = request.POST.get('business')
        supplier_obj.contact_person = request.POST.get('user_name')
        supplier_obj.contact_no = request.POST.get('user_contact_no')
        supplier_obj.contact_no = request.POST.get('user_contact_no')
        supplier_obj.sales_person_name=UserProfile.objects.get(user_id=request.POST.get('sale_person_name'))
        supplier_obj.sales_person_email = request.POST.get('sale_person_email')
        supplier_obj.sales_person_contact_number = request.POST.get('sale_person_contact_no')
        supplier_obj.title =request.POST.get('title')

        supplier_obj.save()
        if request.POST.get('user_email'):
            supplier_obj.contact_email = request.POST.get('user_email')
            supplier_obj.save()
        try:
            supplier_obj.logo = request.FILES['logo']
        except:
            pass
        supplier_obj.save()
        try:
            supplier_edit_mail(supplier_obj)
        except:
            pass
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


# TO GET THE CATEGOTRY
def get_category(request):
    ##    pdb.set_trace()
    cat_list = []
    try:
        category = Category.objects.filter(category_status='1').order_by('category_name')
        for cat in category:
            if cat.category_name !="Event Ticket Resale":
                cat_list.append(
                    {'category_id': cat.category_id, 'category': cat.category_name})

    except Exception, e:
        print 'Exception ', e
    return cat_list

    # TO GET THE STATE


def get_states(request):
    ##    pdb.set_trace()
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
def review(request):
    try:
        # pdb.set_trace()

        business_id = request.GET.get('business_id')
        business_obj = Business.objects.get(business_id=business_id)

        subscriber_info=[]
        subscriber_id=business_obj.supplier.supplier_id
        subscriber_obj = Supplier.objects.get(supplier_id=subscriber_id)
        state_id = subscriber_obj.state.state_name
        business_name = subscriber_obj.business_name
        print '----business_name----',state_id
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

        print '============business_data',business_data

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

            print 'premium_service_list====',premium_service_list

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
        

        temp_data ={
        'business_name':subscriber_obj.business_name,
        'subscriber_id':subscriber_obj.supplier_id,
        'subscriber_city':subscriber_obj.city_place_id.city_id.city_name,
        'business_details' :subscriber_obj.business_details,
        'phone_no':subscriber_obj.phone_no,
        'secondary_phone_no':secondary_phone_no,
        'supplier_email':subscriber_obj.supplier_email,
        'secondary_email': secondary_email,
        'contact_person':subscriber_obj.contact_person,
        'contact_no':subscriber_obj.contact_no,
        'contact_email':subscriber_obj.contact_email,
        'state_id' : subscriber_obj.state.state_name,
        'city_place_id': subscriber_obj.city_place_id.city_id.city_name,
        'pincode_id': subscriber_obj.pincode.pincode,
        'address1':subscriber_obj.address1,
        'address2':subscriber_obj.address2,
        'logo':logo,
        'premium_service_list': premium_service_list,
        'payment_details': payment_details,
        'business_data': business_data,
        'business_id':business_id,
        'enquiry_service_data':enquiry_service_data,
        'flag':"1"
        }
        subscriber_info.append(temp_data)

        data = {
            'success': 'true',
            'subscriber_info':subscriber_info,'business_id':business_id,'business_name':subscriber_obj.business_name
        }

        print "DATA",data

    except Exception, e:
        data = {
            'success': 'false',
            'message': str(e)
        }
    return render(request, 'Admin/review.html', data)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_supplier_confirm(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        business_id = request.GET.get('business_id')
        business_obj = Business.objects.get(business_id=business_id)

        subscriber_info=[]
        subscriber_id=business_obj.supplier.supplier_id
        subscriber_obj = Supplier.objects.get(supplier_id=subscriber_id)
        business_name = subscriber_obj.business_name

        payment_obj = PaymentDetail.objects.get(business_id=str(business_obj.business_id))
        payment_code = payment_obj.payment_code
  


        
        data = {'message': 'Payment Information for Subscriber ' + business_name +'  is succesfully updated with Payment ID - ' + payment_code,'subscriber_id':subscriber_id}
        return render(request, 'Admin/add_supplier_confirmation.html', data)


@csrf_exempt
def review_payment(request):
    try:
        # pdb.set_trace()
        tax_list = Tax.objects.all()
        flag = request.GET.get('flag')
        print "flag",flag
        advert_id = request.GET.get('advert_id')
        business_id = request.GET.get('business_id')
        business_obj = Business.objects.get(business_id=business_id)

        subscriber_info=[]
        subscriber_id=business_obj.supplier.supplier_id
        subscriber_obj = Supplier.objects.get(supplier_id=subscriber_id)
        business_name = subscriber_obj.business_name


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


        data = {
            'success': 'true',
            'payment_details':payment_details,'tax_list':tax_list,'business_id':business_id,'flag':flag,
            'advert_id':advert_id
        }

        print "DATA",data

    except Exception, e:
        data = {
            'success': 'false',
            'message': str(e)
        }
    return render(request,'Admin/edit_payment.html', data)


def renew_subscription(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        advert_id = request.GET.get('advert_id')
        tax_list = Tax.objects.all()
        advert_obj = Advert.objects.get(advert_id=advert_id)
        advert_name = advert_obj.advert_name
        advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)
        business_obj = Business.objects.get(business_id=str(advert_sub_obj.business_id))

        supplier_id = str(advert_obj.supplier_id)
        print 'supplier_id',supplier_id
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

        data = {'tax_list': tax_list, 'advert_service_list': advert_service_list,'telephone_rate_card':telephone_rate_card,
                'username': request.session['login_user'], 'category_list': get_category(request),
                'country_list': get_country(request), 
                'state_list': get_states(request), 'business_data': business_data, 'advert_name': advert_name,
                'category_lvl1_list': category_lvl1_list,
                'category_lvl2_list': category_lvl2_list,
                'category_lvl3_list': category_lvl3_list,
                'category_lvl4_list': category_lvl4_list,
                'category_lvl5_list': category_lvl5_list,
                'cat_id': cat_id, 'cat_lvl': cat_lvl,'supplier_id':supplier_id
                }
        return render(request, 'Admin/renew_subscription.html', data)

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

        rate_obj = CategoryWiseRateCard.objects.get(
                        service_name='Subscription',
                        category_id=cat_id,
                        category_level=cat_lvl
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
                        category_level=str(premium_service.category_level)
                    )
                    if premium_service.no_of_days == '3':
                        amount_1 = float(rate_obj.cost_for_3_days)
                    if premium_service.no_of_days == '7':
                        amount_1 = float(rate_obj.cost_for_7_days)
                    if premium_service.no_of_days == '30':
                        amount_1 = float(rate_obj.cost_for_30_days)
                    if premium_service.no_of_days == '90':
                        amount_1 = float(rate_obj.cost_for_90_days)
                    if premium_service.no_of_days == '180':
                        amount_1 = float(rate_obj.cost_for_180_days)

                if premium_service.premium_service_name == 'No.2 Listing':
                    rate_obj = CategoryWiseRateCard.objects.get(
                        service_name=premium_service.premium_service_name,
                        category_id=premium_service.category_id,
                        category_level=premium_service.category_level,
                    )
                    if premium_service.no_of_days == '3':
                        amount_2 = float(rate_obj.cost_for_3_days)
                    if premium_service.no_of_days == '7':
                        amount_2 = float(rate_obj.cost_for_7_days)
                    if premium_service.no_of_days == '30':
                        amount_2 = float(rate_obj.cost_for_30_days)
                    if premium_service.no_of_days == '90':
                        amount_2 = float(rate_obj.cost_for_90_days)
                    if premium_service.no_of_days == '180':
                        amount_2 = float(rate_obj.cost_for_180_days)

                if premium_service.premium_service_name == 'No.3 Listing':
                    rate_obj = CategoryWiseRateCard.objects.get(
                        service_name=premium_service.premium_service_name,
                        category_id=premium_service.category_id,
                        category_level=premium_service.category_level,
                    )
                    if premium_service.no_of_days == '3':
                        amount_3 = float(rate_obj.cost_for_3_days)
                    if premium_service.no_of_days == '7':
                        amount_3 = float(rate_obj.cost_for_7_days)
                    if premium_service.no_of_days == '30':
                        amount_3 = float(rate_obj.cost_for_30_days)
                    if premium_service.no_of_days == '90':
                        amount_3 = float(rate_obj.cost_for_90_days)
                    if premium_service.no_of_days == '180':
                        amount_3 = float(rate_obj.cost_for_180_days)

                if premium_service.premium_service_name == 'Advert Slider':
                    rate_obj = RateCard.objects.get(service_name=premium_service.premium_service_name,
                                                    city_place_id=premium_service.city_place_id,
                                                    )
                    if premium_service.no_of_days == '3':
                        amount_4 = float(rate_obj.cost_for_3_days)
                    if premium_service.no_of_days == '7':
                        amount_4 = float(rate_obj.cost_for_7_days)
                    if premium_service.no_of_days == '30':
                        amount_4 = float(rate_obj.cost_for_30_days)
                    if premium_service.no_of_days == '90':
                        amount_4 = float(rate_obj.cost_for_90_days)
                    if premium_service.no_of_days == '180':
                        amount_4 = float(rate_obj.cost_for_180_days)

                if premium_service.premium_service_name == 'Top Advert':
                    rate_obj = RateCard.objects.get(service_name=premium_service.premium_service_name,
                                                    city_place_id=premium_service.city_place_id,
                                                    )
                    if premium_service.no_of_days == '3':
                        amount_5 = float(rate_obj.cost_for_3_days)
                    if premium_service.no_of_days == '7':
                        amount_5 = float(rate_obj.cost_for_7_days)
                    if premium_service.no_of_days == '30':
                        amount_5 = float(rate_obj.cost_for_30_days)
                    if premium_service.no_of_days == '90':
                        amount_5 = float(rate_obj.cost_for_90_days)
                    if premium_service.no_of_days == '180':
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
        print "------------------------------------", enquiry_service_data
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
                'username': request.session['login_user'], 'category_list': get_city_category(city_place_id),
                'business_data': business_data, 'telephone_rate_card': telephone_rate_card,
                'premium_service_list': premium_service_list,'enquiry_service_data':enquiry_service_data,
                'total_amount': float(total_amount), 'basic_amount': basic_amount, 'amount_1': amount_1,
                'amount_2': amount_2, 'amount_3': amount_3, 'amount_4': amount_4, 'amount_5': amount_5,
                'tel_amount_1': tel_amount_1, 'tel_amount_2': tel_amount_2, 'tel_amount_3': tel_amount_3,
                'tel_amount_4': tel_amount_4, 'tel_amount_5': tel_amount_5, 'tel_amount_6': tel_amount_6,
                'category_lvl1_list':category_lvl1_list,
                'category_lvl2_list': category_lvl2_list,
                'category_lvl3_list': category_lvl3_list,
                'category_lvl4_list': category_lvl4_list,
                'category_lvl5_list': category_lvl5_list,'business_id':business_id,
                'cat_id':cat_id,'cat_lvl':cat_lvl,'supplier_id':supplier_id,'flag':flag,'advert_id':advert_id
                }
        return render(request, 'Admin/edit_subscription.html', data)

@csrf_exempt
def update_subscription_plan(request):
    print "-----------------save---------------", request.POST
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
        if premium_service_list:
            check_premium_service = update_check_date(zip_premium, cat_id, business_id, city_place_id, cat_lvl)
            if check_premium_service['success'] == 'false':
                data = {'success': 'false', 'message': check_premium_service['msg']}
                return HttpResponse(json.dumps(data), content_type='application/json')

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
        
        data = {'success': 'true',
                'message': 'The subscription is updated successfully with transaction ID :' + transaction_code + '. Please proceed with the payment .',
                'business_id': str(business_obj)
                }
    except Exception as e:
        print e
        data = {'success': 'false', 'message': e}
    return HttpResponse(json.dumps(data), content_type='application/json')

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
    try:
        print "--------------------------------", request.POST

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
            # pdb.set_trace()
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
        print '----------------------------'
        supplier_edit_payment_mail_user(business_obj)
        supplier_edit_payment_sms(business_obj)
        print '----------------------------'

        data = {'success': 'true', 'message': 'Payment done successfully with Payment ID - ' + payment_obj.payment_code}
    except Exception as e:
        print e
        data = {'success': 'true', 'message': e}
    return HttpResponse(json.dumps(data), content_type='application/json')


def supplier_edit_payment_mail_user(business_obj):
    print "business_obj-------->", business_obj
    contact_person = str(business_obj.supplier.contact_person)
    contact_email = str(business_obj.supplier.contact_email)
    gmail_user = "cityhoopla2016"
    gmail_pwd = "cityhoopla@2016"
    FROM = 'CityHoopla Admin: <cityhoopla2016@gmail.com>'
    TO = [contact_email]
    # pdb.set_trace()
    try:
        TEXT = "Dear " + contact_person + ",\n\n" + "Your payment for City Hoopla Subscription with Transaction ID " + str(
            business_obj.transaction_code) + " is processed successfully. Please proceed for Addition of Advert.\nFor any queries contact City Hoopla Admin." + '\n\n' + "Thank You," + '\n' + "City Hoopla Team"
        SUBJECT = "City Hoopla Subscription Payment Processed Successfully!"
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


def supplier_edit_payment_sms(business_obj):
    contact_person = str(business_obj.supplier.contact_person)
    contact_no = str(business_obj.supplier.contact_no)
    print 'contact_no', contact_no
    authkey = "118994AIG5vJOpg157989f23"
    # user_obj = Supplier.objects.get(supplier_id=su_id)
    #    contact_no = user_obj.contact_no
    #    print '---------contact_no------',contact_no

    mobiles = contact_no
    message = "Dear " + contact_person + ",\n" + " Your City Hoopla Subscription Payment has been processed Successfully."
    sender = "DGSPCE"
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
def check_advert(request):
    try:
        print "ID---------", request.POST.get('business_id')
        service_obj = PaymentDetail.objects.filter(business_id=request.POST.get('business_id'))
        if service_obj:
            message = "true"
        else:
            message = "false"

        data = {
            'success': 'true', 'message': message
        }
    except Exception, e:
        print e
        data = {
            'success': 'false',
        }
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def update_subscriber_detail(request):
    try:
        supplier_obj = Supplier.objects.get(username=request.POST.get('user_email'))
        business_obj = Business.objects.get(supplier_id=supplier_obj)
        try:
            payment_obj = PaymentDetail.objects.get(business_id=business_obj)
            payment_obj.note = request.POST.get('note')
            payment_obj.payment_mode = request.POST.get('payment_mode')
            payment_obj.bank_name = request.POST.get('bank_name')
            payment_obj.branch_name = request.POST.get('bank_branch_name')
            payment_obj.cheque_number = request.POST.get('cheque_number')
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
            business_obj = Business.objects.get(supplier_id=str(supplier_obj.supplier_id))

            payment_obj = PaymentDetail(
                business_id=business_obj,
                note=request.POST.get('note'),
                payment_mode=request.POST.get('payment_mode'),
                bank_name=request.POST.get('bank_name'),
                branch_name=request.POST.get('bank_branch_name'),
                cheque_number=request.POST.get('cheque_number'),
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
            'user_id': str(supplier_obj.supplier_id)
        }
        supplier_edit_payment_mail(payment_obj)
    except Exception, e:
        data = {
            'success': 'false',
            'message': str(e)
        }

    return HttpResponse(json.dumps(data), content_type='application/json')


def check_subscription(premium_service_list, premium_day):
    print '==in subscruiption function==================='
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
            print '=========in try============'
            service_rate_card_obj = AdvertRateCard.objects.get(advert_service_name=serv, duration=day)

        except Exception, e:
            print '=============in except================='
            print '==========e=============', e
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


# def check_date(premium_service_list,premium_start_date_list,premium_end_date_list,category_obj,business_obj):
#   premium_service_list = premium_service_list
#   premium_service_list = str(premium_service_list).split(',')

#   premium_start_date_list = str(premium_start_date_list).split(',')
#   premium_end_date_list = str(premium_end_date_list).split(',')

#   zipped_wk = zip(premium_service_list,premium_start_date_list,premium_end_date_list)
#   service_list= []
#   start_day_list= []
#   end_day_list= []
#   false_status = 1    
#   slider_status = 1
#   print '===============zipped_wk=============',zipped_wk
#   for service,start_date,end_date in zipped_wk:
#       print '===========start date=======',start_date
#       print '===========end date=======',end_date

#       if service=='Advert Slider':
#           if business_obj=='':
#               service_rate_card_obj = PremiumService.objects.filter(Q(premium_service_name=service) & Q(Q(start_date__range = (start_date,end_date)) | Q(end_date__range=(start_date,end_date)) | Q(start_date__lte=start_date,end_date__gte=end_date)))
#           else:
#               business_id_list = Business.objects.all().exclude(business_id=str(business_obj))
#               #service_rate_card_obj = PremiumService.objects.filter(premium_service_name=service,start_date__lte=start_date,end_date__gte=start_date,business_id__in=business_id_list)
#               service_rate_card_obj = PremiumService.objects.filter(Q(premium_service_name=service) & Q(Q(start_date__range = (start_date,end_date)) | Q(end_date__range=(start_date,end_date)) | Q(start_date__lte=start_date,end_date__gte=end_date)) & Q(business_id__in=business_id_list))

#           if len(service_rate_card_obj)>=10: 
#               slider_status = 0
#           else:
#               slider_status = 1


#       elif service=='Top Advert':
#           try:
#               if business_obj=='':
#                   service_rate_card_obj = PremiumService.objects.get(Q(premium_service_name=service) & Q(Q(start_date__range = (start_date,end_date)) | Q(end_date__range=(start_date,end_date)) | Q(start_date__lte=start_date,end_date__gte=end_date)))
#                   #service_rate_card_obj = PremiumService.objects.get(Q(Q(start_date__range = (start_date,end_date)) | Q(end_date__range=(start_date,end_date)) | Q(start_date__lte=start_date,end_date__gte=end_date)))


#               else:
#                   business_id_list = Business.objects.all().exclude(business_id=str(business_obj))
#                   service_rate_card_obj = PremiumService.objects.get(Q(premium_service_name=service) & Q(Q(start_date__range = (start_date,end_date)) | Q(end_date__range=(start_date,end_date)) | Q(start_date__lte=start_date,end_date__gte=end_date)) & Q(business_id__in=business_id_list))

#               service_list.append(str(service))
#               start_day_list.append(service_rate_card_obj.start_date)
#               end_day_list.append(service_rate_card_obj.end_date)

#               false_status = 0

#           except Exception,e:
#               print '=========e================',e
#               false_status = 1

#       else:
#           try:
#               business_obj_list = Business.objects.filter(category=category_obj.category_id)

#               if(business_obj==''):
#                   service_rate_card_obj = PremiumService.objects.get(Q(premium_service_name=service) & Q(Q(start_date__range = (start_date,end_date)) | Q(end_date__range=(start_date,end_date)) | Q(start_date__lte=start_date,end_date__gte=end_date)) & Q(business_id__in=business_obj_list))
#               else:
#                   business_id_list = Business.objects.filter(category=category_obj.category_id).exclude(business_id=str(business_obj))


#                   service_rate_card_obj = PremiumService.objects.get(Q(premium_service_name=service) & Q(Q(start_date__range = (start_date,end_date)) | Q(end_date__range=(start_date,end_date)) | Q(start_date__lte=start_date,end_date__gte=end_date)) & Q(business_id__in=business_id_list))

#               service_list.append(str(service))
#               start_day_list.append(service_rate_card_obj.start_date)
#               end_day_list.append(service_rate_card_obj.end_date)

#               false_status = 0

#           except Exception,e:
#               false_status = 1


#   if false_status == 1 and slider_status == 1:
#       data={
#               'success':'true',
#       }

#   if false_status == 0 and slider_status == 0:
#       zipped_list = zip(service_list,start_day_list,end_day_list)
#       message = "Package for Premium Service(s) "
#       for i,j,k in zipped_list:
#           message = message + str(i) + " " + "from "+str(j)+" to " + str(k) + ", \n" 

#       message = message[:-3] + " already exists"

#       if slider_status == 0:
#           message = message + " and Advert slider for selected date is not available"

#       data={
#               'success':'false',
#               'message':message
#           }

#   if false_status == 1 and slider_status == 0:

#       message = "Package for Premium Service(s) "

#       if slider_status == 0:
#           message = message + "\n Advert slider for selected date is not available"

#       data={
#               'success':'false',
#               'message':message
#           }

#   if false_status == 0 and slider_status == 1:
#       zipped_list = zip(service_list,start_day_list,end_day_list)
#       message = "Package for Premium Service(s) "
#       for i,j,k in zipped_list:
#           message = message + str(i) + " " + "from "+str(j)+" to " + str(k) + ", \n" 

#       message = message[:-3] + " already exists"


#       data={
#               'success':'false',
#               'message':message
#           }       

#   return data         

def supplier_add_mail(supplier_obj):
    gmail_user = "cityhoopla2016"
    gmail_pwd = "cityhoopla@2016"
    FROM = 'CityHoopla Admin: <cityhoopla2016@gmail.com>'
    TO = ['cityhoopla2016@gmail.com']
    try:
        TEXT = "Hi Admin,\nSubscriber " + str(supplier_obj.contact_person) + " " + "with Business " + str(
            supplier_obj.business_name) + " " + "has been added successfully.\nTo view complete details visit portal and follow - Customers -> Subscribers" + '\n\n' + "Thank You," + '\n' + "CityHoopla Team"
        SUBJECT = "Subscriber Added Successfully!"
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


def supplier_add_service_mail(business_obj):
    gmail_user = "cityhoopla2016"
    gmail_pwd = "cityhoopla@2016"
    FROM = 'CityHoopla Admin: <cityhoopla2016@gmail.com>'
    TO = ['cityhoopla2016@gmail.com']
    # pdb.set_trace()
    try:
        TEXT = "Hi Admin,\nSubscriber " + str(business_obj.supplier.contact_person) + " " + "with Business " + str(
            business_obj.supplier.business_name) + " " + "has been added successfully.\nTransaction ID " + str(
            business_obj.transaction_code) + " for this transaction has been generated successfully.\nTo view complete details visit portal and follow - Customers -> Subscribers" + '\n\n' + "Thank You," + '\n' + "CityHoopla Team"
        SUBJECT = "Subscriber Added Successfully!"
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


def supplier_add_payment_mail(payment_obj):
    gmail_user = "cityhoopla2016"
    gmail_pwd = "cityhoopla@2016"
    FROM = 'CityHoopla Admin: <cityhoopla2016@gmail.com>'
    TO = ['cityhoopla2016@gmail.com']
    business_obj = Business.objects.get(business_id=str(payment_obj.business_id.business_id))
    supplier_id = Supplier.objects.get(supplier_id=str(business_obj.supplier_id))
    # pdb.set_trace()
    try:
        TEXT = "Hi Admin,\nSubscriber " + str(supplier_id.contact_person) + " " + "with Business " + str(
            supplier_id.business_name) + " " + "has been added successfully.\nPayment ID" + str(
            payment_obj.payment_code) + " for this payment has been generated successfully. \nTo view complete details visit portal and follow - Customers -> Subscribers" + '\n\n' + "Thank You," + '\n' + "CityHoopla Team"
        SUBJECT = "Subscriber Added Successfully!"
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


def supplier_edit_mail(supplier_obj):
    gmail_user = "cityhoopla2016"
    gmail_pwd = "cityhoopla@2016"
    FROM = 'CityHoopla Admin: <cityhoopla2016@gmail.com>'
    TO = ['cityhoopla2016@gmail.com']
    try:
        TEXT = "Hi Admin,\nSubscriber " + str(supplier_obj.contact_person) + " " + "with Business " + str(
            supplier_obj.business_name) + " " + "has been updated successfully.\nTo view complete details visit portal and follow - Customers -> Subscribers" + '\n\n' + "Thank You," + '\n' + "CityHoopla Team"
        SUBJECT = "Subscriber Updated Successfully!"
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


def supplier_edit_service_mail(business_obj):
    gmail_user = "cityhoopla2016"
    gmail_pwd = "cityhoopla@2016"
    FROM = 'CityHoopla Admin: <cityhoopla2016@gmail.com>'
    TO = ['cityhoopla2016@gmail.com']
    # pdb.set_trace()
    try:
        TEXT = "Hi Admin,\nSubscriber " + str(business_obj.supplier.contact_person) + " " + "with Business " + str(
            business_obj.supplier.business_name) + " " + "has been updated successfully. \nTransaction ID " + str(
            business_obj.transaction_code) + " for this transaction has been generated successfully.\nTo view complete details visit portal and follow - Customers -> Subscribers" + '\n\n' + "Thank You," + '\n' + "CityHoopla Team"
        SUBJECT = "Subscriber Updated Successfully!"
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


def supplier_edit_payment_mail(payment_obj):
    gmail_user = "cityhoopla2016"
    gmail_pwd = "cityhoopla@2016"
    FROM = 'CityHoopla Admin: <cityhoopla2016@gmail.com>'
    TO = ['cityhoopla2016@gmail.com']
    business_obj = Business.objects.get(business_id=str(payment_obj.business_id.business_id))
    supplier_id = Supplier.objects.get(supplier_id=str(business_obj.supplier_id))
    # pdb.set_trace()
    try:
        TEXT = "Hi Admin,\nSubscriber " + str(supplier_id.contact_person) + " " + "with Business " + str(
            supplier_id.business_name) + " " + "has been updated successfully.\nPayment ID" + str(
            payment_obj.payment_code) + " for this payment has been generated successfully.\nTo view complete details visit portal and follow - Customers -> Subscribers" + '\n\n' + "Thank You," + '\n' + "CityHoopla Team"
        SUBJECT = "Subscriber Updated Successfully!"
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


def supplier_inactive_mail(user_obj):
    gmail_user = "cityhoopla2016"
    gmail_pwd = "cityhoopla@2016"
    FROM = 'CityHoopla Admin: <cityhoopla2016@gmail.com>'
    TO = ['cityhoopla2016@gmail.com']
    # pdb.set_trace()
    try:
        TEXT = "Hi Admin,\nSubscriber " + str(user_obj.contact_person) + " " + "with Business " + str(
            user_obj.business_name) + " " + "deactivated successfully.\n\nThank You," + '\n' + "CityHoopla Team"
        SUBJECT = "Subscriber Deactivated Successfully!"
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
def active_subscriber(request):
    try:
        subscriber_obj = Supplier.objects.get(supplier_id=request.POST.get('subscriber_id'))
        subscriber_obj.supplier_status = '1'
        subscriber_obj.save()
        supplier_activate_mail(subscriber_obj)
        data = {'message': 'Subscriber activated Successfully', 'success': 'true'}

    except IntegrityError as e:
        print e
    except Exception, e:
        print e
    return HttpResponse(json.dumps(data), content_type='application/json')


def supplier_activate_mail(user_obj):
    gmail_user = "cityhoopla2016"
    gmail_pwd = "cityhoopla@2016"
    FROM = 'CityHoopla Admin: <cityhoopla2016@gmail.com>'
    TO = ['cityhoopla2016@gmail.com']
    # pdb.set_trace()
    try:
        TEXT = "Hi Admin,\nSubscriber " + str(user_obj.contact_person) + " " + "with Business " + str(
            user_obj.business_name) + " " + "activated successfully.\n\nThank You," + '\n' + "CityHoopla Team"
        SUBJECT = "Subscriber Activated Successfully!"
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
