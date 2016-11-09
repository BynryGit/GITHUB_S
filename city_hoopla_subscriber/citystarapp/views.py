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
import os

#SERVER_URL = "http://52.40.205.128"
SERVER_URL = "http://52.66.169.65"
#SERVER_URL = "http://192.168.0.125:8017"

#CTI CRM APIs=============================================================================

def citystar(request):
    return render(request,'City_Star/star_home.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def starhome(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        #print '-----------city obj-----',request.GET.get('city_id')
        city_obj_id = request.GET.get('city_id')
        city_name_obj = City_Place.objects.get(city_place_id=request.GET.get('city_id'))
        city_name = city_name_obj.city_id.city_name

        sts_value = request.GET.get('sts_val')
        #print '-------sts_value------',sts_value
        current_status = ''
        default_status = ''
        if request.GET.get('sts_val'):
            if request.GET.get('sts_val') =='current' or request.GET.get('sts_val')=='default' or request.GET.get('sts_val')=='expired' or request.GET.get('sts_val')=='active' or request.GET.get('sts_val')=='deactivated' :
                sts = request.GET.get('sts_val')
                user_obj = CityStarDetails.objects.filter(city=request.GET.get('city_id'),status=sts)
                #print '-----------user obj--in if---',user_obj
                sts_value = sts_value.title()

            else:
                user_obj = CityStarDetails.objects.filter(city=request.GET.get('city_id'))
                #print '-----------user obj-- in else 1---',user_obj
        else:
            user_obj = CityStarDetails.objects.filter(city=request.GET.get('city_id'))
            #print '-----------user obj---in eles--',user_obj
            sts_value = ''

        # try:
        #     current_status_obj = CityStarDetails.objects.filter(status = 'default',city=request.GET.get('city_id'))
        #     print '------current status object----',current_status_obj
        #     current_status = '1'
        #     print '------current status ----',current_status
        # except:
        #     current_status_obj = ''
        #     print '------current status object----',current_status_obj
        #     current_status = '0'
        #     print '------current status ---',current_status

        try:
            a = CityStarDetails.objects.get(status = 'current',city=request.GET.get('city_id'))
            current_status = a
            print '------current status object----',current_status
        except:
            # a = CityStarDetails.objects.get(status = 'current',city=request.GET.get('city_id'))
            # current_status = a
            print '------current status object----',current_status
        try:
            b = CityStarDetails.objects.get(status = 'default',city=request.GET.get('city_id'))
            default_status = b
            print '------current status object-1111---',default_status
        except :
            # b = CityStarDetails.objects.get(status = 'default',city=request.GET.get('city_id'))
            # default_status = b
            print '------current status object-1111---',default_status


        star_list=[]
        data={}
        star_count = len(user_obj)

        for obj in user_obj:
            #print '-------obj-----',obj
            #print '-------image-------',obj.image
            #print '-------city-------',obj.city
            #print '-----------datetime now---------',datetime.now().strftime("%d/%m/%Y")
            #print '-----------end time now---------',obj.end_date.strftime("%d/%m/%Y")
            sdate = obj.start_date.strftime("%d/%m/%Y")
            tdate = datetime.now().strftime("%d/%m/%Y")
            edate = obj.end_date.strftime("%d/%m/%Y")

            # if tdate == sdate :
            #     obj.status = '1'
            #     obj.save()
            if obj.start_date.strftime("%d/%m/%Y"):
                start_date = obj.start_date.strftime("%d/%m/%Y")
            else:
                start_date = ''
            star={'id':obj.citystarID,'title':obj.title,
                       'name':obj.name,
                       'summary':obj.summary,
                       'status':obj.status,
                       'image':SERVER_URL + obj.image.url,
                       'city':obj.city,
                       'start_date':start_date,
                       'end_date':obj.end_date.strftime("%d/%m/%Y"),
                       'likes': str(CityStar_Like.objects.filter(citystarID=obj.citystarID).count()),
                       'views': str(CityStar_View.objects.filter(citystarID=obj.citystarID).count()),
                       'status':obj.status,
                       'shares':obj.shares

            }

            star_list.append(star)
        data={'username':request.session['login_user'],'star_list':star_list,'default_status':default_status,'current_status':current_status,'status_value':sts_value,'city_id':str(city_obj_id),'city_name':str(city_name),'star_count':star_count}

        return render(request,'City_Star/star_homepage.html',data)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def citystar_home(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:

        star_list=[]
        citylist=[]
        data={}

        city_obj = City_Place.objects.all()
        for c in city_obj:
            #print '---------default stars----',CityStarDetails.objects.filter(city=42,status='default')
            city=c.city_id.city_name
            print '------city-----',city
            country = c.country_id.country_name
            #country=''

            if c.city_image:
                image=SERVER_URL + c.city_image.url
                print '---------image----',image
            else:
                image=''

            try:
                today_date = datetime.now().strftime("%d/%m/%Y")
                print '-------------234234234324234324-----------'
                #if CityStarDetails.objects.get(city=str(c),status='current'):
                try:
                    user_obj = CityStarDetails.objects.get(city=c,status='current')
                    print '-----------user obj-----',user_obj
                    print '-----------------i----------'
                    sid=user_obj.citystarID
                    stitle=user_obj.title
                    sstatus=user_obj.status
                    sname=user_obj.name
                    ssummary=user_obj.summary
                    simage=SERVER_URL + user_obj.image.url
                    scity=user_obj.city.city_id.city_name
                    slike= str(CityStar_Like.objects.filter(citystarID=user_obj.citystarID).count())
                    sview= str(CityStar_View.objects.filter(citystarID=user_obj.citystarID).count())
                    sshares=user_obj.shares

                    star={'country':country,'city':city,'city_id':c,'cimage':image,'id':sid,'title':stitle,'status':sstatus,'name':sname,
                      'summary':ssummary,'image':simage,'likes':slike,'views':sview,'shares':sshares}
                    star_list.append(star)

                #elif CityStarDetails.objects.get(city=str(c),status='default'):
                except:
                    #obj = CityStarDetails.objects.get(city=str(c),status='default')
                    #print '--------in if----------'
                    #star_obj = CityStarDetails.objects.filter(city=c)
                    star_obj = CityStarDetails.objects.get(city=str(c),status='default')
                    # for so in star_obj:
                    #     sdate = (so.start_date).strftime("%d/%m/%Y")
                    #     edate = (so.end_date).strftime("%d/%m/%Y")
                    #     if sdate < today_date < edate:
                    #         print '----a-------'
                    #         user_obj = CityStarDetails.objects.get(city=c,status='default')
                    sid=star_obj.citystarID
                    stitle=star_obj.title
                    sstatus=star_obj.status
                    sname=star_obj.name
                    ssummary=star_obj.summary
                    simage=SERVER_URL + star_obj.image.url
                    scity=star_obj.city.city_id.city_name
                    slike= str(CityStar_Like.objects.filter(citystarID=star_obj.citystarID).count())
                    sview= str(CityStar_View.objects.filter(citystarID=star_obj.citystarID).count())
                    sshares=star_obj.shares

                    star={'country':country,'city':city,'city_id':c,'cimage':image,'id':sid,'title':stitle,'status':sstatus,'name':sname,
                      'summary':ssummary,'image':simage,'likes':slike,'views':sview,'shares':sshares}
                    star_list.append(star)
                    # else:
                    #     pass

            except:
                print '--------in else--------'
                star={'country':country,'city':city,'city_id':c,'cimage':image,'id':'','title':'','status':'','name':'',
                  'summary':'','image':'','likes':'','views':'','shares':''}
                star_list.append(star)
        #print star_list
        data={'username':request.session['login_user'],'star_list':star_list}
        #print data
        return render(request,'City_Star/citystar_home.html',data)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_citystar(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        print '-------city id---------',request.GET.get('city_id')
        city_star_obj = CityStarDetails.objects.filter(city=request.GET.get('city_id'))
        print '----------city_star_obj--------',city_star_obj
        for co in city_star_obj:
            city_id = co.city
        try:
            if CityStarDetails.objects.get(status='default',city=city_id):
                print '------in the if--------'
                default_obj = '1'
            else:
                default_obj = '0'
        except:
            print '--------in the else------'
            default_obj = '0'

        cityobj = City_Place.objects.get(city_place_id=request.GET.get('city_id'))
        print '---------cityobj---------',cityobj
        city_name = cityobj.city_id.city_name
        print '-------city_namr-------',city_name
        data={'default_obj':default_obj,'username':request.session['login_user'],'city_name':city_name,'city_id':request.GET.get('city_id')}
        print data
        return render(request,'City_Star/add_citystar.html',data)

def get_star_dates(request):
    print '---------in get start date------'
    date_list=[]
    data={}
    print '-------city id---------',request.GET.get('city_id')
    city_star_obj = CityStarDetails.objects.filter(status__in=["active","current","expired","default"],city=request.GET.get('city_id'))
    print '----------city_star_obj--------',city_star_obj
    for cst in city_star_obj:
        start_date = cst.start_date.strftime("%m/%d/%Y")
        end_date = cst.end_date.strftime("%m/%d/%Y")
        dlist={'start_date':start_date,'end_date':end_date}
        date_list.append(dlist)

    data={'success':'true','date_list':date_list}
    print '----------date data------',data
    return HttpResponse(json.dumps(data), content_type='application/json')


def addcitystar(request):
    return render(request,'City_Star/addcitystar.html')

# def activate_citystar(request):
#     print '---------star id--------',request.GET.get('star_id')
#     print '---------deactivate date--------',request.GET.get('ddate')
#     star_obj = CityStarDetails.objects.get(citystarID=request.GET.get('star_id'))
#     print '------star_obj------',star_obj
#     city_id = star_obj.city
#     print '-------city id-----',city_id
#     try:
#         act_star_obj = CityStarDetails.objects.get(status='current',city=city_id)
#         print '------activate star id-----',act_star_obj
#         act_star_obj.status = 'deactivated'
#         act_star_obj.end_date=datetime.now()
#         act_star_obj.save()
#         print '-----------star 0-----'
#     except:
#         star_obj.status='1'
#         star_obj.start_date = datetime.now()
#         #star_obj.end_date = request.GET.get('ddate')
#         star_obj.end_date = datetime.strptime(request.GET.get('ddate'),"%d/%m/%Y")
#         star_obj.save()
#         print '-----------star 1-----'
#         data = {'success': 'true','city_id':str(city_id)}
#         return HttpResponse(json.dumps(data), content_type='application/json')
#
#     star_obj.status='1'
#     star_obj.start_date = datetime.now()
#     #star_obj.end_date = request.GET.get('ddate')
#     star_obj.end_date = datetime.strptime(request.GET.get('ddate'),"%d/%m/%Y")
#     star_obj.save()
#     print '-----------star 3-----'
#
#     data = {'success': 'true','city_id':str(city_id)}
#     return HttpResponse(json.dumps(data), content_type='application/json')

def activate_citystar(request):
    print '---------star id--------',request.GET.get('star_id')
    #print '---------deactivate date--------',request.GET.get('ddate')
    star_obj = CityStarDetails.objects.get(citystarID=request.GET.get('star_id'))
    print '------star_obj------',star_obj
    city_id = star_obj.city
    print '-------city id-----',city_id
    try:
        act_star_obj = CityStarDetails.objects.get(citystarID=request.GET.get('star_id'),city=city_id)
        print '------activate star id-----',act_star_obj
        act_star_obj.status = 'deactivated'
        act_star_obj.end_date=datetime.now()
        act_star_obj.save()

    except:
        pass
    data = {'success': 'true','city_id':str(city_id)}
    return HttpResponse(json.dumps(data), content_type='application/json')


# def auto_activate_citystar(request):
#     print '---------activation date--------',datetime.now().strftime("%d/%m/%Y")
#     try:
#         act_date = datetime.now().strftime("%d/%m/%Y")
#
#         star_obj = CityStarDetails.objects.filter(start_date=act_date)
#         for cs in star_obj:
#             cs.status = 'current'
#             cs.end_date=datetime.now()
#             cs.save()
#
#     except:
#         pass
#
# def auto_deactivate_citystar(request):
#     print '---------activation date--------',datetime.now().strftime("%d/%m/%Y")
#     try:
#         deact_date = datetime.now().strftime("%d/%m/%Y")
#         star_obj = CityStarDetails.objects.filter(end_date=deact_date)
#         for cs in star_obj:
#             cs.status = 'deactivated'
#             cs.end_date=datetime.now()
#             cs.save()
#
#     except:
#         pass


@csrf_exempt
def search_starcity(request):
    print '---------city key------',request.POST.get('keyword')
    #print '-----------city obj-----',request.GET.get('city_id')
    user_obj = City.objects.filter(city_name__icontains=request.POST.get('keyword'))
    print '-----------user obj-----',user_obj

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_citystar(request):
    si_list=[]
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        s=''
        obj = CityStarDetails.objects.get(citystarID=request.GET.get('star_id'))
        print '-----------user obj-----',obj
        city_id = obj.city
        try:
            if CityStarDetails.objects.get(status='default',city=city_id):
                print '------in the if--------'
                default_obj = '1'
            else:
                default_obj = '0'
        except:
            print '--------in the else------'
            default_obj = '0'
        str_obj = StarImage.objects.filter(star_id=request.GET.get('star_id'))
        print '----------star obj------',str_obj
        for s in str_obj:
            print '----------starobj-------',s
            si_list.append(s)

        print '-------image-------',obj.citystarID
        print '-------city image id-------',s
        if obj.title:
            title = obj.title
        else:
            title=''
        if obj.address1:
            address1 = obj.address1
        else:
            address1=''
        if obj.address2:
            address2 = obj.address2
        else:
            address2=''
        if obj.phone:
            phone = obj.phone
        else:
            phone=''
        if obj.email:
            email = obj.email
        else:
            email=''
        if obj.age:
            age = obj.age
        else:
            age=''
        if obj.experience:
            experience = obj.experience
        else:
            experience=''
        if obj.education:
            education = obj.education
        else:
            education=''
        if obj.summary:
            summary = obj.summary
        else:
            summary=''
        if obj.occupation:
            occupation = obj.occupation
        else:
            occupation=''
        if obj.description:
            description = obj.description
        else:
            description=''
        if obj.achievements:
            achievements = obj.achievements
        else:
            achievements=''

        if obj.shares:
            shares = obj.shares
        else:
            shares=''

        data={'username':request.session['login_user'],'id':obj.citystarID,'title':title,'name':obj.name,'address1':address1,'address2':address2,
                   'phone':phone,
                   'email':email,
                   'age':age,
                   'exp':experience,
                   'education':education,
                   'summary':summary,
                   'occupation':occupation,
                   'description':description,
                   'achievements':achievements,
                   'image':SERVER_URL + obj.image.url,
                   'image_file':obj.image,
                   'city':obj.city,
                   'city_name':obj.city.city_id.city_name,
                   'start_date':obj.start_date.strftime("%d/%m/%Y"),
                   'end_date':obj.end_date.strftime("%d/%m/%Y"),
                   'status':obj.status,
                   'shares':shares,
                   'si_list':si_list,
                   'img':s,
                   'default_obj':default_obj
        }
        #print '-------star_obj attachments-----',obj.attachment_list
        print data
        return render(request,'City_Star/edit_citystar.html',data)

@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_citystar(request):
    print '---------image file--------',request.POST.get('display_image1')
    data={}
    print '---------city--------',request.POST.get('city')
    status_val=''

    print '---------status--------',request.POST.get('status')
    print '---------status--------',request.POST.get('dstatus')
    today_date = datetime.now().strftime("%d/%m/%Y")
    print '--------today_date------',today_date
    try:
        sdate = datetime.strptime(request.POST.get('activate_date'),"%d/%m/%Y")
        edate = datetime.strptime(request.POST.get('deactivate_date'),"%d/%m/%Y")
        sdate = sdate.strftime("%d/%m/%Y")
        print '-------sdate----------',sdate
        print '-------sdate----------',edate
    except:
        pass

    status_val = request.POST.get('status')
    print '--------status val---1-----',status_val

    try:
        print '---------------in try-default-------'
        if request.POST.get('dstatus') == 'default':
            print '---------in if 123232323------------'
            if CityStarDetails.objects.get(status='default',city=request.POST.get('city')):
                print '-------in the if default----------'
                default_star_obj = CityStarDetails.objects.get(status='default',city=request.POST.get('city'))
                default_star_obj = default_star_obj.citystarID
                print '-----------default-star-obj---------',default_star_obj
                print '-----------default-star-o id---------',request.POST.get('id')
                if str(default_star_obj) == str(request.POST.get('id')):
                    pass
                else:
                    data = {'success': 'default-false'}
                    return HttpResponse(json.dumps(data), content_type='application/json')

        elif today_date == sdate:
            print '-------in date comparison-----'
            status_val = 'current'
            print '--------status val---2-----',status_val

        elif sdate and edate:
            print '-------in date comparison-----'
            status_val = 'active'
            print '--------status val---4545-----',status_val

        elif request.POST.get('status') == '':
            status_val = 'active'
            print '--------status val---3-----',status_val

        # else:
        #     print '-------in the else default----------'
        #     status_val = 'default'
        #     print '--------status val---4-----',status_val

    except:
        pass

    if request.POST.get('dstatus') == 'default':
        print '---------in if ----status------'
        print '--------status val---5-----',status_val
        status_val = 'default'
        start_date = datetime.now()
        end_date = datetime.now()
    else:
        print '---------in else ----status------'
        start_date = datetime.strptime(request.POST.get('activate_date'),"%d/%m/%Y")+ timedelta(hours=6)
        end_date = datetime.strptime(request.POST.get('deactivate_date'),"%d/%m/%Y")+ timedelta(hours=6)



    city_obj = City_Place.objects.get(city_place_id=request.POST.get('city'))
    print '---------city_obj--------',city_obj
    print '---------city_place_id obj--------',city_obj.city_place_id
    a = city_obj.city_place_id
    print '---------city_place_id obj a--------',a
    try:
        print '------in try--------',status_val
        star_obj = CityStarDetails(citystarID = request.POST.get('id'))
        print '-------------star object------',star_obj
        #pdb.set_trace()
        star_obj.title = request.POST.get('title')
        star_obj.name = request.POST.get('name')
        star_obj.address1 = request.POST.get('address1')
        star_obj.address2 = request.POST.get('address2')
        star_obj.phone = request.POST.get('phone')
        star_obj.age = request.POST.get('age')
        star_obj.experience = request.POST.get('exp')
        star_obj.education = request.POST.get('education')
        star_obj.summary = request.POST.get('summary')
        star_obj.city = city_obj
        star_obj.occupation = request.POST.get('prof')
        star_obj.description = request.POST.get('abs')
        star_obj.achievements = request.POST.get('awards')
        star_obj.email = request.POST.get('email')
        #star_obj.status = request.POST.get('status')
        star_obj.status = status_val
        star_obj.shares = request.POST.get('shares')
        try :
            star_obj.image = request.FILES['display_image']
        except:
            star_obj.image = request.POST.get('display_image1')
        #star_obj.start_date = datetime.strptime(request.POST.get('activate_date'),"%d/%m/%Y")
        star_obj.start_date = start_date
        #star_obj.end_date = datetime.strptime(request.POST.get('deactivate_date'),"%d/%m/%Y")
        star_obj.end_date = end_date
        star_obj.updation_date = datetime.now()
        star_obj.updation_by = request.session['login_user']

        star_obj.save()

        print '--------star id------',star_obj
        print '--------city 0d-----',city_obj
        print '----------attachments------------',request.POST.get('attachments')
        attachment_list = []
        attachment_list = request.POST.get('attachments')
        save_attachments(attachment_list, star_obj)
        print '--------attachment list-------',attachment_list
        data = {'username':request.session['login_user'],'success': 'true','city_place_obj':str(request.POST.get('city')),'city_id':str(city_obj),'star_id':str(star_obj)}
        print '------data-----',data
    except Exception, e:
        print 'Exception ', e
        data = {'username':request.session['login_user'],'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def viewstarprofile(request):
    obj = CityStarDetails.objects.get(citystarID=request.GET.get('star_id'))
    print '-----------user obj-----',obj

    #for obj in user_obj:
    print '-------image-------',obj.citystarID
    #like_obj = CityStar_Like.objects.get(citystarID=obj.citystarID)
    #view_obj = CityStar_View.objects.get(citystarID=obj.citystarID)
    data={'username':request.session['login_user'],'id':obj.citystarID,'title':obj.title,'name':obj.name,'address':obj.address1,
               'phone':obj.phone,
               'email':obj.email,
               'age':obj.age,
               'exp':obj.experience,
               'education':obj.education,
               'summary':obj.summary,
               'occupation':obj.occupation,
               'description':obj.description,
               'achievements':obj.achievements,
               'image':SERVER_URL + obj.image.url,
               'city':obj.city,
               'city_name':obj.city.city_id.city_name,
               'start_date':obj.start_date.strftime("%d/%m/%Y"),
               'end_date':obj.end_date.strftime("%d/%m/%Y"),
               'status':obj.status,
               'likes' : str(CityStar_Like.objects.filter(citystarID=obj.citystarID).count()),
               'views' : str(CityStar_View.objects.filter(citystarID=obj.citystarID).count()),
               'shares':obj.shares
    }
    print data
    return render(request,'City_Star/view_star_profile.html',data)

def search_star(request):
    print '-----keywords---------',request.POST.get('keyword')

@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def save_citystar(request):

    print '---------status--------',request.POST.get('status')
    today_date = datetime.now().strftime("%d/%m/%Y")
    print '--------today_date------',today_date
    try:
        sdate = datetime.strptime(request.POST.get('activate_date'),"%d/%m/%Y")
        sdate = sdate.strftime("%d/%m/%Y")
        print '-------sdate----------',sdate
    except:
        pass
    # if today_date == sdate:
    #     print '-------in date comparison-----'
    #     status_val = 'current'

    try:
        if request.POST.get('status') == 'default':
            if CityStarDetails.objects.get(status='default',city=request.POST.get('city')):
                print '-------in the if default----------'
                data = {'success': 'default-false'}
                return HttpResponse(json.dumps(data), content_type='application/json')

        elif today_date == sdate:
            print '-------in date comparison-----'
            status_val = 'current'

        elif request.POST.get('status') == '':
            status_val = 'active'

        else:
            print '-------in the else default----------'
            status_val = 'default'

    except:
        pass

    if request.POST.get('status') == 'default':
        print '---------in if ----status------'
        status_val='default'
        start_date = datetime.now()
        end_date = datetime.now()
    else:
        print '---------in else ----status------'
        start_date = datetime.strptime(request.POST.get('activate_date'),"%d/%m/%Y")+ timedelta(hours=6)
        end_date = datetime.strptime(request.POST.get('deactivate_date'),"%d/%m/%Y")+ timedelta(hours=6)


    print '---------name--------',request.POST.get('title')
    print '---------city--------',request.POST.get('city')
    city_obj = City_Place.objects.get(city_place_id=request.POST.get('city'))
    print '---------date--------',request.POST.get('activate_date')
    try:
        star_obj = CityStarDetails(
            title = request.POST.get('title'),
            name = request.POST.get('name'),
            address1 = request.POST.get('address1'),
            address2 = request.POST.get('address2'),
            phone = request.POST.get('phone'),
            age = request.POST.get('age'),
            experience = request.POST.get('exp'),
            education = request.POST.get('education'),
            summary = request.POST.get('summary'),
            occupation = request.POST.get('prof'),
            description = request.POST.get('abs'),
            achievements = request.POST.get('awards'),
            email = request.POST.get('email'),
            image = request.FILES['display_image'],
            city = city_obj,
            #start_date = datetime.strptime(request.POST.get('activate_date'),"%d/%m/%Y"),
            #end_date = datetime.strptime(request.POST.get('deactivate_date'),"%d/%m/%Y"),
            start_date = start_date,
            end_date = end_date,
            status = status_val,
            shares = '0',
            creation_date = datetime.now(),
            creation_by = request.session['login_user'],
        )
        star_obj.save()
        print '--------star id------',star_obj
        print '--------city_obj id------',city_obj
        attachment_list = []
        attachment_list = request.POST.get('attachments')
        print '--------attachment list-------',attachment_list
        save_attachments(attachment_list, star_obj)
        data = {'success': 'true','city_obj':str(city_obj),'star_id':str(star_obj)}

    except Exception, e:
        print 'Exception ', e
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')




@csrf_exempt
def upload_star_image(request):
    try:
        print '----------in try------',request.GET.get('star_id')
        if request.method == 'POST':
            attachment_file = StarImage(star_image=request.FILES['file[]'])
            attachment_file.save()
            print '---------attachment_file.star_image_id------------',attachment_file.star_image_id
            data = {'success': 'true', 'attachid': attachment_file.star_image_id}
            print data
        else:
            data = {'success': 'false'}
            print data
    except MySQLdb.OperationalError, e:
        data = {'success': 'invalid request'}
    return HttpResponse(json.dumps(data), content_type='application/json')


def save_attachments(attachment_list, star_id):
    try:
        data={}
        print '-------attachment_list------',attachment_list
        print '-------star_id------',star_id
        if attachment_list != '':
            attachment_list = attachment_list.split(',')
            attachment_list = filter(None, attachment_list)
            print attachment_list
            for attached_id in attachment_list:
                attachment_obj = StarImage.objects.get(star_image_id=attached_id)
                attachment_obj.star_id = star_id
                attachment_obj.save()

            data = {'success': 'true'}
        else:
            pass
    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')


# def get_advert_images(request):
#     advert_id = request.GET.get('advert_id')
#     image_list = []
#     advert_image = AdvertImage.objects.filter(advert_id=advert_id)
#     for images in advert_image:
#         image_path = images.advert_image.url
#         filesize = os.stat('/home/admin1/Prod_backup/DigiSpace/' + images.advert_image.url).st_size
#         image_size = round(filesize,2) #/ float(1024)
#         image_path = image_path.split('/')
#         image_name = image_path[-1]
#         image_url = SERVER_URL + images.advert_image.url
#         image_id = images.advert_image_id
#         advert_image_data = {
#             "image_url": image_url,
#             "image_size": image_size,
#             "image_name": image_name,
#             "image_id": image_id,
#             "image_thumbnail": '/home/admin1/Prod_backup/DigiSpace/' + images.advert_image.url
#         }
#         image_list.append(advert_image_data)
#     data = {'data': 'true','image_list':image_list}
#     return HttpResponse(json.dumps(data), content_type='application/json')

def uploaded_images(request):
    try:
        print '----------in uploaded images--',request.GET.get('star_id')
        star_id = request.GET.get('star_id')
        image_list = []
        advert_image = StarImage.objects.filter(star_id=star_id)
        print '-----------advert image--------',advert_image
        for images in advert_image:
            image_path = images.star_image.url
            filesize = os.stat('/home/ec2-user/DigiSpace/' + images.star_image.url).st_size
            image_size = round(filesize,2)
            image_path = image_path.split('/')
            image_name = image_path[-1]
            image_id = images.star_image_id
            image_url = SERVER_URL + images.star_image.url
            advert_image_data = {
                "image_url": image_url,
                "image_id":image_id,
                "image_path": SERVER_URL + images.star_image.url,
                "image_size": image_size,
                "image_name": image_path[-1],
                "image_thumbnail": '/home/ec2-user/DigiSpace/' + images.star_image.url
            }
            image_list.append(advert_image_data)
        data = {'image_list': image_list}
        print '---------data- upload images-----',data
    except Exception, e:
        print 'Exception :', e
        data = {'data': 'none'}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def remove_star_image(request):
    print "in the remove image-----------",request.GET.get('image_id')
    print request.GET
    try:
        image_id = request.GET.get('image_id')
        image = StarImage.objects.get(star_image_id=image_id)
        image.delete()

        data = {'success': 'true'}
    except MySQLdb.OperationalError, e:
        data = {'success': 'false'}
    return HttpResponse(json.dumps(data), content_type='application/json')


