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

import urllib2
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

# Location

# calender
from datetime import date
import calendar

#SERVER_URL = "http://52.40.205.128"
#SERVER_URL = "http://127.0.0.1:8000" 
SERVER_URL = "http://52.66.133.35" 

def view_user_list(request):
    try:
        data = {}
        final_list = []
        city_place = ''
        try:
            print '===========in function====Sortby===='
            sort_by = request.GET.get('sort_by')
            print 'sort_by',sort_by
            if sort_by == "oldest_first":
                user_list = ConsumerProfile.objects.filter(consumer_type = 'register').order_by('-consumer_created_date').reverse()
            else:
                user_list = ConsumerProfile.objects.filter(consumer_type = 'register').order_by('-consumer_created_date')
            for user_obj in user_list:
                #role_id = user_obj.user_role.role_name
                consumer_id = user_obj.consumer_id
                bookings = CouponCode.objects.filter(user_id=consumer_id).count()
                consumer_full_name = user_obj.consumer_full_name
                consumer_contact_no = user_obj.consumer_contact_no
                consumer_email_id = user_obj.consumer_email_id
                consumer_area = user_obj.consumer_area
                if user_obj.consumer_profile_pic:
                    consumer_profile_pic=SERVER_URL + user_obj.consumer_profile_pic.url
                else:
                    consumer_profile_pic=SERVER_URL + '/static/assets/layouts/layout2/img/avatar.png'
                

                view = '<a id="'+str(consumer_id)+'"  style="text-align: center;width:24%;" title="Edit" class="edit" data-toggle="modal" href="/booking/?consumer_id='+str(consumer_id)+'"><i class="fa fa-eye"></i></a>'
                list = {'consumer_profile_pic':consumer_profile_pic,'consumer_id':consumer_id,'bookings':bookings,'consumer_full_name':consumer_full_name,'consumer_contact_no':consumer_contact_no,'consumer_email_id':consumer_email_id,'view':view}
                final_list.append(list)

            data = {'success':'true','sort_by':sort_by,'consumer_list':final_list,'city_places_list':get_city_places(request),'city_place' : city_place}

        except IntegrityError as e:
            print e
            data = {'success':'false','message':'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception,e:
        print 'Exception ',e
    print data
    return render(request,'Admin/consumer_list.html',data)

def view_user_list1(request):
    try:
        data = {}
        final_list = []
        city_place = ''
        try:
            print '===========in function====City===='
            filter_by = request.GET.get('filter_by')
            if filter_by:
                user_list = ConsumerProfile.objects.filter(city_place_id = filter_by,consumer_type = 'register')
                if user_list:
                    for user_obj in user_list:
                        #role_id = user_obj.user_role.role_name
                        consumer_id = user_obj.consumer_id
                        bookings = CouponCode.objects.filter(user_id=consumer_id).count()
                        consumer_full_name = user_obj.consumer_full_name
                        consumer_contact_no = user_obj.consumer_contact_no
                        consumer_email_id = user_obj.consumer_email_id
                        consumer_area = user_obj.consumer_area
                        city_place = user_obj.city_place_id.city_id.city_name
                        

                        if user_obj.consumer_profile_pic:
                            consumer_profile_pic=SERVER_URL + user_obj.consumer_profile_pic.url
                        else:
                            consumer_profile_pic=SERVER_URL + '/static/assets/layouts/layout2/img/avatar.png'
                        
                        view = '<a id="'+str(consumer_id)+'"  style="text-align: center;width:24%;" title="Edit" class="edit" data-toggle="modal" href="/booking/?consumer_id='+str(consumer_id)+'"><i class="fa fa-eye"></i></a>'
                        list = {'consumer_profile_pic':consumer_profile_pic,'consumer_id':consumer_id,'bookings':bookings,'consumer_full_name':consumer_full_name,'consumer_contact_no':consumer_contact_no,'consumer_email_id':consumer_email_id,'view':view}
                        final_list.append(list)
                    data = {'success':'true','consumer_list':final_list,'city_places_list':get_city_places(request),'city_place' : city_place}
                else :
                    print 'in ----------else'

                    final_list = []
                    data = {'success':'true','consumer_list':final_list,'city_places_list':get_city_places(request)}

            else :
                print 'in ----------else'

                final_list = []
                data = {'success':'true','consumer_list':final_list,'city_places_list':get_city_places(request)}
        except IntegrityError as e:
            print e
            data = {'success':'false','message':'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception,e:
        print 'Exception ',e
    print data
    return render(request,'Admin/consumer_list.html',data)

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

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def consumer_booking_details(request):
    #pdb.set_trace()
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        try:
            # pdb.set_trace()
            print '=======request=====last====',request.GET.get('consumer_id')
            data = {}
            final_list = []
            consumer_id = request.GET.get('consumer_id')
            consumer_obj=ConsumerProfile.objects.get(consumer_id=request.GET.get('consumer_id'))
            consumer_full_name = consumer_obj.consumer_full_name

            sort_by = ''
            sort_by = request.GET.get('sort_by')
            
            if sort_by == "new":
                consumer_obj1 = CouponCode.objects.filter(user_id=request.GET.get('consumer_id')).order_by('-creation_date')
                consumer_count = CouponCode.objects.filter(user_id=request.GET.get('consumer_id')).order_by('-creation_date').count()
            else:
                consumer_count = CouponCode.objects.filter(user_id=request.GET.get('consumer_id')).count()
                consumer_obj1 = CouponCode.objects.filter(user_id=request.GET.get('consumer_id'))


            for consumer_obj in consumer_obj1:
                coupon_code = consumer_obj.coupon_code
                advert_name = consumer_obj.advert_id.advert_name
                category_name = consumer_obj.advert_id.category_id.category_name
                business_name = consumer_obj.advert_id.supplier_id.business_name
                city_name = consumer_obj.advert_id.supplier_id.city_place_id.city_id.city_name
                avail_date = consumer_obj.creation_date.strftime("%d/%m/%Y")
                expiry_date_var = str(consumer_obj.advert_id.advert_id)
                advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=str(consumer_obj.advert_id.advert_id))
                expire_date = advert_sub_obj.business_id.end_date
                expire_date = datetime.strptime(expire_date, "%d/%m/%Y")
                coupon_expiry_date=expire_date.strftime("%d/%m/%Y")
                pre_date = datetime.now().strftime("%d/%m/%Y")
                pre_date = datetime.strptime(pre_date, "%d/%m/%Y")
                date_gap = expire_date - pre_date
                date_gap=int(date_gap.days)
                print 'date_gap',date_gap
                if  date_gap>= 0:
                    status = 'Active'
                else:
                    status = 'Inactive'

                list = {'success':'true','coupon_expiry_date':coupon_expiry_date,'status':status,'city_name':city_name,'date_gap':date_gap,'coupon_code':coupon_code,'user_id':str(consumer_obj.user_id),
                        'advert_name':advert_name,'category_name':category_name,'business_name':business_name,'avail_date':avail_date,'expire_date':expire_date }
                final_list.append(list)
            data = {'success':'true','sort_by':sort_by,'consumer_id':consumer_id,'consumer_count':consumer_count,'consumer_full_name':consumer_full_name,'consumer_bookings':final_list,'username':request.session['login_user'],}       
        except MySQLdb.OperationalError, e:
            print e
        except Exception,e:
            print 'Exception ',e
        print data
        return render(request,'Admin/consumer_details.html',data)


def subscriber_bookings(request):
    consumer_id = request.GET.get('consumer_id')
    print "bookings",request.GET.get('consumer_id')
    data = {'consumer_id':consumer_id,'username':request.session['login_user']}
    return render(request,'Admin/bookings.html',data)   

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def sms(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:    
        data = {'username':request.session['login_user']}
        return render(request,'Admin/sms.html',data)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def send_sms(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:    
        #data = {'username':request.session['login_user']}
        #return render(request,'Admin/send_sms.html',data)
        try:
            data = {}
            final_list = []
            try:
                user_list = ConsumerProfile.objects.all()
                print user_list
                for user_obj in user_list:
                    #role_id = user_obj.user_role.role_name
                    consumer_id = user_obj.consumer_id
                    consumer_full_name = user_obj.consumer_full_name
                    consumer_contact_no =user_obj.consumer_contact_no
                    #view = '<a class="col-md-offset-2 col-md-1" id="'+str(user_obj)+'"  style="text-align: center;letter-spacing: 5px;width:15%;" title="Edit" class="edit" data-toggle="modal" href="/booking/?consumer_id='+str(user_id)+'"><i class="fa fa-eye"></i></a>'
                    list = {'consumer_id':consumer_id,'consumer_full_name':consumer_full_name,'consumer_contact_no':consumer_contact_no}
                    final_list.append(list)
                data = {'success':'true','final_list':final_list,'username':request.session['login_user']}
            except IntegrityError as e:
                print e
                data = {'success':'false','message':'Error in  loading page. Please try after some time','username':request.session['login_user']}
        except MySQLdb.OperationalError, e:
            print e
        except Exception,e:
            print 'Exception ',e
        print data
        return render(request,'Admin/send_sms.html',data)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def email(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:    
        
        data = {'username':request.session['login_user']}
        return render(request,'Admin/email.html',data)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def send_email(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:    
        #login_user = {'username':request.session['login_user']}
        try:
            data = {}
            final_list = []
            try:
                #today_date = str(datetime.now().strftime("%Y/%m/%d"))
                # print '-----today-----',today_date
                # next_week_date = str((datetime.now() + timedelta(days=7)).strftime("%Y/%m/%d"))
                # print '-------next date-',next_week_date
                # list = []
                # consumer_obj_list = Business.objects.filter(end_date__range=[today_date,next_week_date])
                # print '--------consumer_obj_list-----',consumer_obj_list

                # if consumer_obj_list:
                #     for consumer_obj in consumer_obj_list:
                #         #supplier_obj = Supplier.objects.get(supplier_id=str(consumer_obj.supplier))
                #     #email_id = supplier_obj.supplier_email 

                #         email_id = consumer_obj.supplier.supplier_email 
                #         list.append(str(email_id))
                #     email_list = set(list)
                #     print 'ssssssssssssssssssssssssssssssss',email_list

                #     for email in email_list:
                #         gmail_user =  "cityhoopla2016"
                #         gmail_pwd =  "cityhoopla@2016"
                #         FROM = 'CityHoopla Admin: <cityhoopla2016@gmail.com>'
                #         TO = [email]

                #         try:
                #             TEXT = 'Your advert is going to expire'
                #             SUBJECT = 'Welcome to City Hoopla'
                #             server = smtplib.SMTP_SSL()
                #             server = smtplib.SMTP("smtp.gmail.com", 587) 
                #             server.ehlo()
                #             server.starttls()

                #             server.login(gmail_user, gmail_pwd)
                #             message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
                #             server.sendmail(FROM, TO, message)
                #             server.quit()
                #             print '==============Successfully Snt==============='
                #         except SMTPException,e:
                #             print e                
             

                user_list = ConsumerProfile.objects.all()
                for user_obj in user_list:
                    #role_id = user_obj.user_role.role_name
                    consumer_id = user_obj.consumer_id
                    consumer_full_name = user_obj.consumer_full_name
                    consumer_email_id = user_obj.consumer_email_id
                    #view = '<a class="col-md-offset-2 col-md-1" id="'+str(user_obj)+'"  style="text-align: center;letter-spacing: 5px;width:15%;" title="Edit" class="edit" data-toggle="modal" href="/booking/?consumer_id='+str(user_id)+'"><i class="fa fa-eye"></i></a>'
                    list = {'consumer_id':consumer_id,'consumer_full_name':consumer_full_name,'consumer_email_id':consumer_email_id}
                    final_list.append(list)
                data = {'success':'true','final_list':final_list,'username':request.session['login_user']}
            except IntegrityError as e:
                print e
                data = {'success':'false','message':'Error in  loading page. Please try after some time','username':request.session['login_user']   }
        except MySQLdb.OperationalError, e:
            print e
        except Exception,e:
            print 'Exception ',e
        print data
        return render(request,'Admin/send_email.html',data)


@csrf_exempt
def admin_send_email(request):
    consumer = request.POST.getlist('consumer')
    consumer01=consumer[0]

    print'================consumer===================',consumer
    print'================consumer===================',consumer01
    consumer_new = consumer01.split(',')

    subject = request.POST.get('subject')
    description = request.POST.get('description') 

    for usernm in consumer_new:
        print '------abc----',usernm
        gmail_user =  "cityhoopla2016"
        gmail_pwd =  "cityhoopla@2016"
        FROM = 'CityHoopla Admin: <cityhoopla2016@gmail.com>'
        TO = [usernm]

        #pdb.set_trace()
        try:
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
        except SMTPException,e:
            print e
    data = {'success':'true','username':request.session['login_user']}
    return HttpResponse(json.dumps(data), content_type='application/json')



@csrf_exempt
def admin_send_sms(request):
    mobile_number_list = request.POST.getlist('consumer')
    number_list = mobile_number_list[0].split(',')
    # for number in number_list:
    #     description = request.POST.get('description')
    #     authkey = "118994AIG5vJOpg157989f23"
    #     mobiles = number
    #     message = description
    #     sender = "DGSPCE"
    #     route = "4"
    #     country = "91"
    #     values = {
    #               'authkey' : authkey,
    #               'mobiles' : mobiles,
    #               'message' : message,
    #               'sender' : sender,
    #               'route' : route,
    #               'country' : country
    #               }

    #     url = "http://api.msg91.com/api/sendhttp.php"
    #     postdata = urllib.urlencode(values)
    #     req = urllib2.Request(url, postdata)
    #     response = urllib2.urlopen(req)
    #     output = response.read()
    #     print output
    data = {'success':'true','username':request.session['login_user']}
    return HttpResponse(json.dumps(data), content_type='application/json')



# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
# def advert_booking(request):
#     if not request.user.is_authenticated():
#         return redirect('backoffice')
#     else:    
#         data = {'username':request.session['login_user']}
#         return render(request,'Admin/advert_booking.html',data)





def pay_collection(request):
    try:
        data = {}
        final_list = []
        try:
            print '=========== in   pay_collection   function========'
            today_date = str(datetime.now())
            user_list = PaymentDetail.objects.filter(payment_created_date=today_date)
            for user_obj in user_list:
                total_amount = user_obj.total_amount
                consumer_contact_no = user_obj.consumer_contact_no
                consumer_email_id = user_obj.consumer_email_id
                consumer_area = user_obj.consumer_area

                list = {'consumer_id':consumer_id,'consumer_full_name':consumer_full_name,'consumer_contact_no':consumer_contact_no,'consumer_email_id':consumer_email_id,'consumer_area':consumer_area,'view':view}
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


def payment_city(request):
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
                city_nm = request.GET.get('city_nm')
                print '........city_nm........',city_nm

                consumer_list0= PaymentDetail.objects.filter(payment_created_date__regex = '00:',payment_created_date__contains = str((datetime.now()).strftime("%Y-%m-%d")))
                if consumer_list0:
                    for consumer_obj in consumer_list0:

                        city_nm1 = consumer_obj.business_id.supplier.city.city_id
                        print '.......................city id .........',city_nm1

                        if str(city_nm) == str(city_nm1):


                            total_amount0 = consumer_obj.total_amount

                            temp_var0 = temp_var0 + int(total_amount0)

                value_0 = str(temp_var0)



                for hour in range(1,9):
                    hour = ' 0'+ str(hour) + ':'
                    consumer_obj_list1 = PaymentDetail.objects.filter(payment_created_date__regex = hour,payment_created_date__contains = str((datetime.now()).strftime("%Y-%m-%d")))

                    
                    if consumer_obj_list1:
                        #print '........................consumer_obj_list..........next............................',consumer_obj_list1
                        for consumer_obj in consumer_obj_list1:
                            city_nm1 = consumer_obj.business_id.supplier.city.city_id
                            print '.......................city id .........',city_nm1
                            
                            if str(city_nm) == str(city_nm1):
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
                            city_nm1 = consumer_obj.business_id.supplier.city.city_id
                            print '.......................city id .........',city_nm1
                            
                            if str(city_nm) == str(city_nm1):

                                total_amount2 = consumer_obj.total_amount
                                temp_var2 = temp_var2 + int(total_amount2)
                            #print '....................total total_amount2 ................',temp_var2

                value_2 = str(temp_var2)   


                for hour in range(17,24):
                    hour = ' '+ str(hour) + ':'
                    consumer_obj_list = PaymentDetail.objects.filter(payment_created_date__contains = str((datetime.now()).strftime("%Y-%m-%d")),payment_created_date__regex= hour)
                    if consumer_obj_list:
                        for consumer_obj in consumer_obj_list:
                            city_nm1 = consumer_obj.business_id.supplier.city.city_id
                            print '.......................city id .........',city_nm1
                            
                            if str(city_nm) == str(city_nm1):

                                total_amount3 = consumer_obj.total_amount
                                temp_var3 = temp_var3 + int(total_amount3)
                            #print '....................total total_amount3 ................',temp_var3

                value_3 = str(temp_var3)
                #print '......................value_3....................',value_3

                data = {'success':'true','value_0':value_0,'value_1':value_1,'value_3':value_3,'value_2':value_2,'username':request.session['login_user'],'city_places_list':get_city_places(request) }


            except IntegrityError as e:
                print e
                data = {'success':'false','message':'Error in  loading page. Please try after some time','username':request.session['login_user']}                

        except MySQLdb.OperationalError, e:
            print e
        except Exception,e:
            print 'Exception ',e
        print data
        return HttpResponse(json.dumps(data), content_type='application/json')

#@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def register_city(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        try:

            temp_var1 = 0
            temp_var2 = 0
            temp_var3 = 0
            temp_var4 = 0
            data = {}
            try:
                ############################Last 1 week new subscription view###############################
                city_nm = request.GET.get('city_nm')
                print '................',city_nm
                current_date = datetime.now()
                first = calendar.day_name[current_date.weekday()]
                print '------------------------current_date------------------------',first

                last_date = (datetime.now() - timedelta(days=7))
                last_date2 = calendar.day_name[last_date.weekday()]
                print '============last_date==============',last_date2

                list = []
                consumer_obj_list = Business.objects.filter(business_created_date__range=[last_date,current_date])
                
                mon=tue=wen=thus=fri=sat=sun=0
                if consumer_obj_list:
                    for consumer_obj in consumer_obj_list:

                        
                        #city_nm1 = consumer_obj.supplier.city.city_name
                        city_nm1 = consumer_obj.supplier.city.city_id
                        print '......................city_nm1 ..........',city_nm1

                        if str(city_nm) == str(city_nm1):
                            print "match"
                            business_created_date=consumer_obj.business_created_date
                            consumer_day = calendar.day_name[business_created_date.weekday()]
                            print '.....................consumer_day............',consumer_day
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
                    data = {'success':'true','mon':mon,'tue':tue,'wen':wen,'thus':thus,'fri':fri,'sat':sat,'sun':sun,'success':'true','username':request.session['login_user'],'city_places_list':get_city_places(request)}


            except IntegrityError as e:
                print e
                data = {'success':'false','message':'Error in  loading page. Please try after some time','username':request.session['login_user']}                

        except MySQLdb.OperationalError, e:
            print e
        except Exception,e:
            print 'Exception ',e
        print data
        return HttpResponse(json.dumps(data), content_type='application/json')
