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

SERVER_URL = "http://52.40.205.128"
#SERVER_URL = "http://52.66.144.182"
#SERVER_URL = "http://192.168.0.125:8011"

#CTI CRM APIs=============================================================================

def citystar(request):
    return render(request,'City_Star/star_home.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def starhome(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        print '-----------city obj-----',request.GET.get('city_id')
        city_obj_id = request.GET.get('city_id')
        city_name_obj = City_Place.objects.get(city_place_id=request.GET.get('city_id'))
        city_name = city_name_obj.city_id.city_name

        sts_value = request.GET.get('sts_val')
        print '-------sts_value------',sts_value

        if request.GET.get('sts_val'):
            if request.GET.get('sts_val') =='1' or request.GET.get('sts_val')=='0':
                sts = request.GET.get('sts_val')
                user_obj = CityStarDetails.objects.filter(city=request.GET.get('city_id'),status=sts)
                print '-----------user obj--in if---',user_obj

            else:
                user_obj = CityStarDetails.objects.filter(city=request.GET.get('city_id'))
                print '-----------user obj-- in else 1---',user_obj
        else:
            user_obj = CityStarDetails.objects.filter(city=request.GET.get('city_id'))
            print '-----------user obj---in eles--',user_obj

        star_list=[]
        data={}
        star_count = len(user_obj)

        for obj in user_obj:
            print '-------obj-----',obj
            print '-------image-------',obj.image
            print '-------city-------',obj.city
            print '-----------datetime now---------',datetime.now().strftime("%d/%m/%Y")
            print '-----------end time now---------',obj.end_date.strftime("%d/%m/%Y")
            sdate = obj.start_date.strftime("%d/%m/%Y")
            tdate = datetime.now().strftime("%d/%m/%Y")
            edate = obj.end_date.strftime("%d/%m/%Y")
            if tdate == edate :
                obj.status = '0'
                obj.save()
            if tdate == sdate :
                obj.status = '1'
                obj.save()
            if obj.start_date.strftime("%d/%m/%Y"):
                start_date = obj.start_date.strftime("%d/%m/%Y")
            else:
                start_date = ''
            star={'id':obj.citystarID,'title':obj.title,
                       'name':obj.name,
                       'summary':obj.summary,
                       'image':SERVER_URL + obj.image.url,
                       'city':obj.city,
                       'start_date':start_date,
                       'end_date':obj.end_date.strftime("%d/%m/%Y"),
                       'likes':obj.likes,
                       'views':obj.views,
                       'status':obj.status,
                       'favourites':obj.favourites,
                       'shares':obj.shares
            }

            star_list.append(star)
        data={'username':request.session['login_user'],'star_list':star_list,'city_id':str(city_obj_id),'city_name':str(city_name),'star_count':star_count}
        print data
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
            print '------c-------',c
            city=c.city_id.city_name
            country = c.country_id.country_name
            if c.city_image:
                image=SERVER_URL + c.city_image.url
                print '---------image----',image
            else:
                image=''
            #country = c.state_id.

            #city_list={'city':city,'city_id':c,'image':image}
            #citylist.append(city_list)
            #if CityStarDetails.objects.get(city=c,status='1'):
            try:
                user_obj = CityStarDetails.objects.get(city=c,status='1')
                print '-----------user obj-----',user_obj
                #for obj in user_obj:
                #print '-------obj-----',obj
                #print '-------status-------',obj.status
                #if obj.status == '1':

                #if user_obj.end_date == datetime.now()
                print '-----------------i----------'
                sid=user_obj.citystarID
                print '------sid-----',sid
                stitle=user_obj.title
                sstatus=user_obj.status
                sname=user_obj.name
                ssummary=user_obj.summary
                simage=SERVER_URL + user_obj.image.url
                scity=user_obj.city.city_id.city_name
                slikes=user_obj.likes
                sviews=user_obj.views
                sshares=user_obj.shares
                # star={'id':user_obj.citystarID,'title':user_obj.title,'status':user_obj.status,
                #            'name':user_obj.name,
                #            'summary':user_obj.summary,
                #            'image':SERVER_URL + user_obj.image.url,
                #            'city':user_obj.city.city_id.city_name,
                #            'likes':user_obj.likes,
                #            'views':user_obj.views,
                #            'favourites':user_obj.favourites,
                #            'shares':user_obj.shares
                # }

                #star_list.append(star)
                #'country':country,
                star={'country':country,'city':city,'city_id':c,'cimage':image,'id':sid,'title':stitle,'status':sstatus,'name':sname,
                  'summary':ssummary,'image':simage,'likes':slikes,'views':sviews,'shares':sshares}
                star_list.append(star)
            except:
                print '--------in else--------'
                star={'country':country,'city':city,'city_id':c,'cimage':image,'id':'','title':'','status':'','name':'',
                  'summary':'','image':'','likes':'','views':'','shares':''}
                star_list.append(star)
        print star_list
        data={'username':request.session['login_user'],'star_list':star_list}
        print data
        return render(request,'City_Star/citystar_home.html',data)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_citystar(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        print '-------city id---------',request.GET.get('city_id')
        data={'username':request.session['login_user'],'city_id':request.GET.get('city_id')}
        return render(request,'City_Star/add_citystar.html',data)

def addcitystar(request):
    return render(request,'City_Star/addcitystar.html')

def activate_citystar(request):
    print '---------star id--------',request.GET.get('star_id')

    print '---------deactivate date--------',request.GET.get('ddate')

    star_obj = CityStarDetails.objects.get(citystarID=request.GET.get('star_id'))
    print '------star_obj------',star_obj
    city_id = star_obj.city
    print '-------city id-----',city_id
    # if CityStarDetails.objects.get(status='1',city=city_id):
    #     #CityStarDetails.objects.get(status='1',city=city_id)
    #     act_star_obj = CityStarDetails.objects.get(status='1',city=city_id)
    #     print '------activate star id-----',act_star_obj
    #     act_star_obj.status = '0'
    #     act_star_obj.end_date=datetime.now()
    #     act_star_obj.save()
    #     print '-----------star 0-----'
    # else:
    #     print '-------in else-------'
    #     pass

    try:
        #CityStarDetails.objects.get(status='1',city=city_id)
        act_star_obj = CityStarDetails.objects.get(status='1',city=city_id)
        print '------activate star id-----',act_star_obj
        act_star_obj.status = '0'
        act_star_obj.end_date=datetime.now()
        act_star_obj.save()
        print '-----------star 0-----'
    except:
        star_obj.status='1'
        star_obj.start_date = datetime.now()
        #star_obj.end_date = request.GET.get('ddate')
        star_obj.end_date = datetime.strptime(request.GET.get('ddate'),"%d/%m/%Y")
        star_obj.save()
        print '-----------star 1-----'
        data = {'success': 'true','city_id':str(city_id)}
        return HttpResponse(json.dumps(data), content_type='application/json')

    star_obj.status='1'
    star_obj.start_date = datetime.now()
    #star_obj.end_date = request.GET.get('ddate')
    star_obj.end_date = datetime.strptime(request.GET.get('ddate'),"%d/%m/%Y")
    star_obj.save()
    print '-----------star 1-----'

    data = {'success': 'true','city_id':str(city_id)}
    return HttpResponse(json.dumps(data), content_type='application/json')

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
        str_obj = StarImage.objects.filter(star_id=request.GET.get('star_id'))
        print '----------star obj------',str_obj
        for s in str_obj:
            print '----------starobj-------',s
            si_list.append(s)

        #for obj in user_obj:

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
        if obj.likes:
            likes = obj.likes
        else:
            likes=''
        if obj.views:
            views = obj.views
        else:
            views=''
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
                   'start_date':obj.start_date.strftime("%d/%m/%Y"),
                   'end_date':obj.end_date.strftime("%d/%m/%Y"),
                   'status':obj.status,
                   'likes':likes,
                   'views':views,
                   'favourites':obj.favourites,
                   'shares':shares,
                   'si_list':si_list,
                   'img':s
        }
        #print '-------star_obj attachments-----',obj.attachment_list
        print data
        return render(request,'City_Star/edit_citystar.html',data)

@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_citystar(request):
    print '---------image file--------',request.POST.get('display_image1')
    data={}
    #print '---------user_img file--------',request.POST.get('user_img')
    city_obj = City_Place.objects.get(city_place_id=request.POST.get('city'))
    print '---------city_obj--------',city_obj
    print '---------city_place_id obj--------',city_obj.city_place_id
    try:
        print '------in try--------'
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
        star_obj.occupation = request.POST.get('occupation')
        star_obj.description = request.POST.get('abs')
        star_obj.achievements = request.POST.get('achievements')
        star_obj.status = request.POST.get('status')
        star_obj.likes = request.POST.get('likes')
        star_obj.views = request.POST.get('views')
        star_obj.shares = request.POST.get('shares')
        try :
            star_obj.image = request.FILES['display_image']
        except:
            star_obj.image = request.POST.get('display_image1')
        star_obj.start_date = datetime.strptime(request.POST.get('activate_date'),"%d/%m/%Y")
        star_obj.end_date = datetime.strptime(request.POST.get('deactivate_date'),"%d/%m/%Y")
        star_obj.updation_date = datetime.now()

        star_obj.save()

        print '--------star id------',star_obj
        print '--------city 0d-----',city_obj
        print '----------attachments------------',request.POST.get('attachments')
        attachment_list = []
        attachment_list = request.POST.get('attachments')
        save_attachments(attachment_list, star_obj)
        print '--------attachment list-------',attachment_list
        data = {'username':request.session['login_user'],'success': 'true','city_place_obj':city_obj.city_place_id,'city_id':str(city_obj),'star_id':str(star_obj)}

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
               'likes':obj.likes,
               'views':obj.views,
               'favourites':obj.favourites,
               'shares':obj.shares
    }
    print data
    return render(request,'City_Star/view_star_profile.html',data)

def search_star(request):
    print '-----keywords---------',request.POST.get('keyword')

@csrf_exempt
def save_citystar(request):
    cst_obj = CityStarDetails.objects.get(status='1',city=request.POST.get('city'))
    print '-------cst_obj--------',cst_obj
    try:
        cst_act_obj = CityStarDetails.objects.filter(start_date=request.POST.get('activate_date'),city=request.POST.get('city'))
        print '--------cstar act date------',cst_act_obj
    except:
        cst_act_obj = ''
    status_val = ''
    print '---------status--------',request.POST.get('status')
    if request.POST.get('status') == 'status_1':
        status_val = '1'
        cst_obj.status='0'
        cst_obj.end_date=datetime.now()
        cst_obj.save()
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
            occupation = request.POST.get('occupation'),
            description = request.POST.get('description'),
            achievements = request.POST.get('achievements'),
            image = request.FILES['display_image'],
            city = city_obj,
            start_date = datetime.strptime(request.POST.get('activate_date'),"%d/%m/%Y"),
            #end_date = request.POST.get('deactivate_date'),
            end_date = datetime.strptime(request.POST.get('deactivate_date'),"%d/%m/%Y"),
            status = status_val,
            likes = '0',
            views = '0',
            favourites = request.POST.get('favourites'),
            shares = '0',
            creation_date = datetime.now(),
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

def uploaded_images(request):
    try:
        print '----------in uploaded images--',request.GET.get('star_id')
        star_id = request.GET.get('star_id')
        image_list = []
        advert_image = StarImage.objects.filter(star_id=star_id)
        for images in advert_image:
            image_path = images.star_image.url
            image_path = image_path.split('/')
            image_id = images.star_image_id
            advert_image_data = {
                "image_id":image_id,
                "image_path": SERVER_URL + images.star_image.url,
                "image_size": "12345",
                "image_name": image_path[-1]
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