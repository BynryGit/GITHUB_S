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
from operator import itemgetter
from django.db.models import Q
import datetime
from datetime import datetime
from datetime import date, timedelta
from django.views.decorators.cache import cache_control
# HTTP Response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from DigiSpace.tasks import send_to_subscriber
from DigiSpace.tasks import send_sms_to_consumer
from DigiSpace.tasks import send_email_to_consumer

#from DigiSpace.tasks import print_some_times
SERVER_URL = "http://52.40.205.128"
#SERVER_URL = "http://127.0.0.1:8000"

#CTI CRM APIs=============================================================================


@csrf_exempt
def get_consumer_detail(request):
    data = {}
    try:
        if request.method == "POST":
            print 'number: ', request.POST.get('number')
            user_obj = CallerDetails.objects.get(IncomingTelNo=request.POST.get('number'))
            print '--------user_obj-----',user_obj
            if user_obj :
                phone_number = user_obj.IncomingTelNo
                data= { 'success' : 'true','phone_number':str(phone_number),'caller_id':str(user_obj)}
            else:
                print '---------record not found---------'
                data= { 'success' : 'false'}

    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def caller_details_api(request):
    print '-----------body--123----',request.GET.get('CallerID')
    try:
        call_obj = CallInfo(
            UCID=request.GET.get('UCID'),
            CallerID=request.GET.get('CallerID'),
            CalledNo=request.GET.get('CalledNo'),
            CallStartTime=request.GET.get('CallStartTime'),
            DialStartTime=request.GET.get('DialStartTime'),
            DialEndTime=request.GET.get('DialEndTime'),
            DisconnectType=request.GET.get('DisconnectType'),
            CallStatus=request.GET.get('CallStatus'),
            CallDuration=request.GET.get('CallDuration'),
            CallType=request.GET.get('CallType'),
            AudioRecordingURL=request.GET.get('RecordingURL'),
            DialedNumber=request.GET.get('DialedNumber'),
            Department=request.GET.get('Department'),
            CallBackParam=request.GET.get('CallBackParam'),
            Extn=request.GET.get('Extn')
        );
        call_obj.save()
        data= { 'success' : 'true'}

    except Exception, e:
        print 'Exception ', e
        data= { 'success' : 'false', 'message':'Invalid data'}
    return HttpResponse(json.dumps(data), content_type='application/json')


def crm_details(request):
    try:
        if request.GET.get('number'):
            request.session['number']=request.GET.get('number')
            user_obj = CallerDetails.objects.get(IncomingTelNo=request.GET.get('number'))
            enquiry=''
            address=''
            e_date=''
            detail_list=[]
            caller_id = user_obj.CallerID
            phone_number = user_obj.IncomingTelNo
            first_name = user_obj.first_name
            last_name = user_obj.last_name
            email = user_obj.email
            CallerArea = user_obj.CallerArea
            CallerCity = user_obj.CallerCity
            CallerPincode = user_obj.CallerPincode

            enquiry_obj = EnquiryDetails.objects.filter(CallerID=user_obj)
            print '--------enquiry obj-----',enquiry_obj
            sr_no=0
            for e in enquiry_obj:
                sr_no=sr_no+1
                enquiry = e.enquiryFor
                print '-----enquiry-----',enquiry
                address = str(e.SelectedArea)
                e_date = e.created_date

                data_list={'sr_no':sr_no,'enquiry':enquiry,'address':address,'e_date':e_date}
                detail_list.append(data_list)

            city_list = City.objects.all()
            category_list = Category.objects.all()

            data = {'city_list':city_list,'category_list':category_list,'detail_list':detail_list,'caller_id':caller_id,'phone_number':phone_number,'email':email,'first_name':first_name,'last_name':last_name,'area':CallerArea,'city':CallerCity,'pincode':CallerPincode,
                    'enquiry':enquiry,'address':address,'e_date':e_date,'number':request.session['number']}
            return render(request,'CTI_CRM/crm_details.html',data)
        else:
            request.session['number1']=request.GET.get('number1')
            user_obj = CallerDetails.objects.get(IncomingTelNo=request.GET.get('number1'))
            enquiry=''
            address=''
            e_date=''
            action=''
            caller_id=''
            detail_list=[]
            caller_id = user_obj.CallerID
            phone_number = user_obj.IncomingTelNo
            first_name = user_obj.first_name
            last_name = user_obj.last_name
            email = user_obj.email
            CallerArea = user_obj.CallerArea
            CallerCity = user_obj.CallerCity
            CallerPincode = user_obj.CallerPincode

            enquiry_obj = EnquiryDetails.objects.filter(CallerID=user_obj)
            print '--------enquiry obj-----',enquiry_obj
            sr_no=0
            for e in enquiry_obj:
                sr_no=sr_no+1
                enquiry = e.enquiryFor
                print '-----enquiry-----',enquiry
                address = str(e.SelectedArea)
                e_date = e.created_date

                data_list={'sr_no':sr_no,'enquiry':enquiry,'address':address,'e_date':e_date}
                detail_list.append(data_list)

            city_list = City.objects.all()
            category_list = Category.objects.all()

            data = {'city_list':city_list,'category_list':category_list,'detail_list':detail_list,'caller_id':caller_id,'phone_number':phone_number,'email':email,'first_name':first_name,'last_name':last_name,'area':CallerArea,'city':CallerCity,'pincode':CallerPincode,
                    'enquiry':enquiry,'address':address,'e_date':e_date,'number1':request.session['number']}
            print '-------data-------',data
            return render(request,'CTI_CRM/crm_details.html',data)
    except:
        city_list = City.objects.all()
        data = {'city_list':city_list,'number':request.session['number']}
        return render(request,'CTI_CRM/new_consumer.html',data)

def new_consumer(request):
    data={}
    number=request.GET.get('number')
    city_list = City.objects.all()
    data = {'city_list':city_list,'number':number}
    return render(request,'CTI_CRM/new_consumer.html',data)

@csrf_exempt
def save_consumer_details(request):
    id = Pincode.objects.get(pincode=request.POST.get('pincode'))
    city = City.objects.get(city_id=request.POST.get('city'))
    try:
        caller_obj = CallerDetails(
            first_name=request.POST.get('fname'),
            last_name=request.POST.get('lname'),
            IncomingTelNo=request.POST.get('mobile'),
            email=request.POST.get('email'),
            CallerArea=request.POST.get('area'),
            CallerPincode=id,
            CallerCity=city,
            caller_created_date=datetime.now()
        )
        caller_obj.save()
        print '--------caller id------',caller_obj.IncomingTelNo
        data = {'success': 'true','number1':str(caller_obj.IncomingTelNo)}

    except Exception, e:
        print 'Exception ', e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')

def get_pincode_list(request):
    data={}
    pincode_list = []
    try:
        city_id = request.GET.get('city_id')
        city_id1 = City_Place.objects.get(city_id=str(city_id))
        city_id2 = City.objects.get(city_id=str(city_id1.city_id.city_id))
        pincode_list1 = Pincode.objects.filter(city_id=city_id2.city_id).order_by('pincode')
        pincode_objs = pincode_list1.values('pincode').distinct()
        for pincode in pincode_objs:
            options_data = '<option>' + pincode['pincode'] + '</option>'
            pincode_list.append(options_data)
        data = {'pincode_list': pincode_list}
    except Exception, ke:
        print ke
        data = {'city_list': 'none', 'message': 'No city available'}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def send_subscriber_details(request):
    i=0
    slist=[]
    list1=[]
    list=[]
    print '------------send data----------',request.POST.get('subscriber_id')
    print '------------all data----------',request.POST.get('es_name_list')
    print '------------sms data----------',request.POST.get('sms')
    print '------------email data----------',request.POST.get('email')
    try:
        list = request.POST.get('subscriber_id')
        searchfor = request.POST.get('searchfor')
        area = request.POST.get('area')
        city = request.POST.get('city')
        cid = request.POST.get('cid')
        cobj = CallerDetails.objects.get(CallerID=cid)
        c_number = cobj.IncomingTelNo
        c_name = cobj.first_name
        c_email = cobj.email
        ele = list.split(',')
        print '---------ele-------',ele
        for i in range(len(ele)):
            print ele[i]
            element = ele[i].split('-')
            print '----id--',element[0]
            print '------',element[1]
            supplier_obj = Supplier.objects.get(supplier_id=element[0])
            supplier_id = str(supplier_obj.supplier_id)
            business_name = supplier_obj.business_name
            email = supplier_obj.supplier_email
            phone = supplier_obj.phone_no
            address = supplier_obj.address1+ ' ' +supplier_obj.address2 +','+str(supplier_obj.city_place_id.city_id)+'-'+supplier_obj.pincode.pincode
            t = datetime.now()
            list1={'supplier_id':supplier_id,'bname':business_name,'email':email,'phone':phone,'address':str(address),'time':t,
                   'searchfor':searchfor,'area':area,'cid':cid,'c_number':c_number,'c_name':c_name,'c_email':c_email}
            slist.append(list1)
            data = {'success':'true'}
        save_enquiry_details(cid,city,searchfor,area)

        if request.POST.get('sms'):
            print '--------in the sms=-------'
            send_sms_to_consumer.delay(slist,c_number)

        if request.POST.get('email'):
            print '--------in email------'
            send_email_to_consumer.delay(slist,c_email)

        send_consumer_details(list,searchfor,area,cid)

    except Exception as e:
        print e
        data = {'success':'false'}

    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def send_consumer_details(list,searchfor,area,cid):
    print '------------in consumer details----------',list,searchfor,area,cid
    i=0
    slist=[]
    list1=[]
    try:
        cobj = CallerDetails.objects.get(CallerID=cid)
        c_number = cobj.IncomingTelNo
        c_name = cobj.first_name
        c_email = cobj.email
        print '--------list----',list
        ele = list.split(',')
        for i in range(len(ele)):
            print '-----i---',ele[i]
            element = ele[i].split('-')
            print '----id--',element[0]
            print '------',element[1]
            supplier_obj = Supplier.objects.get(supplier_id=element[0])
            enquiry_service_name = element[1]
            print '---enquiry_service_name----',enquiry_service_name
            if enquiry_service_name == 'Platinum':
                es_name = 'P'
                n='1'
            elif enquiry_service_name == 'Diamond':
                es_name = 'D'
                n='2'
            elif enquiry_service_name == 'Gold':
                es_name = 'G'
                n='3'
            elif enquiry_service_name == 'Silver':
                es_name = 'S'
                n='4'
            elif enquiry_service_name == 'Bronze':
                es_name = 'B'
                n='5'
            elif enquiry_service_name == 'Value':
                es_name = 'V'
                n='6'

            supplier_id = str(supplier_obj.supplier_id)
            business_name = supplier_obj.business_name
            email = supplier_obj.supplier_email
            phone = supplier_obj.phone_no
            address = supplier_obj.address1+ ' ' +supplier_obj.address2 +','+str(supplier_obj.city_place_id.city_id)+'-'+supplier_obj.pincode.pincode
            t = datetime.now()
            list1={'n':n,'es_name':es_name,'enquiry_service_name':enquiry_service_name,'supplier_id':supplier_id,'bname':business_name,'email':email,'phone':phone,'address':str(address),'time':t,
                   'searchfor':searchfor,'area':area,'cid':cid,'c_number':c_number,'c_name':c_name,'c_email':c_email}
            print '--------list1--------',list1
            slist.append(list1)
            data = {'success':'true'}
        #slist.sort(n)
        newlist = sorted(slist, key=itemgetter('n'))
        print '----------sorted list-----',newlist
        print '-------slist------',slist
        send_to_subscriber.delay(newlist)

    except Exception as e:
        print e
        data = {'success':'false'}

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def save_enquiry_details(cid,city,searchfor,area):
    try:
        print '----------in save enquiry------',cid,city,searchfor,area
        cobj = CallerDetails.objects.get(CallerID=cid)
        enq_obj = EnquiryDetails(
            CallerID = cobj,
            enquiryFor=searchfor,
            SelectedArea = area,
            created_date = datetime.now()
        );
        enq_obj.save()
        data = {'success':'true'}
    except Exception as e:
        print e
        data = {'success':'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def search_details(request):
    print '------------in search----------',request.POST.get('keyword')
    data = {}
    n=0
    try:
        if request.method == "POST":
            if request.POST.get('keyword'):
                text = request.POST.get('keyword')
                area = request.POST.get('area')

                try :
                    print '---------in try-----'
                    if request.POST.get('city') == 'all' and request.POST.get('category')=='all':
                        print '------------in both------'
                        if Supplier.objects.filter(business_name__icontains=text):
                            print '---------if 5-1-----'
                            sobj = Supplier.objects.filter(business_name__icontains=text,supplier_status=1)
                            category_obj = b_search4(sobj)
                            if category_obj:
                                print '---------len-----',len(category_obj)
                                data = {'result_list':category_obj,'success':'true'}
                            else :
                                data = {'success':'false'}
                        elif Advert.objects.filter(keywords__icontains=text):
                            a = Advert.objects.filter(keywords__icontains=text)
                            category_obj = keyword_search(a)
                            if category_obj:
                                print '---------len-----',len(category_obj)
                                data = {'result_list':category_obj,'success':'true'}
                            else :
                                data = {'success':'false'}

                    elif request.POST.get('city') == 'all':
                        print '---------city------',request.POST.get('city')
                        category = request.POST.get('category')
                        if Supplier.objects.filter(business_name__icontains=text):
                            print '---------if 4- 1----'
                            sobj = Supplier.objects.filter(business_name__icontains=text,supplier_status=1)
                            category_obj = b_search1(sobj,category)
                            if category_obj:
                                print '---------len-----',len(category_obj)
                                data = {'result_list':category_obj,'success':'true'}
                            else :
                                data = {'success':'false'}
                        elif Advert.objects.filter(keywords__icontains=text,category_id=category):
                            print '---------if 4-2-----'
                            a = Advert.objects.filter(keywords__icontains=text,category_id=category)
                            category_obj = keyword_search(a)
                            if category_obj:
                                print '---------len-----',len(category_obj)
                                data = {'result_list':category_obj,'success':'true'}
                            else :
                                data = {'success':'false'}

                    elif request.POST.get('category')=='all':
                        print '-----------category------',request.POST.get('category')
                        print '---------if 5-----'
                        city_place = City_Place.objects.get(city_id=request.POST.get('city'))
                        if Supplier.objects.filter(business_name__icontains=text):
                            print '---------if 5-1-----'
                            sobj = Supplier.objects.filter(business_name__icontains=text,supplier_status=1)
                            category_obj = b_search3(sobj,city_place,area)
                            if category_obj:
                                print '---------len-----',len(category_obj)
                                data = {'result_list':category_obj,'success':'true'}
                            else :
                                data = {'success':'false'}
                        elif Advert.objects.filter(keywords__icontains=text,city_place_id=city_place):
                            print '---------if 5-2-----'
                            a = Advert.objects.filter(keywords__icontains=text,city_place_id=city_place,area__icontains=area)
                            category_obj = keyword_search(a)
                            if category_obj:
                                print '---------len-----',len(category_obj)
                                data = {'result_list':category_obj,'success':'true'}
                            else :
                                data = {'success':'false'}

                    else:
                        city_place = City_Place.objects.get(city_id=request.POST.get('city'))
                        print '----city place------',city_place
                        category = request.POST.get('category')
                        if Advert.objects.filter(keywords__icontains=text,city_place_id=city_place,area__icontains=area,category_id=category):
                            print '---------if 1-----'
                            a = Advert.objects.filter(keywords__icontains=text,city_place_id=city_place,area__icontains=area,category_id=category)
                            category_obj = keyword_search(a)
                            if category_obj:
                                print '---------len-----',len(category_obj)
                                data = {'result_list':category_obj,'success':'true'}
                            else :
                                data = {'success':'false'}

                        elif Advert.objects.filter(keywords__icontains=text,city_place_id=city_place,area__icontains=area):
                            print '---------if 2-----'
                            a = Advert.objects.filter(keywords__icontains=text,city_place_id=city_place,area__icontains=area)
                            category_obj = keyword_search(a)
                            if category_obj:
                                print '---------len-----',len(category_obj)
                                data = {'result_list':category_obj,'success':'true'}
                            else :
                                data = {'success':'false'}

                        elif Supplier.objects.filter(business_name__icontains=text):
                            print '---------if 3-----'
                            sobj = Supplier.objects.filter(business_name__icontains=text,supplier_status=1)
                            category_obj = b_search(sobj,area,city_place,category)
                            if category_obj:
                                print '---------len-----',len(category_obj)
                                data = {'result_list':category_obj,'success':'true'}
                            else :
                                data = {'success':'false'}

                except Exception,e:
                    print e
                    data = {'success':'false'}
            else:
                data = {'message': "No Result Found", 'success':'false'}

    except Exception as e:
        print e
        data = {'success':'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')

# def demo(a):
#     print '----------- in demo ---------',a
#     category_obj=[]
#
#     for b in a:
#         print '----------cat obj---',b
#
#         adv_obj = AdvertSubscriptionMap.objects.get(advert_id=b)
#         print '------------adv_obj------',adv_obj
#         business_obj = adv_obj.business_id
#         print '------------business_obj 1------',business_obj
#         if EnquiryService.objects.get(business_id = business_obj):
#             print '------------in if---------'
#             Enquiry_obj = EnquiryService.objects.get(business_id = business_obj)
#             print '------------Enquiry_obj 1------',Enquiry_obj
#             enquiry_service_name = Enquiry_obj.enquiry_service_name
#             print '------------enquiry_service_name 1------',enquiry_service_name
#             b_obj = Enquiry_obj.business_id
#             print '------------b_obj 1------',b_obj
#
#             Business_obj = Business.objects.get(business_id = str(b_obj))
#             print '------------Business_obj 1------',Business_obj
#             supplier_obj = Business_obj.supplier
#             print '------------supplier_obj 1------',supplier_obj
#
#             supplier_id = Supplier.objects.get(supplier_id=str(supplier_obj),supplier_status=1)
#             print '------------supplier_id 1------',supplier_id
#
#             advert_obj = Advert.objects.get(supplier_id=str(supplier_id))
#             print '------------advert_obj 1------',advert_obj
#             category_obj1 = advert_obj.category_id.category_name
#
#             print '------------cat 1------',category_obj1
#             if advert_obj.category_level_1:
#                 subcat1_name = advert_obj.category_level_1.category_name
#                 print '------------sub cat 1------',subcat1_name
#             else:
#                 subcat1_name = ''
#             if advert_obj.category_level_2:
#                 subcat2_name = advert_obj.category_level_2.category_name
#                 print '-----------sub-cat 2------',subcat2_name
#             else:
#                 subcat2_name = ''
#
#             category = str(category_obj1)+'>'+str(subcat1_name)+'>' +str(subcat2_name)
#             business_name = supplier_id.business_name
#             print '---city---',supplier_id.city_place_id.city_id
#             address = str(supplier_id.address1)+' '+str(supplier_id.address2)+','+str(supplier_id.city_place_id.city_id)+'-'+str(supplier_id.pincode)
#             cat_obj = {'supplier_id':supplier_id.supplier_id,'enquiry_service_name':enquiry_service_name,'business_name':business_name,'category':category,'address':address}
#             category_obj.append(cat_obj)
#     return category_obj


def keyword_search(a):
    print '----------- in demo ---------',a
    category_obj=[]
    for b in a:
        print '----------cat obj---',b
        adv_obj = AdvertSubscriptionMap.objects.get(advert_id=b)
        print '-----------adv obj-------',adv_obj
        business_obj = adv_obj.business_id
        print '-------business obj-------',business_obj
        if EnquiryService.objects.get(business_id = business_obj):
            Enquiry_obj = EnquiryService.objects.get(business_id = business_obj)
            enquiry_service_name = Enquiry_obj.enquiry_service_name
            # b_obj = Enquiry_obj.business_id
            # print '--------b obj-----',b_obj
            # Business_obj = Business.objects.get(business_id = str(b_obj))
            # print '---------business obj-------',Business_obj
            # supplier_obj = Business_obj.supplier
            supplier_obj = b.supplier_id
            supplier_id = Supplier.objects.get(supplier_id=str(supplier_obj),supplier_status=1)

            category_obj1 = b.category_id.category_name
            if b.category_level_1:
                subcat1_name = b.category_level_1.category_name
            else:
                subcat1_name = ''
            if b.category_level_2:
                subcat2_name = b.category_level_2.category_name
            else:
                subcat2_name = ''

            category = str(category_obj1)+'>'+str(subcat1_name)+'>' +str(subcat2_name)
            business_name = supplier_id.business_name
            address = str(supplier_id.address1)+' '+str(supplier_id.address2)+','+str(supplier_id.city_place_id.city_id)+'-'+str(supplier_id.pincode)
            cat_obj = {'supplier_id':supplier_id.supplier_id,'enquiry_service_name':enquiry_service_name,'business_name':business_name,'category':category,'address':address}
            category_obj.append(cat_obj)
    category_obj = category_obj[:20]
    return category_obj

# def keyword_search(a):
#     print '----------- 1 ---------',a
#     category_obj=[]
#
#     for b in a:
#         print '----------cat obj---',b
#         supplier_obj = Supplier.objects.get(supplier_id__icontains=b.supplier_id,supplier_status=1)
#         print '-----------supplier obj------',supplier_obj
#         category_obj1 = b.category_id.category_name
#         print '------------cat 1------',category_obj1
#         if b.category_level_1:
#             subcat1_name = b.category_level_1.category_name
#             print '------------sub cat 1------',subcat1_name
#         else:
#             subcat1_name = ''
#         if b.category_level_2:
#             subcat2_name = b.category_level_2.category_name
#             print '-----------sub-cat 2------',subcat2_name
#         else:
#             subcat2_name = ''
#
#         category = str(category_obj1)+'>'+str(subcat1_name)+'>' +str(subcat2_name)
#         business_name = supplier_obj.business_name
#         print '---city---',supplier_obj.city_place_id.city_id
#         address = str(supplier_obj.address1)+' '+str(supplier_obj.address2)+','+str(supplier_obj.city_place_id.city_id)+'-'+str(supplier_obj.pincode)
#         cat_obj = {'supplier_id':supplier_obj.supplier_id,'business_name':business_name,'category':category,'address':address}
#         category_obj.append(cat_obj)
#     category_obj = category_obj[:10]
#     return category_obj


def b_search4(sobj):
    print '----------- b search ---------',sobj
    category_obj=[]
    for b in sobj:
        print '----------cat obj---',b
        a = Advert.objects.filter(supplier_id=b)
        print '-----------supplier obj------',a
        for i in a:
            adv_obj = AdvertSubscriptionMap.objects.get(advert_id=i)
            business_obj = adv_obj.business_id
            if EnquiryService.objects.get(business_id = business_obj):

                Enquiry_obj = EnquiryService.objects.get(business_id = business_obj)
                enquiry_service_name = Enquiry_obj.enquiry_service_name
                # b_obj = Enquiry_obj.business_id
                # Business_obj = Business.objects.get(business_id = str(b_obj))
                # supplier_obj = Business_obj.supplier
                supplier_obj = i.supplier_id
                supplier_id = Supplier.objects.get(supplier_id=str(supplier_obj),supplier_status=1)

                category_obj1 = i.category_id.category_name
                if i.category_level_1:
                    subcat1_name = i.category_level_1.category_name
                else:
                    subcat1_name = ''
                if i.category_level_2:
                    subcat2_name = i.category_level_2.category_name
                else:
                    subcat2_name = ''

                category = str(category_obj1)+'>'+str(subcat1_name)+'>' +str(subcat2_name)
                business_name = supplier_id.business_name
                address = str(supplier_id.address1)+' '+str(supplier_id.address2)+','+str(supplier_id.city_place_id.city_id)+'-'+str(supplier_id.pincode)
                cat_obj = {'supplier_id':supplier_id.supplier_id,'enquiry_service_name':enquiry_service_name,'business_name':business_name,'category':category,'address':address}
                category_obj.append(cat_obj)
        category_obj = category_obj[:20]
    return category_obj


# def b_search4(sobj):
#     print '----------- b search ---------',sobj
#     category_obj=[]
#     for b in sobj:
#         print '----------cat obj---',b
#         a = Advert.objects.filter(supplier_id=b)
#         print '-----------supplier obj------',a
#         for i in a:
#             category_obj1 = i.category_id.category_name
#             print '------------cat 1------',category_obj1
#             if i.category_level_1:
#                 subcat1_name = i.category_level_1.category_name
#                 print '------------sub cat 1------',subcat1_name
#             else:
#                 subcat1_name = ''
#             if i.category_level_2:
#                 subcat2_name = i.category_level_2.category_name
#                 print '-----------sub-cat 2------',subcat2_name
#             else:
#                 subcat2_name = ''
#
#             category = str(category_obj1)+'>'+str(subcat1_name)+'>' +str(subcat2_name)
#             business_name = b.business_name
#             address = str(b.address1)+' '+str(b.address2)+','+str(b.city_place_id.city_id)+'-'+str(b.pincode)
#             cat_obj = {'supplier_id':b.supplier_id,'business_name':business_name,'category':category,'address':address}
#             category_obj.append(cat_obj)
#         category_obj = category_obj[:10]
#     return category_obj

def b_search3(sobj,city_place,area):
    print '----------- b search ---------',sobj,city_place
    category_obj=[]
    for b in sobj:
        print '----------cat obj---',b
        a = Advert.objects.filter(supplier_id=b,city_place_id=city_place,area__icontains=area)
        print '-----------supplier obj------',a
        for i in a:
            adv_obj = AdvertSubscriptionMap.objects.get(advert_id=i)
            business_obj = adv_obj.business_id
            if EnquiryService.objects.get(business_id = business_obj):
                Enquiry_obj = EnquiryService.objects.get(business_id = business_obj)
                enquiry_service_name = Enquiry_obj.enquiry_service_name
                # b_obj = Enquiry_obj.business_id
                # Business_obj = Business.objects.get(business_id = str(b_obj))
                supplier_obj = i.supplier
                supplier_id = Supplier.objects.get(supplier_id=str(supplier_obj),supplier_status=1)
                #advert_obj = Advert.objects.get(supplier_id=str(supplier_id))
                category_obj1 = i.category_id.category_name
                if i.category_level_1:
                    subcat1_name = i.category_level_1.category_name
                else:
                    subcat1_name = ''
                if i.category_level_2:
                    subcat2_name = i.category_level_2.category_name
                else:
                    subcat2_name = ''

                category = str(category_obj1)+'>'+str(subcat1_name)+'>' +str(subcat2_name)
                business_name = supplier_id.business_name
                address = str(supplier_id.address1)+' '+str(supplier_id.address2)+','+str(supplier_id.city_place_id.city_id)+'-'+str(supplier_id.pincode)
                cat_obj = {'supplier_id':supplier_id.supplier_id,'enquiry_service_name':enquiry_service_name,'business_name':business_name,'category':category,'address':address}
                category_obj.append(cat_obj)
        category_obj = category_obj[:20]
    return category_obj



# def b_search3(sobj,city_place,area):
#     print '----------- b search ---------',sobj,city_place
#     category_obj=[]
#     for b in sobj:
#         print '----------cat obj---',b
#         a = Advert.objects.filter(supplier_id=b,city_place_id=city_place,area__icontains=area)
#         print '-----------supplier obj------',a
#         for i in a:
#             category_obj1 = i.category_id.category_name
#             print '------------cat 1------',category_obj1
#             if i.category_level_1:
#                 subcat1_name = i.category_level_1.category_name
#                 print '------------sub cat 1------',subcat1_name
#             else:
#                 subcat1_name = ''
#             if i.category_level_2:
#                 subcat2_name = i.category_level_2.category_name
#                 print '-----------sub-cat 2------',subcat2_name
#             else:
#                 subcat2_name = ''
#
#             category = str(category_obj1)+'>'+str(subcat1_name)+'>' +str(subcat2_name)
#             business_name = b.business_name
#             address = str(b.address1)+' '+str(b.address2)+','+str(b.city_place_id.city_id)+'-'+str(b.pincode)
#             cat_obj = {'supplier_id':b.supplier_id,'business_name':business_name,'category':category,'address':address}
#             category_obj.append(cat_obj)
#         category_obj = category_obj[:10]
#     return category_obj


# def b_search3(sobj,city_place,area):
#     print '----------- b search ---------',sobj,city_place
#     category_obj=[]
#     for b in sobj:
#         print '----------cat obj---',b
#         a = Advert.objects.filter(supplier_id=b,city_place_id=city_place,area__icontains=area)
#         print '-----------supplier obj------',a
#         for i in a:
#             category_obj1 = i.category_id.category_name
#             print '------------cat 1------',category_obj1
#             if i.category_level_1:
#                 subcat1_name = i.category_level_1.category_name
#                 print '------------sub cat 1------',subcat1_name
#             else:
#                 subcat1_name = ''
#             if i.category_level_2:
#                 subcat2_name = i.category_level_2.category_name
#                 print '-----------sub-cat 2------',subcat2_name
#             else:
#                 subcat2_name = ''
#
#             category = str(category_obj1)+'>'+str(subcat1_name)+'>' +str(subcat2_name)
#             business_name = b.business_name
#             address = str(b.address1)+' '+str(b.address2)+','+str(b.city_place_id.city_id)+'-'+str(b.pincode)
#             cat_obj = {'supplier_id':b.supplier_id,'business_name':business_name,'category':category,'address':address}
#             category_obj.append(cat_obj)
#         category_obj = category_obj[:10]
#     return category_obj


def b_search1(sobj,category):
    print '----------- b search ---------',sobj,category
    category_obj=[]
    for b in sobj:
        print '----------cat obj---',b
        a = Advert.objects.filter(supplier_id=b,category_id=category)
        print '-----------supplier obj------',a
        for i in a:
            adv_obj = AdvertSubscriptionMap.objects.get(advert_id=i)
            business_obj = adv_obj.business_id
            if EnquiryService.objects.get(business_id = business_obj):
                Enquiry_obj = EnquiryService.objects.get(business_id = business_obj)
                enquiry_service_name = Enquiry_obj.enquiry_service_name
                # b_obj = Enquiry_obj.business_id
                # Business_obj = Business.objects.get(business_id = str(b_obj))
                supplier_obj = i.supplier
                supplier_id = Supplier.objects.get(supplier_id=str(supplier_obj),supplier_status=1)
                #advert_obj = Advert.objects.get(supplier_id=str(supplier_id))
                category_obj1 = i.category_id.category_name
                if i.category_level_1:
                    subcat1_name = i.category_level_1.category_name
                else:
                    subcat1_name = ''
                if i.category_level_2:
                    subcat2_name = i.category_level_2.category_name
                else:
                    subcat2_name = ''

                category = str(category_obj1)+'>'+str(subcat1_name)+'>' +str(subcat2_name)
                business_name = supplier_id.business_name
                address = str(supplier_id.address1)+' '+str(supplier_id.address2)+','+str(supplier_id.city_place_id.city_id)+'-'+str(supplier_id.pincode)
                cat_obj = {'supplier_id':supplier_id.supplier_id,'enquiry_service_name':enquiry_service_name,'business_name':business_name,'category':category,'address':address}
                category_obj.append(cat_obj)
        category_obj = category_obj[:20]
    return category_obj

# def b_search1(sobj,category):
#     print '----------- b search ---------',sobj,category
#     category_obj=[]
#     for b in sobj:
#         print '----------cat obj---',b
#         a = Advert.objects.filter(supplier_id=b,category_id=category)
#         print '-----------supplier obj------',a
#         for i in a:
#             category_obj1 = i.category_id.category_name
#             print '------------cat 1------',category_obj1
#             if i.category_level_1:
#                 subcat1_name = i.category_level_1.category_name
#                 print '------------sub cat 1------',subcat1_name
#             else:
#                 subcat1_name = ''
#             if i.category_level_2:
#                 subcat2_name = i.category_level_2.category_name
#                 print '-----------sub-cat 2------',subcat2_name
#             else:
#                 subcat2_name = ''
#
#             category = str(category_obj1)+'>'+str(subcat1_name)+'>' +str(subcat2_name)
#             business_name = b.business_name
#             address = str(b.address1)+' '+str(b.address2)+','+str(b.city_place_id.city_id)+'-'+str(b.pincode)
#             cat_obj = {'supplier_id':b.supplier_id,'business_name':business_name,'category':category,'address':address}
#             category_obj.append(cat_obj)
#         category_obj = category_obj[:10]
#     return category_obj

def b_search(sobj,area,city_place,category):
    print '----------- b search ---------',sobj,area,city_place,category
    cat = category
    category_obj=[]
    for b in sobj:
        print '----------cat obj---',b , cat
        a = Advert.objects.filter(supplier_id=b,city_place_id=city_place,area__icontains=area,category_id=cat)
        print '-----------supplier obj------',a
        for i in a:
            adv_obj = AdvertSubscriptionMap.objects.get(advert_id=i)
            business_obj = adv_obj.business_id
            if EnquiryService.objects.get(business_id = business_obj):
                Enquiry_obj = EnquiryService.objects.get(business_id = business_obj)
                enquiry_service_name = Enquiry_obj.enquiry_service_name
                # b_obj = Enquiry_obj.business_id
                # Business_obj = Business.objects.get(business_id = str(b_obj))
                supplier_obj = i.supplier
                supplier_id = Supplier.objects.get(supplier_id=str(supplier_obj),supplier_status=1)
                #advert_obj = Advert.objects.get(supplier_id=str(supplier_id))
                category_obj1 = i.category_id.category_name
                if i.category_level_1:
                    subcat1_name = i.category_level_1.category_name
                else:
                    subcat1_name = ''
                if i.category_level_2:
                    subcat2_name = i.category_level_2.category_name
                else:
                    subcat2_name = ''

                category = str(category_obj1)+'>'+str(subcat1_name)+'>' +str(subcat2_name)
                business_name = supplier_id.business_name
                address = str(supplier_id.address1)+' '+str(supplier_id.address2)+','+str(supplier_id.city_place_id.city_id)+'-'+str(supplier_id.pincode)
                cat_obj = {'supplier_id':supplier_id.supplier_id,'enquiry_service_name':enquiry_service_name,'business_name':business_name,'category':category,'address':address}
                category_obj.append(cat_obj)
        category_obj = category_obj[:20]
    return category_obj


# def b_search(sobj,area,city_place,category):
#     print '----------- b search ---------',sobj,area,city_place,category
#     cat = category
#     category_obj=[]
#     for b in sobj:
#         print '----------cat obj---',b , cat
#         a = Advert.objects.filter(supplier_id=b,city_place_id=city_place,area__icontains=area,category_id=cat)
#         print '-----------supplier obj------',a
#         for i in a:
#             category_obj1 = i.category_id.category_name
#             print '------------cat 1------',category_obj1
#             if i.category_level_1:
#                 subcat1_name = i.category_level_1.category_name
#                 print '------------sub cat 1------',subcat1_name
#             else:
#                 subcat1_name = ''
#             if i.category_level_2:
#                 subcat2_name = i.category_level_2.category_name
#                 print '-----------sub-cat 2------',subcat2_name
#             else:
#                 subcat2_name = ''
#
#             category = str(category_obj1)+'>'+str(subcat1_name)+'>' +str(subcat2_name)
#             business_name = b.business_name
#             address = str(b.address1)+' '+str(b.address2)+','+str(b.city_place_id.city_id)+'-'+str(b.pincode)
#             cat_obj = {'supplier_id':b.supplier_id,'business_name':business_name,'category':category,'address':address}
#             category_obj.append(cat_obj)
#         category_obj = category_obj[:10]
#     return category_obj



#========================================================================================================================


