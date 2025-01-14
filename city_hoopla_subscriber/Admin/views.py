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
from captcha_form import CaptchaForm
from django.shortcuts import *
from digispaceapp.models import UserProfile
import dateutil.relativedelta

# importing mysqldb and system packages
import MySQLdb, sys
from django.db.models import Q
from django.db.models import F
from django.db import transaction
import pdb
import csv
import json
#importing exceptions
from django.db import IntegrityError
from captcha_form import CaptchaForm
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
import random

#SERVER_URL = "http://52.66.133.35"   
SERVER_URL = "http://192.168.0.4:8088"


def about_us(request):
    return render(request,'terms_and_condition/About_us.html')

def faq(request):
    return render(request,'terms_and_condition/FAQ.html')

def listing_policy(request):
    return render(request,'terms_and_condition/Listing_Policy.html')

def privacy_policy(request):
    return render(request,'terms_and_condition/PrivacyPolicy.html')

def terms_of_use(request):
    return render(request,'terms_and_condition/Terms_of_use.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def rate_card(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        cat_list= []
        city_list = City_Place.objects.all()
        first_city = city_list[0]
        first_city_name = first_city.city_id.city_name
        first_city_currency = first_city.currency
        city_name_list = []
        telephone_rate_card_list = []
        for city in city_list:
            rate_card_status = '0'
            active_business_advert = 'false'
            rate_card_obj = RateCard.objects.filter(city_place_id=str(city.city_place_id), rate_card_status='1')
            if rate_card_obj:
                rate_card_status = '1'
            if not rate_card_obj:
                rate_card_obj = RateCard.objects.filter(city_place_id=str(city.city_place_id), rate_card_status='0')
                rate_card_status = '0'
            business_obj = Business.objects.filter(city_place_id=str(city.city_place_id))
            pre_date = datetime.now().strftime("%d/%m/%Y")
            pre_date = datetime.strptime(pre_date, "%d/%m/%Y")

            for business in business_obj:
                end_date = business.end_date
                end_date = datetime.strptime(end_date, "%d/%m/%Y")
                date_gap = (end_date - pre_date).days
                if int(date_gap) >= 0:
                    active_business_advert = 'true'

            if rate_card_obj:
                has_rate_card = 'true'
            else:
                has_rate_card = 'false'
            city_data = {
                'city_id':str(city.city_place_id),
                'city_name':str(city.city_id.city_name),
                'has_rate_card':has_rate_card,
                'rate_card_status':rate_card_status,
                'active_business_advert':active_business_advert
            }
            city_name_list.append(city_data)

        cat_city_obj = CategoryCityMap.objects.filter(city_place_id=str(first_city))
        for objs in cat_city_obj:
            cat_obj = Category.objects.get(category_id=str(objs.category_id))
            if cat_obj.category_name != 'Event Ticket Resale':
                cat_data = {'cat_id': str(cat_obj.category_id), 'cat_name': cat_obj.category_name}
                cat_list.append(cat_data)
        rate_card_list=[]
        rate_card_obj = RateCard.objects.filter(city_place_id=str(first_city),rate_card_status='1')
        if rate_card_obj:
            for rate_card in rate_card_obj:
                if rate_card.service_name == "Advert Slider":
                    rate_card_data = {
                        'service_name':rate_card.service_name,
                        'cost_for_3days':str( "%0.2f" % float(rate_card.cost_for_3_days)),
                        'cost_for_7days':str( "%0.2f" % float(rate_card.cost_for_7_days)),
                        'cost_for_30days':str( "%0.2f" % float(rate_card.cost_for_30_days)),
                        'cost_for_90days':str( "%0.2f" % float(rate_card.cost_for_90_days)),
                        'cost_for_180days':str( "%0.2f" % float(rate_card.cost_for_180_days))
                    }
                    rate_card_list.append(rate_card_data)
                else:
                    rate_card_data = {
                        'service_name': rate_card.service_name,
                        'cost_for_3days': str("%0.2f" % float(rate_card.cost_for_3_days)),
                        'cost_for_7days': str("%0.2f" % float(rate_card.cost_for_7_days)),
                        'cost_for_30days': str("%0.2f" % float(rate_card.cost_for_30_days)),
                        'cost_for_90days': rate_card.cost_for_90_days,
                        'cost_for_180days': rate_card.cost_for_180_days
                    }
                    rate_card_list.append(rate_card_data)
        else:
            rate_card_data = {
                'service_name': "Advert Slider",
                'cost_for_3days': "0.00",
                'cost_for_7days': "0.00",
                'cost_for_30days': "0.00",
                'cost_for_90days': "0.00",
                'cost_for_180days': "0.00",
            }
            rate_card_list.append(rate_card_data)
            rate_card_data = {
                'service_name': "Top Advert",
                'cost_for_3days': "0.00",
                'cost_for_7days': "0.00",
                'cost_for_30days': "0.00",
                'cost_for_90days': "N/A",
                'cost_for_180days': "N/A",
            }
            rate_card_list.append(rate_card_data)
        telephone_rate_card_obj = TelephoneEnquiryRateCard.objects.filter(city_place_id=str(first_city), rate_card_status='1')
        if telephone_rate_card_obj:
            for telephone_rate_card in telephone_rate_card_obj:
                telephone_rate_card_data = {
                    'service_name': telephone_rate_card.service_name,
                    'cost_for_3days': str("%0.2f" % float(telephone_rate_card.cost_for_3_days)),
                    'cost_for_7days': str("%0.2f" % float(telephone_rate_card.cost_for_7_days)),
                    'cost_for_30days': str("%0.2f" % float(telephone_rate_card.cost_for_30_days)),
                    'cost_for_90days': str("%0.2f" % float(telephone_rate_card.cost_for_90_days)),
                    'cost_for_180days': str("%0.2f" % float(telephone_rate_card.cost_for_180_days))
                }
                telephone_rate_card_list.append(telephone_rate_card_data)
        else:
            rate_cards = ['Platinum','Diamond','Gold','Silver','Bronze','Value']
            for rates in rate_cards:
                telephone_rate_card_data = {
                    'service_name': rates,
                    'cost_for_3days': "0.00",
                    'cost_for_7days': "0.00",
                    'cost_for_30days': "0.00",
                    'cost_for_90days': "0.00",
                    'cost_for_180days': "0.00",
                }
                telephone_rate_card_list.append(telephone_rate_card_data)
        print "city_name_list",city_name_list
        data = {
            'username':request.session['login_user'],'telephone_rate_card_list':telephone_rate_card_list,
            'city_list':city_name_list, 'cat_list':cat_list,'rate_card_list':rate_card_list,
            'first_city_name':first_city_name, 'first_city_currency':first_city_currency
        }
        return render(request,'Admin/rate_card.html',data)

def login_open(request):
    if request.user.is_authenticated():
        return redirect('/index/')
    else:
        logout(request)
        form = CaptchaForm()
        return render_to_response('Admin/user_login.html', dict(
            form=form
        ), context_instance=RequestContext(request))

def backoffice(request):
    logout(request)
    form = CaptchaForm()
##    if request.user.is_authenticated():
##        return redirect('/dashboard/')
    #return render_to_response('index.html')
    return render(request,'Admin/user_login.html', dict(form=form))

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dashboard(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        subscriber_obj = Supplier.objects.filter(supplier_status = '1')
        FY_MONTH_LIST = [1,2,3,4,5,6,7,8,9,10,11,12]
        today = date.today()
        start_date = date(today.year,01,01)
        end_date = date(today.year,12,31) 
        monthly_count = []
        # jan,feb,mar,apr,may,jun,jul,aug,sep,octo,nov,dec
        subscriptions = Business.objects.filter(business_created_date__range=[start_date,end_date]).extra(select={'month': "EXTRACT(month FROM business_created_date)"}).values('month').annotate(count=Count('business_id'))
        print "subscriptions",subscriptions
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
        count_zero = 0
        count_first = 0
        count_second = 0
        count_third = 0

        consumer_list0= ConsumerProfile.objects.filter(last_time_login__regex = ' 0:').count()
        count_zero = count_zero + consumer_list0

        for hour in range(0,9):
            print "HOur",hour
            hour = ' 0'+ str(hour) + ':'
            print "hour",hour
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
        temp_var0 = 0
        temp_var1 = 0
        temp_var2 = 0
        temp_var3 = 0
        data = {}

        
        ############################Last 1 week new subscription view###############################
        current_date = datetime.now()
        first = calendar.day_name[current_date.weekday()]

        last_date = (datetime.now() - timedelta(days=7))
        last_date2 = calendar.day_name[last_date.weekday()]

        list = []
        consumer_obj_list = Business.objects.filter(business_created_date__range=[last_date,current_date])
        mon=tue=wen=thus=fri=sat=sun=0
        if consumer_obj_list:
            for consumer_obj in consumer_obj_list:
                business_created_date=consumer_obj.business_created_date
                consumer_day = calendar.day_name[business_created_date.weekday()]
                if consumer_day== 'Monday' :
                    mon = mon+1
                elif consumer_day== 'Tuesday' :
                    tue = tue+1
                elif consumer_day== 'Wednesday' :
                    wen = wen+1
                elif consumer_day== 'Thursday' :
                    thus = thus+1
                elif consumer_day== 'Friday' :
                    fri = fri+1
                elif consumer_day== 'Saturday' :
                    sat = sat+1
                elif consumer_day== 'Sunday' :
                    sun = sun+1
                else :
                    pass

        ############################Todays Payment collection view###############################

        consumer_list0= PaymentDetail.objects.filter(payment_created_date__regex = '00:',payment_created_date__contains = str((datetime.now()).strftime("%Y-%m-%d")))
        if consumer_list0:
            for consumer_obj in consumer_list0:

                total_amount0 = consumer_obj.total_amount

                temp_var0 = temp_var0 + int(total_amount0)

        value_0 = str(temp_var0)

        for hour in range(1,9):
            hour = ' 0'+ str(hour) + ':'
            consumer_obj_list1 = PaymentDetail.objects.filter(payment_created_date__regex = hour,payment_created_date__contains = str((datetime.now()).strftime("%Y-%m-%d")))


            if consumer_obj_list1:
                for consumer_obj in consumer_obj_list1:

                    total_amount1 = consumer_obj.total_amount

                    temp_var1 = temp_var1 + int(total_amount1)


        value_1 = str(temp_var1)

        for hour in range(9,17):
            if hour == 9:
                hour = ' 0'+ str(hour) + ':'
            else:
                hour = ' '+ str(hour) + ':'

            consumer_obj_list = PaymentDetail.objects.filter(advert_name__contains = str((datetime.now()).strftime("%Y-%m-%d")),payment_created_date__regex= hour)
            
            if consumer_obj_list:
                for consumer_obj in consumer_obj_list:

                    total_amount2 = consumer_obj.total_amount
                    temp_var2 = temp_var2 + int(total_amount2)
                    #print '....................total total_amount2 ................',temp_var2

        value_2 = str(temp_var2)   


        for hour in range(17,24):
            hour = ' '+ str(hour) + ':'
            consumer_obj_list = PaymentDetail.objects.filter(payment_created_date__contains = str((datetime.now()).strftime("%Y-%m-%d")),payment_created_date__regex= hour)
            if consumer_obj_list:
                for consumer_obj in consumer_obj_list:

                    total_amount3 = consumer_obj.total_amount
                    temp_var3 = temp_var3 + int(total_amount3)
                    #print '....................total total_amount3 ................',temp_var3

        value_3 = str(temp_var3)


        
        data ={'jan':jan,'feb':feb,'mar':mar,'apr':apr,'may':may,'jun':jun,'jul':jul,
               'aug':aug,'sep':sep,'oct':octo,'nov':nov,'dec':dec,'count_0':count_zero,
                'count_1':count_1,'count_2':count_2,'count_3':count_3,'city_list':get_city_dashboard(request),
                'mon':mon,'tue':tue,'wen':wen,'thus':thus,'fri':fri,'sat':sat,'sun':sun,
                'value_0':value_0,'value_1':value_1,'value_3':value_3,'value_2':value_2,
                'username':request.session['login_user'] ,'city_places_list':get_city_places(request), 
                'subscriber_data':subscriber_obj, 'today_date':today_date, 'pre_date':pre_date}
        return render(request,'Admin/index.html',data)


def get_city_dashboard(request):
   
   city_list=[]
   try:
      city_objs=City.objects.filter(city_status='1')
      for city in city_objs:
         city_list.append({'city_id': city.city_id,'city': city.city_name})
         #print city_list
      data =  city_list
      return data

   except Exception, ke:
      print ke
      data={'city_list': 'none','message':'No city available'}
   return HttpResponse(json.dumps(data), content_type='application/json')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def subscriber(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        data={ 'username':request.session['login_user'] }
        return render(request,'Admin/supplier_list.html',data)  

@cache_control(no_cache=True, must_revalidate=True, no_store=True)        
def consumer(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        data ={}
        return render(request,'Admin/consumer.html',data)        

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        user_role_list = UserRole.objects.filter(role_status='1')
        data = {'user_role_list':user_role_list,'username':request.session['login_user']}
        return render(request,'Admin/user_list.html',data)        

def notification(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        return render(request,'Admin/notification.html')   

# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
# def reference_data(request):
#     if not request.user.is_authenticated():
#         return redirect('backoffice')
#     else:
#         data ={'username':request.session['login_user']}
#         return render(request,'Admin/rdm.html',data)       

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_supplier(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        data = {'username':request.session['login_user'],'category_list':get_category(request),'currency':get_currency(request),'phone_category':get_phone_category(request),'state_list':get_state(request)}
        return render(request,'Admin/add_supplier.html',data)          

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_city(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        data = {'country_list':get_country(request),'category_list':get_category(request),'username':request.session['login_user']}
        return render(request,'Admin/add_city.html',data)  

#@cache_control(no_cache=True, must_revalidate=True, no_store=True)
#def category(request):
#    if not request.user.is_authenticated():
#        return redirect('backoffice')
#    else:
#        data = {'username':request.session['login_user']}
#        return render(request,'Admin/category.html',data)  

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def category(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        data = {}
        final_list = []
        try:
            category_list =[]
            print '----------ids------',request.GET.get('city_id')
            if request.GET.get('city_id'):
                city_obj = City_Place.objects.get(city_place_id=request.GET.get('city_id'))
                #print '------------city obj--------',city_obj
                state = city_obj.state_id
                country = city_obj.country_id
                cat_obj = CategoryCityMap.objects.filter(city_place_id=request.GET.get('city_id'))
                #print '-------cat_obj----',cat_obj
                for c in cat_obj:
                    #print c.category_id
                    category_list.append(Category.objects.get(category_id = str(c.category_id)))
                    #print '----------category list------',category_list
            else:
                #category_list = Category.objects.all()
                category_list = ''
            country_list = Country.objects.filter(country_status='1')
            state_list = State.objects.filter(state_status='1')
            city_list = City_Place.objects.filter(city_status='1')
            #print '------country list-----',city_list

            for cat_obj in category_list:
                #print '---------state-----',state
                #print '---------country-----',country
                category_id = str(cat_obj.category_id)
                active_advert = 'No'
                cat_color = cat_obj.category_color
                advert_obj_list = Advert.objects.filter(category_id=category_id)
                obj_count = Advert.objects.filter(category_id=category_id).count()
                inactive_count = Advert.objects.filter(category_id=category_id,status='0').count()
                if advert_obj_list:
                    if obj_count == inactive_count:
                        active_advert = 'No'
                    else:
                        for advert_obj in advert_obj_list:
                            advert_id = str(advert_obj.advert_id)
                            print "advert_id================",advert_id
                            pre_date = datetime.now().strftime("%m/%d/%Y")
                            pre_date = datetime.strptime(pre_date, "%m/%d/%Y")
                            advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)
                            end_date = advert_sub_obj.business_id.end_date
                            end_date = datetime.strptime(end_date, "%d/%m/%Y")
                            date_gap = end_date - pre_date
                            if int(date_gap.days) >= 0:
                                active_advert = 'Yes'

                category_name = cat_obj.category_name
                city_name = CategoryCityMap.objects.filter(category_id=cat_obj)
                city_list = ''
                if city_name:
                    for city in city_name:
                        city_list = str(city.city_place_id.city_id.city_name) + ',' + city_list
                    city_list = city_list[:-1]
                if not city_list:
                    city_list = 'All'

                category_created_by = str(cat_obj.category_created_by)
                category_updated_by = str(cat_obj.category_updated_by)
                creation_date = str(cat_obj.category_created_date).split()[0]
                updation_date = str(cat_obj.category_updated_date).split()[0]
                if creation_date:
                    creation_date = datetime.strptime(creation_date, "%Y-%m-%d")
                    #creation_date = creation_date.strftime("%d/%m/%Y")
                    creation_date = creation_date.strftime('%b %d,%Y')
                #print '---------creation date------',creation_date.strftime('%b %d,%Y')
                if updation_date :
                    updation_date = datetime.strptime(updation_date, "%Y-%m-%d")
                    #updation_date = updation_date.strftime("%d/%m/%Y")
                    updation_date = updation_date.strftime('%b %d,%Y')

                if (cat_obj.category_status == '1'):
                    status = 'Active'
                    if active_advert == 'No':
                        delete = '<a id="' + str(
                            category_id) + '" onclick="delete_category(this.id)" style="text-align: center;letter-spacing: 5px;width:15%;" title="Delete"  ><i class="fa fa-trash"></i></a>'
                    else:
                        delete = ''
                    edit = '<a  id="' + str(category_id) + '" href="/edit-category/?category_id=' + str(
                        category_id) + '" style="text-align: center;letter-spacing: 5px;width:15%;" title="Edit" class="edit" data-toggle="modal" href="#edit_subscription"><i class="fa fa-pencil"></i></a>'
                    actions = edit + delete
                else:
                    status = 'Inactive'
                    active = '<a class="col-md-2" id="' + str(
                        cat_obj) + '" onclick="active_service(this.id);" style="text-align: center;letter-spacing: 5px;width:15%;margin-left: 36px !important;" title="Activate" class="edit" data-toggle="modal" href="#edit_subscription"><i class="fa fa-repeat"></i></a>'
                    actions = active
                list = {'active_advert':active_advert,'category_id':category_id,'status': status,'cat_color':cat_color, 'category_name': category_name, 'actions': actions, 'city_name': city_list,
                        'creation_date': creation_date,'category_updated_by':category_updated_by,'category_created_by':category_created_by, 'updation_date': updation_date, 'updated_by':cat_obj.category_updated_by}
                final_list.append(list)
            data = {'country_list':country_list,'username':request.session['login_user'],'success': 'true', 'data': final_list}
            #print '----------data------',data
        except IntegrityError as e:
            print e
            data = {'username':request.session['login_user'],'success': 'false', 'message': 'Error in  loading page. Please try after some time'}
            print '----------data------',data
        #data = {'username':request.session['login_user']}
        return render(request,'Admin/category.html',data)

# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
# def category(request):
#     if not request.user.is_authenticated():
#         return redirect('backoffice')
#     else:
#         data = {}
#         final_list = []
#         try:
#             category_list =[]
#             print '----------ids------',request.GET.get('city_id')
#             if request.GET.get('city_id'):
#                 city_obj = City_Place.objects.get(city_place_id=request.GET.get('city_id'))
#                 print '------------city obj--------',city_obj
#                 state = city_obj.state_id
#                 country = city_obj.country_id
#                 cat_obj = CategoryCityMap.objects.filter(city_place_id=request.GET.get('city_id'))
#                 print '-------cat_obj----',cat_obj
#                 for c in cat_obj:
#                     print c.category_id
#                     category_list.append(Category.objects.get(category_id = str(c.category_id)))
#                     print '----------category list------',category_list
#             else:
#                 #category_list = Category.objects.all()
#                 category_list = ''
#             country_list = Country.objects.filter(country_status='1')
#             state_list = State.objects.filter(state_status='1')
#             city_list = City_Place.objects.filter(city_status='1')
#             print '------country list-----',city_list

#             for cat_obj in category_list:
#                 #print '---------state-----',state
#                 #print '---------country-----',country
#                 category_id = str(cat_obj.category_id)
#                 active_advert = 'No'
#                 cat_color = cat_obj.category_color
#                 advert_obj_list = Advert.objects.filter(category_id=category_id)
#                 obj_count = Advert.objects.filter(category_id=category_id).count()
#                 inactive_count = Advert.objects.filter(category_id=category_id,status='0').count()
#                 if advert_obj_list:
#                     if obj_count == inactive_count:
#                         active_advert = 'No'
#                     else:
#                         for advert_obj in advert_obj_list:
#                             advert_id = str(advert_obj.advert_id)
#                             pre_date = datetime.now().strftime("%m/%d/%Y")
#                             pre_date = datetime.strptime(pre_date, "%m/%d/%Y")
#                             advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)
#                             end_date = advert_sub_obj.business_id.end_date
#                             end_date = datetime.strptime(end_date, "%d/%m/%Y")
#                             date_gap = end_date - pre_date
#                             if int(date_gap.days) >= 0:
#                                 active_advert = 'Yes'

#                 category_name = cat_obj.category_name
#                 city_name = CategoryCityMap.objects.filter(category_id=cat_obj)
#                 city_list = ''
#                 if city_name:
#                     for city in city_name:
#                         city_list = str(city.city_place_id.city_id.city_name) + ',' + city_list
#                     city_list = city_list[:-1]
#                 if not city_list:
#                     city_list = 'All'

#                 category_created_by = str(cat_obj.category_created_by)
#                 category_updated_by = str(cat_obj.category_updated_by)
#                 creation_date = str(cat_obj.category_created_date).split()[0]
#                 updation_date = str(cat_obj.category_updated_date).split()[0]
#                 if creation_date:
#                     creation_date = datetime.strptime(creation_date, "%Y-%m-%d")
#                     #creation_date = creation_date.strftime("%d/%m/%Y")
#                     creation_date = creation_date.strftime('%b %d,%Y')
#                 #print '---------creation date------',creation_date.strftime('%b %d,%Y')
#                 if updation_date :
#                     updation_date = datetime.strptime(updation_date, "%Y-%m-%d")
#                     #updation_date = updation_date.strftime("%d/%m/%Y")
#                     updation_date = updation_date.strftime('%b %d,%Y')

#                 if (cat_obj.category_status == '1'):
#                     status = 'Active'
#                     if active_advert == 'No':
#                         delete = '<a id="' + str(
#                             category_id) + '" onclick="delete_category(this.id)" style="text-align: center;letter-spacing: 5px;width:15%;" title="Delete"  ><i class="fa fa-trash"></i></a>'
#                     else:
#                         delete = ''
#                     edit = '<a  id="' + str(category_id) + '" href="/edit-category/?category_id=' + str(
#                         category_id) + '" style="text-align: center;letter-spacing: 5px;width:15%;" title="Edit" class="edit" data-toggle="modal" href="#edit_subscription"><i class="fa fa-pencil"></i></a>'
#                     actions = edit + delete
#                 else:
#                     status = 'Inactive'
#                     active = '<a class="col-md-2" id="' + str(
#                         cat_obj) + '" onclick="active_service(this.id);" style="text-align: center;letter-spacing: 5px;width:15%;margin-left: 36px !important;" title="Activate" class="edit" data-toggle="modal" href="#edit_subscription"><i class="fa fa-repeat"></i></a>'
#                     actions = active
#                 list = {'active_advert':active_advert,'category_id':category_id,'status': status,'cat_color':cat_color, 'category_name': category_name, 'actions': actions, 'city_name': city_list,
#                         'creation_date': creation_date,'category_updated_by':category_updated_by,'category_created_by':category_created_by, 'updation_date': updation_date, 'updated_by':cat_obj.category_updated_by}
#                 final_list.append(list)
#             data = {'country_list':country_list,'username':request.session['login_user'],'success': 'true', 'data': final_list}
#             #print '----------data------',data
#         except IntegrityError as e:
#             print e
#             data = {'username':request.session['login_user'],'success': 'false', 'message': 'Error in  loading page. Please try after some time'}
#             print '----------data------',data
#         #data = {'username':request.session['login_user']}
#         return render(request,'Admin/category.html',data)  

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_role(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        data ={'username':request.session['login_user']}
        return render(request,'Admin/user_role.html',data)  

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_role(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        data ={'username':request.session['login_user']}
        return render(request,'Admin/add_user_role.html',data)  
       

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_advert(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        user_id = request.GET.get('user_id')
        print 'user_id',user_id
        supplier_id=request.GET.get('user_id')
        supplier_obj = Supplier.objects.get(supplier_id = user_id)
        country_id= str(supplier_obj.country_id.country_id)
        state_id= str(supplier_obj.state.state_id) 
        city_place_id= str(supplier_obj.city_place_id.city_place_id)
        supplier_name = supplier_obj.business_name
        user_id=supplier_obj.contact_email
        business_id = request.GET.get('business_id')
        city_place_id = str(supplier_obj.city_place_id.city_place_id)
        print 'business_id',business_id
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
            return render(request, 'Admin/add_advert_form.html', data)
        else:
            return render(request, 'Admin/add_advert.html', data)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def consumer_detail(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        data ={'username':request.session['login_user']}
        return render(request,'Admin/consumer_detail.html',data) 
        
def deal_detail(request):
    data ={}
    return render(request,'Admin/deal_detail.html',data) 


@csrf_exempt
def signin(request):
    data = {}
    try:

        if request.POST:
            form = CaptchaForm(request.POST)
            print 'logs: login request with: ', request.POST
            username = request.POST['username']
            password = request.POST['password']

            if form.is_valid():
                try:
                    user_obj = UserProfile.objects.get(username=username)
                    request.session['login_user'] = ''

                    try:
                        user = authenticate(username=username, password=password)
                        print 'valid form before----->',user
                        if user :
                            print 'valid form before----222->',user
                            if user.is_active:
                                print 'valid form after----->',user.is_active
                                user_profile_obj = UserProfile.objects.get(username=username)
                                print user_profile_obj.user_role.role_name
                                print user_profile_obj.user_role.role_id
                                privilege_obj = Privileges.objects.filter(
                                    role_id=str(user_profile_obj.user_role.role_id))
                                privilege_list = []
                                for privilege in privilege_obj:
                                    privilege_list.append(str(privilege.privilage))
                                request.session['privileges'] = privilege_list
                                print request.session['privileges']
                                if user_profile_obj.user_status == "1":
                                    try:
                                        print 'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS',request.session['login_user']
                                        request.session['login_user'] = user_profile_obj.username
                                        print '#########################################',request.session['login_user']
                                        request.session['first_name'] = user_profile_obj.user_first_name #+ '' + user_profile_obj.user_last_name
                                        login(request, user)
                                        if 'All' in request.session['privileges']:
                                            redirect_url = '/dashboard/'
                                        elif 'View Dashboard Details' in request.session['privileges']:
                                            redirect_url = '/dashboard/'
                                        elif 'Consumer Management' in request.session['privileges']:
                                            redirect_url = '/consumer-list/'
                                        elif 'Subscription Management' in request.session['privileges']:
                                            redirect_url = '/view-subscriber-list/'
                                        elif 'View Financial Details' in request.session['privileges']:
                                            redirect_url = '/admin-report/'
                                        elif 'View Advert Performance' in request.session['privileges']:
                                            redirect_url = '/admin-report/'
                                        elif 'View Selected Subscriber Details' in request.session['privileges']:
                                            redirect_url = '/admin-report/'
                                        elif 'View List of TID with Details' in request.session['privileges']:
                                            redirect_url = '/admin-report/'
                                        elif 'Record Payment Module' in request.session['privileges']:
                                            redirect_url = '/admin-report/'
                                        print "=======================================",redirect_url
                                        print '#########################################',request.session['login_user']
                                    except Exception as e:
                                        print '......ssssssssssssssss...1111..'
                                        print e
                                    print "USERNAME====000", request.session['login_user']
                                    data= {'success' : 'true','username':request.session['first_name'],'redirect_url':redirect_url}
                                else:
                                    print '...........222..........'
                                    data= { 'success' : 'false1', 'message' :'Invalid Username'}
                                    return HttpResponse(json.dumps(data), content_type='application/json') 
                            else:
                                print '.............3333.........'
                                data= { 'success' : 'false', 'message':'User Is Not Active'}
                                print 'SSSSSSSSSSSSSSSSSSS',data
                                return HttpResponse(json.dumps(data), content_type='application/json')
                        else:
                            print '.........444.....'
                            data= { 'success' : 'Invalid Password', 'message' :'Invalid Password'}
                            print "====USERNAME====",data
                            return HttpResponse(json.dumps(data), content_type='application/json')
                    except:
                        print '.......5555.......'
                        data= { 'success' : 'false1', 'message' :'Invalid Username'}
                        return HttpResponse(json.dumps(data), content_type='application/json') 

                except:
                    print '.........666........'
                    data= { 'success' : 'false', 'message' :'Invalid Username'}
                    return HttpResponse(json.dumps(data), content_type='application/json')            
            else:
                print '.......7777.....'
                form = CaptchaForm()
                data= { 'success' : 'Invalid Captcha', 'message' :'Invalid Captcha'} 
                print "INVALID CAPTCHA"       
                return HttpResponse(json.dumps(data), content_type='application/json')
    except MySQLdb.OperationalError, e:
        print '........8888.......'
        print e
        data= {'success' : 'false', 'message':'Internal server'}
        return HttpResponse(json.dumps(data), content_type='application/json')
    except Exception, e:
        print '......9999........'
        print 'Exception ', e
        data= { 'success' : 'false', 'message':'Invalid Username or Password'}
    print 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',data
    return HttpResponse(json.dumps(data), content_type='application/json')




def signing_out(request):
    logout(request)
    form = CaptchaForm()
    return render_to_response('Admin/user_login.html', dict(
        form=form, message_logout='You have successfully logged out.'
    ), context_instance=RequestContext(request))


@csrf_exempt
def forgot_password(request):
    # pdb.set_trace()
    username = request.POST.get("email")
    try:
        if request.POST:
            try:
                user_obj = UserProfile.objects.get(username=username)
                print "user_obj",user_obj
                if user_obj:
                    print '.........username......', user_obj.username
                    print '.........user_id......', user_obj.user_id
                    ret = u''
                    ret=''.join(random.choice('0123456789ABCDEF') for i in range(6))
                    OTP = ret
                    print "OTP",OTP
                    user_reset_password_mail(user_obj,OTP)
                    user_reset_password_sms(user_obj,OTP)
                    data = {'success': 'true', 'message': 'Login Successfully'}
                else:
                    data = {'success': 'true', 'message': 'Invalid Username'}


            except Exception as e:
                print e
                data = {'success': 'Invalid Username', 'message': 'Invalid Username'}
                print "INvalid",data

    except Exception as e:
        print e
        data = {'success': 'false', 'message': 'Invalid Username'}
        return HttpResponse(json.dumps(data), content_type='application/json')
    except Exception, e:
        print 'Exception|view_py|forgot_pwd', e
    return HttpResponse(json.dumps(data), content_type='application/json')

def user_reset_password_mail(user_obj,OTP):
    poc =str(user_obj.usre_email_id)
    gmail_user = "donotreply@city-hoopla.com"# "cityhoopla2016"
    gmail_pwd =  "Hoopla123#"#"cityhoopla@2016"
    FROM = 'Team CityHoopla<donotreply@city-hoopla.com>'
    TO = [poc]
    try:
        TEXT = "Dear " + str(user_obj.user_first_name) + ", \n\n"+ "Greetings from CityHoopla !!! \n\n"+  "Click on the link below to reset your password!!!" + "\n"+SERVER_URL+"/reset-password/?user_id="+str(user_obj.user_id)+ "\n\n"+ "Best Wishes," + '\n' + "Team CityHoopla "
        SUBJECT = "Reset Password Link!"
        #server = smtplib.SMTP_SSL()
        #server = smtplib.SMTP("smtp.gmail.com", 587) 
        server = smtplib.SMTP("smtpout.asia.secureserver.net", 80)
        #server = smtplib.SMTP_TSL('smtpout.secureserver.net', 465)
        server.ehlo()
        #server.starttls()
        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException, e:
        print e
    return 1

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def reset_password(request):
    user_id =request.GET.get('user_id')
    print user_id
    data={'user_id':user_id }
    return render(request,'Admin/reset_password.html',data)


def user_reset_password_sms(user_obj,OTP):
    # pdb.set_trace()

    authkey = "118994AIG5vJOpg157989f23"

    mobiles = str(user_obj.user_contact_no)

    message = "Dear " + str(user_obj.user_first_name) + ", \n\n"+ "Greetings from CityHoopla !!! \n\n"+ "Click on the link below to reset your password!!!" + "\n"+SERVER_URL+"/reset-password/?user_id="+str(user_obj.user_id)+ "\n\n"+ "Best Wishes," + '\n' + "Team CityHoopla "
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


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def reset_new_password(request):
    try:
        # pdb.set_trace()
        print 'in login'
        if request.POST:
            user_id = request.POST.get('user_id')
            try:
                print "user_id",user_id
                user_obj1=UserProfile.objects.get(user_id=user_id)
                username = user_obj1.usre_email_id

                user_obj = UserProfile.objects.get(usre_email_id=username)
                new_password = request.POST.get('confirm_password')
                user_obj.set_password(request.POST.get('confirm_password'));
                user_obj.save();
                reset_password_mail(user_obj,new_password)
                reset_password_sms(user_obj,new_password)

                data={
                    'success':'true',
                    'message':'Password Updated Successfully.'
                }
                print "DATA",data

            except Exception, e:
                print 'Exception',e
                data={
                    'success':'false',
                    'message':'Password Updated Successfully.'
                }


    except Exception, e:
        data={
            'success':'false',
            'message':str(e)
        }
    print data
    return HttpResponse(json.dumps(data),content_type='application/json')

def reset_password_mail(user_obj,OTP):
    poc = str(user_obj.usre_email_id)    
    gmail_user = "donotreply@city-hoopla.com"# "cityhoopla2016"
    gmail_pwd =  "Hoopla123#"#"cityhoopla@2016"
    FROM = 'Team CityHoopla<donotreply@city-hoopla.com>'
    TO = [poc]
    try:
        TEXT = "Dear " + str(user_obj.user_first_name) + ", \n\n"+ "Greetings from CityHoopla !!! \n\n"+ "Your password has been successfully chnaged. Please find below your login credentials to manage your Account. \n\n"+ "Username: "+ str(user_obj.usre_email_id)+ "\n"+ "Password: "+  str(OTP)+ '\n\n' + "Click on the link below to configure your account!!!" + "\n"+SERVER_URL+"/backoffice/"+"\n\n"+"Best Wishes," + '\n' + "Team CityHoopla "
        SUBJECT = "Your CityHoopla Password has been changed!"
        #server = smtplib.SMTP_SSL()
        #server = smtplib.SMTP("smtp.gmail.com", 587) 
        server = smtplib.SMTP("smtpout.asia.secureserver.net", 80)
        #server = smtplib.SMTP_TSL('smtpout.secureserver.net', 465)
        server.ehlo()
        #server.starttls()
        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException, e:
        print e
    return 1


def reset_password_sms(user_obj,OTP):
    # pdb.set_trace()

    authkey = "118994AIG5vJOpg157989f23"

    mobiles = str(user_obj.user_contact_no)

    message = "Dear " + str(user_obj.user_first_name) + ", \n\n"+ "Greetings from CityHoopla !!! \n\n"+ "Your password has been successfully chnaged. Please find below your login credentials to manage your Account. \n\n"+ "Username: "+ str(user_obj.usre_email_id)+ "\n"+ "Password: "+  str(OTP)+ '\n\n' + "Click on the link below to configure your account!!!" + "\n"+SERVER_URL+"/backoffice/"+"\n\n"+"Best Wishes," + '\n' + "Team CityHoopla "
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
def add_user(request):
    try:
        role_id = UserRole.objects.get(role_id=request.POST.get('user_role'))
        user_obj=UserProfile(
            username=request.POST.get('username'),
            user_name=request.POST.get('username'),
            user_contact_no=request.POST.get('contact_no'),
            usre_email_id=request.POST.get('email'),
            user_role=role_id,
            user_created_date = datetime.now(),
            user_status = '1',
            user_created_by = request.session['login_user']
        );
        user_obj.save();
        user_obj.set_password(request.POST.get('password'));
        user_obj.save();

        data={
            'success':'true',
            'message':'User Created Successfully.'
        }
    except Exception, e:
        data={
            'success':'false',
            'message':str(e)
        }
    return HttpResponse(json.dumps(data),content_type='application/json')    


def view_user_detail(request):
    print 'in user detail'
    print request.method
    try:
        data = {}
        final_list = []
        #print 'User ID: ',request.GET.get('user_id')
        try:
            if request.method == "GET":
                user_obj = UserProfile.objects.get(user_name=request.GET.get('user_id'))
                print user_obj
                role_id = str(user_obj.user_role.role_id)
                role_name = user_obj.user_role.role_name
                user_name = user_obj.user_name
                user_email_id = user_obj.usre_email_id
                user_contact_no = user_obj.user_contact_no
                data = {'success':'true','role_name':role_name,'role_id':role_id,'user_name':user_name,'user_email_id':user_email_id,'user_contact_no':user_contact_no}            
        except IntegrityError as e:
            print e
            data = {'success':'false','message':'Error in  loading page. Please try after some time'}

    except MySQLdb.OperationalError, e:
        print e

    except Exception,e:
        print 'Exception ',e
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def update_user_detail(request):    
    try:
        if request.method=="POST":
            print "POST method"
            user_obj = UserProfile.objects.get(user_name=request.POST.get('user_id'))
            print user_obj
            print 'role_id :',request.POST.get('e_user_role')
            role_obj = UserRole.objects.get(role_id=request.POST.get('e_user_role'))
            print role_obj
            #user_obj.username=request.POST.get('username'),
            #user_obj.user_name=request.POST.get('username'),
            user_obj.user_contact_no=request.POST.get('e_contact_no')
            user_obj.usre_email_id=request.POST.get('e_email')
            user_obj.user_role=role_obj               
            user_obj.save()
            user_obj.set_password(request.POST.get('new_password'))
            user_obj.save()
            data={'success':'true','message':'User Updated Successfully.'}
    except Exception, e:
            data={
                'success':'false',
                'message':str(e)
            }
    return HttpResponse(json.dumps(data),content_type='application/json')


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

# TO GET THE STATE
def get_states(request):
##    pdb.set_trace()
    print "IN states"
    state_list = []
    try:
        state = State.objects.filter(state_status='1')
        for sta in state:
            options_data = {
            'state_id':str(sta.state_id),
            'state_name':str(sta.state_name)

            }
            state_list.append(options_data)
            #print state_list
        return  state_list
    except Exception, e:
        print 'Exception ', e
        data = {'state_list':'No states available' }
    return HttpResponse(json.dumps(data), content_type='application/json')

# TO GET THE STATE
def get_state(request):
##    pdb.set_trace()
    country_id=request.GET.get('country_id')
    print '>>>>>>>>>>>country ID',country_id
    currency = Currency.objects.get(country_id=country_id)
    state_list = []
    try:
        state = State.objects.filter(state_status='1',country_id=country_id)
        for sta in state:
            options_data = '<option value=' + str(
                   sta.state_id) + '>' + sta.state_name + '</option>'
            state_list.append(options_data)
        data = {'state_list':state_list,'currency':currency.currency }    
    except Exception, e:
        print 'Exception ', e
        data = {'state_list':'No states available' }
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



# To Get The Currecny
def add_currency(request):
   country_id=request.GET.get('country_id')
   currency_list=[]
   try:
      currency_objs=Currency.objects.filter(country_id=country_id,status='1')
      for cur in currency_objs:
         curr=cur.currency_id
         curr=str(curr)
         cur_name=cur.currency
         cur_name=str(cur_name)
         options_data = {
            'id':curr,
            'currency':cur_name
         }
         
         currency_list.append(options_data)
         print currency_list
      data = {'currency_list': currency_list}

   except Exception, ke:
      print ke
      data={'currency_list': 'none','message':'No Currency available'}
   return HttpResponse(json.dumps(data), content_type='application/json')

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

# TO GET THE CITY
def get_city_places(request):
   
   city_list=[]
   try:
      city_objs=City_Place.objects.filter(city_status='1')
      for city in city_objs:
         city_list.append({'city_place_id': city.city_place_id,'city': city.city_id.city_name})
         #print city_list
      data =  city_list
      return data

   except Exception, ke:
      print ke
      data={'city_list': 'none','message':'No city available'}
   return HttpResponse(json.dumps(data), content_type='application/json')

# TO GET THE CITY
def get_city(request):
   
   state_id=request.GET.get('state_id')
   city_list=[]
   try:
      city_objs=City.objects.filter(state_id=state_id,city_status='1').order_by('city_name')
      for city in city_objs:
         options_data = '<option value=' + str(
                   city.city_id) + '>' + city.city_name + '</option>'
         city_list.append(options_data)
         #print city_list
      data = {'city_list': city_list}

   except Exception, ke:
      print ke
      data={'city_list': 'none','message':'No city available'}
   return HttpResponse(json.dumps(data), content_type='application/json')


# TO GET THE PINCODE
def get_pincode(request):
   #pdb.set_trace()

   pincode_list=[]
   try:
      city_id = request.GET.get('city_id')
      pincode_list1=Pincode.objects.filter(city_id=city_id).order_by('pincode')
      pincode_objs = pincode_list1.values('pincode').distinct()
      #print pincode_objs
      for pincode in pincode_objs:
         options_data = '<option>' +pincode['pincode']+ '</option>'
         pincode_list.append(options_data)
         #print pincode_list
      data = {'pincode_list': pincode_list}

   except Exception, ke:
      print ke
      data={'city_list': 'none','message':'No city available'}
   return HttpResponse(json.dumps(data), content_type='application/json')  
   

# payal
@csrf_exempt
def add_user_role(request):
    try:
        print '=========request============',request
        print '=========post==============',request.POST
        try:
            user_role_obj = UserRole.objects.get(role_name=request.POST.get('user_role'),role_status='1')
            print user_role_obj
            data={
                'success':'false',
                'message':'User role already exist.'
            }
        except:

            user_role_obj=UserRole(
                role_name=request.POST.get('user_role'),
                role_status="1",
                role_created_date=datetime.now(),
                role_created_by=request.session['login_user'],
                role_updated_by=request.session['login_user'],
                role_updated_date=datetime.now(),
                
            );
            user_role_obj.save();
            print "user_role_obj",user_role_obj

            prv_list = request.POST.get('privil_list')
            prv_list = prv_list.split(',')
            save_privilege(prv_list,user_role_obj)
            user_role_add(user_role_obj)
            data={
                'success':'true',
                'message':'User role created successfully.'
            }
    except Exception, e:
        data={
            'success':'false',
            'message':str(e)
        }
    print '===========data================',data    
    return HttpResponse(json.dumps(data),content_type='application/json')  

def save_privilege(prv_list,user_role_obj):
##    pdb.set_trace()
    print "IN SAVE PRIVILEGE"
    try:
        print "User Role Id",user_role_obj
        for prv in prv_list:
            if prv == 'sub_mang':
                privi='Subscription Management'
            elif prv == 'adm_mang':
                privi="Admin Management"
            elif prv == 'cons_mang':
                privi="Consumer Management" 
            elif prv == 'push_not':
                privi="Push Notification" 
            elif prv == 'rcm':
                privi="Rate Card Management" 
            elif prv == 'rdm':
                privi="Ref Data Management" 
            elif prv == 'rpm':
                privi="Record Payment Module"
            elif prv == 'vdd':
                privi="View Dashboard Details"
            elif prv == 'vfd':
                privi="View Financial Details"
            elif prv == 'vlt':
                privi="View List of TID with Details"
            elif prv == 'asr':
                privi="Assign Roles"
            elif prv == 'vsd':
                privi="View Selected Subscriber Details"
            elif prv == 'all':
                privi="All"
            elif prv == 'none':
                privi="None"
            else:
                privi="View Advert Performance"
            pvr_obj = Privileges(
                role_id = user_role_obj,
                privilage=privi
            )
            pvr_obj.save()
            data = {'success': 'true'}
        
    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json') 


def user_role_add(user_role_obj):
    gmail_user = "donotreply@city-hoopla.com"# "cityhoopla2016"
    gmail_pwd =  "Hoopla123#"#"cityhoopla@2016"
    FROM = 'Team CityHoopla<donotreply@city-hoopla.com>'
    TO = ['cityhoopla2016@gmail.com']
    #pdb.set_trace()
    try:
        TEXT = "Hi Admin,\nUser Role " + str(user_role_obj.role_name) + " " +"has been added successfully.\nTo view complete details visit portal and follow - Reference Data -> User Role\n\n Thank You,"+'\n'+"CityHoopla Team"
        SUBJECT = "User Role Added Successfully!"
        #server = smtplib.SMTP_SSL()
        #server = smtplib.SMTP("smtp.gmail.com", 587) 
        server = smtplib.SMTP("smtpout.asia.secureserver.net", 80)
        #server = smtplib.SMTP_TSL('smtpout.secureserver.net', 465)
        server.ehlo()
        #server.starttls()
        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException,e:
        print e
    return 1    
 
def view_user_role_list(request):
    try:
        data = {}
        final_list = []
        try:
            user_role_list = UserRole.objects.all()
            for role_obj in user_role_list:
                role_id=role_obj.role_id
                role_name = role_obj.role_name
                role_created_by=role_obj.role_created_by
                role_updated_by=role_obj.role_updated_by
                role_creation_date = str(role_obj.role_created_date).split(' ')[0]
                
                if role_obj.role_updated_date:
                    role_updation_date = str(role_obj.role_updated_date).split(' ')[0]
                    to_date = datetime.strptime(role_updation_date, "%Y-%m-%d")
                    to_date = to_date.strftime("%d/%m/%Y")
                else :
                    role_updation_date = ''
                    to_date = ''
                from_date = datetime.strptime(role_creation_date, "%Y-%m-%d")                
                from_date = from_date.strftime("%d/%m/%Y")
                
                
                if role_obj.role_status == '1':
                    # edit = '<a class="col-md-offset-2 col-md-1" id="'+str(role_id)+'" onclick="edit_user_role(this.id);" style="text-align: center;letter-spacing: 5px;width:15%;" title="Edit" class="edit" data-toggle="modal" href="#edit_subscription"><i class="fa fa-pencil"></i></a>'
                    edit = '<a class="col-md-offset-2 col-md-1" href="/edit-user-role/?role_id='+str(role_id) + '" style="text-align: center;letter-spacing: 5px;width:15%;" title="Edit"  ><i class="fa fa-pencil"></i></a>'
                    delete = '<a id="'+str(role_name)+'" onclick="delete_user_role('+str(role_id)+',this.id)" style="text-align: center;letter-spacing: 5px;width:15%;" title="Delete"  ><i class="fa fa-trash"></i></a>'
                    status = 'Active'
                    actions =  edit + delete
                else:
                    status = 'Inactive'
                    active = '<a class="col-md-2" id="'+str(role_name)+'" onclick="active_service('+str(role_id)+',this.id);" style="text-align: center;letter-spacing: 5px;width:10%;margin-left: 22px !important;" title="Activate" class="edit" data-toggle="modal" href="#edit_subscription"><i class="fa fa-repeat"></i></a>'
                    actions =  active
             
                list = {'role_name':role_name,'actions':actions,'role_id':role_id,'from_date':from_date,'to_date':to_date,
                        'created_by':role_created_by,'updated_by':role_updated_by}
                final_list.append(list)
            data = {'success':'true','data':final_list}
        except IntegrityError as e:
            print e
            data = {'success':'false','message':'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception,e:
        print 'Exception ',e
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def edit_user_role(request):
    # pdb.set_trace()
    try:
        data = {}
        final_list = []
        try:
            if request.method == "GET":
                print request
                role_obj = UserRole.objects.get(role_id=request.GET.get('role_id'))
                role_id = str(role_obj.role_id)
                role_name = role_obj.role_name

                prv = ""
                prv1 =""
                prv2 =""
                prv3 =""
                prv4 =""
                prv5 =""
                prv6 =""
                prv7 =""  
                prv8 =""
                prv9 =""
                prv10 =""
                prv11 =""
                prv12 =""
                prv13 =""
                prv14 =""
                #amenity_list = []
                amenity_lis = Privileges.objects.filter(role_id=role_obj)
                print 'amenity_lis',amenity_lis
                if amenity_lis.count()>0:
                    for amenities in amenity_lis:
                        if amenities.privilage == "Subscription Management":
                            prv="Subscription Management"
                        elif amenities.privilage == "Admin Management":
                            prv1="Admin Management"
                        elif amenities.privilage == "Consumer Management":
                            prv2="Consumer Management" 
                        elif amenities.privilage == "Push Notification":
                            prv3="Push Notification" 
                        elif amenities.privilage == "Rate Card Management":
                            prv4="Rate Card Management" 
                        elif amenities.privilage == "Ref Data Management":
                            prv5="Ref Data Management" 
                        elif amenities.privilage == "Record Payment Module":
                            prv6="Record Payment Module"
                        elif amenities.privilage == "View Dashboard Details":
                            prv7="View Dashboard Details"
                        elif amenities.privilage == "View List of TID with Details":
                            prv8="View List of TID with Details"
                        elif amenities.privilage == "Assign Roles":
                            prv9="Assign Roles"
                        elif amenities.privilage == "View Selected Subscriber Details":
                            prv10="View Selected Subscriber Details"
                        elif amenities.privilage == "View Financial Details":
                            prv11="View Financial Details"
                        elif amenities.privilage == "View Advert Performance":
                            prv12="View Advert Performance"
                        elif amenities.privilage == "All":
                            prv13="All"
                        elif amenities.privilage == "None":
                            prv14="None"
        
                amenity_list = {'prv':prv,'prv1':prv1,'prv2':prv2,'prv3':prv3,'prv4':prv4,'prv5':prv5,'prv6':prv6,'prv7':prv7,'prv8':prv8,'prv9':prv9,
                                        'prv10':prv10,'prv11':prv11,'prv12':prv12,'prv13':prv13,'prv14':prv14}                       
               
                data = {'success':'true','role_name':role_name,'role_id':role_id,'prv_list':amenity_list,'username':request.session['login_user']}
            

        except IntegrityError as e:
            print e
            data = {'success':'false','message':'Error in  loading page. Please try after some time'}

    except MySQLdb.OperationalError, e:
        print e

    except Exception,e:
        print 'Exception ',e 
    return render(request,'Admin/edit_user_role.html',data)    


@csrf_exempt
def update_user_role(request):
    # pdb.set_trace()
    try:
        print request.POST
        data = {}
        role_obj = request.POST.get('user_role')
        role_id = request.POST.get('role_id')
        try:
            print "==========IN UPDATE ROLE======="
            role_object=UserRole.objects.get(role_name=request.POST.get('edit_role'))
            print "========role_object",role_object
            if(str(role_id)==str(role_object)):
                role_object=UserRole.objects.get(role_name=request.POST.get('edit_role'),role_status=1)
                role_object.role_name = request.POST.get('edit_role')
                role_object.role_updated_by=request.session['login_user']
                role_object.role_updated_date=datetime.now()
                role_object.save()

                amenity_lis = Privileges.objects.filter(role_id=role_object)
                amenity_lis.delete()
                
                amenity_list = request.POST.get('privil_list')
                amenity_list = amenity_list.split(',')
                save_privilege(amenity_list,role_object)
                user_role_edit(role_object)  
                data = {'success':'true'}
            else:
                data = {'success':'false'}
        except:
            role_object=UserRole.objects.get(role_id=role_id)
            role_object.role_name = request.POST.get('edit_role')
            role_object.role_updated_by=request.session['login_user']
            role_object.role_updated_date=datetime.now()
            role_object.save() 
            amenity_lis = Privileges.objects.filter(role_id=role_object)
            amenity_lis.delete()
            amenity_list = request.POST.get('privil_list')
            amenity_list = amenity_list.split(',')
            save_privilege(amenity_list,role_object)
            user_role_edit(role_object)  

            data={
                'success':'true',
                }
    except Exception, e:
            data={
                'success':'false',
                'message':str(e)
            }
    print '========data====================',data        
    return HttpResponse(json.dumps(data),content_type='application/json') 


def user_role_edit(role_object):
    gmail_user = "donotreply@city-hoopla.com"# "cityhoopla2016"
    gmail_pwd =  "Hoopla123#"#"cityhoopla@2016"
    FROM = 'Team CityHoopla<donotreply@city-hoopla.com>'
    TO = ['cityhoopla2016@gmail.com']
    #pdb.set_trace()
    try:
        TEXT = "Hi Admin,\nUser Role " + str(role_object.role_name) + " " +" has been updated successfully.\nTo view complete details visit portal and follow - Reference Data -> User Role\n\n Thank You,"+'\n'+"CityHoopla Team"
        SUBJECT = "User Role Added Successfully!"
        #server = smtplib.SMTP_SSL()
        #server = smtplib.SMTP("smtp.gmail.com", 587) 
        server = smtplib.SMTP("smtpout.asia.secureserver.net", 80)
        #server = smtplib.SMTP_TSL('smtpout.secureserver.net', 465)
        server.ehlo()
        #server.starttls()
        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException,e:
        print e
    return 1    

@csrf_exempt
def delete_user_role(request):
        try:
            role_obj = UserRole.objects.get(role_id=request.POST.get('role_id'))
            role_obj.role_status = '0'
            role_obj.save()
            user_role_delete(role_obj)
            data = {'message': 'User Role De-activeted Successfully', 'success':'true'}

        except IntegrityError as e:
          print e
        except Exception,e:
            print e
        print "Final Data: ",data
        return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def active_user_role(request):
        # pdb.set_trace()
        try:
            role_obj = UserRole.objects.get(role_id=request.POST.get('role_id'))
            role_obj.role_status = '1'
            role_obj.save()
            user_role_active(role_obj)
            data = {'message': 'User Role activated Successfully', 'success':'true'}

        except IntegrityError as e:
          print e
        except Exception,e:
            print e
        print "Final Data: ",data
        return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def role_list(request):
    try:
        try:
            data = {'success':'true'}

        except IntegrityError as e:
            print e
            data = {'success':'false','message':'Error in  loading page. Please try after some time','username':request.session['login_user']}
    except MySQLdb.OperationalError, e:
        print e
    except Exception,e:
        print 'Exception ',e
    print data
    return render(request,'Admin/role-list.html',data)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_new_role(request):
    try:
        try:
            data = {'success':'true'}

        except IntegrityError as e:
            print e
            data = {'success':'false','message':'Error in  loading page. Please try after some time','username':request.session['login_user']}
    except MySQLdb.OperationalError, e:
        print e
    except Exception,e:
        print 'Exception ',e
    print data
    return render(request,'Admin/add-new-role.html',data)



def user_role_active(role_obj):
    gmail_user = "donotreply@city-hoopla.com"# "cityhoopla2016"
    gmail_pwd =  "Hoopla123#"#"cityhoopla@2016"
    FROM = 'Team CityHoopla<donotreply@city-hoopla.com>'
    TO = ['cityhoopla2016@gmail.com']
    #pdb.set_trace()
    try:
        TEXT = "Hi Admin,\nUser Role " + str(role_obj.role_name) + " " +" has been activated successfully.\nTo view complete details visit portal and follow - Reference Data -> User Role\n\n Thank You,"+'\n'+"CityHoopla Team"
        SUBJECT = "User Role Activated Successfully!"
        #server = smtplib.SMTP_SSL()
        #server = smtplib.SMTP("smtp.gmail.com", 587) 
        server = smtplib.SMTP("smtpout.asia.secureserver.net", 80)
        #server = smtplib.SMTP_TSL('smtpout.secureserver.net', 465)
        server.ehlo()
        #server.starttls()
        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException,e:
        print e
    return 1 

def user_role_delete(role_obj):
    gmail_user = "donotreply@city-hoopla.com"# "cityhoopla2016"
    gmail_pwd =  "Hoopla123#"#"cityhoopla@2016"
    FROM = 'Team CityHoopla<donotreply@city-hoopla.com>'
    TO = ['cityhoopla2016@gmail.com']
    #pdb.set_trace()
    try:
        TEXT = "Hi Admin,\nUser Role " + str(role_obj.role_name) + " " +" has been updated successfully.\nTo view complete details visit portal and follow - Reference Data -> User Role\n\n Thank You,"+'\n'+"CityHoopla Team"
        SUBJECT = "User Role Added Successfully!"
        #server = smtplib.SMTP_SSL()
        #server = smtplib.SMTP("smtp.gmail.com", 587) 
        server = smtplib.SMTP("smtpout.asia.secureserver.net", 80)
        #server = smtplib.SMTP_TSL('smtpout.secureserver.net', 465)
        server.ehlo()
        #server.starttls()
        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException,e:
        print e
    return 1 
   
@csrf_exempt
def save_city(request):
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
    # print "IN SAVE CITY", request.POST
    try:
        data = {}
        # print request.POST
        # print request.FILES
        print '=====type========', type(request.FILES)
        # pdb.set_trace()
        try:
            print '-------------city name-------', request.POST.get('city_name')
            city_obj = City_Place.objects.get(city_id=request.POST.get('city_name'))
            print '-------------city- obj---------', city_obj
            data = {'success': 'false', 'messege': 'City Already Exist'}
        except Exception, e:
            city_obj = City_Place(

                city_id=City.objects.get(city_id=request.POST.get('city_name')),
                state_id=State.objects.get(state_id=request.POST.get('state')),
                country_id=Country.objects.get(country_id=request.POST.get('country'))

            )
            city_obj.save()
            if request.POST.get('about_city'):
                city_obj.about_city = request.POST.get('about_city')

            if request.POST.get('climate'):
                city_obj.climate = request.POST.get('climate')

            if request.POST.get('population'):
                city_obj.population = request.POST.get('population')

            if request.POST.get('timezone'):
                city_obj.time_zone = request.POST.get('timezone')

            if request.POST.get('language'):
                city_obj.language = request.POST.get('language')

            if request.POST.get('currency'):
                city_obj.currency = request.POST.get('currency')

            city_obj.save();
            city_place_id = city_obj.city_place_id
            print "city ID", city_place_id
            city_name = city_obj.city_id.city_name
            print '---------city name-----', city_name
            if request.POST['check_image'] == "1":
                city_obj.city_image = request.FILES['city_image']
                city_obj.save()

            city_id = request.POST.get('city_name')
            print '---------city_id -----', city_id
            city_obj = City_Place.objects.get(city_id=city_id)
            print '---------city_obj-----', city_obj

            poi_range = request.POST.get('poi_range')
            point_of_interest_list = request.POST.get('point_of_interest_list')
            point_of_interest_list = str(point_of_interest_list).split('_POI_CH')
            point_of_interest_image_list = []

            for i in range(int(poi_range)):
                image = "point_of_interest_image" + str(i)
                try:
                    point_of_interest_image_list.append(request.FILES[image])
                except:
                    point_of_interest_image_list.append('')

            zipped_wk = zip(point_of_interest_list, point_of_interest_image_list)
            place_type = 'point_of_interest'
            if (zipped_wk != []):
                save_places(zipped_wk, city_obj, place_type)

            shop_list = request.POST.get('shop_list')
            shop_list = str(shop_list).split('_SOP_CH')
            shop_range = request.POST.get('shop_range')
            shop_image_list = []
            for i in range(int(shop_range)):
                image = "shop_image" + str(i)
                try:
                    shop_image_list.append(request.FILES[image])
                except:
                    shop_image_list.append('')

            zipped_wk = zip(shop_list, shop_image_list)
            place_type = 'where_to_shop'

            save_places(zipped_wk, city_obj, place_type)

            hospital_list = request.POST.get('hospital_list')
            hospital_list = str(hospital_list).split('_HOS_CH')

            hospital_range = request.POST.get('hospital_range')
            hospital_image_list = []
            for i in range(int(hospital_range)):
                image = "hospital_image" + str(i)
                try:
                    hospital_image_list.append(request.FILES[image])
                except:
                    hospital_image_list.append('')
            zipped_wk = zip(hospital_list, hospital_image_list)
            place_type = 'reputed_hospitals'

            save_places(zipped_wk, city_obj, place_type)

            college_list = request.POST.get('college_list')
            college_list = str(college_list).split('_EDU_CH')

            college_range = request.POST.get('college_range')
            college_image_list = []
            for i in range(int(college_range)):
                image = "college_image" + str(i)
                try:
                    college_image_list.append(request.FILES[image])
                except:
                    college_image_list.append('')
            zipped_wk = zip(college_list, college_image_list)
            place_type = 'college_and_universities'
            save_places(zipped_wk, city_obj, place_type)
            city_add(city_obj)

            data = {
                'success': 'true',
                'message': 'City Added Successfully.',
                "city_place_id": city_place_id,
                "city_name": city_name
            }


    except Exception, e:
        data = {
            'success': 'false',
            'message': str(e)
        }
    return HttpResponse(json.dumps(data), content_type='application/json')
 




@csrf_exempt
def check_city(request):
    #pdb.set_trace()
    try:
            city_nm = request.POST.get('city');
            city_obj = City_Place.objects.all();
            for cit in city_obj:
                if city_nm == city_obj.city_name:
                    data = {'success':'false'}
                    return HttpResponse(json.dumps(data),content_type='application/json')
            data = {'success':'true'}
            return HttpResponse(json.dumps(data),content_type='application/json')
    except Exception,e:
        pass

@csrf_exempt
def save_city_data(request):
    try:
        print request.POST
        city_obj=City_Place.objects.get(city_id=request.POST.get('city_name'))

        poi_range = request.POST.get('poi_range')
        point_of_interest_list = request.POST.get('point_of_interest_list')
        point_of_interest_list = str(point_of_interest_list).split(',')
        point_of_interest_image_list = []
        
        for i in range(int(poi_range)):
            image = "point_of_interest_image" + str(i)
            try:
                point_of_interest_image_list.append(request.FILES[image])                 
            except:
                point_of_interest_image_list.append('')

        zipped_wk = zip(point_of_interest_list,point_of_interest_image_list)
        place_type = 'point_of_interest'
        if(zipped_wk!=[]):
            save_places(zipped_wk,city_obj,place_type)
       
        shop_list = request.POST.get('shop_list')
        shop_list = str(shop_list).split(',')
        shop_range = request.POST.get('shop_range')
        shop_image_list = []
        for i in range(int(shop_range)):
            image = "shop_image" + str(i)
            try:
                shop_image_list.append(request.FILES[image])                 
            except: 
                shop_image_list.append('')

        zipped_wk = zip(shop_list,shop_image_list)
        place_type = 'where_to_shop'

        save_places(zipped_wk,city_obj,place_type)

        hospital_list = request.POST.get('hospital_list')
        hospital_list = str(hospital_list).split(',')

        hospital_range = request.POST.get('hospital_range')
        hospital_image_list = []
        for i in range(int(hospital_range)):
            image = "hospital_image" + str(i)
            try:
                hospital_image_list.append(request.FILES[image])                 
            except:
                hospital_image_list.append('')
        zipped_wk = zip(hospital_list,hospital_image_list)
        place_type = 'reputed_hospitals'

        save_places(zipped_wk,city_obj,place_type)

        college_list = request.POST.get('college_list')
        college_list = str(college_list).split(',')


        college_range = request.POST.get('college_range')
        college_image_list = []
        for i in range(int(college_range)):
            image = "college_image" + str(i)
            try:
                college_image_list.append(request.FILES[image])                 
            except:
                college_image_list.append('')
        zipped_wk = zip(college_list,college_image_list)
        place_type = 'college_and_universities'
        save_places(zipped_wk,city_obj,place_type)
        city_add(city_obj)
        
        data={
            'success':'true',
            'message':'City Added Successfully.'
        }

    except Exception, e:
        print e
        data={
            'success':'false',
            'message':str(e)
        }
    return HttpResponse(json.dumps(data),content_type='application/json')    


def update_places(zipped_wk, city_obj, place_type):
    try:
        # pdb.set_trace()
        print "in update places"
        i = 0
        for interest_id, interest_name, interest_img in zipped_wk:
            print "interest_name:",interest_name,"interest_img:",interest_img
            if i == 0:
                interest_name = interest_name.strip()
            if i != 0:
                interest_name = interest_name[1:].strip()
            i = i + 1
            try:
                print "update places try", interest_id

                splitId = interest_id.split('_')

                print 'splitId', splitId

                if splitId[0] == 'old':
                    place_obj = Places.objects.get(place_id=splitId[1])
                    if interest_name != "":
                        print "-----place_obj", place_obj
                        place_obj.place_name = interest_name
                        if interest_img != '':
                            place_obj.place_image = interest_img
                        else:
                            pass
                        place_obj.updated_by = "Admin",
                        place_obj.updated_date = datetime.now()
                        place_obj.save()
                    else:
                        place_obj.delete()
                else:
                    if interest_name != '' and interest_img !='':
                        interest_name_obj = Places(
                            city_place_id=city_obj,
                            place_name=interest_name,
                            place_image=interest_img,
                            place_type=place_type,
                            created_date=datetime.now(),
                            created_by="Admin",
                            updated_by="Admin",
                            updated_date=datetime.now()
                        )
                        interest_name_obj.save()
                    else:
                        pass

            except Exception, e:
                print 'Exception', e

            data = {'success': 'true'}

    except Exception, e:
        print "====Exception", e
        data = {
            'success': 'false',
            'message': str(e)
        }
    return 1



def save_places(zipped_wk, city_obj, place_type):
    try:
        i = 0
        for interest_name, interest_img in zipped_wk:
            print "============================================================\n\n"
            print interest_name
            print "============================================================\n\n"
            interest_name = interest_name.strip()
            if i != 0:
                interest_name = interest_name[1:]
            i = i + 1
            print "============================================================\n\n"
            print interest_name
            print "============================================================\n\n"
            if interest_name != '' and interest_img != '':
                interest_name_obj = Places(
                    city_place_id=city_obj,
                    place_name=str(interest_name),
                    place_image=interest_img,
                    place_type=place_type,
                    created_date=datetime.now(),
                    created_by="Admin",
                    updated_by="Admin",
                    updated_date=datetime.now()
                )
                interest_name_obj.save()
            data = {'success': 'true'}

    except Exception, e:
        data = {
            'success': 'false',
            'message': str(e)
        }
    return 1 


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def reference_data(request):
    try:
        adv_list = []
        country=''
        country = request.GET.get('country')
        state=''
        state = request.GET.get('state')
        status1 = ''
        status1 = request.GET.get('status')
        print 'status',status1
        if country:
            city_obj = City_Place.objects.filter(country_id=country)
            city_obj1 = City_Place.objects.filter(country_id=country).count()
        elif state:
            city_obj = City_Place.objects.filter(state_id=state)
            city_obj1 = City_Place.objects.filter(state_id=state).count()
        elif status1 == "active":
            city_obj = City_Place.objects.filter(city_status="1")
            city_obj1 = City_Place.objects.filter(city_status="1").count()
        elif status1 == "inactive":
            city_obj = City_Place.objects.filter(city_status="0")
            city_obj1 = City_Place.objects.filter(city_status="0").count()
        elif status1 == "show_all":
            city_obj = City_Place.objects.all()
            city_obj1 = City_Place.objects.all().count() 
        else:
            city_obj = City_Place.objects.all()
            city_obj1 = City_Place.objects.all().count()    

        for adv in city_obj:
            city_place_id = str(adv.city_place_id)

            if adv.city_image:
                city_image=SERVER_URL + adv.city_image.url
            else:
                city_image=SERVER_URL + '/static/assets/layouts/layout2/img/City_Hoopla_Logo.png'

            active_advert = 'No'
            advert_active_list = Advert.objects.filter(city_place_id=city_place_id,status="1").count()
            advert_inactive_list = Advert.objects.filter(city_place_id=city_place_id,status="0").count()
            print "advert_active_list",advert_active_list
            print "advert_inactive_list",advert_inactive_list
            advert_obj_list = Advert.objects.filter(city_place_id=city_place_id,status="1")
            for advert_obj in advert_obj_list:
                advert_id = str(advert_obj.advert_id)
                pre_date = datetime.now().strftime("%m/%d/%Y")
                advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)
                end_date = advert_sub_obj.business_id.end_date
                if pre_date<end_date:
                    active_advert = 'Yes'

            if adv.city_status == '1':
                status="Active"
                if active_advert == 'No':
                    print "IN ACTIVE IF"
                    if advert_active_list == 0:
                       print "=========IN Active if"
                       edit = 'edit'
                       delete = 'delete'
                    else:
                        edit = 'edit'
                        delete = 'delete1'
                else:
                    print "IN ACTIVE ELSE"
                    delete = 'delete1'
                    edit = 'edit'
                # edit = '<a class="col-md-offset-1 col-md-1" style="text-align: center; margin-left: 32% ! important;" href="/edit-city/?city_place_id=' + str(adv.city_place_id) + '" class="edit" data-toggle="modal"><i class="fa fa-pencil"></i></a>'    
                # delete = '<a class="col-md-1" style="text-align: center;" id="'+str(adv.city_place_id)+'" onclick="delete_user_detail(this.id)" class="fa  fa-trash-o fa-lg"><i class="fa fa-trash"></a>'    
                # action=edit + delete
            else:
                status="Inactive"
                edit = 'no'
                delete = 'no'
                # active = '<a class="col-md-2" id="'+str(adv.city_place_id)+'" onclick="active_service(this.id);" style="text-align: center;letter-spacing: 5px;width:15%;margin-left: 31% !important;" title="Activate" class="edit" data-toggle="modal" ><i class="fa fa-repeat"></i></a>'
                
            temp_obj = {'edit':edit,'delete':delete,'city_image':city_image,'city_place_id':city_place_id,'city_name':adv.city_id.city_name,'country':adv.country_id.country_name,'state':adv.state_id.state_name,'status':status}
            adv_list.append(temp_obj)
                
        data = {'success':'true','country':country,'username':request.session['login_user'],'city_status':status1,'state':state,'city_count':city_obj1,'city_list':adv_list,'country_list':get_country(request),'state_list': get_states(request)}

    except Exception, e:
        print 'Exception : ', e
        data = {'data': 'none'}
    return render(request,'Admin/rdm.html',data)  



@csrf_exempt
def delete_city(request):
        try:
            adv_obj = City_Place.objects.get(city_place_id=request.POST.get('city_place_id'))
            adv_obj.city_status = '0'
            adv_obj.save()
            data = {'message': 'City Inactivated Successfully', 'success':'true'}
            city_delete(adv_obj)
            delete_city_sms(adv_obj)
        except IntegrityError as e:
          print e
        except Exception,e:
            print e
        print "Final Data: ",data
        return HttpResponse(json.dumps(data), content_type='application/json')


def delete_city_sms(city_obj):
    authkey = "118994AIG5vJOpg157989f23"
    # user_obj = Supplier.objects.get(supplier_id=su_id)
    #    contact_no = user_obj.contact_no
    #    print '---------contact_no------',contact_no

    mobiles = "+919403884595"
    message = "Hi Admin, \n City \t" + str(city_obj.city_id.city_name) + "\t has been deactivated successfully"
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
def active_city(request):
        # pdb.set_trace()
        try:
            city_obj = City_Place.objects.get(city_place_id=request.POST.get('city_place_id'))
            city_obj.city_status = '1'
            city_obj.save()
            city_activate_mail(city_obj)
            data = {'message': 'City_Place activated Successfully', 'success':'true'}

        except IntegrityError as e:
          print e
        except Exception,e:
            print e
        print "Final Data: ",data
        return HttpResponse(json.dumps(data), content_type='application/json')


def city_activate_mail(city_obj):
    gmail_user = "donotreply@city-hoopla.com"# "cityhoopla2016"
    gmail_pwd =  "Hoopla123#"#"cityhoopla@2016"
    FROM = 'Team CityHoopla<donotreply@city-hoopla.com>'
    TO = ['cityhoopla2016@gmail.com']
    #pdb.set_trace()
    try:
        TEXT = "Hi Admin,\nCity " + str(city_obj.city_id.city_name) + " " +"has been activated successfully.\nTo view complete details visit portal and follow - Reference Data -> City\n\n Thank You,"+'\n'+"CityHoopla Team"
        SUBJECT = "City Activated Successfully!"
        #server = smtplib.SMTP_SSL()
        #server = smtplib.SMTP("smtp.gmail.com", 587) 
        server = smtplib.SMTP("smtpout.asia.secureserver.net", 80)
        #server = smtplib.SMTP_TSL('smtpout.secureserver.net', 465)
        server.ehlo()
        #server.starttls()
        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException,e:
        print e
    return 1
 
@csrf_exempt
def delete_place_image(request):
    place_obj = Places.objects.get(place_id=request.POST.get('place_id'))
    place_obj.delete()
    data = {"success":"true"}
    return HttpResponse(json.dumps(data), content_type='application/json')
      
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_city(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        try:
            city_obj = City_Place.objects.get(city_place_id=request.GET.get('city_place_id'))

            if city_obj.city_image:
                city_image = SERVER_URL + city_obj.city_image.url
                file_name = city_image[47:]
            else:
                city_image = SERVER_URL + '/static/assets/layouts/layout2/img/City_Hoopla_Logo.png'
                file_name = ""

            city_dict = {
                'success': 'true',
                'city_place_id': city_obj.city_place_id,
                'city_name': city_obj.city_id.city_id,
                'city_place_name': city_obj.city_id.city_name,
                'state': city_obj.state_id.state_id,
                'state_name': city_obj.state_id.state_name,
                'climate': city_obj.climate or '',
                'about_city': city_obj.about_city or '',
                'language': city_obj.language or '',
                'population': city_obj.population or '',
                'timezone': str(city_obj.time_zone) ,
                'cityimage': city_image,
                'filename': file_name,
                'country': city_obj.country_id.country_id,
                'country_name': city_obj.country_id.country_name,
                'currency': city_obj.currency
            }

            city_list = City.objects.filter(state_id=city_obj.state_id.state_id)

            intr_list = []
            point_of_intrest = Places.objects.filter(city_place_id=city_obj, place_type='point_of_interest')
            poi_index = 0

            if point_of_intrest:
                print 'point_of_intrest====>', point_of_intrest
                poi_index = len(point_of_intrest) - 1
                i = 0;
                for place in point_of_intrest:
                    try:
                        place_image = SERVER_URL + place.place_image.url
                        file_name = place_image[47:]
                    except:
                        place_image = ''
                        file_name = ''
                    place_data = {
                        'image_id': i,
                        'place_id': 'old_' + str(place.place_id),
                        'place_name': place.place_name,
                        'place_image': place_image,
                        'filename': file_name
                    }

                    intr_list.append(place_data)
                    i = i + 1

            shop_list = []
            shop_name = Places.objects.filter(city_place_id=city_obj, place_type='where_to_shop')
            shop_index = 0
            if shop_name:
                shop_index = len(shop_name) - 1
                i = 0;
                for shop in shop_name:
                    place_image = SERVER_URL + shop.place_image.url
                    file_name = place_image[47:]
                    place_data = {
                        'place_id': 'old_' + str(shop.place_id),
                        'image_id': i,
                        'place_name': shop.place_name,
                        'place_image': place_image,
                        'filename': file_name
                    }
                    shop_list.append(place_data)
                    i = i + 1
            hosp_list = []
            hospital = Places.objects.filter(city_place_id=city_obj, place_type='reputed_hospitals')
            hospital_index = 0
            if hospital:
                hospital_index = len(hospital) - 1
                i = 0;
                for hosp in hospital:
                    place_image = SERVER_URL + hosp.place_image.url
                    file_name = place_image[47:]
                    place_data = {
                        'place_id': 'old_' + str(hosp.place_id),
                        'image_id': i,
                        'place_name': hosp.place_name,
                        'place_image': place_image,
                        'filename': file_name
                    }
                    hosp_list.append(place_data)
                    i = i + 1
            clg_list = []
            college = Places.objects.filter(city_place_id=city_obj, place_type='college_and_universities')
            college_index = 0
            if college:
                college_index = len(college) - 1
                i = 0;
                for clg in college:
                    place_image = SERVER_URL + clg.place_image.url
                    file_name = place_image[32:]
                    place_data = {
                        'image_id': i,
                        'place_id': 'old_' + str(clg.place_id),
                        'place_name': clg.place_name,
                        'place_image': place_image,
                        'filename': file_name
                    }
                    clg_list.append(place_data)
                    i = i + 1
            data = {'poi_index': poi_index, 'shop_index': shop_index,
                    'hospital_index': hospital_index, 'college_index': college_index, 'city': city_dict,
                    'city_list': city_list, 'interest': intr_list, 'shops': shop_list, 'hospitals': hosp_list,
                    'colleges': clg_list, 'username': request.session['login_user']}
        except Exception, e:
            print 'Exception:', e
            data = {'data': e}
        return render(request, 'Admin/edit_city.html', data)  

@csrf_exempt
def update_city(request):
    print 'in update city'
    # pdb.set_trace()
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
    try:
        if request.method == "POST":
            print "===Data===",request.POST
            print "===Data===",request.FILES
            

            city_obj = City_Place.objects.get(city_place_id=request.POST.get('city_place_id'))
            
            if request.POST.get('about_city'):
                city_obj.about_city=request.POST.get('about_city')

            if request.POST.get('climate'):
                city_obj.climate=request.POST.get('climate')

            if request.POST.get('population'):
                city_obj.population = request.POST.get('population')

            if request.POST.get('timezone'):
                city_obj.time_zone=request.POST.get('timezone')

            if request.POST.get('language'):
                city_obj.language=request.POST.get('language')

            if request.POST.get('currency'):
                city_obj.currency=request.POST.get('currency')

            city_obj.save();

            if request.POST['check_image'] == "1":
                city_obj.city_image = request.FILES['city_image']
                city_obj.save()

            city_id=request.POST.get('city_place_id')

            city_obj = City_Place.objects.get(city_place_id=request.POST.get('city_place_id'))

            poi_range = request.POST.get('poi_range')
            print 'poi_range',poi_range
            point_of_interest_id_list = request.POST.get('point_of_interest_id_list')
            point_of_interest_id_list = str(point_of_interest_id_list).split(',')
            
            point_of_interest_list = request.POST.get('point_of_interest_list')
            point_of_interest_list = str(point_of_interest_list).split('_POI_CH')

            point_of_interest_image_list = []
        
            for i in range(int(poi_range)+1):
                image = "point_of_interest_image" + str(i)
                try:
                    point_of_interest_image_list.append(request.FILES[image]) 
                    print "IN TRY---,point_of_interest_image_list",point_of_interest_image_list                
                except:
                    point_of_interest_image_list.append('')
                    print "IN EXCEPT ---,point_of_interest_image_list",point_of_interest_image_list

            place_type = 'point_of_interest'

            zipped_wk = zip(point_of_interest_id_list,point_of_interest_list,point_of_interest_image_list)
            update_places(zipped_wk,city_obj,place_type)
                 
            shop_id_list = request.POST.get('shop_id_list')
            shop_id_list = str(shop_id_list).split(',')
            
            shop_list = request.POST.get('shop_list')
            shop_list = str(shop_list).split('_SOP_CH')

            shop_range = request.POST.get('shop_range')
            shop_image_list = []
            for i in range(int(shop_range)+1):
                image = "shop_image" + str(i)
                try:
                    shop_image_list.append(request.FILES[image])                 
                except: 
                    shop_image_list.append('')

            zipped_wk = zip(shop_id_list,shop_list,shop_image_list)
            place_type = 'where_to_shop'
            update_places(zipped_wk,city_obj,place_type)
            
            hospital_id_list = request.POST.get('hospital_id_list')
            hospital_id_list = str(hospital_id_list).split(',')
            
            hospital_list = request.POST.get('hospital_list')
            hospital_list = str(hospital_list).split('_HOS_CH')

            hospital_range = request.POST.get('hospital_range')
            hospital_image_list = []
            for i in range(int(hospital_range)+1):
                image = "hospital_image" + str(i)
                try:
                    hospital_image_list.append(request.FILES[image])                 
                except:
                    hospital_image_list.append('')

            zipped_wk = zip(hospital_id_list,hospital_list,hospital_image_list)
            place_type = 'reputed_hospitals'
            update_places(zipped_wk,city_obj,place_type)
            

            college_id_list = request.POST.get('college_id_list')
            college_id_list = str(college_id_list).split(',')

            college_list = request.POST.get('college_list')
            college_list = str(college_list).split('_EDU_CH')


            college_range = request.POST.get('college_range')
            college_image_list = []
            for i in range(int(college_range)+1):
                image = "college_image" + str(i)
                try:
                    college_image_list.append(request.FILES[image])                 
                except:
                    college_image_list.append('')

            zipped_wk = zip(college_id_list,college_list,college_image_list)
            place_type = 'college_and_universities'
            update_places(zipped_wk,city_obj,place_type)

           
            
            city_update(city_obj)
            update_city_sms(city_obj)
            data = {'success': 'true'}
        else:
            data = {'success': 'false'}
    except Exception,e:
        print 'Exception:',e
        data = {'data':'none'}
    return HttpResponse(json.dumps(data), content_type='application/json')

def update_city_sms(city_obj):
    authkey = "118994AIG5vJOpg157989f23"
    # user_obj = Supplier.objects.get(supplier_id=su_id)
    #    contact_no = user_obj.contact_no
    #    print '---------contact_no------',contact_no

    mobiles = "+919403884595"
    message = "City \t" + str(city_obj.city_id.city_name) + "\t has been updated successfully"
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
def update_city_data(request):
    print 'in update city data'
##    pdb.set_trace()
    try:
        if request.method == "POST":
            
            city_obj = City_Place.objects.get(city_place_id=request.POST.get('city_place_id'))

            poi_range = request.POST.get('poi_range')
            point_of_interest_id_list = request.POST.get('point_of_interest_id_list')
            point_of_interest_id_list = str(point_of_interest_id_list).split(',')
            
            point_of_interest_list = request.POST.get('point_of_interest_list')
            point_of_interest_list = str(point_of_interest_list).split(',')

            point_of_interest_image_list = []
        
            for i in range(int(poi_range)+1):
                image = "point_of_interest_image" + str(i)
                try:
                    point_of_interest_image_list.append(request.FILES[image])                 
                except:
                    point_of_interest_image_list.append('')

            place_type = 'point_of_interest'

            zipped_wk = zip(point_of_interest_id_list,point_of_interest_list,point_of_interest_image_list)
            update_places(zipped_wk,city_obj,place_type)
                 
            shop_id_list = request.POST.get('shop_id_list')
            shop_id_list = str(shop_id_list).split(',')
            
            shop_list = request.POST.get('shop_list')
            shop_list = str(shop_list).split(',')

            shop_range = request.POST.get('shop_range')
            shop_image_list = []
            for i in range(int(shop_range)+1):
                image = "shop_image" + str(i)
                try:
                    shop_image_list.append(request.FILES[image])                 
                except: 
                    shop_image_list.append('')

            zipped_wk = zip(shop_id_list,shop_list,shop_image_list)
            place_type = 'where_to_shop'
            update_places(zipped_wk,city_obj,place_type)
            
            hospital_id_list = request.POST.get('hospital_id_list')
            hospital_id_list = str(hospital_id_list).split(',')
            
            hospital_list = request.POST.get('hospital_list')
            hospital_list = str(hospital_list).split(',')

            hospital_range = request.POST.get('hospital_range')
            hospital_image_list = []
            for i in range(int(hospital_range)+1):
                image = "hospital_image" + str(i)
                try:
                    hospital_image_list.append(request.FILES[image])                 
                except:
                    hospital_image_list.append('')

            zipped_wk = zip(hospital_id_list,hospital_list,hospital_image_list)
            place_type = 'reputed_hospitals'
            update_places(zipped_wk,city_obj,place_type)
            

            college_id_list = request.POST.get('college_id_list')
            college_id_list = str(college_id_list).split(',')

            college_list = request.POST.get('college_list')
            college_list = str(college_list).split(',')


            college_range = request.POST.get('college_range')
            college_image_list = []
            for i in range(int(college_range)+1):
                image = "college_image" + str(i)
                try:
                    college_image_list.append(request.FILES[image])                 
                except:
                    college_image_list.append('')

            zipped_wk = zip(college_id_list,college_list,college_image_list)
            place_type = 'college_and_universities'
            update_places(zipped_wk,city_obj,place_type)
            
            data = {'success': 'true'}
        else:
            data = {'success': 'false'}
    except Exception,e:
        data = {'data':'none'}
    return HttpResponse(json.dumps(data), content_type='application/json')
 
def city_update(city_obj):
    gmail_user = "donotreply@city-hoopla.com"# "cityhoopla2016"
    gmail_pwd =  "Hoopla123#"#"cityhoopla@2016"
    FROM = 'Team CityHoopla<donotreply@city-hoopla.com>'
    TO = ['cityhoopla2016@gmail.com']
    #pdb.set_trace()
    try:
        TEXT = "Hi Admin,\nCity " + str(city_obj.city_id.city_name) + " " +"has been updated successfully.\nTo view complete details visit portal and follow - Reference Data -> City\n\nThank You,"+'\n'+"CityHoopla Team"
        SUBJECT = "City Updated Successfully!"
        #server = smtplib.SMTP_SSL()
        #server = smtplib.SMTP("smtp.gmail.com", 587) 
        server = smtplib.SMTP("smtpout.asia.secureserver.net", 80)
        #server = smtplib.SMTP_TSL('smtpout.secureserver.net', 465)
        server.ehlo()
        #server.starttls()
        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException,e:
        print e
    return 1
 
def city_delete(adv_obj):
    gmail_user = "donotreply@city-hoopla.com"# "cityhoopla2016"
    gmail_pwd =  "Hoopla123#"#"cityhoopla@2016"
    FROM = 'Team CityHoopla<donotreply@city-hoopla.com>'
    TO = ['cityhoopla2016@gmail.com']
    #pdb.set_trace()
    try:
        TEXT = "Hi Admin,\nCity " + str(adv_obj.city_id.city_name) + " " +"has been deactivated successfully.\nTo view complete details visit portal and follow - Reference Data -> City\n\nThank You,"+'\n'+"CityHoopla Team"
        SUBJECT = "City Deactivated Successfully!"
        #server = smtplib.SMTP_SSL()
        #server = smtplib.SMTP("smtp.gmail.com", 587) 
        server = smtplib.SMTP("smtpout.asia.secureserver.net", 80)
        #server = smtplib.SMTP_TSL('smtpout.secureserver.net', 465)
        server.ehlo()
        #server.starttls()
        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException,e:
        print e
    return 1

def city_add(city_obj):
    gmail_user = "donotreply@city-hoopla.com"# "cityhoopla2016"
    gmail_pwd =  "Hoopla123#"#"cityhoopla@2016"
    FROM = 'Team CityHoopla<donotreply@city-hoopla.com>'
    TO = ['cityhoopla2016@gmail.com']
    #pdb.set_trace()
    try:
        TEXT = "Hi Admin,\nCity " + str(city_obj.city_id.city_name) + " " +"has been added successfully.\nTo view complete details visit portal and follow - Reference Data -> City\n\nThank You,"+'\n'+"CityHoopla Team"
        SUBJECT = "City Added Successfully!"
        #server = smtplib.SMTP_SSL()
        #server = smtplib.SMTP("smtp.gmail.com", 587) 
        server = smtplib.SMTP("smtpout.asia.secureserver.net", 80)
        #server = smtplib.SMTP_TSL('smtpout.secureserver.net', 465)
        server.ehlo()
        #server.starttls()
        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException,e:
        print e
    return 1   


@csrf_exempt
def user_list(request):
    try:
        try:
            data = {'success':'true'}

        except IntegrityError as e:
            print e
            data = {'success':'false','message':'Error in  loading page. Please try after some time','username':request.session['login_user']}
    except MySQLdb.OperationalError, e:
        print e
    except Exception,e:
        print 'Exception ',e

    print data
    return render(request,'Admin/user-list.html',data)

@csrf_exempt
def admin_add_user(request):
    try:
        try:
            user_role_list = UserRole.objects.filter(role_status='1')
            data = {'success':'true','user_role_list':user_role_list,'city_places_list':get_city_places(request)}
            #data = {,'username':request.session['login_user']}

        except IntegrityError as e:
            print e
            data = {'success':'false','message':'Error in  loading page. Please try after some time','username':request.session['login_user']}
    except MySQLdb.OperationalError, e:
        print e
    except Exception,e:
        print 'Exception ',e

    print data
    return render(request,'Admin/add-user.html',data)

@csrf_exempt
def add_new_user(request):
    try:
        role_id = UserRole.objects.get(role_id=request.POST.get('role'))
        user_obj=UserProfile(
            username = request.POST.get('Username'),
            user_first_name = request.POST.get('First_name'),
            user_last_name = request.POST.get('Last_name'),
            user_contact_no=request.POST.get('phone_no'),
            usre_email_id=request.POST.get('Username'),
            user_role=role_id,
            city_place_id=City_Place.objects.get(city_place_id=request.POST.get('city')) if request.POST.get(
                    'city') else None,
            user_created_date = datetime.now(),
            user_status = '1',
            #user_created_by = request.session['login_user']
        );
        user_obj.save();
        user_obj.set_password(request.POST.get('password'));
        user_obj.save();

        data={
            'success':'true',
            'message':'User Created Successfully.'
        }
    except Exception, e:
        data={
            'success':'false',
            'message':str(e)
        }
    print data
    return HttpResponse(json.dumps(data),content_type='application/json')


def edit_user_detail(request):
    print request.method
    try:
        data = {}
        final_list = []
        #print 'User ID: ',request.GET.get('user_id')
        try:
            if request.method == "GET":
                user_obj = UserProfile.objects.get(usre_email_id=request.GET.get('user_id'))
                print user_obj
                user_role_list = UserRole.objects.filter(role_status='1')
                role_id = str(user_obj.user_role.role_id)
                role_name = user_obj.user_role.role_name
                city_id = str(user_obj.city_place_id)
                user_first_name = user_obj.user_first_name
                user_last_name = user_obj.user_last_name
                user_email_id = user_obj.usre_email_id
                user_contact_no = user_obj.user_contact_no
                data = {'success':'true','city_id':city_id,'city_places_list':get_city_places(request),'user_role_list':user_role_list,'role_name':role_name,'role_id':role_id,'user_first_name':user_first_name,'user_last_name':user_last_name,'user_email_id':user_email_id,'user_contact_no':user_contact_no}
        except IntegrityError as e:
            print e
            data = {'success':'false','message':'Error in  loading page. Please try after some time'}

    except MySQLdb.OperationalError, e:
        print e

    except Exception,e:
        print 'Exception ',e
    print data
    return render(request,'Admin/edit-user.html',data)


def edit_profile(request):
    print request.method
    try:
        data = {}
        final_list = []
        #print 'User ID: ',request.GET.get('user_id')
        try:
            if request.method == "GET":
                user_obj = UserProfile.objects.get(usre_email_id=request.GET.get('user_id'))
                print user_obj
                user_role_list = UserRole.objects.filter(role_status='1')
                role_id = str(user_obj.user_role.role_id)
                role_name = user_obj.user_role.role_name
                user_first_name = user_obj.user_first_name
                user_last_name = user_obj.user_last_name
                user_email_id = user_obj.usre_email_id
                user_contact_no = user_obj.user_contact_no
                data = {'success':'true','user_role_list':user_role_list,'role_name':role_name,'role_id':role_id,'user_first_name':user_first_name,'user_last_name':user_last_name,'user_email_id':user_email_id,'user_contact_no':user_contact_no}
        except IntegrityError as e:
            print e
            data = {'success':'false','message':'Error in  loading page. Please try after some time'}

    except MySQLdb.OperationalError, e:
        print e

    except Exception,e:
        print 'Exception ',e
    print data
    return render(request,'Admin/edit_profile.html',data)

    

@csrf_exempt
def save_user(request):
    try:
        print 'in login'
        if request.POST:
            username = request.POST.get('Username')
            password = request.POST.get('oldpassword')
            try:
                user = authenticate(username=username, password=password)
                print 'valid form befor----->'
                if user:
                    role_id = UserRole.objects.get(role_id=request.POST.get('role'))
                    user_obj = UserProfile.objects.get(usre_email_id=request.POST.get('Username'))

                    user_obj.user_first_name = request.POST.get('First_name')
                    user_obj.user_last_name = request.POST.get('Last_name')
                    user_obj.user_contact_no = request.POST.get('phone_no')
                    user_obj.user_role = role_id
                    user_obj.city_place_id=City_Place.objects.get(city_place_id=request.POST.get('city')) if request.POST.get(
                    'city') else None
                    user_obj.user_updated_date = datetime.now()
                    user_obj.user_status = '1'

                    user_obj.save();
                    user_obj.set_password(request.POST.get('newpassword'));
                    user_obj.save();

                    data={
                        'success':'true',
                        'message':'User Updated Successfully.'
                    }
                else:
                    data = {'success': 'false', 'message': 'Invalid Password'}
                    return HttpResponse(json.dumps(data), content_type='application/json')


            except Exception as e:
                print e
                data = {'success': 'false', 'message': 'Invalid Username'}
                return HttpResponse(json.dumps(data), content_type='application/json')

    except Exception, e:
        data={
            'success':'false',
            'message':str(e)
        }
    print data
    return HttpResponse(json.dumps(data),content_type='application/json')

@csrf_exempt
def save_user1(request):
    try:
        if request.POST:
            Username=request.POST.get('Username')
            print '............Username............',Username
            role_id = UserRole.objects.get(role_id=request.POST.get('role'))
            user_obj = UserProfile.objects.get(usre_email_id=request.POST.get('Username'))
            user_obj.user_first_name = request.POST.get('First_name')
            user_obj.user_last_name = request.POST.get('Last_name')
            user_obj.user_contact_no = request.POST.get('phone_no')
            user_obj.user_role = role_id
            user_obj.city_place_id=City_Place.objects.get(city_place_id=request.POST.get('city')) if request.POST.get(
            'city') else None
            user_obj.user_updated_date = datetime.now()
            user_obj.user_status = '1'

            user_obj.save()

            data={
                'success':'true',
                'message':'User Updated Successfully.'
            }
    except Exception, e:
        data={
            'success':'false',
            'message':str(e)
        }
    print data
    return HttpResponse(json.dumps(data),content_type='application/json')

def get_data(request):
    try:
        data = {}
        final_list = []
        try:
            sort_var=request.GET.get('sort_var')
            if sort_var == 'show_all':
                user_list = UserProfile.objects.filter()
                for user_obj in user_list:
                    if user_obj.user_role:
                        role_id = user_obj.user_role.role_name
                        user_first_name = str(user_obj.user_first_name)
                        user_last_name = str(user_obj.user_last_name)
                        user_name = user_first_name +" "+ user_last_name
                        usre_email_id = user_obj.usre_email_id
                        user_contact_no = user_obj.user_contact_no
                        edit = '<a id="'+str(user_obj)+' " style="text-align: center;letter-spacing: 5px;width:15%;" title="Edit" class="edit" data-toggle="modal" href="/edit-user-detail/?user_id='+str(user_obj)+'"><i class="fa fa-pencil"></i></a>'
                        delete = '<a id="'+str(user_obj)+'" onclick="delete_user_detail(this.id)" style="text-align: center;letter-spacing: 5px;width:15%;" title="Delete"  ><i class="fa fa-trash"></i></a>'
                        if user_obj.user_status == "1":                        
                            status = 'Active'
                            actions =  edit +" "+ delete
                        else:
                            status = 'Inactive'
                            actions = '<a id="'+str(user_obj)+'" onclick="reactivate_user(this.id)" style="text-align: center;letter-spacing: 5px;width:15%;" title="Reactivate"><i class="fa fa-undo"></i></a>'                       
                        list = {'user_name':user_name,'actions':actions,'role_id':role_id,'usre_email_id':usre_email_id,'user_contact_no':user_contact_no,'status':status}
                        final_list.append(list)


                data = {'success':'true','data':final_list}

            else :
                user_list = UserProfile.objects.filter(user_status=sort_var)
                if user_list:
                    for user_obj in user_list:
                        if user_obj.user_role:
                            role_id = user_obj.user_role.role_name
                            user_first_name = str(user_obj.user_first_name)
                            user_last_name = str(user_obj.user_last_name)
                            user_name = user_first_name +" "+ user_last_name
                            usre_email_id = user_obj.usre_email_id
                            user_contact_no = user_obj.user_contact_no
                            edit = '<a id="'+str(user_obj)+' " style="text-align: center;letter-spacing: 5px;width:15%;" title="Edit" class="edit" data-toggle="modal" href="/edit-user-detail/?user_id='+str(user_obj)+'"><i class="fa fa-pencil"></i></a>'
                            delete = '<a id="'+str(user_obj)+'" onclick="delete_user_detail(this.id)" style="text-align: center;letter-spacing: 5px;width:15%;" title="Delete"  ><i class="fa fa-trash"></i></a>'
                            if user_obj.user_status == "1":                        
                                status = 'Active'
                                actions =  edit +" "+ delete
                            else:
                                status = 'Inactive'
                                actions = '<a id="'+str(user_obj)+'" onclick="reactivate_user(this.id)" style="text-align: center;letter-spacing: 5px;width:15%;" title="Reactivate"><i class="fa fa-undo"></i></a>'                       
                            list = {'user_name':user_name,'actions':actions,'role_id':role_id,'usre_email_id':usre_email_id,'user_contact_no':user_contact_no,'status':status}
                 
                            final_list.append(list)
                else :
                    final_list = []


                data = {'success':'true','data':final_list}


        except IntegrityError as e:
            print e
            data = {'success':'false','message':'Error in  loading page. Please try after some time'}
        except MySQLdb.OperationalError, e:
            print e
    except Exception,e:
        print 'Exception ',e
    return HttpResponse(json.dumps(data), content_type='application/json')


def view_user_list(request):
    try:
        data = {}
        final_list = []
        try:
            user_list = UserProfile.objects.filter()
            for user_obj in user_list:
                if user_obj.user_role:
                    role_id = user_obj.user_role.role_name
                    city =user_obj.city_place_id.city_id.city_name
                    user_first_name = str(user_obj.user_first_name)
                    user_last_name = str(user_obj.user_last_name)
                    user_name = user_first_name +" "+ user_last_name
                    usre_email_id = user_obj.usre_email_id
                    user_contact_no = user_obj.user_contact_no
                    edit = '<a id="'+str(user_obj)+' " style="text-align: center;letter-spacing: 5px;width:15%;" title="Edit" class="edit" data-toggle="modal" href="/edit-user-detail/?user_id='+str(user_obj)+'"><i class="fa fa-pencil"></i></a>'
                    delete = '<a id="'+str(user_obj)+'" onclick="delete_user_detail(this.id)" style="text-align: center;letter-spacing: 5px;width:15%;" title="Delete"  ><i class="fa fa-trash"></i></a>'
                    if user_obj.user_status == "1":
                        print "if"
                        status = 'Active'
                        actions =  edit +" "+ delete
                    else:
                        print "else"
                        status = 'Inactive'
                        actions = '<a id="'+str(user_obj)+'" onclick="reactivate_user(this.id)" style="text-align: center;letter-spacing: 5px;width:15%;" title="Reactivate"><i class="fa fa-undo"></i></a>'
                    list = {'city':city,'user_name':user_name,'actions':actions,'role_id':role_id,'usre_email_id':usre_email_id,'user_contact_no':user_contact_no,'status':status}
                    final_list.append(list)
                data = {'success':'true','data':final_list}
        except IntegrityError as e:
            print e
            data = {'success':'false','message':'Error in  loading page. Please try after some time'}
        except MySQLdb.OperationalError, e:
            print e
    except Exception,e:
        print 'Exception ',e
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def delete_user(request):
    try:
        user_obj = UserProfile.objects.get(usre_email_id=request.POST.get('user_id'))
        user_obj.user_status = '0'
        user_obj.save()
        data = {'message': 'User Inactivated Successfully', 'success': 'true'}

    except IntegrityError as e:
        print e
    except Exception, e:
        print e
    print "Final Data: ", data
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def activate_user(request):
        try:
            user_obj = UserProfile.objects.get(usre_email_id=request.POST.get('user_id'))
            user_obj.user_status = '1'
            user_obj.save()
            data = {'message': 'User Activated Successfully', 'success':'true'}

        except IntegrityError as e:
          print e
        except Exception,e:
            print e
        print "Final Data: ",data
        return HttpResponse(json.dumps(data), content_type='application/json')
