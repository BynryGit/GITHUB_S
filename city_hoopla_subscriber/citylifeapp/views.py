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
import operator
from django.db.models import Q
import datetime
from datetime import datetime
from datetime import date, timedelta
from django.views.decorators.cache import cache_control
# HTTP Response
from django.http import HttpResponse
from django.http import HttpResponseRedirect

SERVER_URL = "http://52.66.169.65"
#SERVER_URL = "http://52.66.144.182"
#SERVER_URL = "http://192.168.0.125:8011"



####################.......city_dashboard..........%%%%%%%%%%##########

@csrf_exempt
def city_dashboard(request):
    try:
        data = {}
        final_list = []
        final_list1 = []
        try:
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
                    total_payment_count = float(total_payment_count) + float(paid_amount)
                    
            #New Subscribers
            total_new_subscriber = Business.objects.filter(business_created_date__range=[last_date,current_date]).count()
            
            #New Bookings
            total_new_booking = CouponCode.objects.filter(creation_date__range=[last_date,current_date]).count()
            # Adverts Expiring
            current_date = datetime.now().strftime("%m/%d/%Y")
            last_date = (datetime.now() + timedelta(days=7)).strftime("%m/%d/%Y")
            total_advert_expiring = Business.objects.filter(end_date__range=[current_date,last_date]).count()
            print "..#########......total_advert_expiring.........",total_advert_expiring


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
                            mon = mon+float(view_obj.paid_amount)
                    elif consumer_day== 'Tuesday' :
                        if view_obj.paid_amount:
                            tue = tue+float(view_obj.paid_amount)
                    elif consumer_day== 'Wednesday' :
                        if view_obj.paid_amount:
                            wen = wen+float(view_obj.paid_amount)
                    elif consumer_day== 'Thursday' :
                        if view_obj.paid_amount:
                            thus = thus+float(view_obj.paid_amount)
                    elif consumer_day== 'Friday' :
                        if view_obj.paid_amount:
                            fri = fri+float(view_obj.paid_amount)
                    elif consumer_day== 'Saturday' :
                        if view_obj.paid_amount:
                            sat = sat+float(view_obj.paid_amount)
                    elif consumer_day== 'Sunday' :
                        if view_obj.paid_amount:
                            sun = sun+float(view_obj.paid_amount)
                    else :
                        pass

            data = {'success':'true','total_payment_count':total_payment_count,'total_new_subscriber':total_new_subscriber,
                'total_new_booking':total_new_booking,'total_advert_expiring':total_advert_expiring,'mon':mon,'tue':tue,'wen':wen,'thus':thus,'fri':fri,'sat':sat,'sun':sun,'city_places_list':get_city_places(request)
               }

        except IntegrityError as e:
            print e
            data = {'success':'false','message':'Error in  loading page. Please try after some time','username':request.session['login_user']}
    except MySQLdb.OperationalError, e:
        print e
    except Exception,e:
        print 'Exception ',e

    print data
    return render(request,'City_Life/life-dashboard.html',data)

@csrf_exempt
def city_life(request):
    try:
        data = {}
        final_list = []
        today_post_count = 0
        post_var = 0
        posting_date_old = '2000-01-01'
        try:
            pre_date = datetime.now().strftime("%Y-%m-%d")
            post_list = PostDetails.objects.all()
            print '........post_list.......',post_list
            for post_obj in post_list:
                print 'WWWWWWWWWWWWW',posting_date_old
                city_id = post_obj.city_id
                print 'AAAAAAAAAAAA',city_id
                new_list = PostDetails.objects.filter(city_id = city_id)
                print 'BBBBBBBBBBBB',new_list
                for obj in new_list:
                    city_name = obj.city_id.city_name
                    country_name = obj.country_id.country_name
                    unread_post = obj.post_file_id.unread_post
                    post_var = post_var + int(unread_post)
                   
                    creation_date = obj.creation_date.strftime("%Y-%m-%d")
                    if creation_date == pre_date :
                        today_post_count = today_post_count +1
                
                    posting_date_new = obj.posting_date.strftime("%Y-%m-%d")
                    if posting_date_new > posting_date_old:
                        posting_date_old = posting_date_new
                        username = obj.username
                        posting_date = obj.posting_date.strftime("%Y-%m-%d")
                        print 'ssssssssssssssss',posting_date
                        file = SERVER_URL + obj.post_file_id.file.url
                        reviews = obj.post_file_id.reviews

                post_data = {
                    'city_name':city_name,
                    'country_name':country_name,
                    'post_var':post_var,
                    'today_post_count':today_post_count,
                    'username':username,
                    'posting_date':posting_date,
                    'file':file,
                    'reviews':reviews

                }
                final_list.append(post_data)

            data = {'success':'true','final_list':final_list,'country_list':get_country(request)
                   }
            print '$$$$$$$$$$$$$$$$$$$$$$',data
        except IntegrityError as e:
            print e
            data = {'success':'false','message':'Error in  loading page. Please try after some time','username':request.session['login_user']}
    except MySQLdb.OperationalError, e:
        print e
    except Exception,e:
        print 'Exception ',e

    print data
    return render(request,'City_Life/city-life.html',data)

# TO GET THE CITY
def get_country(request):
   
    country_list=[]
    try:
        con_objs=Country.objects.filter(country_status='1')
        for country in con_objs:
            country_list.append({'country_id': country.country_id,'country': country.country_name})
        data =  country_list
        return data

    except Exception, ke:
        print ke
        data={'country_list': 'none','message':'No country available'}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def category_life(request):
    try:
        data = {}
        final_list = []
        final_list1 = []
        try:
            data = {'success':'true','country_list':get_country(request)
                   }

        except IntegrityError as e:
            print e
            data = {'success':'false','message':'Error in  loading page. Please try after some time','username':request.session['login_user']}
    except MySQLdb.OperationalError, e:
        print e
    except Exception,e:
        print 'Exception ',e

    print data
    return render(request,'City_Life/category-life.html',data)

# TO GET THE CITY countrybase
def get_city_countrybase(request):
   
    cont_id=request.GET.get('cont_id')
    print '.................cont_id.....................',cont_id
    city_list=[]
    try:
        city_objs=City_Place.objects.filter(country_id=cont_id,city_status='1').order_by('city_id')
  
        for city in city_objs:
            print '-----city---',city
            options_data = '<option value=' + str(
                   city) + '>' + city.city_id.city_name + '</option>'
            city_list.append(options_data)
        data = {'city_list': city_list}

    except Exception, ke:
        print ke
        data={'city_list': 'none','message':'No city available'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def save_category_citylife(request):
    try:
        final_list = []

        city = request.POST.get('city')
        city_objs = City_Place.objects.get(city_place_id=city,city_status='1')

        cate_id = request.POST.getlist('list1')
        cat_name = request.POST.getlist('list')
        print '...............category id.............',cate_id
        print '--------------cat name-----------------',cat_name

        name_list = cat_name[0].split(',')

        id_list = cate_id[0].split(',')

        for i in range(len(name_list)):
            print name_list[i],id_list[i]
            if name_list[i] != '':   
                if id_list[i]:
                    cat_obj_1 = citylife_category.objects.get(category_id=id_list[i],city_id=city_objs)
                    cat_obj_1.category_name = name_list[i]
                    cat_obj_1.city_id = city_objs
                    cat_obj_1.save()
                    message = 'Category edited successfully'
                else :
                    cat_obj_level_1 = citylife_category(
                                category_name = name_list[i],
                                city_id = city_objs,
                                creation_date = datetime.now()
                            )
                    cat_obj_level_1.save()
                    message = 'Category added successfully'
            

        category_list = citylife_category.objects.filter(city_id=city_objs)

        if category_list:  
            for cat_obj in category_list:
                category_name = cat_obj.category_name
                city_name = cat_obj.city_id.city_id.city_name
                country_name = cat_obj.city_id.country_id.country_name
                category_id = cat_obj.category_id

                cate_data = {
                    'category_name':category_name,
                    'category_id':category_id
                }
                final_list.append(cate_data)

            data = {
                'success': 'true',
                'message': message,
                'final_list':final_list,
                'city_name':city_name,
                'country_name':country_name

            }
        else:
            data = {
                'success': 'true1',
                'message': message

            }
    except Exception as e:
        print e
        data = {
                'success': 'false',
                'message': message
            }
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def citylife_cat(request):
    try:
        final_list = []
        final_list1 = []
        city = request.POST.get('city')
        city_objs=City_Place.objects.get(city_place_id=city,city_status='1')
          
        category_list = citylife_category.objects.filter(city_id=city_objs)

        for cat_obj in category_list:
            category_id = cat_obj.category_id
            category_name = cat_obj.category_name

            cate_data = {
                'category_id':category_id,
                'category_name':category_name
            }
            final_list.append(cate_data)

        data = {
            'success': 'true',
            'message': "Category added successfully",
            'final_list':final_list  }
    except Exception as e:
        print e
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def delete_citylife_cat(request):
    try:
        final_list = []
        final_list1 = []
        cat_id_global = request.POST.get('cat_id_global')
        
        cat_obj = citylife_category.objects.get(category_id=cat_id_global)
        city_id = cat_obj.city_id
        cat_obj.delete()
        
        category_list = citylife_category.objects.filter(city_id=city_id)

        for cat_obj in category_list:
            category_id = cat_obj.category_id
            category_name = cat_obj.category_name

            cate_data = {
                'category_id':category_id,
                'category_name':category_name
            }
            final_list.append(cate_data)

        data = {
            'success': 'true',
            'message': "Category added successfully",
            'final_list':final_list  }
    except Exception as e:
        print e
    return HttpResponse(json.dumps(data), content_type='application/json')

