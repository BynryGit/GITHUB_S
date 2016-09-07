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
# calender
from datetime import date
import calendar
from datetime import datetime
from django.db.models import Count
#forgot Pass
import string
import random


SERVER_URL = "http://192.168.0.3:8080"   
#SERVER_URL = "http://127.0.0.1:8000"

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def rate_card(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:    
        data = {'username':request.session['login_user']}
        return render(request,'Admin/rate_card.html',data)

def login_open(request):
    if request.user.is_authenticated():
        return redirect('/index/')
    else:
        form = CaptchaForm()
        return render_to_response('Admin/user_login.html', dict(
            form=form
        ), context_instance=RequestContext(request))

def backoffice(request):
    form = CaptchaForm()
##    if request.user.is_authenticated():
##        return redirect('/dashboard/')
    #return render_to_response('index.html')
    return render(request,'Admin/user_login.html', dict(form=form))

@csrf_exempt
def subscriber_dashboard(request):
    try:
        data = {}
        final_list = []
        final_list1 = []
        try:
            print '......$$.supplier_id....$$..',request.GET.get('supplier_id')

            Supplier_obj = Supplier.objects.get(supplier_id=request.GET.get('supplier_id'))
            print "..................Supplier_obj.........",Supplier_obj

            logo= SERVER_URL + Supplier_obj.logo.url

            #########.............Advert Stats.........................#####
            Advert_list = Advert.objects.filter(supplier_id=request.GET.get('supplier_id'))
            print "..................Advert_list.........",Advert_list

            avail_discount_count = 0
            avail_callbacks_count = 0
            avail_callsmade_count = 0
            avail_shares_count = 0

            for advert_obj in Advert_list:
                advert_id = advert_obj.advert_id
                discount_count = CouponCode.objects.filter(advert_id=advert_id).count()
                callbacks_count = AdvertCallbacks.objects.filter(advert_id=advert_id).count()
                callsmade_count = AdvertCallsMade.objects.filter(advert_id=advert_id).count()
                shares_count = AdvertShares.objects.filter(advert_id=advert_id).count()


                avail_discount_count = avail_discount_count + discount_count
                avail_callbacks_count = avail_callbacks_count + callbacks_count
                avail_callsmade_count = avail_callsmade_count + callsmade_count
                avail_shares_count = avail_shares_count + shares_count


            #######.................Total Bookings Graph...............########
            
            FY_MONTH_LIST = [1,2,3,4,5,6,7,8,9,10,11,12]
            today = date.today()
            print '.......today.........',today
            start_date = date(today.year,01,01)
            print '...........start_date..........',start_date
            end_date = date(today.year,12,31) 
            monthly_count = []
            # jan,feb,mar,apr,may,jun,jul,aug,sep,octo,nov,dec
            coupon_code_list = CouponCode.objects.filter(creation_date__range=[start_date,end_date]).extra(select={'month': "EXTRACT(month FROM creation_date)"}).values('month').annotate(count=Count('advert_id'))
            print "...........coupon_code_list.......",coupon_code_list
            list={}


            for sub_obj in coupon_code_list:
                print "sub_obj.get('count')",sub_obj.get('count')
                if sub_obj.get('month'):
                    list[sub_obj.get('month')]=sub_obj.get('count') or '0.00'
                    print list
            

            for i in FY_MONTH_LIST:
                try:
                    monthly_count.append(list[i])
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

            ##########..................Total Views Graph.....................############

            current_date = datetime.now()
            print '...........current_date.........',current_date
            first = calendar.day_name[current_date.weekday()]
            print '...........first.........',first

            last_date = (datetime.now() - timedelta(days=7))
            print '...........last_date.........',last_date
            last_date2 = calendar.day_name[last_date.weekday()]
            print '...........last_date2.........',last_date2

            list = []
            total_view_list = AdvertTotalViews.objects.filter(creation_date__range=[last_date,current_date])
            mon=tue=wen=thus=fri=sat=sun=0
            if total_view_list:
                for view_obj in total_view_list:
                    creation_date=view_obj.creation_date
                    consumer_day = calendar.day_name[creation_date.weekday()]
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

            print "$$$",mon,tue,wen,thus,fri,sat,sun

            data = {'success':'true','logo':logo,'avail_callbacks_count':avail_callbacks_count,'avail_callsmade_count':avail_callsmade_count,'avail_shares_count':avail_shares_count,'avail_discount_count':avail_discount_count,'jan':jan,'feb':feb,'mar':mar,'apr':apr,'may':may,'jun':jun,'jul':jul,
               'aug':aug,'sep':sep,'oct':octo,'nov':nov,'dec':dec,'mon':mon,'tue':tue,'wen':wen,'thus':thus,'fri':fri,'sat':sat,'sun':sun}

        except IntegrityError as e:
            print e
            data = {'success':'false','message':'Error in  loading page. Please try after some time','username':request.session['login_user']}
    except MySQLdb.OperationalError, e:
        print e
    except Exception,e:
        print 'Exception ',e

    print data
    return render(request,'Admin/subscriber-dashboard.html',data)

@csrf_exempt
def get_filter(request):
    try:
        data = {}
        final_list = []
        final_list1 = []
        try: 
            if request.GET.get('week_var') == 'month':
                var1 = str(request.GET.get('week_var'))

                Supplier_obj = Supplier.objects.get(supplier_id=request.GET.get('supplier_id'))

                logo= SERVER_URL + Supplier_obj.logo.url

                #########.............Advert Stats.......For a Month..................#####
                today_date = str(datetime.now())
                one_month_date = str(datetime.now() - timedelta(days=30))
                Advert_list = Advert.objects.filter(supplier_id=request.GET.get('supplier_id'))

                avail_discount_count = 0
                avail_callbacks_count = 0
                avail_callsmade_count = 0
                avail_shares_count = 0

                for advert_obj in Advert_list:
                    advert_id = advert_obj.advert_id
                    discount_count = CouponCode.objects.filter(advert_id=advert_id,creation_date__range=[one_month_date,today_date]).count()
                    callbacks_count = AdvertCallbacks.objects.filter(advert_id=advert_id,creation_date__range=[one_month_date,today_date]).count()
                    callsmade_count = AdvertCallsMade.objects.filter(advert_id=advert_id,creation_date__range=[one_month_date,today_date]).count()
                    shares_count = AdvertShares.objects.filter(advert_id=advert_id,creation_date__range=[one_month_date,today_date]).count()


                    avail_discount_count = avail_discount_count + discount_count
                    avail_callbacks_count = avail_callbacks_count + callbacks_count
                    avail_callsmade_count = avail_callsmade_count + callsmade_count
                    avail_shares_count = avail_shares_count + shares_count

                
                #######.................Total Bookings Graph....For a Month...........########
                print '............Total Bookings Graph....For a Month....'
                today = date.today()
                date_cal=datetime(today.year,today.month,today.day)
                numb = (date_cal.day-1)//7+1

                coupon_code_count1 = 0
                coupon_code_count2 = 0
                coupon_code_count3 = 0
                coupon_code_count4 = 0
                coupon_code_count5 = 0
                for i in range(0,numb):
                    if i==0:
                        start_date = date(today.year,today.month,01)
                        end_date = date(today.year,today.month,8) 
                        coupon_code_count1 = CouponCode.objects.filter(creation_date__range=[start_date,end_date]).count()
                    elif i==1:
                        start_date = date(today.year,today.month,8)
                        end_date = date(today.year,today.month,16) 
                        coupon_code_count2 = CouponCode.objects.filter(creation_date__range=[start_date,end_date]).count()
                    elif i==2:
                        start_date = date(today.year,today.month,16)
                        end_date = date(today.year,today.month,23) 
                        coupon_code_count3 = CouponCode.objects.filter(creation_date__range=[start_date,end_date]).count()
                    elif i==3:
                        start_date = date(today.year,today.month,23)
                        end_date = date(today.year,today.month,30) 
                        coupon_code_count4 = CouponCode.objects.filter(creation_date__range=[start_date,end_date]).count()
                    elif i==4:
                        start_date = date(today.year,today.month,30)
                        end_date = date(today.year,today.month,31) 
                        coupon_code_count5 = CouponCode.objects.filter(creation_date__range=[start_date,end_date]).count()



                ##########..................Total Views Graph........for a month.............############
                
                print '.......Total Views Graph........for a month........'
                today = date.today()
                date_cal=datetime(today.year,today.month,today.day)
                numb = (date_cal.day-1)//7+1

                advert_total_count1 = 0
                advert_total_count2 = 0
                advert_total_count3 = 0
                advert_total_count4 = 0
                advert_total_count5 = 0

                for i in range(0,numb):
                    if i==0:
                        start_date = date(today.year,today.month,01)
                        end_date = date(today.year,today.month,8) 
                        advert_total_count1 = AdvertTotalViews.objects.filter(creation_date__range=[start_date,end_date]).count()
                    elif i==1:
                        start_date = date(today.year,today.month,8)
                        end_date = date(today.year,today.month,16) 
                        advert_total_count2 = AdvertTotalViews.objects.filter(creation_date__range=[start_date,end_date]).count()
                    elif i==2:
                        start_date = date(today.year,today.month,16)
                        end_date = date(today.year,today.month,23) 
                        advert_total_count3 = AdvertTotalViews.objects.filter(creation_date__range=[start_date,end_date]).count()
                    elif i==3:
                        start_date = date(today.year,today.month,23)
                        end_date = date(today.year,today.month,30) 
                        advert_total_count4 = AdvertTotalViews.objects.filter(creation_date__range=[start_date,end_date]).count()
                    elif i==4:
                        start_date = date(today.year,today.month,30)
                        end_date = date(today.year,today.month,31) 
                        advert_total_count5 = AdvertTotalViews.objects.filter(creation_date__range=[start_date,end_date]).count()
                data = {'var1':var1,'success':'true','logo':logo,'avail_callbacks_count':avail_callbacks_count,'avail_callsmade_count':avail_callsmade_count,'avail_shares_count':avail_shares_count,'avail_discount_count':avail_discount_count,
                    'coupon_code_count1':coupon_code_count1,'coupon_code_count2':coupon_code_count2,'coupon_code_count3':coupon_code_count3,'coupon_code_count4':coupon_code_count4,'coupon_code_count5':coupon_code_count5,'advert_total_count1':advert_total_count1,'advert_total_count2':advert_total_count2,
                   'advert_total_count3':advert_total_count3,'advert_total_count4':advert_total_count4,'advert_total_count5':advert_total_count5}

            if request.GET.get('week_var') == 'week':
                var1 = str(request.GET.get('week_var'))

                Supplier_obj = Supplier.objects.get(supplier_id=request.GET.get('supplier_id'))

                logo= SERVER_URL + Supplier_obj.logo.url

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
                    discount_count = CouponCode.objects.filter(advert_id=advert_id,creation_date__range=[one_month_date,today_date]).count()
                    callbacks_count = AdvertCallbacks.objects.filter(advert_id=advert_id,creation_date__range=[one_month_date,today_date]).count()
                    callsmade_count = AdvertCallsMade.objects.filter(advert_id=advert_id,creation_date__range=[one_month_date,today_date]).count()
                    shares_count = AdvertShares.objects.filter(advert_id=advert_id,creation_date__range=[one_month_date,today_date]).count()


                    avail_discount_count = avail_discount_count + discount_count
                    avail_callbacks_count = avail_callbacks_count + callbacks_count
                    avail_callsmade_count = avail_callsmade_count + callsmade_count
                    avail_shares_count = avail_shares_count + shares_count

                
                #######.................Total Bookings Graph....For a week...........########
                print '....Total Bookings Graph....For a week....'
                current_date = datetime.now()
                last_date = (datetime.now() - timedelta(days=7))

                list = []
                total_view_list = CouponCode.objects.filter(creation_date__range=[last_date,current_date])
                mon1=tue1=wen1=thus1=fri1=sat1=sun1=0
                if total_view_list:
                    for view_obj in total_view_list:
                        creation_date=view_obj.creation_date
                        consumer_day = calendar.day_name[creation_date.weekday()]
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

                print ".........total Bookings Graph....For a week...",mon1,tue1,wen1,thus1,fri1,sat1,sun1

                ##########..................Total Views Graph........for a week.............############

                current_date = datetime.now()
                last_date = (datetime.now() - timedelta(days=7))

                list = []
                total_view_list = AdvertTotalViews.objects.filter(creation_date__range=[last_date,current_date])
                mon2=tue2=wen2=thus2=fri2=sat2=sun2=0
                if total_view_list:
                    for view_obj in total_view_list:
                        creation_date=view_obj.creation_date
                        consumer_day = calendar.day_name[creation_date.weekday()]
                        if consumer_day== 'Monday' :
                            mon2 = mon2+1
                        elif consumer_day== 'Tuesday' :
                            tue2 = tue2+1
                        elif consumer_day== 'Wednesday' :
                            wen2 = wen2+1
                        elif consumer_day== 'Thursday' :
                            thus2 = thus2+1
                        elif consumer_day== 'Friday' :
                            fri2 = fri2+1
                        elif consumer_day== 'Saturday' :
                            sat2 = sat2+1
                        elif consumer_day== 'Sunday' :
                            sun2 = sun2+1
                        else :
                            pass

                data = {'var1':var1,'success':'true','logo':logo,'avail_callbacks_count':avail_callbacks_count,'avail_callsmade_count':avail_callsmade_count,'avail_shares_count':avail_shares_count,'avail_discount_count':avail_discount_count,
                        'mon1':mon1,'tue1':tue1,'wen1':wen1,'thus1':thus1,'fri1':fri1,'sat1':sat1,
                        'sun1':sun1,'mon2':mon2,'tue2':tue2,'wen2':wen2,'thus2':thus2,'fri2':fri2,'sat2':sat2,'sun2':sun2}


        except IntegrityError as e:
            print e
            data = {'success':'false','message':'Error in  loading page. Please try after some time','username':request.session['login_user']}
    except MySQLdb.OperationalError, e:
        print e
    except Exception,e:
        print 'Exception ',e

    print data
    return HttpResponse(json.dumps(data),content_type='application/json')

def subscriber_profile(request):
    try:
        data = {}
        final_list = []
        final_list1 = []

        try:
            supplier_id = request.GET.get('supplier_id')
            print '=======request======first===',supplier_id 
            Supplier_obj = Supplier.objects.get(supplier_id=request.GET.get('supplier_id'))
            print "..................Supplier_obj.........",Supplier_obj

            advert_list = Advert.objects.filter(supplier_id=request.GET.get('supplier_id'))
            print "..................advert_list.........",advert_list
            for advert_obj in advert_list:
                advert_id = advert_obj.advert_id
                advert_name = advert_obj.advert_name
                address_line_1 = advert_obj.address_line_1
                area = advert_obj.area
                category_name = advert_obj.category_id.category_name
                display_image= SERVER_URL + advert_obj.display_image.url
                count_total = CouponCode.objects.filter(advert_id=advert_id).count()

                pre_date = datetime.now().strftime("%Y-%m-%d")
                print '..............pre_date......pre_date........',pre_date
                pre_date = datetime.strptime(pre_date, "%Y-%m-%d")
                print '..............pre_date...222...pre_date........',pre_date
                advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)
                
                start_date =advert_sub_obj.business_id.start_date

                end_date = advert_sub_obj.business_id.end_date
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
                
                date_gap = (end_date - pre_date).days

                if date_gap>0 :
                    date_gap=date_gap
                else:
                    date_gap=0

                business_id = advert_sub_obj.business_id
                print business_id
                premium_ser_list = PremiumService.objects.filter(business_id=business_id)
                for obj in premium_ser_list:

                    start_date1 = obj.start_date
                    end_date1 = obj.end_date
                    end_date1 = datetime.strptime(end_date1, "%Y-%m-%d")
                    date_gap1 = (end_date1 - pre_date).days

                    if date_gap1>0 :
                        date_gap1=date_gap1
                    else:
                        date_gap1=0


                    list1={'start_date1':start_date1,'date_gap1':date_gap1}
                    final_list1.append(list1)


                list = {'advert_id':advert_id,'advert_name':advert_name,'address_line_1':address_line_1,'area':area,'category_name':category_name,'display_image':display_image,'count_total':count_total,'start_date':start_date,'date_gap':date_gap}
                final_list.append(list)


            logo= SERVER_URL + Supplier_obj.logo.url
            business_name = Supplier_obj.business_name

            business_details = Supplier_obj.business_details
            business_details_count = Supplier_obj.business_details
            business_details_length = len(business_details_count);
            phone_no = Supplier_obj.phone_no
            secondary_phone_no = Supplier_obj.secondary_phone_no
            supplier_email = Supplier_obj.supplier_email
            secondary_email = Supplier_obj.secondary_email
            address1 = Supplier_obj.address1
            address2 = Supplier_obj.address2
            country_id = Supplier_obj.country.country_id
            state_id = Supplier_obj.state.state_id
            city_id = Supplier_obj.city.city_id
            pincode_id = Supplier_obj.pincode.pincode_id
            print '...............country_nm...............',country_id

            city = Supplier_obj.city
            pincode = Supplier_obj.pincode
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
           
            data = {'country_list':country_list,'country_id':country_id, 'state_id':state_id, 'city_id':city_id, 'pincode_id':pincode_id,
            'business_details_length':business_details_length,'pincode_list':pincode_list,'city_list':city_list,'state_list':state_list,'address2':address2,'pincode':pincode,'notification_status':notification_status,'reminders_status':reminders_status,'discounts_status':discounts_status,'request_call_back_status':request_call_back_status,'no_call_status':no_call_status,'supplier_id':supplier_id,'final_list1':final_list1,'final_list':final_list,'success':'true','logo':logo,'business_name':business_name,'city':city,'business_details':business_details,'phone_no':phone_no,'secondary_phone_no':secondary_phone_no,'supplier_email':supplier_email,'secondary_email':secondary_email,'address1':address1,'contact_person':contact_person,'contact_no':contact_no,'contact_email':contact_email }

        except IntegrityError as e:
            print e
            data = {'success':'false','message':'Error in  loading page. Please try after some time','username':request.session['login_user']}
    except MySQLdb.OperationalError, e:
        print e
    except Exception,e:
        print 'Exception ',e
    print data
    return render(request,'Admin/subscriber-profile.html',data)

@csrf_exempt
def update_profile(request):
    try:
        if request.POST:
            print '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$'
            supplier_id=request.POST.get('supplier_id')
            print '............supplier_id............',supplier_id
            supplier_obj = Supplier.objects.get(supplier_id=request.POST.get('supplier_id'))
            supplier_obj.business_name = request.POST.get('business_name')
            supplier_obj.phone_no = request.POST.get('phone_no')
            supplier_obj.secondary_phone_no = request.POST.get('sec_phone_no')
            supplier_obj.supplier_email = request.POST.get('email')
            supplier_obj.secondary_email = request.POST.get('sec_email')
            supplier_obj.address1 = request.POST.get('address1')
            supplier_obj.address2 = request.POST.get('address2')
            print supplier_obj.address2
            supplier_obj.city = City.objects.get(city_id=request.POST.get('city'))
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

            data={
                'success':'true',
                'message':"Subscriber edited successfully"
            }
    except Exception, e:
        print e
        data={
            'success':'false',
            'message':str(e)
        }
    return HttpResponse(json.dumps(data),content_type='application/json')


@csrf_exempt
def subscriber_advert(request):
    try:
        data = {}
        final_list = []
        final_list1 = []
        final_list2 = []
        print "------------------------------", request.GET
        try:
            supplier_id = request.GET.get('supplier_id')

            print '=======request======first===',supplier_id ,request.GET.get('category_var')
            
            comm_list = []

            start_date_var = request.GET.get('start_date_var')
            end_date_var = request.GET.get('end_date_var')
            category_var = request.GET.get('category_var')
            status_var = request.GET.get('status_var')  


            if start_date_var and end_date_var and status_var and category_var:
                Advert_list1 = Advert.objects.filter(category_id=request.GET.get('category_var') ,
                creation_date__range=[start_date_var,end_date_var ], status= request.GET.get('status_var'))
 
                print '...................All..........................',Advert_list1

            elif  start_date_var and end_date_var  and category_var:
                Advert_list1 = Advert.objects.filter(category_id=request.GET.get('category_var') ,
                creation_date__range=[start_date_var,end_date_var ])
 
                print '...........start_date_var and end_date_var  and category_var............',Advert_list1


            elif  start_date_var and end_date_var  and status_var:
                Advert_list1 = Advert.objects.filter(
                creation_date__range=[start_date_var,end_date_var ], status= request.GET.get('status_var'))
 
                print '...................start_date_var and end_date_var  and status_var..........................',Advert_list1

            elif  status_var:
                Advert_list1 = Advert.objects.filter(
                status= request.GET.get('status_var'))
 
                print '...................status_var  and category_var..........................',Advert_list1

            elif  start_date_var and end_date_var :
                Advert_list1 = Advert.objects.filter(
                creation_date__range=[start_date_var,end_date_var ])
 
                print '...................start_date_var and end_date_var..........................',Advert_list1

            elif  category_var :
                Advert_list1 = Advert.objects.filter(
                category_id=request.GET.get('category_var'))
 
                print '...................category_var..........................',Advert_list1

            else:
                Advert_list1 = Advert.objects.filter(supplier_id=request.GET.get('supplier_id'))
                print "..................ELSE.........",Advert_list1


            category_list = Category.objects.all()
            for category_obj in category_list:
                category_id = category_obj.category_id
                category_name = category_obj.category_name
                list2= {'category_name':category_name,'category_id':category_id}
                final_list2.append(list2)

            


            Supplier_obj = Supplier.objects.get(supplier_id=request.GET.get('supplier_id'))
            print "..................Supplier_obj.........",Supplier_obj

            logo= SERVER_URL + Supplier_obj.logo.url
            business_name = Supplier_obj.business_name
            city = Supplier_obj.city
            business_details = Supplier_obj.business_details
            phone_no=Supplier_obj.phone_no
            secondary_phone_no=Supplier_obj.secondary_phone_no
            supplier_email=Supplier_obj.supplier_email
            secondary_email=Supplier_obj.secondary_email
            
            address1=Supplier_obj.address1

            contact_person=Supplier_obj.contact_person
            contact_no=Supplier_obj.contact_no
            contact_email=Supplier_obj.contact_email

            notification_status = Supplier_obj.notification_status
            reminders_status = Supplier_obj.reminders_status
            discounts_status = Supplier_obj.discounts_status
            request_call_back_status = Supplier_obj.request_call_back_status
            no_call_status = Supplier_obj.no_call_status

            for advert_obj in Advert_list1:
                print '..............advert_obj..........',advert_obj
                advert_id = advert_obj.advert_id
                advert_views = advert_obj.advert_views
                print '.................advert_views...........',advert_views
                thumbs_count = AdvertLike.objects.filter(advert_id=advert_id).count()
                print '.................thumbs_count...........',thumbs_count
                advert_name = advert_obj.advert_name
                address_line_1 = advert_obj.address_line_1
                area = advert_obj.area
                category_name = advert_obj.category_id.category_name

                display_image= SERVER_URL + advert_obj.display_image.url
                count_total = CouponCode.objects.filter(advert_id=advert_id).count()

                pre_date = datetime.now().strftime("%Y-%m-%d")
                pre_date = datetime.strptime(pre_date, "%Y-%m-%d")
                
                advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)
                
                
                start_date =advert_sub_obj.business_id.start_date

                end_date5 = advert_sub_obj.business_id.end_date
                end_date = datetime.strptime(end_date5, "%Y-%m-%d")
                
                date_gap = (end_date - pre_date).days

                if date_gap>0 :
                    date_gap=date_gap
                else:
                    date_gap=0

                if date_gap<=10 and date_gap>=1:
                    status_advert =1
                elif date_gap==0:
                    status_advert =0
                else:
                    status_advert = 2


                business_id = advert_sub_obj.business_id
                print '..................business_id..........',business_id
                premium_ser_list = PremiumService.objects.filter(business_id=business_id)
                print 'ssssssssssssss',premium_ser_list
                for obj in premium_ser_list:

                    premium_service_name = obj.premium_service_name
                    start_date1 = obj.start_date
                    end_date6 = obj.end_date
                    print '...............end_date6.................',end_date6
                    end_date1 = datetime.strptime(end_date6, "%Y-%m-%d")
                    date_gap1 = (end_date1 - pre_date).days

                    if date_gap1>0 :
                        date_gap1=date_gap1
                    else:
                        date_gap1=0


                    if date_gap1<=10 and date_gap1>=1:
                        status_advert1 =1
            
                    else:
                        status_advert1 = 2


                    list = {'premium_service_name':premium_service_name,'start_date1':start_date1,'date_gap1':date_gap1,'end_date6':end_date6,'status_advert1':status_advert1,'thumbs_count':thumbs_count,'advert_views':advert_views,'advert_id':advert_id,'advert_name':advert_name,'display_image':display_image,'address_line_1':address_line_1,'area':area,'category_name':category_name,'count_total':count_total,'start_date':start_date,'end_date5':end_date5 ,'date_gap':date_gap,'status_advert':status_advert}
                    final_list.append(list)



            data = {'final_list1':final_list1,'final_list2':final_list2,'start_date_var':start_date_var,'end_date_var':end_date_var,'category_var':
            category_var,'status_var':status_var,'notification_status':notification_status,'reminders_status':reminders_status,'discounts_status':discounts_status,'request_call_back_status':request_call_back_status,'no_call_status':no_call_status,'supplier_id':supplier_id,'final_list1':final_list1,'final_list':final_list,'success':'true','logo':logo,'business_name':business_name,'city':city,'business_details':business_details,'phone_no':phone_no,'secondary_phone_no':secondary_phone_no,'supplier_email':supplier_email,'secondary_email':secondary_email,'address1':address1,'contact_person':contact_person,'contact_no':contact_no,'contact_email':contact_email }

        except IntegrityError as e:
            print e
            data = {'success':'false','message':'Error in  loading page. Please try after some time','username':request.session['login_user']}
    except MySQLdb.OperationalError, e:
        print e
    except Exception,e:
        print 'Exception ',e
    print data
    return render(request,'Admin/subscriber-advert.html',data)


@csrf_exempt
def subscriber_advert_stat(request):
    try:
        data = {}
        final_list = []
        final_list1 = []
        final_list2 = []
        print "----------------request--------------", request.GET
        try:
            supplier_id = request.GET.get('supplier_id')

            Advert_list1 = Advert.objects.filter(supplier_id=request.GET.get('supplier_id'))
            print "..................Advert_list1.........",Advert_list1

          


            Supplier_obj = Supplier.objects.get(supplier_id=request.GET.get('supplier_id'))
            print "..................Supplier_obj.........",Supplier_obj

            logo= SERVER_URL + Supplier_obj.logo.url

        #########################advert_views_total#############################
            advert_views_total = 0
            thumbs_count_total = 0
            shares_count_total = 0

            jan1=feb1=mar1=apr1=may1=jun1=jul1=aug1=sep1=oct1=nov1=dec1=0
            jan2=feb2=mar2=apr2=may2=jun2=jul2=aug2=sep2=oct2=nov2=dec2=0
            jan3=feb3=mar3=apr3=may3=jun3=jul3=aug3=sep3=oct3=nov3=dec3=0

            for advert_obj in Advert_list1:
                print advert_obj
                advert_id = advert_obj.advert_id
                advert_views = Advert.objects.filter(advert_id=advert_id).count()
                thumbs_count = AdvertLike.objects.filter(advert_id=advert_id).count()
                shares_count = AdvertShares.objects.filter(advert_id=advert_id).count()


                advert_views_total = advert_views_total + advert_views
                thumbs_count_total = thumbs_count_total + thumbs_count
                shares_count_total = shares_count_total + shares_count
                print '.................advert_views_total...........',advert_views_total
                print '.................thumbs_count_total...........',thumbs_count_total
                print '.................shares_count_total...........',shares_count_total

            #######.................Total views Graph........for a year.......########
            
                FY_MONTH_LIST = [1,2,3,4,5,6,7,8,9,10,11,12]
                today = date.today()
                print '.......today.........',today
                start_date = date(today.year,01,01)
                print '...........start_date..........',start_date
                end_date = date(today.year,12,31) 
                monthly_count = []
                # jan,feb,mar,apr,may,jun,jul,aug,sep,octo,nov,dec

                coupon_code_list = Advert.objects.filter(advert_id = advert_id,creation_date__range=[start_date,end_date]).extra(select={'month': "EXTRACT(month FROM creation_date)"}).values('month').annotate(count=Count('advert_id'))
                print "...........coupon_code_list...11....",coupon_code_list
                list={}


                for sub_obj in coupon_code_list:
                    # advert_id = sub_obj.advert_id
                    # print 'SS advert SS',advert_id
                    print "sub_obj.get('count')",sub_obj.get('count')
                    if sub_obj.get('month'):
                        list[sub_obj.get('month')]=sub_obj.get('count') or '0.00'
                        print list
                

                for i in FY_MONTH_LIST:
                    try:
                        monthly_count.append(list[i])
                    except:
                        monthly_count.append(0)
                        
                jan1=jan1+monthly_count[0]
                print jan1
                feb1=feb1+monthly_count[1]
                print feb1
                mar1=mar1+monthly_count[2]
                print mar1
                apr1=apr1+monthly_count[3]
                may1=may1+monthly_count[4]
                jun1=jun1+monthly_count[5]
                jul1=jul1+monthly_count[6]
                aug1=aug1+monthly_count[7]
                print aug1
                sep1=sep1+monthly_count[8]
                oct1=oct1+monthly_count[9]            
                nov1=nov1+monthly_count[10]            
                dec1=dec1+monthly_count[11]


                #######.................Total Like Graph........for a year.......########
                
                FY_MONTH_LIST = [1,2,3,4,5,6,7,8,9,10,11,12]
                today = date.today()
                print '.......today......AdvertLike...',today
                start_date = date(today.year,01,01)
                print '...........start_date....AdvertLike......',start_date
                end_date = date(today.year,12,31) 
                monthly_count = []
                # jan,feb,mar,apr,may,jun,jul,aug,sep,octo,nov,dec
                coupon_code_list = AdvertLike.objects.filter(advert_id = advert_id,creation_date__range=[start_date,end_date]).extra(select={'month': "EXTRACT(month FROM creation_date)"}).values('month').annotate(count=Count('advert_id'))
                print "...........coupon_code_list....AdvertLike...",coupon_code_list
                list={}


                for sub_obj in coupon_code_list:

                    print "sub_obj.get('count')",sub_obj.get('count')
                    if sub_obj.get('month'):
                        list[sub_obj.get('month')]=sub_obj.get('count') or '0.00'
                        print list
                

                for i in FY_MONTH_LIST:
                    try:
                        monthly_count.append(list[i])
                    except:
                        monthly_count.append(0)
                        
                jan2=jan2+monthly_count[0]
                print jan2
                feb2=feb2+monthly_count[1]
                print feb2
                mar2=mar2+monthly_count[2]
                print mar2
                apr2=apr2+monthly_count[3]
                may2=may2+monthly_count[4]
                jun2=jun2+monthly_count[5]
                jul2=jul2+monthly_count[6]
                print jul2
                aug2=aug2+monthly_count[7]
                print aug2
                sep2=sep2+monthly_count[8]
                oct2=oct2+monthly_count[9]            
                nov2=nov2+monthly_count[10]            
                dec2=dec2+monthly_count[11]


            #######.................Total shares Graph........for a year.......########
            
                FY_MONTH_LIST = [1,2,3,4,5,6,7,8,9,10,11,12]
                today = date.today()
                print '.......today.........',today
                start_date = date(today.year,01,01)
                print '...........start_date..........',start_date
                end_date = date(today.year,12,31) 
                monthly_count = []
                # jan,feb,mar,apr,may,jun,jul,aug,sep,octo,nov,dec
                coupon_code_list = AdvertShares.objects.filter(advert_id = advert_id,creation_date__range=[start_date,end_date]).extra(select={'month': "EXTRACT(month FROM creation_date)"}).values('month').annotate(count=Count('advert_id'))
                print "...........coupon_code_list.......",coupon_code_list
                list={}


                for sub_obj in coupon_code_list:
                    print "sub_obj.get('count')",sub_obj.get('count')
                    if sub_obj.get('month'):
                        list[sub_obj.get('month')]=sub_obj.get('count') or '0.00'
                        print list
                

                for i in FY_MONTH_LIST:
                    try:
                        monthly_count.append(list[i])
                    except:
                        monthly_count.append(0)
                        
                jan3=jan3+monthly_count[0]
                print jan3
                feb3=feb3+monthly_count[1]
                print feb3
                mar3=mar3+monthly_count[2]
                print mar3
                apr3=apr3+monthly_count[3]
                may3=may3+monthly_count[4]
                jun3=jun3+monthly_count[5]
                jul3=jul3+monthly_count[6]
                aug3=aug3+monthly_count[7]
                print aug3
                sep3=sep3+monthly_count[8]
                oct3=oct3+monthly_count[9]            
                nov3=nov3+monthly_count[10]            
                dec3=dec3+monthly_count[11]



            data = {'success':'true','supplier_id':supplier_id,'logo':logo,'advert_views_total':advert_views_total,'thumbs_count_total':thumbs_count_total,'shares_count_total':shares_count_total,'jan1':jan1,'feb1':feb1,'mar1':mar1,'apr1':apr1,'may1':may1,'jun1':jun1,'jul1':jul1,'aug1':aug1,'sep1':sep1,'oct1':oct1,'nov1':nov1,'dec1':dec1,
                    'jan2':jan2,'feb2':feb2,'mar2':mar2,'apr2':apr2,'may2':may2,'jun2':jun2,'jul2':jul2,'aug2':aug2,'sep2':sep2,'oct2':oct2,'nov2':nov2,'dec2':dec2,
                    'jan3':jan3,'feb3':feb3,'mar3':mar3,'apr3':apr3,'may3':may3,'jun3':jun3,'jul3':jul3,'aug3':aug3,'sep3':sep3,'oct3':oct3,'nov3':nov3,'dec3':dec3}

        except IntegrityError as e:
            print e
            data = {'success':'false','message':'Error in  loading page. Please try after some time','username':request.session['login_user']}
    except MySQLdb.OperationalError, e:
        print e
    except Exception,e:
        print 'Exception ',e
    print './........777..........',data
    return render(request,'Admin/subscriber-advert-stat.html',data)


def subscriber_booking(request):
    try:
        data = {}
        final_list = []
        final_list1 = []
        final_list2 = []

        try:
            supplier_id = request.GET.get('supplier_id')
            print '=======......supplier_id........======',supplier_id 

            start_date_var = request.GET.get('start_date_var')
            print start_date_var
            end_date_var = request.GET.get('end_date_var')
            print end_date_var
            category_var = request.GET.get('category_var')
            print category_var
            status_var = request.GET.get('status_var')
            print status_var


            if start_date_var and end_date_var and status_var and category_var:
                Advert_list1 = Advert.objects.filter(category_id=request.GET.get('category_var') ,
                creation_date__range=[start_date_var,end_date_var ], status= request.GET.get('status_var'))
 
                print '...................All..........................',Advert_list1

            elif  start_date_var and end_date_var  and category_var:
                Advert_list1 = Advert.objects.filter(category_id=request.GET.get('category_var') ,
                creation_date__range=[start_date_var,end_date_var ])
 
                print '...........start_date_var and end_date_var  and category_var............',Advert_list1


            elif  start_date_var and end_date_var  and status_var:
                Advert_list1 = Advert.objects.filter(
                creation_date__range=[start_date_var,end_date_var ], status= request.GET.get('status_var'))
 
                print '...................start_date_var and end_date_var  and status_var..........................',Advert_list1

            elif  status_var:
                Advert_list1 = Advert.objects.filter(
                status= request.GET.get('status_var'))
 
                print '...................status_var  and category_var..........................',Advert_list1

            elif  start_date_var and end_date_var :
                Advert_list1 = Advert.objects.filter(
                creation_date__range=[start_date_var,end_date_var ])
 
                print '...................start_date_var and end_date_var..........................',Advert_list1

            elif  category_var :
                Advert_list1 = Advert.objects.filter(
                category_id=request.GET.get('category_var'))
 
                print '...................category_var..........................',Advert_list1

            else:
                Advert_list1 = Advert.objects.filter(supplier_id=request.GET.get('supplier_id'))
                print "..................ELSE.........",Advert_list1    

            category_list = Category.objects.all()
            for category_obj in category_list:
                category_id = category_obj.category_id
                category_name = category_obj.category_name
                list2= {'category_name':category_name,'category_id':category_id}
                final_list2.append(list2)


            for advert_obj in Advert_list1:

                # # To find out coupon code
                advert_id = advert_obj.advert_id
                display_image    = SERVER_URL + advert_obj.display_image.url
                advert_sub_list = CouponCode.objects.filter(advert_id=advert_id)
                
                for advert_sub_obj in advert_sub_list:
                    coupon_code = advert_sub_obj.coupon_code
                     #Availed date
                    creation_date = (advert_sub_obj.creation_date).strftime('%b %d,%Y')
                    print '............creation_date..............',creation_date
                    
                    #consumer personal data
                    user_id = advert_sub_obj.user_id

                    consumer_obj = ConsumerProfile.objects.get(consumer_id=str(user_id))
                    consumer_full_name = str(consumer_obj.consumer_full_name)   

                    consumer_contact_no = consumer_obj.consumer_contact_no
                    consumer_email_id = consumer_obj.consumer_email_id
                    consumer_area = consumer_obj.consumer_area              
                    consumer_profile_pic= SERVER_URL + consumer_obj.consumer_profile_pic.url


                    #Expiry Date
                    pre_date = datetime.now().strftime("%Y-%m-%d")
                    pre_date = datetime.strptime(pre_date, "%Y-%m-%d")
                    
                    expiry_data_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)
                    business_id = expiry_data_obj.business_id
                    end_date = expiry_data_obj.business_id.end_date
                    end_date = datetime.strptime(end_date, "%Y-%m-%d")
                    
                    date_gap = (end_date - pre_date).days        

                    if date_gap>0 :
                        date_gap=date_gap
                        status_advert = 1
                    else:
                        date_gap=0
                        status_advert = 0

                    end_date=end_date.strftime('%b %d,%Y')
                    #logo

                    list = {'display_image':display_image,'consumer_full_name':consumer_full_name,'consumer_contact_no':consumer_contact_no,'consumer_email_id':consumer_email_id,'consumer_area':consumer_area,'consumer_profile_pic':consumer_profile_pic,'end_date':end_date,'coupon_code':coupon_code,'creation_date':creation_date,'date_gap':date_gap,'status_advert':status_advert}
                    final_list.append(list)

            Supplier_obj = Supplier.objects.get(supplier_id=request.GET.get('supplier_id'))
            logo= SERVER_URL + Supplier_obj.logo.url
      
            data = {'logo':logo,'final_list':final_list,'success':'true','final_list2':final_list2}

        except IntegrityError as e:
            print e
            data = {'success':'false','message':'Error in  loading page. Please try after some time','username':request.session['login_user']}
    except MySQLdb.OperationalError, e:
        print e
    except Exception,e:
        print 'Exception ',e
    print data
    return render(request,'Admin/subscriber-booking.html',data)



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dashboard(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        try:
            temp_var0 = 0
            temp_var1 = 0
            temp_var2 = 0
            temp_var3 = 0
            data = {}

            try:
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
                        #print '........................consumer_obj_list..........next............................',consumer_obj_list1
                        for consumer_obj in consumer_obj_list1:

                            total_amount1 = consumer_obj.total_amount

                            temp_var1 = temp_var1 + int(total_amount1)
                            #print '....................total total_amount1 ................',temp_var1

                value_1 = str(temp_var1)
                #   print '......................value_1....................',value_1
                
                for hour in range(9,17):
                    if hour == 9:
                        hour = ' 0'+ str(hour) + ':'
                    else:
                        hour = ' '+ str(hour) + ':'
                    
                    consumer_obj_list = PaymentDetail.objects.filter(payment_created_date__contains = str((datetime.now()).strftime("%Y-%m-%d")),payment_created_date__regex= hour)
                    
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
                #print '......................value_3....................',value_3

                data = {'mon':mon,'tue':tue,'wen':wen,'thus':thus,'fri':fri,'sat':sat,'sun':sun,'success':'true','value_0':value_0,'value_1':value_1,'value_3':value_3,'value_2':value_2,'username':request.session['login_user'],'city_list':get_city_dashboard(request)     }


            except IntegrityError as e:
                print e
                data = {'success':'false','message':'Error in  loading page. Please try after some time','username':request.session['login_user']}                

        except MySQLdb.OperationalError, e:
            print e
        except Exception,e:
            print 'Exception ',e
        print data
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
        data ={ 'username':request.session['login_user'] }
        return render(request,'Admin/consumer.html',data)        

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
    	user_role_list = UserRole.objects.filter(role_status='1')
    	data = {'user_role_list':user_role_list}
    	return render(request,'Admin/user_list.html',data)        

def notification(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        return render(request,'Admin/notification.html')   

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def reference_data(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        data ={'username':request.session['login_user']}
        return render(request,'Admin/rdm.html',data)       

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
        data = {'state_list':get_state(request),'category_list':get_category(request),'username':request.session['login_user']}
        return render(request,'Admin/add_city.html',data)  

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def category(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        data = {'username':request.session['login_user']}
        return render(request,'Admin/category.html',data)  

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_role(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        data ={'username':request.session['login_user']}
        return render(request,'Admin/user_role.html',data)  
       

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_advert(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        user_id = request.GET.get('user_id')
        tax_list = Tax.objects.all()

        service_list = ServiceRateCard.objects.filter(service_rate_card_status='1').values('service_name').distinct()
        advert_service_list, item_ids = [], []
        for item in AdvertRateCard.objects.filter(advert_rate_card_status='1'):
            if item.advert_service_name not in item_ids:
                advert_service_list.append(str(item.advert_rate_card_id))
                item_ids.append(item.advert_service_name)

        advert_service_list = AdvertRateCard.objects.filter(advert_rate_card_id__in=advert_service_list)

        data = {'tax_list': tax_list, 'advert_service_list': advert_service_list, 'service_list': service_list,
                'username': request.session['login_user'], 'user_id': user_id, 'category_list': get_category(request),
                'currency': get_currency(request), 'phone_category': get_phone_category(request),
                'state_list': get_state(request)}
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
            print '........................signin.........................'

            if request.POST:
                form = CaptchaForm(request.POST)
                print 'logs: login request with: ', request.POST
                username = request.POST['username']
                password = request.POST['password']

                if form.is_valid():
                    try:
                        user_obj = Supplier.objects.get(username=username)

                        user = authenticate(username=username, password=password)
                        print 'valid form befor----->'
                        if user :
                            if user.is_active:
                                print 'valid form after----->',user
                                user_Supplier_obj = Supplier.objects.get(username=username)
                                if user_Supplier_obj.supplier_status=="1":
                     
                                    request.session['login_user'] = user_Supplier_obj.username
                                    request.session['first_name'] = user_Supplier_obj.contact_person 
                                    login(request,user)
                                    print "USERNAME",request.session['login_user']
                                    data= { 'success' : 'true','username':request.session['first_name']}

                            else:
                                data= { 'success' : 'false', 'message':'User Is Not Active'}
                                return HttpResponse(json.dumps(data), content_type='application/json')
                        else:
                                data= { 'success' : 'Invalid Password', 'message' :'Invalid Password'}
                                print "====USERNAME",data
                                return HttpResponse(json.dumps(data), content_type='application/json')
                    except Exception as e:
                        print e
                        data= { 'success' : 'false', 'message' :'Invalid Username'}
                        return HttpResponse(json.dumps(data), content_type='application/json')            
                else:
                    form = CaptchaForm()
                    data= { 'success' : 'Invalid Captcha', 'message' :'Invalid Captcha'} 
                    print "INVALID CAPTCHA"       
                    return HttpResponse(json.dumps(data), content_type='application/json')
        except MySQLdb.OperationalError, e:
            print e
            data= {'success' : 'false', 'message':'Internal server'}
            return HttpResponse(json.dumps(data), content_type='application/json')
        except Exception, e:
            print 'Exception ', e
            data= { 'success' : 'false', 'message':'Invalid Username or Password'}
        print data
        return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def forgot_password(request):
    #pdb.set_trace()
    username = request.POST.get("email")
    try:
        if request.POST:
            user_obj = None
            try:
                user_obj = Supplier.objects.get(username=username)
                print '.........username......',user_obj.username
                print '.........supplier_id......',user_obj.supplier_id
                new_pass = id_generator()
                print '......NEW PASS......',new_pass
                user_obj.set_password(new_pass)
                

            except:
                pass

            if user_obj:
                send_password_email(user_obj.contact_email,new_pass)
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
def send_password_email(user_email_id,user_pass):
    try:
        #pdb.set_trace()

        subject = "New password for login"
        description ="Your new password is"

        gmail_user =  "cityhoopla2016"
        gmail_pwd ="cityhoopla@2016"
        FROM = 'CityHoopla Admin: <cityhoopla2016@gmail.com>'
        TO = [user_email_id]

        TEXT = description+'='+user_pass
        SUBJECT = subject
        server = smtplib.SMTP_SSL()
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()

        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException,e:
        print e
    except Exception,e:
        print 'exception',e

    return 1

# @csrf_exempt
# def admin_send_email(request):
#     consumer = request.POST.getlist('consumer')
#     consumer01=consumer[0]

#     print'================consumer===================',consumer
#     print'================consumer===================',consumer01
#     consumer_new = consumer01.split(',')

#     subject = request.POST.get('subject')
#     description = request.POST.get('description') 

#     for usernm in consumer_new:
#         print '------abc----',usernm
#         gmail_user =  "cityhoopla2016"
#         gmail_pwd =  "cityhoopla@2016"
#         FROM = 'CityHoopla Admin: <cityhoopla2016@gmail.com>'
#         TO = [usernm]

#         #pdb.set_trace()
#         try:
#             TEXT = description
#             SUBJECT = subject
#             server = smtplib.SMTP_SSL()
#             server = smtplib.SMTP("smtp.gmail.com", 587) 
#             server.ehlo()
#             server.starttls()

#             server.login(gmail_user, gmail_pwd)
#             message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
#             server.sendmail(FROM, TO, message)
#             server.quit()
#         except SMTPException,e:
#             print e
#     data = {'success':'true','username':request.session['login_user']}
#     return HttpResponse(json.dumps(data), content_type='application/json')

def signing_out(request):
    logout(request)
    form = CaptchaForm()
    return render_to_response('Admin/user_login.html', dict(
        form=form, message_logout='You have successfully logged out.'
    ), context_instance=RequestContext(request))

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


def view_user_list(request):
	try:
		data = {}
		final_list = []
		try:
			user_list = UserProfile.objects.filter(user_status='1')
			for user_obj in user_list:
				if user_obj.user_role:
					role_id = user_obj.user_role.role_name
					user_name = user_obj.user_name
					usre_email_id = user_obj.usre_email_id
					user_contact_no = user_obj.user_contact_no
					edit = '<a class="col-md-offset-2 col-md-1" id="'+str(user_obj)+'" onclick="edit_user_detail(this.id);" style="text-align: center;letter-spacing: 5px;width:15%;" title="Edit" class="edit" data-toggle="modal" href="#edit_subscription"><i class="fa fa-pencil"></i></a>'
					delete = '<a class="col-md-1" id="'+str(user_obj)+'" onclick="delete_user_detail(this.id)" style="text-align: center;letter-spacing: 5px;width:15%;" title="Delete"  ><i class="fa fa-trash"></i></a>'
					actions =  edit + delete
					list = {'user_name':user_name,'actions':actions,'role_id':role_id,'usre_email_id':usre_email_id,'user_contact_no':user_contact_no}
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
            user_obj = UserProfile.objects.get(user_id=request.POST.get('user_id'))
            user_obj.user_status = '0'
            user_obj.save()
            data = {'message': 'User Inactivated Successfully', 'success':'true'}

        except IntegrityError as e:
          print e
        except Exception,e:
            print e
        print "Final Data: ",data
        return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def view_user_detail(request):
    try:
        data = {}
        final_list = []
        try:
            if request.method == "GET":
                user_obj = UserProfile.objects.get(user_id=request.GET.get('user_id'))
                role_id = str(user_obj.user_role)
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
        #pdb.set_trace()
        data = {}
        #print 'role_id====',request.POST.get('e_user_role')
        role_id = UserRole.objects.get(role_id=request.POST.get('e_user_role'))
        #print '++++++++++++++++++++++hidden id================',request.POST.get('hidden_id')
        user_obj=UserProfile.objects.get(user_id=request.POST.get('hidden_id'))
        #print 'user_obj',user_obj
        #print '=============request.POST.get(user_id)=====',request.POST.get('user_id')

        user_obj.username=str(request.POST.get('e_username'))
        user_obj.user_name=str(request.POST.get('e_username'))
        #print 'Contact No====',request.POST.get('e_contact_no')
        user_obj.user_contact_no=request.POST.get('e_contact_no')
        user_obj.usre_email_id=str(request.POST.get('e_email'))
        user_obj.role_name=role_id
        user_obj.user_created_date = datetime.now()
        user_obj.user_status = '1'
        user_obj.user_created_by = request.session['login_user']
                
        user_obj.save();
        #user_obj.set_password(request.POST.get('e_password'));
        #user_obj.save();

        data={
            'success':'true',
            'message':'User Updated Successfully.'
        }
    except Exception, e:
            data={
                'success':'false',
                'message':str(e)
            }
    return HttpResponse(json.dumps(data),content_type='application/json')      

@csrf_exempt
def view_user_detail(request):
    try:
        data = {}
        final_list = []
        try:
            if request.method == "GET":
                user_obj = UserProfile.objects.get(user_id=request.GET.get('user_id'))
                role_id = str(user_obj.user_role)
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

# TO GET THE STATE
def get_state(request):
##    pdb.set_trace()
    state_list = []
    try:
        state = State.objects.filter(state_status='1')
        for sta in state:
            state_list.append(
                {'state_id': sta.state_id, 'state': sta.state_name})

    except Exception, e:
        print 'Exception ', e
    return state_list

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

# TO GET THE CITY
def get_city(request):
   
   state_id=request.GET.get('state_id')
   print '.................state_id.....................',state_id
   city_list=[]
   try:
      city_objs=City.objects.filter(state_id=state_id,city_status='1').order_by('city_name')
      for city in city_objs:
         options_data = '<option value=' + str(
                   city.city_id) + '>' + city.city_name + '</option>'
         city_list.append(options_data)
         print city_list
      data = {'city_list': city_list}

   except Exception, ke:
      print ke
      data={'city_list': 'none','message':'No city available'}
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


# TO GET THE PINCODE
def get_pincode(request):
   #pdb.set_trace()

   pincode_list=[]
   try:
      city_id = request.GET.get('city_id')
      pincode_list1=Pincode.objects.filter(city_id=city_id).order_by('pincode')
      #pincode_objs = pincode_list1.values('pincode').distinct()
      #print pincode_objs
      for pincode in pincode_list1:
         options_data = '<option value='+str(pincode.pincode_id)+'>' +pincode.pincode+ '</option>'
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
                role_created_by="Admin",
                role_updated_by="Admin",
                role_updated_date = datetime.now(),
                
            );
            user_role_obj.save();
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


def user_role_add(user_role_obj):
    gmail_user =  "cityhoopla2016"
    gmail_pwd =  "cityhoopla@2016"
    FROM = 'CityHoopla Admin: <cityhoopla2016@gmail.com>'
    TO = ['cityhoopla2016@gmail.com']
    #pdb.set_trace()
    try:
        TEXT = "Hi Admin,\nUser Role " + str(user_role_obj.role_name) + " " +"has been added successfully.\nTo view complete details visit portal and follow - Reference Data -> User Role\n\n Thank You,"+'\n'+"CityHoopla Team"
        SUBJECT = "User Role Added Successfully!"
        #server = smtplib.SMTP_SSL()
        server = smtplib.SMTP("smtp.gmail.com", 587) 
        server.ehlo()
        server.starttls()

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
            print user_role_list
            for role_obj in user_role_list:
                role_id=role_obj.role_id
                role_name = role_obj.role_name
                role_creation_date = str(role_obj.role_created_date).split(' ')[0]

                if role_obj.role_status == '1':
                    # edit = '<a class="col-md-offset-2 col-md-1" id="'+str(role_id)+'" onclick="edit_user_role(this.id);" style="text-align: center;letter-spacing: 5px;width:15%;" title="Edit" class="edit" data-toggle="modal" href="#edit_subscription"><i class="fa fa-pencil"></i></a>'
                    edit = '<a class="col-md-offset-2 col-md-1" id="'+str(role_id)+'" onclick="edit_user_role(this.id);" style="text-align: center;letter-spacing: 5px;width:15%;" title="Edit" class="edit" data-toggle="modal" href="#edit_subscription"><i class="fa fa-pencil"></i></a>'
                    delete = '<a id="'+str(role_id)+'" onclick="delete_user_role(this.id)" style="text-align: center;letter-spacing: 5px;width:15%;" title="Delete"  ><i class="fa fa-trash"></i></a>'
                    status = 'Active'
                    actions =  edit + delete
                else:
                    status = 'Inactive'
                    active = '<a class="col-md-2" id="'+str(role_id)+'" onclick="active_service(this.id);" style="text-align: center;letter-spacing: 5px;width:15%;margin-left: 50px !important;" title="Activate" class="edit" data-toggle="modal" href="#edit_subscription"><i class="fa fa-repeat"></i></a>'
                    actions =  active
             
                list = {'role_name':role_name,'actions':actions,'role_id':role_id,'role_creation_date':role_creation_date}
                final_list.append(list)
            data = {'success':'true','data':final_list}
        except IntegrityError as e:
            print e
            data = {'success':'false','message':'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception,e:
        print 'Exception ',e
    print data    
    return HttpResponse(json.dumps(data), content_type='application/json')



@csrf_exempt
def edit_user_role(request):
    try:
        data = {}
        final_list = []
        try:
            if request.method == "GET":
                print request
                role_obj = UserRole.objects.get(role_id=request.GET.get('role_id'))
                role_id = str(role_obj.role_id)
                role_name = role_obj.role_name
               
                data = {'success':'true','role_name':role_name,'role_id':role_id}


        except IntegrityError as e:
            print e
            data = {'success':'false','message':'Error in  loading page. Please try after some time'}

    except MySQLdb.OperationalError, e:
        print e

    except Exception,e:
        print 'Exception ',e
    print data    
    return HttpResponse(json.dumps(data),content_type='application/json')      


@csrf_exempt
def update_user_role(request):
    # pdb.set_trace()
    try:
        print request.POST
        data = {}
        role_obj = request.POST.get('edit_role')
        role_id = request.POST.get('role_id')
        try:
            print "==========IN UPDATE ROLE======="
            role_object=UserRole.objects.get(role_name=request.POST.get('edit_role'))
            print "========role_object",role_object
            if(str(role_id)==str(role_object)):
                role_object=UserRole.objects.get(role_name=request.POST.get('edit_role'),role_status=1)
                role_object.role_name = request.POST.get('edit_role')
                role_object.save()
                user_role_edit(role_object)  
                data = {'success':'true'}
            else:
                data = {'success':'false'}
        except:
            role_object=UserRole.objects.get(role_id=role_id)
            role_object.role_name = request.POST.get('edit_role')
            role_object.save() 
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
    gmail_user =  "cityhoopla2016"
    gmail_pwd =  "cityhoopla@2016"
    FROM = 'CityHoopla Admin: <cityhoopla2016@gmail.com>'
    TO = ['cityhoopla2016@gmail.com']
    #pdb.set_trace()
    try:
        TEXT = "Hi Admin,\nUser Role " + str(role_object.role_name) + " " +" has been updated successfully.\nTo view complete details visit portal and follow - Reference Data -> User Role\n\n Thank You,"+'\n'+"CityHoopla Team"
        SUBJECT = "User Role Added Successfully!"
        #server = smtplib.SMTP_SSL()
        server = smtplib.SMTP("smtp.gmail.com", 587) 
        server.ehlo()
        server.starttls()

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

def user_role_active(role_obj):
    gmail_user =  "cityhoopla2016"
    gmail_pwd =  "cityhoopla@2016"
    FROM = 'CityHoopla Admin: <cityhoopla2016@gmail.com>'
    TO = ['cityhoopla2016@gmail.com']
    #pdb.set_trace()
    try:
        TEXT = "Hi Admin,\nUser Role " + str(role_obj.role_name) + " " +" has been activated successfully.\nTo view complete details visit portal and follow - Reference Data -> User Role\n\n Thank You,"+'\n'+"CityHoopla Team"
        SUBJECT = "User Role Activated Successfully!"
        #server = smtplib.SMTP_SSL()
        server = smtplib.SMTP("smtp.gmail.com", 587) 
        server.ehlo()
        server.starttls()

        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException,e:
        print e
    return 1 

def user_role_delete(role_obj):
    gmail_user =  "cityhoopla2016"
    gmail_pwd =  "cityhoopla@2016"
    FROM = 'CityHoopla Admin: <cityhoopla2016@gmail.com>'
    TO = ['cityhoopla2016@gmail.com']
    #pdb.set_trace()
    try:
        TEXT = "Hi Admin,\nUser Role " + str(role_obj.role_name) + " " +" has been updated successfully.\nTo view complete details visit portal and follow - Reference Data -> User Role\n\n Thank You,"+'\n'+"CityHoopla Team"
        SUBJECT = "User Role Added Successfully!"
        #server = smtplib.SMTP_SSL()
        server = smtplib.SMTP("smtp.gmail.com", 587) 
        server.ehlo()
        server.starttls()

        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException,e:
        print e
    return 1 
   
@csrf_exempt
def save_city(request):
    print "IN SAVE CITY", request.POST
    try:
        data = {}
        print request.POST
        print request.FILES
        print '=====type========',type(request.FILES)
        #pdb.set_trace()
        try:
            city_obj=City_Place.objects.get(city_id=request.POST.get('city_name'))
            data={'success':'false','messege':'City Already Exist'}   
        except Exception,e:
            city_obj=City_Place(
         
            city_id=City.objects.get(city_id=request.POST.get('city_name')),
            state_id =State.objects.get(state_id=request.POST.get('state')),   
            )
            city_obj.save()
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


            city_obj.save();
            city_place_id = city_obj.city_place_id
            print "city ID",city_place_id

            if request.POST['check_image'] == "1":
                city_obj.city_image = request.FILES['city_image']
                city_obj.save()
   
            data={
                    'success':'true',
                    'message':'City Added Successfully.',
                    "city_place_id":  city_place_id 
                    }


    except Exception, e:
        data={
            'success':'false',
            'message':str(e)
        }
    return HttpResponse(json.dumps(data),content_type='application/json') 



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


def update_places(zipped_wk,city_obj,place_type):
    try:

        for interest_id,interest_name,interest_img in zipped_wk:
            try:
                place_obj = Places.objects.get(place_id=interest_id)
                place_obj.place_name = interest_name
                if interest_img != '':
                    place_obj.place_image=interest_img
                else:
                    pass
                place_obj.updated_by="Admin",
                place_obj.updated_date=datetime.now()
                place_obj.save()        
            except:
                if interest_name != '' and interest_img != '' : 
                    interest_name_obj = Places(
                    city_place_id=city_obj,
                    place_name = interest_name,
                    place_image=interest_img,
                    place_type=place_type,
                    created_date=datetime.now(),
                    created_by="Admin",
                    updated_by="Admin",
                    updated_date=datetime.now()
                )
                    interest_name_obj.save()
            data = {'success': 'true'}
            print "RESPONSE",data

    except Exception, e:
        data={
            'success':'false',
            'message':str(e)
        }
    return HttpResponse(json.dumps(data),content_type='application/json') 


def save_places(zipped_wk,city_obj,place_type):
    
    try:
        for interest_name,interest_img in zipped_wk:

            if interest_name != '' and interest_img != '' :
            
                interest_name_obj = Places(
                city_place_id=city_obj,
                place_name = interest_name,
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
        data={
            'success':'false',
            'message':str(e)
        }
    return 1 




def view_city(request):
    try:
        adv_list = []
        city_obj = City_Place.objects.all()
        for adv in city_obj:
            if adv.city_status == '1':
                status="Active"
                edit = '<a class="col-md-offset-1 col-md-1" style="text-align: center;" href="/edit-city/?city_place_id=' + str(adv.city_place_id) + '" class="edit" data-toggle="modal"><i class="fa fa-pencil"></i></a>'    
                delete = '<a class="col-md-1" id="'+str(adv.city_place_id)+'" onclick="delete_user_detail(this.id)" class="fa  fa-trash-o fa-lg"><i class="fa fa-trash"></a>'    
                action=edit + delete
            else:
                status="Inactive"
                edit = '--'
                delete = '--'
                active = '<a class="col-md-2" id="'+str(adv.city_place_id)+'" onclick="active_service(this.id);" style="text-align: center;letter-spacing: 5px;width:15%;margin-left: 20px !important;" title="Activate" class="edit" data-toggle="modal" ><i class="fa fa-repeat"></i></a>'
                action=active
            temp_obj = {'city_name':adv.city_id.city_name,'population':adv.population,'state':adv.state_id.state_name,'status':status,'action':action}
            adv_list.append(temp_obj)
                
        data = {'data':adv_list}

    except Exception, e:
        print 'Exception : ', e
        data = {'data': 'none'}
    return HttpResponse(json.dumps(data), content_type='application/json')  



@csrf_exempt
def delete_city(request):
        try:
            adv_obj = City_Place.objects.get(city_place_id=request.POST.get('city_place_id'))
            adv_obj.city_status = '0'
            adv_obj.save()
            data = {'message': 'City Inactivated Successfully', 'success':'true'}
            city_delete(adv_obj)
        except IntegrityError as e:
          print e
        except Exception,e:
            print e
        print "Final Data: ",data
        return HttpResponse(json.dumps(data), content_type='application/json')


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
    gmail_user =  "cityhoopla2016"
    gmail_pwd =  "cityhoopla@2016"
    FROM = 'CityHoopla Admin: <cityhoopla2016@gmail.com>'
    TO = ['cityhoopla2016@gmail.com']
    #pdb.set_trace()
    try:
        TEXT = "Hi Admin,\nCity " + str(city_obj.city_id.city_name) + " " +"has been activated successfully.\nTo view complete details visit portal and follow - Reference Data -> City\n\n Thank You,"+'\n'+"CityHoopla Team"
        SUBJECT = "City Activated Successfully!"
        #server = smtplib.SMTP_SSL()
        server = smtplib.SMTP("smtp.gmail.com", 587) 
        server.ehlo()
        server.starttls()

        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException,e:
        print e
    return 1
 
      
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
                city_image = ""
                file_name  = ""

            city_dict = {
                'success': 'true',
                'city_place_id':city_obj.city_place_id,
                'city_name':city_obj.city_id.city_id,
                'state':city_obj.state_id.state_id, 
                'climate': city_obj.climate or '',
                'about_city': city_obj.about_city or '',
                'language': city_obj.language or '',
                'population': city_obj.population or '',
                'timezone':city_obj.time_zone,
                'cityimage':city_image,
                'filename': file_name

            }

            city_list = City.objects.filter(state_id = city_obj.state_id.state_id)

            intr_list = []      
            point_of_intrest = Places.objects.filter(city_place_id = city_obj,place_type = 'point_of_interest')
            poi_index = 0
            if point_of_intrest:
                    poi_index = len(point_of_intrest)-1
                    i = 0;
                    for place in point_of_intrest:
                        try:
                            place_image = SERVER_URL + place.place_image.url
                            file_name = place_image[47:]
                        except:
                            place_image = ''
                            file_name = ''
                        place_data = {
                            'image_id':i,
                            'place_id':place.place_id,
                            'place_name':place.place_name,
                            'place_image':place_image,
                            'filename':file_name
                        }
                        intr_list.append(place_data)
                        i = i+1 
                    
            shop_list = []      
            shop_name = Places.objects.filter(city_place_id = city_obj,place_type = 'where_to_shop')
            shop_index = 0
            if shop_name:
                    shop_index = len(shop_name)-1
                    i = 0;
                    for shop in shop_name:
                        place_image = SERVER_URL + shop.place_image.url
                        file_name = place_image[47:]
                        place_data = {
                             'place_id':shop.place_id,
                             'image_id':i,
                            'place_name':shop.place_name,
                            'place_image':place_image,
                            'filename':file_name
                        }
                        shop_list.append(place_data) 
                        i = i+1
            hosp_list = []      
            hospital = Places.objects.filter(city_place_id = city_obj,place_type = 'reputed_hospitals')
            hospital_index = 0
            if hospital:
                    hospital_index = len(hospital)-1
                    i = 0;
                    for hosp in hospital:
                        place_image = SERVER_URL + hosp.place_image.url
                        file_name = place_image[47:]
                        place_data = {
                             'place_id':hosp.place_id,
                             'image_id':i,
                            'place_name':hosp.place_name,
                            'place_image':place_image,
                            'filename':file_name
                        }
                        hosp_list.append(place_data) 
                        i = i+1
            clg_list = []      
            college = Places.objects.filter(city_place_id = city_obj,place_type = 'college_and_universities')
            college_index = 0
            if college:
                    college_index = len(hospital)-1
                    i = 0;
                    for clg in college:
                        place_image = SERVER_URL + clg.place_image.url
                        file_name = place_image[32:]
                        place_data = {
                            'image_id':i,
                            'place_id':clg.place_id,
                            'place_name':clg.place_name,
                            'place_image':place_image,
                            'filename':file_name
                        }
                        clg_list.append(place_data) 
                        i = i+1
            data = {'poi_index':poi_index,'shop_index':shop_index,'hospital_index':hospital_index,'college_index':college_index,'city':city_dict,'city_list':city_list,'state_list':get_state(request),'interest':intr_list,'shops':shop_list,'hospitals':hosp_list,'colleges':clg_list,'username':request.session['login_user']}
        except Exception,e:
            print 'Exception:',e
            data = {'data':e}    
        print "Final Data",data
        return render(request,'Admin/edit_city.html',data)  

@csrf_exempt
def update_city(request):
    print 'in update city'
##    pdb.set_trace()
    try:
        if request.method == "POST":
            city_obj = City_Place.objects.get(city_place_id=request.POST.get('city_place_id'))
            city_obj.city_id= City.objects.get(city_id = request.POST.get('city_name'))
            city_obj.state_id =State.objects.get(state_id=request.POST.get('state')) 
            city_obj.save()
            
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

            city_obj.save();

            if request.POST['check_image'] == "1":
                city_obj.city_image = request.FILES['city_image']
                city_obj.save()

            city_update(city_obj)
            data = {'success': 'true'}
        else:
            data = {'success': 'false'}
    except Exception,e:
        print 'Exception:',e
        data = {'data':'none'}
    return HttpResponse(json.dumps(data), content_type='application/json')


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
        
            for i in range(int(poi_range)):
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
            for i in range(int(shop_range)):
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
            for i in range(int(hospital_range)):
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
            for i in range(int(college_range)):
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
    gmail_user =  "cityhoopla2016"
    gmail_pwd =  "cityhoopla@2016"
    FROM = 'CityHoopla Admin: <cityhoopla2016@gmail.com>'
    TO = ['cityhoopla2016@gmail.com']
    #pdb.set_trace()
    try:
        TEXT = "Hi Admin,\nCity " + str(city_obj.city_id.city_name) + " " +"has been updated successfully.\nTo view complete details visit portal and follow - Reference Data -> City\n\nThank You,"+'\n'+"CityHoopla Team"
        SUBJECT = "City Updated Successfully!"
        #server = smtplib.SMTP_SSL()
        server = smtplib.SMTP("smtp.gmail.com", 587) 
        server.ehlo()
        server.starttls()

        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException,e:
        print e
    return 1
 
def city_delete(adv_obj):
    gmail_user =  "cityhoopla2016"
    gmail_pwd =  "cityhoopla@2016"
    FROM = 'CityHoopla Admin: <cityhoopla2016@gmail.com>'
    TO = ['cityhoopla2016@gmail.com']
    #pdb.set_trace()
    try:
        TEXT = "Hi Admin,\nCity " + str(adv_obj.city_id.city_name) + " " +"has been deactivated successfully.\nTo view complete details visit portal and follow - Reference Data -> City\n\nThank You,"+'\n'+"CityHoopla Team"
        SUBJECT = "City Deactivated Successfully!"
        #server = smtplib.SMTP_SSL()
        server = smtplib.SMTP("smtp.gmail.com", 587) 
        server.ehlo()
        server.starttls()

        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException,e:
        print e
    return 1

def city_add(city_obj):
    gmail_user =  "cityhoopla2016"
    gmail_pwd =  "cityhoopla@2016"
    FROM = 'CityHoopla Admin: <cityhoopla2016@gmail.com>'
    TO = ['cityhoopla2016@gmail.com']
    #pdb.set_trace()
    try:
        TEXT = "Hi Admin,\nCity " + str(city_obj.city_id.city_name) + " " +"has been added successfully.\nTo view complete details visit portal and follow - Reference Data -> City\n\nThank You,"+'\n'+"CityHoopla Team"
        SUBJECT = "City Added Successfully!"
        #server = smtplib.SMTP_SSL()
        server = smtplib.SMTP("smtp.gmail.com", 587) 
        server.ehlo()
        server.starttls()

        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException,e:
        print e
    return 1    
