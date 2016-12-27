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
import urllib2
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
import Image
#importing exceptions
from django.db import IntegrityError
import operator
from django.db.models import Q
from operator import itemgetter
import datetime
from datetime import datetime
from datetime import date, timedelta
from django.views.decorators.cache import cache_control
# HTTP Response
from django.http import HttpResponse
from django.http import HttpResponseRedirect

#SERVER_URL = "http://52.40.205.128"
SERVER_URL = "http://52.66.133.35"
#SERVER_URL = "http://52.66.144.182"
#SERVER_URL = "http://192.168.0.125:8011"



####################.......city_dashboard..........%%%%%%%%%%##########

@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def city_feed(request):
    try:
        data = {}
        final_list = []
        today_post_count = 0
        post_var = 0
        posting_date_old = '2000-01-01'
        category_list=[]
        city_name=''
        total_posts=''
        country_name = ''
        user_pic=''
        cat_val=''
        sts_val=''
        tm_val=''
        post_file_list=[]
        post_list=[]
        img_data={}
        val=''
        tdr=''
        total_post_list_count=''
        try:
            city_obj_id = request.GET.get('city_id')
            city_name_obj = City_Place.objects.get(city_place_id=request.GET.get('city_id'))
            city_name = city_name_obj.city_id.city_name
            city_image = SERVER_URL + city_name_obj.city_image.url
            country_name = city_name_obj.state_id.country_id.country_name

            #if request.GET.get('sts_val'):
            #    if request.GET.get('sts_val') =='unread':
            #        print '-------unread-----'
            #        sts = request.GET.get('sts_val')
            #        post_list = PostDetails.objects.filter(city_id=request.GET.get('city_id'),status=sts)
            #        sts_val = 'Unread'
            #    elif request.GET.get('sts_val') =='appropriate':
            #        print '-------appropriate-----'
            #        sts = request.GET.get('sts_val')
            #        post_list = PostDetails.objects.filter(city_id=request.GET.get('city_id'),status=sts)
            #        sts_val = 'Appropriate'
            #    elif request.GET.get('sts_val') =='inappropriate':
            #        print '-------inappropriate-----'
            #        sts = request.GET.get('sts_val')
            #        post_list = PostDetails.objects.filter(city_id=request.GET.get('city_id'),status=sts)
            #        sts_val = 'Inappropriate'
            #    elif request.GET.get('sts_val') =='deleted':
            #        print '-------deleted-----'
            #        sts = request.GET.get('sts_val')
            #        post_list = PostDetails.objects.filter(city_id=request.GET.get('city_id'),status=sts)
            #        sts_val = 'Deleted by User'
            #    elif request.GET.get('sts_val') =='all':
            #        sts = request.GET.get('sts_val')
            #        post_list = PostDetails.objects.filter(city_id=request.GET.get('city_id'))
            #        sts_val = 'All'
            #elif request.GET.get('cat_val'):
            #    if request.GET.get('cat_val')=='all':
            #        post_list = PostDetails.objects.filter(city_id=request.GET.get('city_id'))
            #        cat_val = 'All'
            #    else:
            #        cat = request.GET.get('cat_val')
            #        cat_obj = citylife_category.objects.get(category_id=cat)
            #        cat_val = cat_obj.category_name
            #        post_list = PostDetails.objects.filter(city_id=request.GET.get('city_id'),citylife_category=cat_obj)

            #elif request.GET.get('time_val'):
            #    if request.GET.get('time_val') =='today' :
            #        td = datetime.now().strftime("%Y-%m-%d")
            #        post_list = PostDetails.objects.filter(city_id=request.GET.get('city_id'),creation_date=td)
            #        tm_val = 'Today'
            #    elif request.GET.get('time_val')=='yesterday':
            #        yd = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            #        post_list = PostDetails.objects.filter(city_id=request.GET.get('city_id'),creation_date=yd)
            #        tm_val = 'Yesterday'
            #    elif request.GET.get('time_val')=='last_week':
            #        tim = request.GET.get('time_val')
            #        last_date = (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d")
            #        current_date = datetime.now().strftime("%Y-%m-%d")
            #        post_list = PostDetails.objects.filter(city_id=request.GET.get('city_id'),creation_date__range=[last_date,current_date])
            #        tm_val = 'Last Week'
            #    elif request.GET.get('time_val') =='all':
            #        post_list = PostDetails.objects.filter(city_id=request.GET.get('city_id'))
            #else :
            #    post_list = PostDetails.objects.filter(city_id=request.GET.get('city_id'))

            #----------------------------filter updation-------------------
            #if request.GET.get('time_val') =='today' :
            #    td = datetime.now().strftime("%Y-%m-%d")
            #elif request.GET.get('time_val')=='yesterday':
            #    td = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            #elif request.GET.get('time_val')=='last_week':
            #    tim = request.GET.get('time_val')
            #    last_date = (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d")
            #    current_date = datetime.now().strftime("%Y-%m-%d")
            #    tdr = [last_date,current_date]
            #else:
            #    td=''

            if request.GET.get('time_val') =='today' :
                past_date = date.today() + timedelta(1)
                past_date = past_date.strftime("%Y-%m-%d 00:00:00")

                tdate = datetime.now()
                tdate = tdate.strftime("%Y-%m-%d 00:00:00")

                td = [tdate,past_date]

            elif request.GET.get('time_val')=='yesterday':
                past_date = date.today() - timedelta(1)
                past_date = past_date.strftime("%Y-%m-%d 00:00:00")

                ydate = datetime.now()
                ydate = ydate.strftime("%Y-%m-%d 00:00:00")

                td = [past_date,ydate]

            elif request.GET.get('time_val')=='last_week':
                tim = request.GET.get('time_val')
                last_date = (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d 00:00:00")
                current_date = datetime.now()+ timedelta(1)
                current_date = current_date.strftime("%Y-%m-%d 00:00:00")
                tdr = [last_date,current_date]
                print '---------tdr------',tdr
            else:
                td=''

            if request.GET.get('sts_val')=='all':
                sts = ''
            else:
                sts = request.GET.get('sts_val')

            if request.GET.get('cat_val')=='all':
                cat_obj = ''
            elif request.GET.get('cat_val')=='None':
                cat_obj = ''
            else:
                try:
                    if request.GET.get('cat_val')=='':
                        print '-------------1111111------'
                        cat_obj=''
                    else:
                        print '-------------1222------'
                        cat_obj = citylife_category.objects.get(category_id=request.GET.get('cat_val'))
                except:
                    cat_obj=''
                    pass

            if request.GET.get('sts_val') and request.GET.get('cat_val') and request.GET.get('time_val'):
                print '-------------13------'
                if tdr:
                    print '-------------14------',tdr
                    if cat_obj == '':
                        print '-------------1411------'
                        post_list = PostDetails.objects.filter(city_id=request.GET.get('city_id'),status=sts,creation_date__range=tdr)
                        sts_val = sts.upper()
                        tm_val = 'LAST WEEK'
                        total_post_list_count = str(post_list.count())
                    else:
                        print '-------------142222------'
                        post_list = PostDetails.objects.filter(city_id=request.GET.get('city_id'),status=sts,citylife_category=cat_obj,creation_date__range=tdr)
                        sts_val = sts.upper()
                        tm_val = 'LAST WEEK'
                        cat_val = cat_obj.category_name.upper()
                        total_post_list_count = str(post_list.count())
                else:
                    print '-------------15------'
                    if request.GET.get('cat_val')=='all':
                        post_list = PostDetails.objects.filter(city_id=request.GET.get('city_id'),status=sts,creation_date__range=td)
                    else:
                        post_list = PostDetails.objects.filter(city_id=request.GET.get('city_id'),status=sts,citylife_category=cat_obj,creation_date__range=td)
                        cat_val = cat_obj.category_name.upper()
                    sts_val = sts.upper()
                    
                    tm_val = request.GET.get('time_val').upper()
                    total_post_list_count = str(post_list.count())

            elif request.GET.get('cat_val') and request.GET.get('time_val'):
                print '-------------10------'
                if tdr:
                    if cat_obj == '':
                        print '-------------11------'
                        post_list = PostDetails.objects.filter(city_id=request.GET.get('city_id'),creation_date__range=tdr)
                        tm_val = request.GET.get('time_val').upper()
                        total_post_list_count = str(post_list.count())
                    else:
                        post_list = PostDetails.objects.filter(city_id=request.GET.get('city_id'),citylife_category=cat_obj,creation_date__range=tdr)
                        cat_val = cat_obj.category_name.upper()
                        tm_val = 'LAST WEEK'
                        total_post_list_count = str(post_list.count())
                else:
                    print '-------------12------'
                    post_list = PostDetails.objects.filter(city_id=request.GET.get('city_id'),citylife_category=cat_obj,creation_date__range=td)
                    cat_val = cat_obj.category_name.upper()
                    tm_val = request.GET.get('time_val').upper()
                    total_post_list_count = str(post_list.count())

            elif request.GET.get('sts_val') and request.GET.get('time_val'):
                print '-------------7------'
                if tdr:
                    print '-------------8------'
                    if request.GET.get('sts_val')=='all':
                        post_list = PostDetails.objects.filter(city_id=request.GET.get('city_id'),creation_date__range=tdr)
                    else:
                        post_list = PostDetails.objects.filter(city_id=request.GET.get('city_id'),status=sts,creation_date__range=tdr)
                    sts_val = sts.upper()
                    tm_val = 'LAST WEEK'
                    total_post_list_count = str(post_list.count())
                else:
                    print '-------------9------'
                    if request.GET.get('sts_val')=='all':
                        post_list = PostDetails.objects.filter(city_id=request.GET.get('city_id'),creation_date__range=td)
                    else:
                        post_list = PostDetails.objects.filter(city_id=request.GET.get('city_id'),status=sts,creation_date__range=td)
                    sts_val = sts.upper()
                    tm_val = request.GET.get('time_val').upper()
                    total_post_list_count = str(post_list.count())

            #elif request.GET.get('sts_val') and request.GET.get('cat_val'):
            elif sts and cat_obj:
                print '-------------6------'
                post_list = PostDetails.objects.filter(city_id=request.GET.get('city_id'),status=sts,citylife_category=cat_obj)
                sts_val = sts.upper()
                cat_val = cat_obj.category_name.upper()
                total_post_list_count = str(post_list.count())

            elif request.GET.get('sts_val'):
                print '-------------1------'
                if request.GET.get('sts_val')=='all':
                    post_list = PostDetails.objects.filter(city_id=request.GET.get('city_id'))
                    total_post_list_count = str(post_list.count())
                else:
                    post_list = PostDetails.objects.filter(city_id=request.GET.get('city_id'),status=sts)
                    sts_val = sts.upper()
                    total_post_list_count = str(post_list.count())

            elif request.GET.get('cat_val'):
                print '-------------2------'
                if cat_obj == '':
                    post_list = PostDetails.objects.filter(city_id=request.GET.get('city_id'))
                    total_post_list_count = str(post_list.count())
                else:
                    post_list = PostDetails.objects.filter(city_id=request.GET.get('city_id'),citylife_category=cat_obj)
                    cat_val = cat_obj.category_name.upper()
                    total_post_list_count = str(post_list.count())

            elif request.GET.get('time_val'):
                print '-------------3------'
                if tdr:
                    print '-------------4------'
                    post_list = PostDetails.objects.filter(city_id=request.GET.get('city_id'),creation_date__range=tdr)
                    tm_val = 'LAST WEEK'
                    total_post_list_count = str(post_list.count())
                else:
                    print '-------------5------',td
                    post_list = PostDetails.objects.filter(city_id=request.GET.get('city_id'),creation_date__range=td)
                    tm_val = request.GET.get('time_val').upper()
                    total_post_list_count = str(post_list.count())

            else :
                print '-------------16------'
                post_list = PostDetails.objects.filter(city_id=request.GET.get('city_id'))
                total_post_list_count = str(post_list.count())

            category_list_obj = citylife_category.objects.filter(status='1').order_by('category_name')

            total_posts = str(PostDetails.objects.all().count())


            current_date = datetime.now()
            year = current_date.year
            month = current_date.month
            day = current_date.day

            past_date = datetime(year, month, day)

            todays_posts_count = str(PostDetails.objects.filter(creation_date__range=[past_date,datetime.now()]).count())
            print '-------------todays_posts_count------------',todays_posts_count




            server_url = SERVER_URL
            today_date = datetime.now().strftime("%d/%m/%Y")
            if post_list:
                for obj in post_list:
                    post_id = obj.post_id
                    print '---------post_id==================',post_id
                    post_mood = obj.mood
                    description = obj.description
                    user_name = obj.user_id.consumer_full_name
                    if obj.user_id.consumer_profile_pic:
                        user_pic = SERVER_URL + obj.user_id.consumer_profile_pic.url
                    else:
                        user_pic = ''

                    creation_date = obj.creation_date.strftime("%d %b.%y  %I:%M %P")
                    status = obj.status
                    if status == 'inappropriate':
                        dact_date = obj.deleted_date.strftime("%B %d, %Y  %I:%M %P")
                    elif status == 'deleted':
                        dact_date = obj.deleted_date.strftime("%B %d, %Y  %I:%M %P")
                    else:
                        status == ''
                        dact_date=''

                    unread_comment_count = PostComments.objects.filter(post_id=obj,comment_status='unread').count()
                    total_comment_count = PostComments.objects.filter(post_id=obj).count()
                    print '-------------total comments--------',total_comment_count

                    city_name = obj.city_id.city_id.city_name
                    #country_name = obj.country_id.country_id.country_name
                    category_name = obj.citylife_category.category_name
                    city_image = SERVER_URL + obj.city_id.city_image.url

                    try:
                        post_files = PostFile.objects.filter(post_id=obj)
                        post_files_count = PostFile.objects.filter(post_id=obj).count()
                        print '--------post_files----',post_files
                        print '--------post_files--count--',post_files_count
                        slider_width_val = (post_files_count * 201) + 35
                        print '------------slider val-----',slider_width_val
                        for fl in post_files:
                            #img_path = '/home/hduser/New_Projects/1_9_2016/DigiSpace'+fl.post_file
                            img_path = '/home/ec2-user/DigiSpace/'+fl.post_file.url
                            print '--------img_path--------',img_path
                            try:
                                img = Image.open(img_path)
                                print '----------------img---------',img
                                img_format = 'img'
                            except:
                                print '-----------no image--------'
                                img_format = 'vdo'
                            img_data={'img_post_id':post_id,'img_format':img_format,'img_path':SERVER_URL + fl.post_file.url}
                            post_file_list.append(img_data)

                    except:
                        post_files = ''

                    print '--------------post_file_list--------------',post_file_list

                    country_name = obj.country_id.country_name
                    slike= str(PostMood.objects.filter(post_id=obj.post_id,status='like').count())
                    sdislike= str(PostMood.objects.filter(post_id=obj.post_id,status='dislike').count())
                    sview= str(PostView.objects.filter(post_id=obj.post_id).count())
                    #sreview= str(PostReview.objects.filter(post_id=obj.post_id).count())
                    sshare= obj.share

                    post_like_count = PostMood.objects.filter(status = "like",post_id=obj.post_id).count()
                    post_dislike_count = PostMood.objects.filter(status = "dislike",post_id=obj.post_id).count()
                    if post_dislike_count == 0 and post_like_count == 0:
                        dislike_like_percentage = 50
                    else:
                        dislike_like_percentage = (float(post_like_count)/float(PostMood.objects.filter(post_id=obj.post_id).count()))*100

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


                    post_data = {
                        'city_name':city_name,
                        'city_image':city_image,
                        'country_name':country_name,
                        'post_mood':post_mood,
                        'description':description,
                        'user_name':user_name,
                        'category_name':category_name,
                        'user_pic':user_pic,
                        'creation_date':creation_date,
                        'status':status,
                        'status1':status.upper(),
                        'post_id':post_id,
                        'share':sshare,
                        'likes':slike,
                        'mood':mood,
                        'views':sview,
                        'dislike':sdislike,
                        'dact_date':dact_date,
                        'post_files':post_files,
                        'post_file_list':post_file_list,
                        'post_files_count':post_files_count,
                        'slider_width_val':slider_width_val,
                        'unread_comment_count':unread_comment_count,
                        'total_comment_count':total_comment_count,

                    }
                    final_list.append(post_data)
                    finallist = sorted(final_list, key=itemgetter('post_id'),reverse=True)

                data = {'username':request.session['login_user'],'success':'true','total_post_list_count':total_post_list_count,'final_list':finallist,'server_url':server_url,'tm_val':tm_val,'sts_val':sts_val,'cat_val':cat_val,'city_id':city_obj_id,'country_name':country_name,'city_name':city_name,'city_image':city_image,'category_list':category_list_obj,'todays_posts_count':todays_posts_count,'total_posts':total_posts}

            else:
                data = {'username':request.session['login_user'],'success':'false','total_post_list_count':total_post_list_count,'city_id':city_obj_id,'tm_val':tm_val,'sts_val':sts_val,'cat_val':cat_val,'country_name':country_name,'city_image':city_image,'city_name':city_name,'category_list':category_list_obj,'todays_posts_count':todays_posts_count,'total_posts':total_posts}
        except IntegrityError as e:
            print e
            data = {'username':request.session['login_user'],'success':'false','message':'Error in  loading page. Please try after some time','username':request.session['login_user']}
    except MySQLdb.OperationalError, e:
        print e
    except Exception,e:
        print 'Exception ',e

    #print data
    return render(request,'City_Life/city-feed.html',data)

def view_comments(request):
    data = {}
    final_list = []
    reply_list = []
    reply_list1 = []
    comments_list=[]
    comments_list1=[]
    pf_list = []
    status=''
    poc_id = ''
    uname = ''
    cdate = ''
    comment = ''
    cmt_count_value = ''
    newlist=''
    new_reply_list=''
    reply_count=0
    rid = ''
    rname = ''
    rdate = ''
    reply = ''
    rstatus = ''
    rd_date = ''
    rlikes = ''
    rply_cnt_val = ''

    post_obj = PostDetails.objects.get(post_id=request.GET.get('post_id'))
    print '------------------post object------------',post_obj
    try:
        server_url = SERVER_URL
        post_id = post_obj.post_id
        print '------------------post id------------',post_id

        if post_obj.status == 'unread':
            print '--------in unread if----------'
            post_obj.status = 'appropriate'
            post_obj.save()
        elif post_obj.status == 'inappropriate':
            print '--------in inappropriate elif----------'
            post_obj.status = 'inappropriate'
            post_obj.save()
        else:
            print '--------in else----------'
            pass

        post_status=post_obj.status

        description = post_obj.description
        user_name = post_obj.user_id.consumer_full_name
        if post_obj.user_id.consumer_profile_pic:
            user_pic = SERVER_URL + post_obj.user_id.consumer_profile_pic.url
        else:
            user_pic = ''

        category_name = post_obj.citylife_category.category_name
        creation_date = post_obj.creation_date.strftime("%d %b.%y  %I:%M %P")

        try:
            post_files = PostFile.objects.filter(post_id=post_obj)
            print '------------------post post_files------------',post_files
            pf_file_count = PostFile.objects.filter(post_id=post_obj).count()
            img_number = 0
            for fl in post_files:
                print '--------in fl-------'
                #img_path = '/home/hduser/New_Projects/1_9_2016/DigiSpace'+fl.post_file
                img_path = '/home/ec2-user/DigiSpace/'+fl.post_file.url
                print '--------img_path--------',img_path
                try:
                    img = Image.open(img_path)
                    print '----------------img---------',img
                    img_format = 'img'
                    print '--------------in fl2---------'
                except:
                    print '-----------no image--------'
                    img_format = 'vdo'
                img_number=img_number+1
                img_data={'img_number':img_number,'p_id':post_id,'img_format':img_format,'img_path':SERVER_URL + fl.post_file.url}
                pf_list.append(img_data)
                print '------------pf list---------',pf_list


        except:
            post_files = ''
        slike= str(PostMood.objects.filter(post_id=post_obj.post_id,status='like').count())
        sdislike= str(PostMood.objects.filter(post_id=post_obj.post_id,status='dislike').count())
        sview= str(PostView.objects.filter(post_id=post_obj.post_id).count())
        #sreview= str(PostReview.objects.filter(post_id=post_obj.post_id).count())
        scomments = PostComments.objects.filter(post_id=post_obj)
        #scomments= PostComments.objects.filter(post_id=post_obj).latest('comment_id')
        cmt_count = PostComments.objects.filter(post_id=post_obj).count()
        print '-------------comment count----------',cmt_count
        comment_count = cmt_count
        if cmt_count>2:
            cmt_count_value=cmt_count-2
        #    print '---------comment count------',comment_count
        #else:
        #    comment_count = cmt_count
        inumber = 0
        for s in scomments:
            inumber = inumber+1
            poc_id = s.comment_id
            uname = s.user_id.consumer_full_name
            cdate = s.creation_date.strftime("%d %b.%y  %I:%M %P")
            if s.updated_date:
                cdate = s.updated_date.strftime("%d %b.%y  %I:%M %P")
            comment = s.comment
            status = s.status
            print '-----------status-----',status
            ddate = ''
            if status == "0":
                ddate = s.deleted_date.strftime("%d %b.%y  %I:%M %P")

            if s.user_id.consumer_profile_pic:
                upic = SERVER_URL + s.user_id.consumer_profile_pic.url
            else:
                upic = ''

            clikes = str(LikeDislikeComment.objects.filter(comment_id=s.comment_id,status='like').count())

            reply_count = PostReplys.objects.filter(comment_id = s).count()

            if reply_count>2:
                rply_cnt_val = reply_count-2
                print '-----------reply count----------',rply_cnt_val
            # else:
            #     rply_cnt = reply_count
            #     print '-----------reply count----------',rply_cnt

            reply_list=[]
            new_reply_list=[]

            post_reply__obj = PostReplys.objects.filter(comment_id = s)
            reply_count = str(PostReplys.objects.filter(comment_id = s).count())
            reply_list=[]
            new_reply_list=[]
            for reply_obj in post_reply__obj:
                rid = reply_obj.reply_id
                print '----------------r id------',rid
                comment_id=s.comment_id
                rname = reply_obj.user_id.consumer_full_name
                rdate = reply_obj.creation_date.strftime("%d %b.%y - %I.%M%P")
                reply = reply_obj.reply
                rstatus = reply_obj.status
                rd_date=''
                if rstatus=='0':
                    rd_date = reply_obj.deleted_date.strftime("%d %b.%y - %I:%M%P")
                if reply_obj.user_id.consumer_profile_pic:
                    rpic = SERVER_URL + reply_obj.user_id.consumer_profile_pic.url
                else:
                    rpic = ''
                #print '-------poc_id-------',poc_id

                rlikes = str(LikeDislikeReply.objects.filter(reply_id=reply_obj.reply_id,status='like').count())

                rply_data = {'rname':rname,'rdate':rdate,'reply':reply,'comment_id':comment_id,'rstatus':rstatus,'rd_date':rd_date,'rpic':rpic,'poc_id':poc_id,'rlikes':rlikes,'rid':rid}
                reply_list.append(rply_data)

                newlist1 = sorted(reply_list, key=itemgetter('rid'),reverse=True)
                reply_list1 = newlist1[:2]

                #reply_list1.append(rply_data)
                new_reply_list = sorted(reply_list, key=itemgetter('rid'),reverse=True)
                new_reply_list = new_reply_list[2:]

            print '--------------reply count------------',len(reply_list),len(new_reply_list)


            cm_data = {'uname':uname,'cdate':cdate,'reply_list':reply_list1,'new_reply_list':new_reply_list,'comment':comment,'upic':upic,'poc_id':poc_id,'status_val':status,'ddate':ddate,'clikes':clikes,'rply_cnt_val':rply_cnt_val,'reply_count':reply_count}
            comments_list.append(cm_data)
            newlist = sorted(comments_list, key=itemgetter('poc_id'),reverse=True)
            comments_list = newlist[:2]

            comments_list1.append(cm_data)
            newlist = sorted(comments_list1, key=itemgetter('poc_id'),reverse=True)
            newlist = newlist[2:]


            #post_reply__obj = PostReplys.objects.filter(comment_id = s)
            #reply_count = str(PostReplys.objects.filter(comment_id = s).count())
            #for reply_obj in post_reply__obj:
            #    rid = reply_obj.reply_id
            #    rname = reply_obj.user_id.consumer_full_name
            #    rdate = reply_obj.creation_date.strftime("%d %b.%y  %I:%M %P")
            #    reply = reply_obj.reply
            #    rstatus = reply_obj.status
            #    rd_date = ''
            #    if rstatus == "0":
            #        rd_date = reply_obj.deleted_date.strftime("%d %b.%y  %I:%M %P")
            #    if reply_obj.user_id.consumer_profile_pic:
            #        rpic = SERVER_URL + reply_obj.user_id.consumer_profile_pic.url
            #    else:
            #        rpic = ''
            #
            #    rlikes = str(LikeDislikeReply.objects.filter(reply_id=reply_obj.reply_id,status='like').count())
            #
            #    rply_data = {'rname':rname,'rdate':rdate,'reply':reply,'rstatus':rstatus,'rd_date':rd_date,'rpic':rpic,'poc_id':poc_id,'rlikes':rlikes,'rid':rid}
            #    reply_list.append(rply_data)
            #
            #    newlist1 = sorted(reply_list, key=itemgetter('rid'),reverse=True)
            #    reply_list = newlist1[:2]
            #
            #    reply_list1.append(rply_data)
            #    new_reply_list = sorted(reply_list1, key=itemgetter('rid'),reverse=True)
            #    new_reply_list = new_reply_list[2:]


        sshare= post_obj.share

        post_data = {
            'success':'true',
            'description':description,
            'user_name':user_name,
            'category_name':category_name,
            'user_pic':user_pic,
            'creation_date':creation_date,
            'status':status,
            'post_status':post_status.upper(),
            'post_status1':post_status,
            'post_id':post_id,
            'share':sshare,
            'likes':slike,
            'dislike':sdislike,
            'views':sview,
            #'review':sreview,
            'post_files':str(post_files),
            'server_url':server_url,
            'uname':uname,
            'cdate':cdate,
            'comment':comment,
            'comment_count':comment_count,
            'cmt_count_value':cmt_count_value,
            'inumber':inumber,
        }
        final_list.append(post_data)
        data = {'success':'true','final_list':final_list,'pf_file_count':pf_file_count,'post_id':post_id,'reply_count':reply_count,'comment_count':comment_count,'comments_list':comments_list,'pf_list':pf_list,'new_comments_list':newlist,'reply_list':reply_list,'new_reply_list':new_reply_list}

    except Exception,e:
        print 'Exception ',e
    return HttpResponse(json.dumps(data), content_type='application/json')

def deactivate_reply(request):
    print '---------reply id--------',request.GET.get('reply_id')
    rp_obj = PostReplys.objects.get(reply_id=request.GET.get('reply_id'))
    print '------reply------',rp_obj
    try:
        rp_obj.status = '0'
        rp_obj.deleted_date=datetime.now()
        rp_obj.save()

        d_date = rp_obj.deleted_date.strftime("%B %d, %Y  %I:%M %P")
        print '-------d date-----',d_date
    except:
        pass
    data = {'success': 'true','d_date':d_date,'reply_id':request.GET.get('reply_id')}
    return HttpResponse(json.dumps(data), content_type='application/json')


def deactivate_comment(request):
    print '---------comment_id id--------',request.GET.get('comment_id')
    cm_obj = PostComments.objects.get(comment_id=request.GET.get('comment_id'))
    print '------comment_id------',cm_obj
    try:
        cm_obj.status = '0'
        cm_obj.deleted_date=datetime.now()
        cm_obj.save()

        d_date = cm_obj.deleted_date.strftime("%B %d, %Y  %I:%M %P")
        print '-------d date-----',d_date
    except:
        pass
    data = {'success': 'true','d_date':d_date,'comment_id':request.GET.get('comment_id')}
    #email_to_commenter(cm_obj)
    #sms_to_commenter(cm_obj)
    return HttpResponse(json.dumps(data), content_type='application/json')


def email_to_commenter(cm_obj):
    print '============in email function---------',cm_obj
    print '-------------user id--------',cm_obj.user_id.consumer_email_id

    cuser_name = cm_obj.user_id.consumer_full_name
    cemail = cm_obj.user_id.consumer_email_id

    pusername = cm_obj.post_id.user_id.consumer_full_name
    title = cm_obj.post_id.title
    pemail = cm_obj.post_id.user_id.consumer_email_id
    print '-----------------post user name-----& email-------',pusername, pemail

    if pemail:
        gmail_user =  "donotreply@city-hoopla.com"
        gmail_pwd =  "Hoopla123#"
        FROM = 'Team CityHoopla <donotreply@city-hoopla.com>'
        TO = [pemail]
        try:
            TEXT = "Dear "+pusername+","+'\n\n'+"Thank you for sharing your views in our CityLife feature. However, after detailed study of your comment, we regret to inform you that it is now marked as inappropriate based on our listing policy. Your comment on the post will not be displayed in CityHoopla anymore."+'\n\n'+"Please write to us at info@city-hoopla.com in case you would like to discuss further."+'\n\n'+"Best Wishes,"+'\n'+"Team CityHoopla"
            SUBJECT = "Inappropriate Post"
            server = smtplib.SMTP("smtpout.asia.secureserver.net", 80)
            server.ehlo()
            server.login(gmail_user, gmail_pwd)
            message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
            server.sendmail(FROM, TO, message)
            server.quit()
        except SMTPException,e:
            print e

    gmail_user =  "donotreply@city-hoopla.com"
    gmail_pwd =  "Hoopla123#"
    FROM = 'Team CityHoopla <donotreply@city-hoopla.com>'
    TO = [cemail]
    try:
        TEXT = "Dear "+cuser_name+","+'\n\n'+"Thank you for sharing your views in our CityLife feature. However, after detailed study of your comment, we regret to inform you that it is now marked as inappropriate based on our listing policy. Your comment on the post will not be displayed in CityHoopla anymore."+'\n\n'+"Please write to us at info@city-hoopla.com in case you would like to discuss further."+'\n\n'+"Best Wishes,"+'\n'+"Team CityHoopla"
        SUBJECT = "Inappropriate Post"
        server = smtplib.SMTP("smtpout.asia.secureserver.net", 80)
        server.ehlo()
        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException,e:
        print e


def sms_to_commenter(cm_obj):
    print '============in sms function---------'
    print '-------------user id--------',cm_obj.user_id.consumer_contact_no

    description=''
    user_name = cm_obj.user_id.consumer_full_name
    mobile_number = cm_obj.user_id.consumer_contact_no

    pusername = cm_obj.post_id.user_id.consumer_full_name
    pmobile_number = cm_obj.post_id.user_id.consumer_contact_no
    title = cm_obj.post_id.title
    print '-----------------post user name-----& email-------',pusername, pmobile_number

    if pmobile_number:
        authkey = "118994AIG5vJOpg157989f23"
        mobiles = pmobile_number
        message = "Dear "+pusername+","+'\n\n'+"Thank you for sharing your views in our CityLife feature. However, after detailed study of your comment, we regret to inform you that it is now marked as inappropriate based on our listing policy. Your comment on the post will not be displayed in CityHoopla anymore."+'\n\n'+"Please write to us at info@city-hoopla.com in case you would like to discuss further."+'\n'+"Best Wishes,"+'\n'+"Team CityHoopla"
        sender = "CTHPLA"
        route = "4"
        country = "91"
        values = {
                  'authkey' : authkey,
                  'mobiles' : mobiles,
                  'message' : message,
                  'sender' : sender,
                  'route' : route,
                  'country' : country
                  }

        url = "http://api.msg91.com/api/sendhttp.php"
        postdata = urllib.urlencode(values)
        req = urllib2.Request(url, postdata)
        response = urllib2.urlopen(req)
        output = response.read()
        print output


    authkey = "118994AIG5vJOpg157989f23"
    mobiles = mobile_number
    message = "Dear "+user_name+","+'\n\n'+"Thank you for sharing your views in our CityLife feature. However, after detailed study of your comment, we regret to inform you that it is now marked as inappropriate based on our listing policy. Your comment on the post will not be displayed in CityHoopla anymore."+'\n\n'+"Please write to us at info@city-hoopla.com in case you would like to discuss further."+'\n'+"Best Wishes,"+'\n'+"Team CityHoopla"
    sender = "CTHPLA"
    route = "4"
    country = "91"
    values = {
              'authkey' : authkey,
              'mobiles' : mobiles,
              'message' : message,
              'sender' : sender,
              'route' : route,
              'country' : country
              }

    url = "http://api.msg91.com/api/sendhttp.php"
    postdata = urllib.urlencode(values)
    req = urllib2.Request(url, postdata)
    response = urllib2.urlopen(req)
    output = response.read()
    print output



def deactivate_post(request):
    print '---------post id--------',request.GET.get('post_id')
    post_obj = PostDetails.objects.get(post_id=request.GET.get('post_id'))
    print '------post_obj------',post_obj
    try:
        #act_post_obj = PostFile.objects.get(post_id=request.GET.get('post_id'))
        #print '------activate star id-----',act_post_obj
        post_obj.status = 'inappropriate'
        post_obj.updation_date=datetime.now()
        post_obj.deleted_date=datetime.now()
        post_obj.save()

        d_date = post_obj.deleted_date.strftime("%B %d, %Y  %I:%M %P")
        print '-------d date-----',d_date
        #email_to_poster(post_obj)
        #sms_to_poster(post_obj)
    except:
        pass
    data = {'success': 'true','d_date':d_date,'post_id':request.GET.get('post_id')}
    return HttpResponse(json.dumps(data), content_type='application/json')

def email_to_poster(post_obj):
    print '============in email function---------',post_obj
    print '-------------user id--------',post_obj.user_id.consumer_email_id

    user_name = post_obj.user_id.consumer_full_name
    email = post_obj.user_id.consumer_email_id
    title = post_obj.title

    gmail_user =  "donotreply@city-hoopla.com"
    gmail_pwd =  "Hoopla123#"
    FROM = 'Team CityHoopla <donotreply@city-hoopla.com>'
    TO = [email]
    try:
        TEXT = "Dear "+user_name+","+'\n\n'+"Thank you for posting in our CityLife feature. However, after detailed study of your post, we regret to inform you that it is now marked as inappropriate based on our listing policy. This post will not be displayed in CityHoopla anymore. "+'\n\n'+"Please write to us at info@city-hoopla.com in case you would like to discuss further."+'\n\n'+"Best Wishes,"+'\n'+"Team CityHoopla"
        SUBJECT = "Inappropriate Post"
        server = smtplib.SMTP("smtpout.asia.secureserver.net", 80)
        server.ehlo()
        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException,e:
        print e


def sms_to_poster(post_obj):
    print '============in sms function---------'
    print '-------------user id--------',post_obj.user_id.consumer_contact_no

    user_name = post_obj.user_id.consumer_full_name
    mobile_number = post_obj.user_id.consumer_contact_no
    title = post_obj.title

    authkey = "118994AIG5vJOpg157989f23"
    mobiles = mobile_number
    message = "Dear "+user_name+","+'\n\n'+"Thank you for posting in our CityLife feature. However, after detailed study of your post, we regret to inform you that it is now marked as inappropriate based on our listing policy. This post will not be displayed in CityHoopla anymore. "+'\n\n'+"Please write to us at info@city-hoopla.com in case you would like to discuss further."+'\n'+"Best Wishes,"+'\n'+"Team CityHoopla"
    sender = "CTHPLA"
    route = "4"
    country = "91"
    values = {
              'authkey' : authkey,
              'mobiles' : mobiles,
              'message' : message,
              'sender' : sender,
              'route' : route,
              'country' : country
              }

    url = "http://api.msg91.com/api/sendhttp.php"
    postdata = urllib.urlencode(values)
    req = urllib2.Request(url, postdata)
    response = urllib2.urlopen(req)
    output = response.read()
    print output

def re_activate_post(request):
    print '---------post id--------',request.GET.get('post_id')
    post_obj = PostDetails.objects.get(post_id=request.GET.get('post_id'))
    print '------post_obj------',post_obj
    try:
        #act_post_obj = PostFile.objects.get(post_id=request.GET.get('post_id'))
        #print '------activate star id-----',act_post_obj
        post_obj.status = 'appropriate'
        post_obj.updation_date=datetime.now()
        post_obj.save()

        d_date = post_obj.updation_date.strftime("%B %d, %Y  %I:%M %P")
        print '-------d date-----',d_date
    except:
        pass
    data = {'success': 'true','d_date':d_date,'post_id':request.GET.get('post_id')}
    return HttpResponse(json.dumps(data), content_type='application/json')


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
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def city_life(request):
    try:
        data = {}
        final_list = []
        today_post_count = 0
        post_var = 0
        city_obj=[]
        cntry_name= ''
        file=''
        try:
            if request.GET.get('cntry_val'):
                print '------cntry value------',request.GET.get('cntry_val')
                if request.GET.get('cntry_val') =='1':
                    print '-------in india--------'
                    post_list = PostDetails.objects.filter(country_id=request.GET.get('cntry_val'))
                    state_list = State.objects.filter(country_id=request.GET.get('cntry_val'))
                    print '--------state list------',state_list
                    city_obj = City_Place.objects.filter(state_id__in = state_list)
                    cntry_name = ' India'
                if request.GET.get('cntry_val') =='2':
                    print '------in uae--------'
                    post_list = PostDetails.objects.filter(country_id=request.GET.get('cntry_val'))
                    state_list = State.objects.filter(country_id=request.GET.get('cntry_val'))
                    print '--------state list------',state_list
                    city_obj = City_Place.objects.filter(state_id__in = state_list)
                    cntry_name = ' UAE'
            else:
                print '-------in else-----'
                pass
                #post_list = PostDetails.objects.all()
                #print '........post_details list...ALL....',post_list
                #city_obj = City_Place.objects.all()
                #print '--------city_name_obj obj id------',city_obj
                #cntry_name=''
            for c_obj in city_obj:
                city_id = c_obj
                print '............city_id...............',city_id
                country_name = city_id.state_id.country_id.country_name
                total_unread_posts_count = str(PostDetails.objects.filter(post_status='unread',city_id = city_id).count())

                current_date = datetime.now()
                year = current_date.year
                month = current_date.month
                day = current_date.day

                past_date = datetime(year, month, day)

                todays_posts_count = str(PostDetails.objects.filter(city_id = city_id,creation_date__range=[past_date,datetime.now()]).count())
                print '-------------todays_posts_count------------',todays_posts_count

                if PostDetails.objects.filter(city_id = city_id):
                    print '----------in if ---------'
                    ps_details= PostDetails.objects.filter(city_id = city_id).latest('post_id')

                    print '....LIST BY CITY PARTICULAR....',ps_details
                    city_name = ps_details.city_id.city_id.city_name
                    city_id = ps_details.city_id
                    city_image = SERVER_URL + ps_details.city_id.city_image.url
                    country_name = ps_details.country_id.country_name

                    description = ps_details.title
                    print '---------description------',description
                    user_name = ps_details.user_id.consumer_full_name
                    print '----------user name------',user_name
                    if ps_details.user_id.consumer_profile_pic:
                        user_pic = SERVER_URL + ps_details.user_id.consumer_profile_pic.url
                        print '----------user_pic---------',user_pic
                    else:
                        user_pic = ''

                    creation_date = ps_details.creation_date.strftime("%d %b.%y - %I:%M%P")
                    print '----------creation date------',creation_date

                    cat_name = ps_details.citylife_category.category_name
                    print '--------cat name------',cat_name
                    #file = SERVER_URL + obj.post_id.file.url
                    pid = ps_details.post_id
                    print '----pid------',pid
                    file_obj = PostFile.objects.filter(post_id = pid)
                    print '--------city_name_obj obj id------',file_obj
                    for f in file_obj:
                        print '--------------f----------------------',f
                        file = SERVER_URL + f.post_file.url
                        print '-----------file name-------',file
                    print '-------------------file--------------sdsd',file

                    post_data = {
                        'city_name':city_name,
                        'city_id':city_id,
                        'city_image':city_image,
                        'country_name':country_name,
                        'description':description,
                        'today_post_count':todays_posts_count,
                        'user_name':user_name,
                        'user_pic':user_pic,
                        'creation_date':creation_date,
                        'post_var':total_unread_posts_count,
                        'file':file,
                        'cat_name':cat_name,
                    }
                    final_list.append(post_data)

                    post_var = total_unread_posts_count
                    today_post_count = todays_posts_count

                else :
                    print '----------in else ---------'
                    city_name = city_id.city_id.city_name
                    print '--------city_name---else-----',city_name
                    city_id = city_id
                    city_image = SERVER_URL + city_id.city_image.url
                    #country_name = city_id.country_id.country_name

                    post_data = {
                        'city_name':city_name,
                        'city_id':city_id,
                        'city_image':city_image,
                        'country_name':country_name,
                        'today_post_count':todays_posts_count,
                        'post_var':total_unread_posts_count,
                        'cl_details':'no',
                    }
                    final_list.append(post_data)

                    post_var = total_unread_posts_count
                    today_post_count = 0

            data = {'username':request.session['login_user'],'success':'true','final_list':final_list,'cntry_val':cntry_name,'country_list':get_country(request)
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
        country_objs=Country.objects.filter(country_id=cont_id,country_status='1')
        state_objs=State.objects.filter(country_id=country_objs,state_status='1')
        city_objs=City_Place.objects.filter(state_id=state_objs,city_status='1').order_by('city_id')

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

