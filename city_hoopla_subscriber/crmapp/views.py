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


#from DigiSpace.tasks import print_some_times
#SERVER_URL = "http://52.40.205.128"
SERVER_URL = "http://52.66.169.65"
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
            telno = user_obj.TelNo
            first_name = user_obj.first_name
            last_name = user_obj.last_name
            email = user_obj.email
            if user_obj.CallerArea=='':
                CallerArea = ''
            else:
                CallerArea = user_obj.CallerArea
            CallerCity = user_obj.CallerCity
            if user_obj.CallerPincode ==None:
                CallerPincode = ''
            else:
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
            category_list = Category.objects.all().order_by('category_name')

            data = {'telno':telno,'city_list':city_list,'category_list':category_list,'detail_list':detail_list,'caller_id':caller_id,'phone_number':phone_number,'email':email,'first_name':first_name,'last_name':last_name,'area':CallerArea,'city':CallerCity,'pincode':CallerPincode,
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
            telno = user_obj.TelNo
            first_name = user_obj.first_name
            last_name = user_obj.last_name
            email = user_obj.email
            #CallerArea = user_obj.CallerArea
            if user_obj.CallerArea=='':
                CallerArea = ''
            else:
                CallerArea = user_obj.CallerArea
            CallerCity = user_obj.CallerCity
            #CallerPincode = user_obj.CallerPincode
            if user_obj.CallerPincode ==None:
                CallerPincode = ''
            else:
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
            category_list = Category.objects.all().order_by('category_name')

            data = {'telno':telno,'city_list':city_list,'category_list':category_list,'detail_list':detail_list,'caller_id':caller_id,'phone_number':phone_number,'email':email,'first_name':first_name,'last_name':last_name,'area':CallerArea,'city':CallerCity,'pincode':CallerPincode,
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
    try:
        id = Pincode.objects.get(pincode=request.POST.get('pincode'))
    except:
        id=''
        pass
    try:
        city = City.objects.get(city_id=request.POST.get('city'))
        print '-------------city------',city
    except:
        city=''
        pass
    try:
        mobile_obj = CallerDetails.objects.get(IncomingTelNo=request.POST.get('mobile1'))
        data = {'success': 'exists','number':str(request.POST.get('mobile1'))}
        return HttpResponse(json.dumps(data), content_type='application/json')
    except:
        #pass
        try:
            caller_obj = CallerDetails(
                first_name=request.POST.get('fname'),
                last_name=request.POST.get('lname'),
                IncomingTelNo=request.POST.get('mobile1'),
                TelNo=request.POST.get('mobile'),
                email=request.POST.get('email'),
                CallerCity = City.objects.get(city_id=request.POST.get('city')),
                #CallerPincode = id,
                CallerArea=request.POST.get('area'),
                caller_created_date=datetime.now()
            )
            caller_obj.save()
            if id:
                caller_obj.CallerPincode=id
                caller_obj.save()
            if city:
                caller_obj.CallerCity=city
                caller_obj.save()
            print '--------caller id------',caller_obj.IncomingTelNo
            data = {'success': 'true','number1':str(caller_obj.IncomingTelNo)}

        except Exception, e:
            print 'Exception ', e
            data = {'success': 'false'}
        return HttpResponse(json.dumps(data), content_type='application/json')

def get_category_l1(request):
    data={}
    category_list = []
    cat_list = []
    try:
        cat_id = request.GET.get('category')
        print '----------category list-----',cat_id
        if cat_id == 'all':
            print '------in the if-------'
            data = {'success': 'false'}
            return HttpResponse(json.dumps(data), content_type='application/json')
        else:
            cat_obj = CategoryLevel1.objects.filter(parent_category_id=cat_id).order_by('category_name')
        print '----------category level list-----',cat_obj
        if cat_obj:
            for cat in cat_obj:
                options_data = '<option value=' + str(cat.category_id) + '>' + cat.category_name + '</option>'
                cat_list.append(options_data)
            data = {'category_list1': cat_list}
        else:
            data = {'success': 'false'}
            return HttpResponse(json.dumps(data), content_type='application/json')
    except Exception, ke:
        print ke
        data = {'category_list1': 'none', 'message': 'No Category Available'}
    return HttpResponse(json.dumps(data), content_type='application/json')

def get_category_l2(request):
    data={}
    category_list = []
    cat_list = []
    try:
        cat_id = request.GET.get('category')
        print '----------category list-----',cat_id
        cat_obj = CategoryLevel2.objects.filter(parent_category_id=cat_id).order_by('category_name')
        print '----------category level list-----',cat_obj
        if cat_obj:
            for cat in cat_obj:
                options_data = '<option value=' + str(cat.category_id) + '>' + cat.category_name + '</option>'
                cat_list.append(options_data)
            data = {'category_list2': cat_list}
        else:
            data = {'success': 'false'}
            return HttpResponse(json.dumps(data), content_type='application/json')
    except Exception, ke:
        print ke
        data = {'category_list2': 'none', 'message': 'No Category Available'}
    return HttpResponse(json.dumps(data), content_type='application/json')

# @csrf_exempt
# def check_category(request):
#     # pdb.set_trace()
#     print request.POST
#     try:
#         if request.POST.get('cat_level') == '1':
#             cat_obj = CategoryLevel1.objects.filter(parent_category_id=request.POST.get('category_id'))
#         if request.POST.get('cat_level') == '2':
#             cat_obj = CategoryLevel2.objects.filter(parent_category_id=request.POST.get('category_id'))
#         if request.POST.get('cat_level') == '3':
#             cat_obj = CategoryLevel3.objects.filter(parent_category_id=request.POST.get('category_id'))
#         if request.POST.get('cat_level') == '4':
#             cat_obj = CategoryLevel4.objects.filter(parent_category_id=request.POST.get('category_id'))
#         if request.POST.get('cat_level') == '5':
#             cat_obj = CategoryLevel5.objects.filter(parent_category_id=request.POST.get('category_id'))
#         print cat_obj
#         cat_list = []
#         if cat_obj:
#             for cat in cat_obj:
#                 options_data = '<option value=' + str(cat.category_id) + '>' + cat.category_name + '</option>'
#                 cat_list.append(options_data)
#             data = {'category_list': cat_list}
#         else:
#             data = {'success': 'false'}
#         print data
#     except Exception, e:
#         print e
#     return HttpResponse(json.dumps(data), content_type='application/json')



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

# @csrf_exempt
# def send_subscriber_details(request):
#     i=0
#     slist=[]
#     list1=[]
#     list=[]
#     print '------------send data----------',request.POST.get('subscriber_id')
#     print '------------sms data----------',request.POST.get('sms')
#     print '------------email data----------',request.POST.get('email')
#     try:
#         list = request.POST.get('subscriber_id')
#         searchfor = request.POST.get('searchfor')
#         area = request.POST.get('area')
#         city = request.POST.get('city')
#         cid = request.POST.get('cid')
#         cobj = CallerDetails.objects.get(CallerID=cid)
#         c_number = cobj.IncomingTelNo
#         c_name = cobj.first_name
#         c_email = cobj.email
#         ele = list.split(',')
#         for i in range(len(ele)):
#             print ele[i]
#             supplier_obj = Supplier.objects.get(supplier_id=ele[i])
#             supplier_id = str(supplier_obj.supplier_id)
#             business_name = supplier_obj.business_name
#             email = supplier_obj.supplier_email
#             phone = supplier_obj.phone_no
#             address = supplier_obj.address1+ ' ' +supplier_obj.address2 +','+str(supplier_obj.city_place_id.city_id)+'-'+supplier_obj.pincode.pincode
#             t = datetime.now()
#             list1={'supplier_id':supplier_id,'bname':business_name,'email':email,'phone':phone,'address':str(address),'time':t,
#                    'searchfor':searchfor,'area':area,'cid':cid,'c_number':c_number,'c_name':c_name,'c_email':c_email}
#             slist.append(list1)
#             data = {'success':'true'}
#         save_enquiry_details(cid,city,searchfor,area)
#
#         if request.POST.get('sms'):
#             print '--------in the sms=-------'
#             send_sms_to_consumer.delay(slist,c_number)
#
#         if request.POST.get('email'):
#             print '--------in email------'
#             send_email_to_consumer.delay(slist,c_email)
#
#         send_consumer_details(list,searchfor,area,cid)
#
#     except Exception as e:
#         print e
#         data = {'success':'false'}
#
#     return HttpResponse(json.dumps(data), content_type='application/json')

# @csrf_exempt
# def send_consumer_details(list,searchfor,area,cid):
#     print '------------in consumer details----------',list,searchfor,area,cid
#     i=0
#     slist=[]
#     list1=[]
#     try:
#         cobj = CallerDetails.objects.get(CallerID=cid)
#         c_number = cobj.IncomingTelNo
#         c_name = cobj.first_name
#         c_email = cobj.email
#         print '--------list----',list
#         ele = list.split(',')
#         for i in range(len(ele)):
#             print '-----i---',ele[i]
#             supplier_obj = Supplier.objects.get(supplier_id=ele[i])
#             supplier_id = str(supplier_obj.supplier_id)
#             business_name = supplier_obj.business_name
#             email = supplier_obj.supplier_email
#             phone = supplier_obj.phone_no
#             address = supplier_obj.address1+ ' ' +supplier_obj.address2 +','+str(supplier_obj.city_place_id.city_id)+'-'+supplier_obj.pincode.pincode
#             t = datetime.now()
#             list1={'supplier_id':supplier_id,'bname':business_name,'email':email,'phone':phone,'address':str(address),'time':t,
#                    'searchfor':searchfor,'area':area,'cid':cid,'c_number':c_number,'c_name':c_name,'c_email':c_email}
#             slist.append(list1)
#             data = {'success':'true'}
#         send_to_subscriber.delay(slist)
#
#     except Exception as e:
#         print e
#         data = {'success':'false'}
#
#     return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def send_subscriber_details(request):
    i=0
    slist=[]
    list1=[]
    list=[]
    print '------------send data----------',request.POST.get('subscriber_id')
    print '------------sms data----------',request.POST.get('sms')
    print '------------email data----------',request.POST.get('email')
    try:
        list = request.POST.get('subscriber_id')
        #list = list1[:10]
        searchfor = request.POST.get('searchfor')
        area = request.POST.get('area')
        city = request.POST.get('city')
        cid = request.POST.get('cid')
        cobj = CallerDetails.objects.get(CallerID=cid)
        #c_number = cobj.IncomingTelNo
        c_number = cobj.TelNo
        c_name = cobj.first_name +' '+cobj.last_name
        c_email = cobj.email
        ele = list.split(',')
        for i in range(len(ele)):
            print ele[i]
            print '-----i---',ele[i]
            element = ele[i].split('-')
            print '----id--',element[0]
            print '------',element[1]
            #adv_obj = Advert.objects.get(supplier_id=element[0])
            adv_obj = Advert.objects.get(advert_id = element[0])
            supplier_id = str(adv_obj.supplier_id)
            advert_name = adv_obj.advert_name
            email = adv_obj.email_primary
            phone = adv_obj.contact_no
            city = adv_obj.city_place_id.city_id.city_name
            address = adv_obj.address_line_1+ ' ' +adv_obj.address_line_2 +','+str(adv_obj.city_place_id.city_id)+'-'+adv_obj.pincode_id.pincode
            t = datetime.now()
            list1={'supplier_id':supplier_id,'bname':advert_name,'email':email,'phone':phone,'address':str(address),'time':t,
                   'searchfor':searchfor,'city':city,'area':area,'cid':cid,'c_number':c_number,'c_name':c_name,'c_email':c_email}
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

# @csrf_exempt
# def send_consumer_details(list,searchfor,area,cid):
#     print '------------in consumer details----------',list,searchfor,area,cid
#     i=0
#     slist=[]
#     list1=[]
#     try:
#         cobj = CallerDetails.objects.get(CallerID=cid)
#         c_number = cobj.IncomingTelNo
#         c_name = cobj.first_name
#         c_email = cobj.email
#         print '--------list----',list
#         ele = list.split(',')
#         for i in range(len(ele)):
#             print '-----i---',ele[i]
#             adv_obj = Advert.objects.get(supplier_id=ele[i])
#             supplier_id = str(adv_obj.supplier_id)
#             advert_name = adv_obj.advert_name
#             email = adv_obj.email_primary
#             phone = adv_obj.contact_no
#             address = adv_obj.address_line_1+ ' ' +adv_obj.address_line_2 +','+str(adv_obj.city_place_id.city_id)+'-'+adv_obj.pincode_id.pincode
#             t = datetime.now()
#             list1={'supplier_id':supplier_id,'bname':advert_name,'email':email,'phone':phone,'address':str(address),'time':t,
#                    'searchfor':searchfor,'area':area,'cid':cid,'c_number':c_number,'c_name':c_name,'c_email':c_email}
#             slist.append(list1)
#             data = {'success':'true'}
#         send_to_subscriber.delay(slist)
#
#     except Exception as e:
#         print e
#         data = {'success':'false'}
#
#     return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def send_consumer_details(list,searchfor,area,cid):
    print '------------in consumer details----------',list,searchfor,area,cid
    i=0
    j=0
    b=0
    v=0
    n=''
    ns=0
    es_name=''
    slist=[]
    list1=[]
    try:
        cobj = CallerDetails.objects.get(CallerID=cid)
        #c_number = cobj.IncomingTelNo
        c_number = cobj.TelNo
        c_name = cobj.first_name +" "+cobj.last_name
        c_email = cobj.email
        print '--------list----',list
        ele = list.split(',')
        for i in range(len(ele)):
            print '-----i---',ele[i]
            element = ele[i].split('-')
            print '----id--',element[0]
            print '------',element[1]
            print '---------enquiry service --------------',element[2]
            if element[2] == 'yes':
                asdasd = AdvertSubscriptionMap.objects.get(advert_id = element[0])
                print '---------------',asdasd
                adv_obj = Advert.objects.get(advert_id = element[0])
                supplier_id = str(adv_obj.supplier_id)
                advert_name = adv_obj.advert_name
                email = adv_obj.email_primary
                phone = adv_obj.contact_no
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
                    j=j+1
                    if j==1:
                        es_name = 'S1'
                        n='4'
                    if j==2:
                        es_name = 'S2'
                        n='5'
                    if j>=3:
                        pass
                elif enquiry_service_name == 'Bronze':
                    b=b+1
                    if b==1:
                        es_name = 'B1'
                        n='6'
                    if b==2:
                        es_name = 'B2'
                        n='7'
                    if b==3:
                        es_name = 'B3'
                        n='8'
                    if b>=4:
                        pass
                elif enquiry_service_name == 'Value':
                    v=v+1
                    if v==1:
                        es_name = 'V1'
                        n='9'
                    if v==2:
                        es_name = 'V2'
                        n='10'
                    if v>=3:
                        pass


                address = adv_obj.address_line_1+ ' ' +adv_obj.address_line_2 +','+str(adv_obj.city_place_id.city_id)+'-'+adv_obj.pincode_id.pincode
                t = datetime.now()
                list1={'sequence_number':int(n),'es_name':es_name,'enquiry_service_name':enquiry_service_name,'supplier_id':supplier_id,'bname':advert_name,'email':email,'phone':phone,'address':str(address),'time':t,
                       'searchfor':searchfor,'area':area,'cid':cid,'c_number':c_number,'c_name':c_name,'c_email':c_email}
                print '--------list1--------',list1
                slist.append(list1)
                data = {'success':'true'}
            else:
                pass
        #slist.sort(n)
        newlist = sorted(slist, key=itemgetter('sequence_number'))
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
                            print '---------in else if 5-1-----'
                            a = Advert.objects.filter(keywords__icontains=text)
                            print '-----------a-----------------',a
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


def keyword_search(a):
    print '----------- 1 ---------',a
    category_obj=[]

    for b in a:
        print '----------cat obj---',b
        supplier_obj = Supplier.objects.get(supplier_id__icontains=b.supplier_id,supplier_status=1)
        print '-----------supplier obj------',supplier_obj
        category_obj1 = b.category_id.category_name
        print '------------cat 1------',category_obj1
        if b.category_level_1:
            subcat1_name = b.category_level_1.category_name
            print '------------sub cat 1------',subcat1_name
        else:
            subcat1_name = ''
        if b.category_level_2:
            subcat2_name = b.category_level_2.category_name
            print '-----------sub-cat 2------',subcat2_name
        else:
            subcat2_name = ''

        category = str(category_obj1)+'>'+str(subcat1_name)+'>' +str(subcat2_name)
        business_name = supplier_obj.business_name
        print '---city---',supplier_obj.city_place_id.city_id
        address = str(supplier_obj.address1)+' '+str(supplier_obj.address2)+','+str(supplier_obj.city_place_id.city_id)+'-'+str(supplier_obj.pincode)
        cat_obj = {'supplier_id':supplier_obj.supplier_id,'business_name':business_name,'category':category,'address':address}
        category_obj.append(cat_obj)
    category_obj = category_obj[:10]
    return category_obj


def b_search4(sobj):
    print '----------- b search ---------',sobj
    category_obj=[]
    for b in sobj:
        print '----------cat obj---',b
        a = Advert.objects.filter(supplier_id=b)
        print '-----------supplier obj------',a
        for i in a:
            category_obj1 = i.category_id.category_name
            print '------------cat 1------',category_obj1
            if i.category_level_1:
                subcat1_name = i.category_level_1.category_name
                print '------------sub cat 1------',subcat1_name
            else:
                subcat1_name = ''
            if i.category_level_2:
                subcat2_name = i.category_level_2.category_name
                print '-----------sub-cat 2------',subcat2_name
            else:
                subcat2_name = ''

            category = str(category_obj1)+'>'+str(subcat1_name)+'>' +str(subcat2_name)
            business_name = b.business_name
            address = str(b.address1)+' '+str(b.address2)+','+str(b.city_place_id.city_id)+'-'+str(b.pincode)
            cat_obj = {'supplier_id':b.supplier_id,'business_name':business_name,'category':category,'address':address}
            category_obj.append(cat_obj)
        category_obj = category_obj[:10]
    return category_obj


def b_search3(sobj,city_place,area):
    print '----------- b search ---------',sobj,city_place
    category_obj=[]
    for b in sobj:
        print '----------cat obj---',b
        a = Advert.objects.filter(supplier_id=b,city_place_id=city_place,area__icontains=area)
        print '-----------supplier obj------',a
        for i in a:
            category_obj1 = i.category_id.category_name
            print '------------cat 1------',category_obj1
            if i.category_level_1:
                subcat1_name = i.category_level_1.category_name
                print '------------sub cat 1------',subcat1_name
            else:
                subcat1_name = ''
            if i.category_level_2:
                subcat2_name = i.category_level_2.category_name
                print '-----------sub-cat 2------',subcat2_name
            else:
                subcat2_name = ''

            category = str(category_obj1)+'>'+str(subcat1_name)+'>' +str(subcat2_name)
            business_name = b.business_name
            address = str(b.address1)+' '+str(b.address2)+','+str(b.city_place_id.city_id)+'-'+str(b.pincode)
            cat_obj = {'supplier_id':b.supplier_id,'business_name':business_name,'category':category,'address':address}
            category_obj.append(cat_obj)
        category_obj = category_obj[:10]
    return category_obj


def b_search1(sobj,category):
    print '----------- b search ---------',sobj,category
    category_obj=[]
    for b in sobj:
        print '----------cat obj---',b
        a = Advert.objects.filter(supplier_id=b,category_id=category)
        print '-----------supplier obj------',a
        for i in a:
            category_obj1 = i.category_id.category_name
            print '------------cat 1------',category_obj1
            if i.category_level_1:
                subcat1_name = i.category_level_1.category_name
                print '------------sub cat 1------',subcat1_name
            else:
                subcat1_name = ''
            if i.category_level_2:
                subcat2_name = i.category_level_2.category_name
                print '-----------sub-cat 2------',subcat2_name
            else:
                subcat2_name = ''

            category = str(category_obj1)+'>'+str(subcat1_name)+'>' +str(subcat2_name)
            business_name = b.business_name
            address = str(b.address1)+' '+str(b.address2)+','+str(b.city_place_id.city_id)+'-'+str(b.pincode)
            cat_obj = {'supplier_id':b.supplier_id,'business_name':business_name,'category':category,'address':address}
            category_obj.append(cat_obj)
        category_obj = category_obj[:10]
    return category_obj


def b_search(sobj,area,city_place,category):
    print '----------- b search ---------',sobj,area,city_place,category
    cat = category
    category_obj=[]
    for b in sobj:
        print '----------cat obj---',b , cat
        a = Advert.objects.filter(supplier_id=b,city_place_id=city_place,area__icontains=area,category_id=cat)
        print '-----------supplier obj------',a
        for i in a:
            category_obj1 = i.category_id.category_name
            print '------------cat 1------',category_obj1
            if i.category_level_1:
                subcat1_name = i.category_level_1.category_name
                print '------------sub cat 1------',subcat1_name
            else:
                subcat1_name = ''
            if i.category_level_2:
                subcat2_name = i.category_level_2.category_name
                print '-----------sub-cat 2------',subcat2_name
            else:
                subcat2_name = ''

            category = str(category_obj1)+'>'+str(subcat1_name)+'>' +str(subcat2_name)
            business_name = b.business_name
            address = str(b.address1)+' '+str(b.address2)+','+str(b.city_place_id.city_id)+'-'+str(b.pincode)
            cat_obj = {'supplier_id':b.supplier_id,'business_name':business_name,'category':category,'address':address}
            category_obj.append(cat_obj)
        category_obj = category_obj[:10]
    return category_obj



#========================================================================================================================

# def b_searching4(sobj):
#     print '----------- b search ---------',sobj
#     category_obj=[]
#     for b in sobj:
#         print '----------cat obj---',b
#         a = Advert.objects.filter(supplier_id=b)
#         print '-----------supplier obj------',a
#         for i in a:
#             advert_name = i.advert_name
#             contact_no = b.contact_no
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
#             category = str(category_obj1)
#             business_name = b.business_name
#             address = str(i.address_line_1)+' '+str(i.address_line_2)+','+str(i.city_place_id.city_id)+'-'+str(i.pincode_id.pincode)
#             cat_obj = {'supplier_id':b.supplier_id,'contact_no':contact_no,'business_name':advert_name,'category':category,'address':address}
#             category_obj.append(cat_obj)
#         category_obj = category_obj[:10]
#     return category_obj
#
# def b_searching3(sobj,city_place,area):
#     print '----------- b search ---------',sobj,city_place
#     category_obj=[]
#     for b in sobj:
#
#         print '----------cat obj---',b
#         a = Advert.objects.filter(supplier_id=b,city_place_id=city_place,area__icontains=area)
#         print '-----------supplier obj------',a
#         for i in a:
#             advert_name = i.advert_name
#             contact_no = b.contact_no
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
#             category = str(category_obj1)
#             business_name = b.business_name
#             address = str(i.address_line_1)+' '+str(i.address_line_2)+','+str(i.city_place_id.city_id)+'-'+str(i.pincode_id.pincode)
#             cat_obj = {'supplier_id':b.supplier_id,'contact_no':contact_no,'business_name':advert_name,'category':category,'address':address}
#             category_obj.append(cat_obj)
#         category_obj = category_obj[:10]
#     return category_obj
#
#
# def b_searching1(sobj,category):
#     print '----------- b search ---------',sobj,category
#     category_obj=[]
#     for b in sobj:
#         print '----------cat obj---',b
#         a = Advert.objects.filter(supplier_id=b,category_id=category)
#         print '-----------supplier obj------',a
#         for i in a:
#             advert_name = i.advert_name
#             contact_no = b.contact_no
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
#             category = str(category_obj1)
#             business_name = b.business_name
#             address = str(i.address_line_1)+' '+str(i.address_line_2)+','+str(i.city_place_id.city_id)+'-'+str(i.pincode_id.pincode)
#             cat_obj = {'supplier_id':b.supplier_id,'contact_no':contact_no,'business_name':advert_name,'category':category,'address':address}
#             category_obj.append(cat_obj)
#         category_obj = category_obj[:10]
#     return category_obj
#
#
# def b_searching(sobj,area,city_place,category):
#     print '----------- b search ---------',sobj,area,city_place,category
#     cat = category
#     category_obj=[]
#     for b in sobj:
#         print '----------cat obj---',b , cat
#         a = Advert.objects.filter(supplier_id=b,city_place_id=city_place,area__icontains=area,category_id=cat)
#         print '-----------supplier obj------',a
#         for i in a:
#             advert_name = i.advert_name
#             contact_no = b.contact_no
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
#             category = str(category_obj1)
#             address = str(i.address_line_1)+' '+str(i.address_line_2)+','+str(i.city_place_id.city_id)+'-'+str(i.pincode_id.pincode)
#             cat_obj = {'supplier_id':b.supplier_id,'contact_no':contact_no,'business_name':advert_name,'category':category,'address':address}
#             category_obj.append(cat_obj)
#         category_obj = category_obj[:10]
#     return category_obj
#
#
# def keyword_searching(a):
#     print '----------- 1 ---keyword_searching------',a
#     category_obj=[]
#     for b in a:
#         print '----------cat obj---',b
#         advert_name = b.advert_name
#         print '----------advert_name--------',advert_name
#         contact_no = b.contact_no
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
#         print '------------cat 1------',category_obj1
#
#         category = str(category_obj1)
#         address = str(b.address_line_1)+' '+str(b.address_line_2)+','+str(b.city_place_id.city_id)+'-'+str(b.pincode_id.pincode)
#         cat_obj = {'supplier_id':str(b.supplier_id),'contact_no':contact_no,'business_name':advert_name,'category':category,'address':address}
#         category_obj.append(cat_obj)
#     category_obj = category_obj[:10]
#     print '-----------cat obj--------',category_obj
#     return category_obj

#-----------------------------------------------------------------------
@csrf_exempt
def searching_details(request):
    print '------------in searching details----------',request.POST.get('keyword')
    data = {}
    n=0
    sort_params = {}
    try:
        if request.method == "POST":
            if request.POST.get('keyword'):
                text = request.POST.get('keyword')
                area = request.POST.get('area')
                category = request.POST.get('category')
                city = request.POST.get('city')
                try :
                    if request.POST.get('city') == 'all' and request.POST.get('category')=='all':
                        print '------------in both------'
                        if Supplier.objects.filter(business_name__icontains=text):
                            print '---------if 5-1-----'
                            sobj = Supplier.objects.filter(business_name__icontains=text,supplier_status=1)
                            category_obj = b_searching4(sobj)
                            if category_obj:
                                print '---------len-----',len(category_obj)
                                data = {'result_list':category_obj,'success':'true'}
                            else :
                                data = {'success':'false'}

                        elif Advert.objects.filter(keywords__icontains=text):
                            a = Advert.objects.filter(keywords__icontains=text)
                            category_obj = keyword_searching(a)
                            if category_obj:
                                print '---------len-----',len(category_obj)
                                data = {'result_list':category_obj,'success':'true'}
                            else :
                                data = {'success':'false'}

                        elif Advert.objects.filter(advert_name__icontains=text):
                            a = Advert.objects.filter(advert_name__icontains=text)
                            category_obj = keyword_searching(a)
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
                            category_obj = b_searching1(sobj,category)
                            if category_obj:
                                print '---------len-----',len(category_obj)
                                data = {'result_list':category_obj,'success':'true'}
                            else :
                                data = {'success':'false'}
                        elif Advert.objects.filter(keywords__icontains=text,category_id=category):
                            print '---------if 4-2-----'
                            a = Advert.objects.filter(keywords__icontains=text,category_id=category)
                            category_obj = keyword_searching(a)
                            if category_obj:
                                print '---------len-----',len(category_obj)
                                data = {'result_list':category_obj,'success':'true'}
                            else :
                                data = {'success':'false'}

                        elif Advert.objects.filter(advert_name__icontains=text,category_id=category):
                            a = Advert.objects.filter(advert_name__icontains=text,category_id=category)
                            category_obj = keyword_searching(a)
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
                            category_obj = b_searching3(sobj,city_place,area)
                            if category_obj:
                                print '---------len-----',len(category_obj)
                                data = {'result_list':category_obj,'success':'true'}
                            else :
                                data = {'success':'false'}
                        elif Advert.objects.filter(keywords__icontains=text,city_place_id=city_place):
                            print '---------if 5-2-----'
                            a = Advert.objects.filter(keywords__icontains=text,city_place_id=city_place,area__icontains=area)
                            category_obj = keyword_searching(a)
                            if category_obj:
                                print '---------len-----',len(category_obj)
                                data = {'result_list':category_obj,'success':'true'}
                            else :
                                data = {'success':'false'}

                        elif Advert.objects.filter(advert_name__icontains=text,city_place_id=city_place,area__icontains=area):
                            a = Advert.objects.filter(advert_name__icontains=text,city_place_id=city_place,area__icontains=area)
                            category_obj = keyword_searching(a)
                            if category_obj:
                                print '---------len-----',len(category_obj)
                                data = {'result_list':category_obj,'success':'true'}
                            else :
                                data = {'success':'false'}

                    else:
                        city_place = City_Place.objects.get(city_id=request.POST.get('city'))
                        print '----city place------',city_place
                        category = request.POST.get('category')
                        print '-----------category-ewqeq------',category
                        if Advert.objects.filter(keywords__icontains=text,city_place_id=city_place,area__icontains=area,category_id=category):
                            print '---------if 1-----'
                            a = Advert.objects.filter(keywords__icontains=text,city_place_id=city_place,area__icontains=area,category_id=category)
                            category_obj = keyword_searching(a)
                            if category_obj:
                                print '---------len-----',len(category_obj)
                                data = {'result_list':category_obj,'success':'true'}
                            else :
                                data = {'success':'false'}

                        elif Advert.objects.filter(keywords__icontains=text,city_place_id=city_place,area__icontains=area,category_id=category):
                            print '---------if 2-----'
                            a = Advert.objects.filter(keywords__icontains=text,city_place_id=city_place,area__icontains=area,category_id=category)
                            category_obj = keyword_searching(a)
                            if category_obj:
                                print '---------len-----',len(category_obj)
                                data = {'result_list':category_obj,'success':'true'}
                            else :
                                data = {'success':'false'}

                        elif Supplier.objects.filter(business_name__icontains=text):
                            print '---------if 3-----'
                            sobj = Supplier.objects.filter(business_name__icontains=text,supplier_status=1)
                            category_obj = b_searching(sobj,area,city_place,category)
                            if category_obj:
                                print '---------len-----',len(category_obj)
                                data = {'result_list':category_obj,'success':'true'}
                            else :
                                data = {'success':'false'}

                        elif Advert.objects.filter(advert_name__icontains=text,city_place_id=city_place,area__icontains=area,category_id=category):
                            a = Advert.objects.filter(advert_name__icontains=text,city_place_id=city_place,area__icontains=area,category_id=category)
                            category_obj = keyword_searching(a)
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

#---------------------------------------------------------------------------------

def keyword_searching(a):
    print '----------- in demo ---------',a
    category_obj=[]
    for b in a:
        if AdvertSubscriptionMap.objects.get(advert_id=b):
            print '----------cat obj---',b
            adv_obj = AdvertSubscriptionMap.objects.get(advert_id=b)
            print '-----------adv obj-------',adv_obj
            business_obj = adv_obj.business_id
            print '-------business obj-------',business_obj
            #if EnquiryService.objects.get(business_id = business_obj):
            try:
                Enquiry_obj = EnquiryService.objects.get(business_id = business_obj)
                enquiry_service_name = Enquiry_obj.enquiry_service_name

                category_obj1 = b.category_id.category_name

                category = str(category_obj1)
                advert_name = b.advert_name
                contact_no = b.contact_no

                address = str(b.address_line_1)+' '+str(b.address_line_2)+','+str(b.city_place_id.city_id)+'-'+str(b.pincode_id.pincode)
                cat_obj = {'contact_no':contact_no,'supplier_id':str(b.supplier_id),'enquiry_service_name':enquiry_service_name,'business_name':advert_name,'category':category,'address':address}
                category_obj.append(cat_obj)
            except:
                advert_name = b.advert_name
                contact_no = b.contact_no
                category_obj1 = b.category_id.category_name

                category = str(category_obj1)
                address = str(b.address_line_1)+' '+str(b.address_line_2)+','+str(b.city_place_id.city_id)+'-'+str(b.pincode_id.pincode)
                cat_obj = {'supplier_id':str(b.supplier_id),'contact_no':contact_no,'enquiry_service_name':'','business_name':advert_name,'category':category,'address':address}
                category_obj.append(cat_obj)
        else:
            print '----------cat obj---',b
            advert_name = b.advert_name
            print '----------advert_name--------',advert_name
            contact_no = b.contact_no
            category_obj1 = b.category_id.category_name
            print '------------cat 1------',category_obj1
            if b.category_level_1:
                subcat1_name = b.category_level_1.category_name
                print '------------sub cat 1------',subcat1_name
            else:
                subcat1_name = ''
            if b.category_level_2:
                subcat2_name = b.category_level_2.category_name
                print '-----------sub-cat 2------',subcat2_name
            else:
                subcat2_name = ''
            print '------------cat 1------',category_obj1

            category = str(category_obj1)
            address = str(b.address_line_1)+' '+str(b.address_line_2)+','+str(b.city_place_id.city_id)+'-'+str(b.pincode_id.pincode)
            cat_obj = {'supplier_id':str(b.supplier_id),'contact_no':contact_no,'enquiry_service_name':'','business_name':advert_name,'category':category,'address':address}
            category_obj.append(cat_obj)

    category_obj = category_obj[:20]
    return category_obj

def b_searching4(sobj):
    print '----------- b search ---------',sobj
    category_obj=[]
    for b in sobj:
        print '----------cat obj---',b
        a = Advert.objects.filter(supplier_id=b)
        print '-----------supplier obj------',a
        for i in a:
            if AdvertSubscriptionMap.objects.get(advert_id=i):
                adv_obj = AdvertSubscriptionMap.objects.get(advert_id=i)
                business_obj = adv_obj.business_id
                #if EnquiryService.objects.get(business_id = business_obj):
                try:
                    Enquiry_obj = EnquiryService.objects.get(business_id = business_obj)
                    enquiry_service_name = Enquiry_obj.enquiry_service_name

                    category_obj1 = i.category_id.category_name

                    category = str(category_obj1)
                    advert_name = i.advert_name
                    contact_no = i.contact_no

                    address = str(i.address_line_1)+' '+str(i.address_line_2)+','+str(i.city_place_id.city_id)+'-'+str(i.pincode_id.pincode)
                    cat_obj = {'contact_no':contact_no,'supplier_id':str(i.supplier_id),'enquiry_service_name':enquiry_service_name,'business_name':advert_name,'category':category,'address':address}
                    category_obj.append(cat_obj)
                except:
                    advert_name = i.advert_name
                    contact_no = b.contact_no
                    category_obj1 = i.category_id.category_name

                    category = str(category_obj1)
                    address = str(i.address_line_1)+' '+str(i.address_line_2)+','+str(i.city_place_id.city_id)+'-'+str(i.pincode_id.pincode)
                    cat_obj = {'supplier_id':str(b.supplier_id),'contact_no':contact_no,'enquiry_service_name':'','business_name':advert_name,'category':category,'address':address}
                    category_obj.append(cat_obj)
            else:
                print '----------cat obj---',b
                a = Advert.objects.filter(supplier_id=b)
                print '-----------supplier obj------',a
                for i in a:
                    advert_name = i.advert_name
                    contact_no = b.contact_no
                    category_obj1 = i.category_id.category_name
                    print '------------cat 1------',category_obj1

                    category = str(category_obj1)
                    address = str(i.address_line_1)+' '+str(i.address_line_2)+','+str(i.city_place_id.city_id)+'-'+str(i.pincode_id.pincode)
                    cat_obj = {'supplier_id':b.supplier_id,'contact_no':contact_no,'enquiry_service_name':'','business_name':advert_name,'category':category,'address':address}
                    category_obj.append(cat_obj)
        category_obj = category_obj[:20]
    return category_obj


def b_searching3(sobj,city_place,area):
    print '----------- b search ---------',sobj,city_place
    category_obj=[]
    for b in sobj:
        print '----------cat obj---',b
        a = Advert.objects.filter(supplier_id=b,city_place_id=city_place,area__icontains=area)
        print '-----------supplier obj------',a
        for i in a:
            if AdvertSubscriptionMap.objects.get(advert_id=i):
                adv_obj = AdvertSubscriptionMap.objects.get(advert_id=i)
                print '-------------adv object-------',adv_obj
                business_obj = adv_obj.business_id
                print '-------------business_obj object-------',business_obj
                #if EnquiryService.objects.get(business_id = business_obj):
                try:
                    print '--------in if------'
                    Enquiry_obj = EnquiryService.objects.get(business_id = business_obj)
                    enquiry_service_name = Enquiry_obj.enquiry_service_name

                    category_obj1 = i.category_id.category_name

                    category = str(category_obj1)
                    advert_name = i.advert_name
                    contact_no = i.contact_no
                    address = str(i.address_line_1)+' '+str(i.address_line_2)+','+str(i.city_place_id.city_id)+'-'+str(i.pincode_id.pincode)
                    cat_obj = {'contact_no':contact_no,'supplier_id':str(i.supplier_id),'enquiry_service_name':enquiry_service_name,'business_name':advert_name,'category':category,'address':address}
                    category_obj.append(cat_obj)
                except:
                    advert_name = i.advert_name
                    contact_no = b.contact_no
                    category_obj1 = i.category_id.category_name

                    category = str(category_obj1)
                    address = str(i.address_line_1)+' '+str(i.address_line_2)+','+str(i.city_place_id.city_id)+'-'+str(i.pincode_id.pincode)
                    cat_obj = {'supplier_id':b.supplier_id,'contact_no':contact_no,'enquiry_service_name':'','business_name':advert_name,'category':category,'address':address}
                    category_obj.append(cat_obj)
            else:
                advert_name = i.advert_name
                contact_no = b.contact_no
                category_obj1 = i.category_id.category_name

                category = str(category_obj1)
                address = str(i.address_line_1)+' '+str(i.address_line_2)+','+str(i.city_place_id.city_id)+'-'+str(i.pincode_id.pincode)
                cat_obj = {'supplier_id':b.supplier_id,'contact_no':contact_no,'enquiry_service_name':'','business_name':advert_name,'category':category,'address':address}
                category_obj.append(cat_obj)
        category_obj = category_obj[:20]
    return category_obj


def b_searching1(sobj,category):
    print '----------- b search ---------',sobj,category
    category_obj=[]
    for b in sobj:
        print '----------cat obj---',b
        a = Advert.objects.filter(supplier_id=b,category_id=category)
        print '-----------supplier obj------',a
        for i in a:
            if AdvertSubscriptionMap.objects.get(advert_id=i):
                adv_obj = AdvertSubscriptionMap.objects.get(advert_id=i)
                business_obj = adv_obj.business_id
                #if EnquiryService.objects.get(business_id = business_obj):
                try:
                    Enquiry_obj = EnquiryService.objects.get(business_id = business_obj)
                    enquiry_service_name = Enquiry_obj.enquiry_service_name

                    category_obj1 = i.category_id.category_name

                    category = str(category_obj1)
                    advert_name = i.advert_name
                    contact_no = i.contact_no
                    address = str(i.address_line_1)+' '+str(i.address_line_2)+','+str(i.city_place_id.city_id)+'-'+str(i.pincode_id.pincode)
                    cat_obj = {'contact_no':contact_no,'supplier_id':str(i.supplier_id),'enquiry_service_name':enquiry_service_name,'business_name':advert_name,'category':category,'address':address}
                    category_obj.append(cat_obj)
                except:
                    advert_name = i.advert_name
                    contact_no = b.contact_no
                    category_obj1 = i.category_id.category_name

                    category = str(category_obj1)
                    address = str(i.address_line_1)+' '+str(i.address_line_2)+','+str(i.city_place_id.city_id)+'-'+str(i.pincode_id.pincode)
                    cat_obj = {'supplier_id':b.supplier_id,'contact_no':contact_no,'enquiry_service_name':'','business_name':advert_name,'category':category,'address':address}
                    category_obj.append(cat_obj)
            else:
                advert_name = i.advert_name
                contact_no = b.contact_no
                category_obj1 = i.category_id.category_name
                print '------------cat 1------',category_obj1

                category = str(category_obj1)
                address = str(i.address_line_1)+' '+str(i.address_line_2)+','+str(i.city_place_id.city_id)+'-'+str(i.pincode_id.pincode)
                cat_obj = {'supplier_id':b.supplier_id,'contact_no':contact_no,'enquiry_service_name':'','business_name':advert_name,'category':category,'address':address}
                category_obj.append(cat_obj)
        category_obj = category_obj[:20]
    return category_obj


def b_searching(sobj,area,city_place,category):
    print '----------- b search ---------',sobj,area,city_place,category
    cat = category
    category_obj=[]
    for b in sobj:
        print '----------cat obj---',b , cat
        a = Advert.objects.filter(supplier_id=b,city_place_id=city_place,area__icontains=area,category_id=cat)
        print '-----------supplier obj------',a
        for i in a:
            if AdvertSubscriptionMap.objects.get(advert_id=i):
                adv_obj = AdvertSubscriptionMap.objects.get(advert_id=i)
                business_obj = adv_obj.business_id
                #if EnquiryService.objects.get(business_id = business_obj):
                try:
                    Enquiry_obj = EnquiryService.objects.get(business_id = business_obj)
                    enquiry_service_name = Enquiry_obj.enquiry_service_name

                    category_obj1 = i.category_id.category_name

                    category = str(category_obj1)
                    advert_name = i.business_name
                    contact_no = i.contact_no
                    address = str(i.address_line_1)+' '+str(i.address_line_2)+','+str(i.city_place_id.city_id)+'-'+str(i.pincode_id.pincode)
                    cat_obj = {'contact_no':contact_no,'supplier_id':str(i.supplier_id),'enquiry_service_name':enquiry_service_name,'business_name':advert_name,'category':category,'address':address}
                    category_obj.append(cat_obj)
                except:
                    advert_name = i.advert_name
                    contact_no = b.contact_no
                    category_obj1 = i.category_id.category_name

                    category = str(category_obj1)
                    address = str(i.address_line_1)+' '+str(i.address_line_2)+','+str(i.city_place_id.city_id)+'-'+str(i.pincode_id.pincode)
                    cat_obj = {'supplier_id':b.supplier_id,'contact_no':contact_no,'enquiry_service_name':'','business_name':advert_name,'category':category,'address':address}
                    category_obj.append(cat_obj)
            else:
                advert_name = i.advert_name
                contact_no = b.contact_no
                category_obj1 = i.category_id.category_name
                print '------------cat 1------',category_obj1

                category = str(category_obj1)
                address = str(i.address_line_1)+' '+str(i.address_line_2)+','+str(i.city_place_id.city_id)+'-'+str(i.pincode_id.pincode)
                cat_obj = {'supplier_id':b.supplier_id,'contact_no':contact_no,'enquiry_service_name':'','business_name':advert_name,'category':category,'address':address}
                category_obj.append(cat_obj)
        category_obj = category_obj[:20]
    return category_obj

#--------------------------------------New updated-------------------------------------
@csrf_exempt
def searching_advert(request):
    try:
        text = request.POST.get('keyword')
        area = request.POST.get('area')
        category = request.POST.get('category')
        print '-------category------',category
        if category =='all':
            print '-------in category if------'
            cobj_id = 'all'
        else:
            print '-------in category else------'
            cobj_id = Category.objects.get(category_id=category)
            cobj_id = cobj_id.category_id
            print '---------category object---------',cobj_id

            #cobj_id = request.POST.get('category')

        category_level_1 = request.POST.get('category_level_1')
        category_level_2 = request.POST.get('category_level_2')
        city = request.POST.get('city')

        list = []
        advert_list = []

        if request.POST.get('city') == 'all' and request.POST.get('category')=='all':
            supplier_obj = Supplier.objects.filter(business_name__icontains=text,supplier_status=1)
            for supplier in supplier_obj:
                advert_obj = Advert.objects.filter(status=1,supplier_id=str(supplier.supplier_id),area__icontains=area)
                list.extend(advert_obj)

            supplier_obj = Supplier.objects.filter(supplier_status=1)
            advert_obj = Advert.objects.filter(status=1,advert_name__icontains=text,area__icontains=area,supplier_id__in=supplier_obj)
            # for a in advert_obj:
            #     sid = a.supplier_id.supplier_id
            #     s_obj = Supplier.objects.get(supplier_id=str(sid))
            #     s_status=s_obj.supplier_status
            #     if s_status == 1:
            #         list.extend(a)
            list.extend(advert_obj)

            advert_obj = Advert.objects.filter(status=1,keywords__icontains=text,area__icontains=area,supplier_id__in=supplier_obj)
            # for a in advert_obj:
            #     sid = a.supplier_id.supplier_id
            #     s_obj = Supplier.objects.get(supplier_id=str(sid))
            #     s_status=s_obj.supplier_status
            #     if s_status == 1:
            #         list.extend(a)
            list.extend(advert_obj)

        elif request.POST.get('city') == 'all':
            supplier_obj = Supplier.objects.filter(business_name__icontains=text,supplier_status=1)
            for supplier in supplier_obj:
                advert_obj = Advert.objects.filter(status=1,supplier_id=str(supplier.supplier_id),area__icontains=area,category_id=cobj_id)
                list.extend(advert_obj)

            supplier_obj = Supplier.objects.filter(supplier_status=1)
            advert_obj = Advert.objects.filter(status=1,advert_name__icontains=text,area__icontains=area,category_id=cobj_id,supplier_id__in=supplier_obj)
            # for a in advert_obj:
            #     sid = a.supplier_id.supplier_id
            #     s_obj = Supplier.objects.get(supplier_id=str(sid))
            #     s_status=s_obj.supplier_status
            #     if s_status == 1:
            #         list.extend(a)
            list.extend(advert_obj)

            advert_obj = Advert.objects.filter(status=1,keywords__icontains=text,area__icontains=area,category_id=cobj_id,supplier_id__in=supplier_obj)
            # for a in advert_obj:
            #     sid = a.supplier_id.supplier_id
            #     s_obj = Supplier.objects.get(supplier_id=str(sid))
            #     s_status=s_obj.supplier_status
            #     if s_status == 1:
            #         list.extend(a)
            list.extend(advert_obj)

        elif request.POST.get('category')=='all':
            city_place = City_Place.objects.get(city_id=request.POST.get('city'))
            supplier_obj = Supplier.objects.filter(business_name__icontains=text,supplier_status=1)
            for supplier in supplier_obj:
                advert_obj = Advert.objects.filter(status=1,supplier_id=str(supplier.supplier_id),area__icontains=area,city_place_id=city_place)
                list.extend(advert_obj)

            supplier_obj = Supplier.objects.filter(supplier_status=1)
            advert_obj = Advert.objects.filter(status=1,advert_name__icontains=text,area__icontains=area,city_place_id=city_place,supplier_id__in=supplier_obj)
            # for a in advert_obj:
            #     sid = a.supplier_id.supplier_id
            #     s_obj = Supplier.objects.get(supplier_id=str(sid))
            #     s_status=s_obj.supplier_status
            #     if s_status == 1:
            #         list.extend(a)
            list.extend(advert_obj)

            advert_obj = Advert.objects.filter(status=1,keywords__icontains=text,area__icontains=area,city_place_id=city_place,supplier_id__in=supplier_obj)
            # for a in advert_obj:
            #     sid = a.supplier_id.supplier_id
            #     s_obj = Supplier.objects.get(supplier_id=str(sid))
            #     s_status=s_obj.supplier_status
            #     if s_status == 1:
            #         list.extend(a)
            list.extend(advert_obj)

        elif request.POST.get('category_level_1')!='' and request.POST.get('category_level_2')!='':
            cobj_level1_id = CategoryLevel1.objects.get(category_id=str(category_level_1))
            cobj_level2_id = CategoryLevel2.objects.get(category_id=str(category_level_2))
            city_place = City_Place.objects.get(city_id=request.POST.get('city'))

            supplier_obj = Supplier.objects.filter(supplier_status=1)
            advert_obj = Advert.objects.filter(status=1,keywords__icontains=text,area__icontains=area,city_place_id=city_place,category_id=cobj_id,category_level_1=str(cobj_level1_id),category_level_2=str(cobj_level2_id),supplier_id__in=supplier_obj)
            # for a in advert_obj:
            #     sid = a.supplier_id.supplier_id
            #     s_obj = Supplier.objects.get(supplier_id=str(sid))
            #     s_status=s_obj.supplier_status
            #     if s_status == 1:
            #         list.extend(a)
            list.extend(advert_obj)

        elif request.POST.get('category_level_1')!='':
            cobj_level1_id = CategoryLevel1.objects.get(category_id=str(category_level_1))
            city_place = City_Place.objects.get(city_id=request.POST.get('city'))
            supplier_obj = Supplier.objects.filter(supplier_status=1)
            advert_obj = Advert.objects.filter(status=1,keywords__icontains=text,area__icontains=area,city_place_id=city_place,category_id=cobj_id,category_level_1=str(cobj_level1_id),supplier_id__in=supplier_obj)
            # for a in advert_obj:
                # sid = a.supplier_id.supplier_id
                # s_obj = Supplier.objects.get(supplier_id=str(sid))
                # s_status=s_obj.supplier_status
                # if s_status == 1:
                #     list.extend(a)
            list.extend(advert_obj)

        else:
            #cobj_level1_id = CategoryLevel1.objects.get(category_id=str(category_level_1))
            #cobj_level2_id = CategoryLevel2.objects.get(category_id=str(category_level_2))
            city_place = City_Place.objects.get(city_id=request.POST.get('city'))
            supplier_obj = Supplier.objects.filter(business_name__icontains=text,supplier_status=1)
            for supplier in supplier_obj:
                advert_obj = Advert.objects.filter(status=1,supplier_id=str(supplier.supplier_id),area__icontains=area,city_place_id=city_place,category_id=cobj_id)
                list.extend(advert_obj)

            supplier_obj = Supplier.objects.filter(supplier_status=1)
            advert_obj = Advert.objects.filter(status=1,advert_name__icontains=text,area__icontains=area,city_place_id=city_place,category_id=cobj_id,supplier_id__in=supplier_obj)
            list.extend(advert_obj)
            # for a in advert_obj:
            #     sid = a.supplier_id.supplier_id
            #     s_obj = Supplier.objects.get(supplier_id=str(sid))
            #     s_status=s_obj.supplier_status
            #     if s_status == 1:
            #         list.extend(a)

            advert_obj = Advert.objects.filter(status=1,keywords__icontains=text,area__icontains=area,city_place_id=city_place,category_id=cobj_id,supplier_id__in=supplier_obj)
            # for a in advert_obj:
            #     sid = a.supplier_id.supplier_id
            #     s_obj = Supplier.objects.get(supplier_id=str(sid))
            #     s_status=s_obj.supplier_status
            #     if s_status == 1:
            #         list.extend(a)
            list.extend(advert_obj)

            # advert_obj = Advert.objects.filter(keywords__icontains=text,area__icontains=area,city_place_id=city_place,category_id=str(cobj_id),category_level_1=str(cobj_level1_id))
            # list.extend(advert_obj)
            #
            # advert_obj = Advert.objects.filter(keywords__icontains=text,area__icontains=area,city_place_id=city_place,category_id=str(cobj_id),category_level_1=str(cobj_level1_id),category_level_2=str(cobj_level2_id))
            # list.extend(advert_obj)

        list = set(list)
        # for advert in list:
        #     phone_list = []
        #     email_list = []
        #     advert_id = str(advert.advert_id)
        #     pre_date = datetime.now().strftime("%d/%m/%Y")
        #     pre_date = datetime.strptime(pre_date, "%d/%m/%Y")
        #     advert_sub_obj = AdvertSubscriptionMap.objects.get(advert_id=advert_id)
        #     end_date = advert_sub_obj.business_id.end_date
        #     start_date = datetime.strptime(advert_sub_obj.business_id.start_date, "%d/%m/%Y")
        #     if start_date <= pre_date:
        #         end_date = datetime.strptime(end_date, "%d/%m/%Y")
        #         date_gap = end_date - pre_date
        #         if int(date_gap.days) >= 0:
        #             advert_obj = Advert.objects.get(advert_id=advert_id)
        #             advert_data = {
        #                 "advert_id": str(advert_obj.advert_id),
        #                 "advert_name": str(advert_obj.advert_name),
        #                 "category_name": str(advert_obj.category_id.category_name)
        #             }
        #             advert_list.append(advert_data)

        category_obj=[]
        print '----------list-------',list
        i=0
        n=''
        j=0
        b1=0
        v=0
        p1=0
        d1=0
        g1=0
        ns=0
        for b in list:
            print '---------------b in list-----------',b
            if AdvertSubscriptionMap.objects.get(advert_id=b):
                adv_obj = AdvertSubscriptionMap.objects.get(advert_id=b)
                business_obj = adv_obj.business_id

                try:
                    Enquiry_obj = EnquiryService.objects.get(business_id = business_obj)
                    enquiry_service_name = Enquiry_obj.enquiry_service_name

                    print '---enquiry_service_name----',enquiry_service_name
                    if enquiry_service_name == 'Platinum':
                        # p1=p1+1
                        # if p1==1:
                        #     n='1'
                        # else:
                        #     pass
                        n='1'
                    elif enquiry_service_name == 'Diamond':
                        n='2'
                        # d1=d1+1
                        # if d1==1:
                        #     n='2'
                        # else:
                        #     pass
                    elif enquiry_service_name == 'Gold':
                        n='3'
                        # g1=g1+1
                        # if g1==1:
                        #     n='3'
                        # else:
                        #     pass
                    elif enquiry_service_name == 'Silver':
                        j=j+1
                        if j==1:
                            n='4'
                        if j==2:
                            n='5'
                        if j>=3:
                            pass
                    elif enquiry_service_name == 'Bronze':
                        b1=b1+1
                        print '----------'
                        if b1==1:
                            n='6'
                        if b1==2:
                            n='7'
                        if b1==3:
                            n='8'
                        if b1>=4:
                            pass
                    elif enquiry_service_name == 'Value':
                        v=v+1
                        if v==1:
                            n='9'
                        if v==2:
                            n='10'
                        if v>=3:
                            pass

                    elif enquiry_service_name == '':
                        ns=ns+1

                    category_obj1 = b.category_id.category_name

                    category = str(category_obj1)
                    advert_name = b.advert_name
                    contact_no = b.contact_no

                    address = str(b.address_line_1)+'\n'+str(b.address_line_2)+',\n'+str(b.area)+'\n'+str(b.city_place_id.city_id)+'-'+str(b.pincode_id.pincode)
                    cat_obj = {'sequence_number':int(n),'contact_no':contact_no,'premium_service':'yes','supplier_id':str(b),'enquiry_service_name':enquiry_service_name,'business_name':advert_name,'category':category,'address':address}
                    category_obj.append(cat_obj)
                except:
                    advert_name = b.advert_name
                    contact_no = b.contact_no
                    category_obj1 = b.category_id.category_name
                    i=i+1
                    n=10+i
                    category = str(category_obj1)
                    address = str(b.address_line_1)+'\n'+str(b.address_line_2)+',\n'+str(b.area)+'\n'+str(b.city_place_id.city_id)+'-'+str(b.pincode_id.pincode)
                    cat_obj = {'sequence_number':int(n),'supplier_id':str(b),'premium_service':'no','contact_no':contact_no,'enquiry_service_name':'','business_name':advert_name,'category':category,'address':address}
                    category_obj.append(cat_obj)
            else:
                advert_name = b.advert_name
                contact_no = b.contact_no
                category_obj1 = b.category_id.category_name

                i=i+1
                n=20+i
                category = str(category_obj1)
                address = str(b.address_line_1)+'\n'+str(b.address_line_2)+',\n'+str(b.area)+'\n'+str(b.city_place_id.city_id)+'-'+str(b.pincode_id.pincode)
                cat_obj = {'sequence_number':int(n),'supplier_id':str(b),'premium_service':'no','contact_no':contact_no,'enquiry_service_name':'','business_name':advert_name,'category':category,'address':address}
                category_obj.append(cat_obj)

        newlist = sorted(category_obj, key=itemgetter('sequence_number'))
        print '---------newlist--------',newlist
        category_obj = newlist[:10]

        #print '-----------category_obj-------',category_obj
        if category_obj == []:
            print '-----------in elsej-------'
            data = {'success': 'false'}
        else:
            print '-----------in if-------'
            data = {'success': 'true', 'result_list': category_obj}
        # #return category_obj
        #
        # data = {'success': 'true', 'result_list': category_obj}
    except Exception, e:
        print e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')

