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
#SERVER_URL = "http://35.163.150.203"
SERVER_URL = "http://52.66.133.35"
#SERVER_URL = "http://52.66.144.182"
#SERVER_URL = "http://192.168.0.125:8011"



####################.......city_dashboard..........%%%%%%%%%%##########

@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def ticket_resell_feed(request):
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
        ticket_file_list=[]
        ticket_file_list1=[]
        ticket_list = []
        img_data={}
        tdr=''
        try:
            city_obj_id = request.GET.get('city_id')
            city_name_obj = City_Place.objects.get(city_place_id=request.GET.get('city_id'))
            city_name = city_name_obj.city_id.city_name
            city_image = SERVER_URL + city_name_obj.city_image.url
            country_name = city_name_obj.state_id.country_id.country_name

            # if request.GET.get('sts_val'):
            #     if request.GET.get('sts_val') =='unread':
            #         sts = request.GET.get('sts_val')
            #         ticket_list = SellTicket.objects.filter(city_id=request.GET.get('city_id'),status=sts)
            #         sts_val = 'Unread'
            #     elif request.GET.get('sts_val') =='appropriate':
            #         sts = request.GET.get('sts_val')
            #         ticket_list = SellTicket.objects.filter(city_id=request.GET.get('city_id'),status=sts)
            #         sts_val = 'Appropriate'
            #     elif request.GET.get('sts_val') =='inappropriate':
            #         sts = request.GET.get('sts_val')
            #         ticket_list = SellTicket.objects.filter(city_id=request.GET.get('city_id'),status=sts)
            #         sts_val = 'Inappropriate'
            #     elif request.GET.get('sts_val') =='deleted':
            #         sts = request.GET.get('sts_val')
            #         ticket_list = SellTicket.objects.filter(city_id=request.GET.get('city_id'),status=sts)
            #         sts_val = 'Deleted by User'
            #     elif request.GET.get('sts_val') =='all':
            #         sts = request.GET.get('sts_val')
            #         ticket_list = SellTicket.objects.filter(city_id=request.GET.get('city_id'))
            #         sts_val = 'All'
            #
            # elif request.GET.get('time_val'):
            #     if request.GET.get('time_val') =='today' :
            #         td = datetime.now().strftime("%Y-%m-%d")
            #         ticket_list = SellTicket.objects.filter(city_id=request.GET.get('city_id'),created_date=td)
            #         tm_val = 'Today'
            #     elif request.GET.get('time_val')=='yesterday':
            #         yd = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            #         ticket_list = SellTicket.objects.filter(city_id=request.GET.get('city_id'),created_date=yd)
            #         tm_val = 'Yesterday'
            #     elif request.GET.get('time_val')=='last_week':
            #         tim = request.GET.get('time_val')
            #         last_date = (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d")
            #         current_date = datetime.now().strftime("%Y-%m-%d")
            #         ticket_list = SellTicket.objects.filter(city_id=request.GET.get('city_id'),created_date__range=[last_date,current_date])
            #         tm_val = 'Last Week'
            #     elif request.GET.get('time_val') =='all':
            #         ticket_list = SellTicket.objects.filter(city_id=request.GET.get('city_id'))
            # else :
            #     ticket_list = SellTicket.objects.filter(city_id=request.GET.get('city_id'))



            #----------------------------------------------------
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


            if request.GET.get('sts_val') and request.GET.get('time_val'):
                print '-------------7------'
                if tdr:
                    print '-------------8------'
                    if request.GET.get('sts_val')=='all':
                        ticket_list = SellTicket.objects.filter(city_id=request.GET.get('city_id'),status=sts,created_date__range=tdr)

                    else:
                        ticket_list = SellTicket.objects.filter(city_id=request.GET.get('city_id'),status=sts,created_date__range=tdr)
                    sts_val = sts.upper()
                    tm_val = 'LAST WEEK'
                    total_ticket_list_count = str(ticket_list.count())
                else:
                    print '-------------9------'
                    if request.GET.get('sts_val')=='all':
                        ticket_list = SellTicket.objects.filter(city_id=request.GET.get('city_id'),created_date__range=td)
                    else:
                        print '-----------td-------',td
                        ticket_list = SellTicket.objects.filter(city_id=request.GET.get('city_id'),status=sts,created_date__range=td)
                    sts_val = sts.upper()
                    tm_val = request.GET.get('time_val').upper()
                    total_ticket_list_count = str(ticket_list.count())

            elif request.GET.get('sts_val'):
                print '-------------1------'
                if request.GET.get('sts_val')=='all':
                    ticket_list = SellTicket.objects.filter(city_id=request.GET.get('city_id'))
                    total_ticket_list_count = str(ticket_list.count())
                else:
                    ticket_list = SellTicket.objects.filter(city_id=request.GET.get('city_id'),status=sts)
                    sts_val = sts.upper()
                    total_ticket_list_count = str(ticket_list.count())

            elif request.GET.get('time_val'):
                print '-------------3------'
                if tdr:
                    print '-------------4------'
                    ticket_list = SellTicket.objects.filter(city_id=request.GET.get('city_id'),created_date__range=tdr)
                    tm_val = 'LAST WEEK'
                    total_ticket_list_count = str(ticket_list.count())
                else:
                    print '-------------5------',td
                    if request.GET.get('time_val')=='all':
                        ticket_list = SellTicket.objects.filter(city_id=request.GET.get('city_id'))
                    else:
                        ticket_list = SellTicket.objects.filter(city_id=request.GET.get('city_id'),created_date__range=td)
                    tm_val = request.GET.get('time_val').upper()
                    total_ticket_list_count = str(ticket_list.count())

            else :
                print '-------------16------'
                ticket_list = SellTicket.objects.filter(city_id=request.GET.get('city_id'))
                total_ticket_list_count = str(ticket_list.count())



            total_tickets = str(SellTicket.objects.all().count())


            current_date = datetime.now()
            year = current_date.year
            month = current_date.month
            day = current_date.day

            past_date = datetime(year, month, day)

            todays_tickets_count = str(SellTicket.objects.filter(created_date__range=[past_date,datetime.now()]).count())
            total_tickets_count = str(SellTicket.objects.filter(city_id=request.GET.get('city_id')).count())
            #ticket_share_count = str(SellTicketShares.objects.all().count())
            #print '-------------todays_posts_count------------',todays_tickets_count


            server_url = SERVER_URL
            today_date = datetime.now().strftime("%d/%m/%Y")
            if ticket_list:
                for obj in ticket_list:
                    ticket_id = obj.sellticket_id
                    print '---------ticket id==================',ticket_id
                    event_name = obj.event_name
                    event_start_date = obj.start_date
                    event_start_time = obj.start_time
                    comments = obj.other_comments
                    contact_number = obj.contact_number
                    ticket_share_count = str(SellTicketShares.objects.filter(sellticket_id=obj).count())
                    sview = str(SellTicketView.objects.filter(sellticket_id=obj).count())
                    try:
                        activation_date = obj.select_activation_date
                    except:
                        activation_date = ''
                    #deactivation_date = obj.select_deactivation_date

                    user_name = obj.user_id.consumer_full_name
                    if obj.user_id.consumer_profile_pic:
                        user_pic = SERVER_URL + obj.user_id.consumer_profile_pic.url
                    else:
                        user_pic = ''

                    creation_date = obj.created_date.strftime("%d %b.%y - %I:%M %P")
                    status = obj.status
                    if status == 'inappropriate':
                        dact_date = obj.deleted_date.strftime("%B %d, %Y  %I:%M %P")
                    elif status == 'deleted':
                        dact_date = obj.deleted_date.strftime("%B %d, %Y  %I:%M %P")
                    else:
                        status == ''
                        dact_date=''

                    city_name = obj.city_id.city_id.city_name
                    city_image = SERVER_URL + obj.city_id.city_image.url
                    # img_1 = ''
                    # img_2 = ''
                    # img_3 = ''
                    # img_4 = ''

                    if obj.image_one:
                        #img_1 = SERVER_URL + obj.image_one.url
                        img = SERVER_URL + obj.image_one.url
                        #ticket_file_list.append(img_1)
                        img_data={'ticket_id':ticket_id,'img_path':img}
                        ticket_file_list1.append(img_data)

                    if obj.image_two:
                        #img_2 = SERVER_URL + obj.image_two.url
                        img = SERVER_URL + obj.image_two.url
                        #ticket_file_list.append(img_2)
                        img_data={'ticket_id':ticket_id,'img_path':img}
                        ticket_file_list1.append(img_data)

                    if obj.image_three:
                        #img_3 = SERVER_URL + obj.image_three.url
                        img = SERVER_URL + obj.image_three.url
                        #ticket_file_list.append(img_3)
                        img_data={'ticket_id':ticket_id,'img_path':img}
                        ticket_file_list1.append(img_data)


                    if obj.image_four:
                        #img_4 = SERVER_URL + obj.image_four.url
                        img = SERVER_URL + obj.image_four.url
                        #ticket_file_list.append(img_4)
                        img_data={'ticket_id':ticket_id,'img_path':img}
                        ticket_file_list1.append(img_data)

                    #img_data={'ticket_id':ticket_id,'img_path':ticket_file_list}
                    #ticket_file_list1.append(img_data)
                    print '-----------ticket_file_list1----------',ticket_file_list1

                    # try:
                    #     ticket_files = SellTicket.objects.filter(sellticket_id=obj)
                    #     ticket_files_count = SellTicket.objects.filter(sellticket_id=obj).count()
                    #
                    #     slider_width_val = (ticket_files_count * 200) + 25
                    #     print '------------slider val-----',slider_width_val
                    #     for fl in ticket_files:
                    #         img_path = '/home/hduser/New_Projects/1_9_2016/DigiSpace'+fl.post_file
                    #         #img_path = '/home/ec2-user/DigiSpace/'+fl.post_file
                    #         print '--------img_path--------',img_path
                    #         try:
                    #             img = Image.open(img_path)
                    #             print '----------------img---------',img
                    #             img_format = 'img'
                    #         except:
                    #             print '-----------no image--------'
                    #             img_format = 'vdo'
                    #         img_data={'img_post_id':post_id,'img_format':img_format,'img_path':fl.post_file}
                    #         post_file_list.append(img_data)
                    #
                    # except:
                    #     ticket_files = ''

                    print '--------------ticket_file_list--------------',ticket_file_list


                    #country_name = obj.country_id.country_name
                    country_name = country_name
                    #sview= obj.sellticket_views
                    #sreview= str(PostReview.objects.filter(post_id=obj.post_id).count())
                    #sshare= obj.share

                    post_data = {
                        'ticket_id':ticket_id,
                        'city_name':city_name,
                        'city_image':city_image,
                        'event_name':event_name,
                        'event_start_date':event_start_date,
                        'event_start_time':event_start_time,
                        'comments':comments,
                        'contact_number':contact_number,
                        'activation_date':activation_date,
                        #'deactivation_date':deactivation_date,
                        # 'img_1':img_1,
                        # 'img_2':img_2,
                        # 'img_3':img_3,
                        # 'img_4':img_4,
                        'country_name':country_name,
                        'user_name':user_name,
                        'user_pic':user_pic,
                        'creation_date':creation_date,
                        'status':status,
                        'status1':status.upper(),
                        'views':sview,
                        'share':ticket_share_count,
                        'dact_date':dact_date,
                        'ticket_file_list':ticket_file_list,
                        'ticket_file_list1':ticket_file_list1,
                        #'todays_tickets_count':todays_tickets_count,
                        #'total_tickets_count':total_tickets_count,
                    }

                    final_list.append(post_data)
                    finallist = sorted(final_list, key=itemgetter('ticket_id'),reverse=True)

                data = {'username':request.session['login_user'],'success':'true','total_ticket_list_count':total_ticket_list_count,'final_list':finallist,'server_url':server_url,'tm_val':tm_val,'sts_val':sts_val,'cat_val':cat_val,'city_id':city_obj_id,'country_name':country_name,'city_name':city_name,'city_image':city_image,'todays_tickets_count':todays_tickets_count,'total_tickets_count':total_tickets_count}

            else:
                data = {'username':request.session['login_user'],'success':'false','total_ticket_list_count':total_ticket_list_count,'city_id':city_obj_id,'tm_val':tm_val,'sts_val':sts_val,'cat_val':cat_val,'country_name':country_name,'city_image':city_image,'city_name':city_name,'todays_tickets_count':todays_tickets_count,'total_tickets_count':total_tickets_count}
        except IntegrityError as e:
            print e
            data = {'username':request.session['login_user'],'success':'false','message':'Error in  loading page. Please try after some time','username':request.session['login_user']}
    except MySQLdb.OperationalError, e:
        print e
    except Exception,e:
        print 'Exception ',e

    print data
    return render(request,'Ticket_Resell/ticket-resell-feed.html',data)


def view_comments(request):
    data = {}
    final_list = []
    reply_list1 = []
    comments_list=[]
    comments_list1=[]
    status=''
    newlist=''
    new_reply_list=''
    ddate=''
    tkt_count_value=''
    ticket_file_list=[]

    ticket_obj = SellTicket.objects.get(sellticket_id=request.GET.get('ticket_id'))
    try:
        server_url = SERVER_URL
        ticket_id = ticket_obj.sellticket_id
        if ticket_obj.status == 'unread':
            ticket_obj.status = 'appropriate'
            ticket_obj.save()
        elif ticket_obj.status == 'inappropriate':
            ticket_obj.status = 'inappropriate'
            ticket_obj.save()
        else:
            pass

        ticket_status=ticket_obj.status
        event_name = ticket_obj.event_name
        event_start_date = ticket_obj.start_date
        try:
            activation_date = ticket_obj.select_activation_date
        except:
            activation_date = ''
        #deactivation_date = ticket_obj.select_deactivation_date

        user_name = ticket_obj.user_id.consumer_full_name
        if ticket_obj.user_id.consumer_profile_pic:
            user_pic = SERVER_URL + ticket_obj.user_id.consumer_profile_pic.url
        else:
            user_pic = ''

        creation_date = ticket_obj.created_date.strftime("%d %b.%y - %I:%M %P")

        #sview= ticket_obj.sellticket_views

        #ticket_share_count = str(SellTicketShares.objects.all().count())

        ticket_share_count = str(SellTicketShares.objects.filter(sellticket_id=ticket_obj).count())
        sview = str(SellTicketView.objects.filter(sellticket_id=ticket_obj).count())

        try:
            print '---------imge 1- try-------'
            img_1 = SERVER_URL + ticket_obj.image_one.url
            #img_1 = obj.image_one
            print '---------imge 1--------',img_1
            img_data1 = {'img_number':'1','img_path':img_1}
            ticket_file_list.append(img_data1)
        except:
            print '---------imge 1 else--------'
            img_1 = ''

        try:
            img_2 = SERVER_URL + ticket_obj.image_two.url
            img_data2 = {'img_number':'2','img_path':img_2}
            ticket_file_list.append(img_data2)
            #ticket_file_list.append(img_2)
        except:
            img_2 = ''

        try:
            img_3 = SERVER_URL + ticket_obj.image_three.url
            img_data3 = {'img_number':'3','img_path':img_3}
            ticket_file_list.append(img_data3)
            #ticket_file_list.append(img_3)
        except:
            img_3 = ''

        try:
            img_4 = SERVER_URL + ticket_obj.image_four.url
            img_data4 = {'img_number':'4','img_path':img_4}
            ticket_file_list.append(img_data4)
            #ticket_file_list.append(img_4)
        except:
            img_4 = ''

        print '--------------ticket_file_list--------------',ticket_file_list

        ticket_file_list_count = len(ticket_file_list)
        print '--------------ticket_file_list_count--------------',ticket_file_list_count

        tickets = SellTicketDetails.objects.filter(sellticket_id=ticket_obj)
        print '--------tickets --------',tickets

        ttickets_count = tickets.count()
        if ttickets_count > 2:
            tkt_count_value=ttickets_count-2

        inumber = 0
        for t in tickets:
            print '---------------t---------',t
            inumber = inumber+1
            sell_ticket_detail_id = t.sell_ticket_detail_id
            print '---------------sell ---------',sell_ticket_detail_id
            ticket_class = t.ticket_class
            no_of_tickets = t.no_of_tickets
            original_price = t.original_price
            asking_price = t.asking_price
            status_val = t.status

            if status_val=='0':
                ddate = t.deleted_date.strftime("%d %b.%y - %I:%M %P")
                print '-----------ddate-------------',ddate

            cm_data = {'inumber':inumber,'status_val':status_val,'sell_ticket_id':ticket_id,'sell_ticket_detail_id':sell_ticket_detail_id,'ticket_class':ticket_class,'no_of_tickets':no_of_tickets,'original_price':original_price,'asking_price':asking_price,'ddate':ddate}

            comments_list.append(cm_data)
            newlist = sorted(comments_list, key=itemgetter('sell_ticket_detail_id'))
            comments_list = newlist[:2]

            comments_list1.append(cm_data)
            newlist = sorted(comments_list1, key=itemgetter('sell_ticket_detail_id'))
            newlist = newlist[2:]

        #sshare= post_obj.share

        post_data = {
            'success':'true',
            'user_name':user_name,
            'ticket_id':ticket_id,
            'user_pic':user_pic,
            'event_name':event_name,
            'event_start_date':event_start_date,
            'activation_date':activation_date,
            #'deactivation_date':deactivation_date,
            'creation_date':creation_date,
            'tstatus':ticket_status,
            'views':sview,
            'share':ticket_share_count,
            'server_url':server_url,
            'ticket_status':ticket_status.upper(),
            'inumber':inumber,
            'ttickets_count':ttickets_count,
            'tkt_count_value':tkt_count_value,
        }
        final_list.append(post_data)
        data = {'success':'true','final_list':final_list,'ticket_file_list_count':ticket_file_list_count,'ticket_id':ticket_id,'ticket_file_list':ticket_file_list,'ttickets_count':ttickets_count,'tkt_count_value':tkt_count_value,'new_tickets_list':newlist,'tickets_list':comments_list}

    except Exception,e:
        print 'Exception ',e
    print '--------------data-----------',data
    return HttpResponse(json.dumps(data), content_type='application/json')


def deactivate_ticket(request):
    print '---------------------in deactivate----------'
    td_obj = SellTicketDetails.objects.get(sell_ticket_detail_id=request.GET.get('ticket_id'))
    print '-----------td object---------',td_obj
    try:
        td_obj.status = '0'
        td_obj.updated_date=datetime.now()
        td_obj.deleted_date=datetime.now()
        td_obj.save()

        d_date = td_obj.deleted_date.strftime("%B %d, %Y  %I:%M%P")
    except:
        pass
    data = {'success': 'true','d_date':d_date,'ticket_id':request.GET.get('ticket_id')}
    return HttpResponse(json.dumps(data), content_type='application/json')


def deactivate_ticket_event(request):
    print '---------ticket_event_id--------',request.GET.get('ticket_event_id')
    ticket_ids = request.GET.get('ticket_event_id')
    sell_ticket_obj = SellTicket.objects.get(sellticket_id=request.GET.get('ticket_event_id'))
    print '------sell_ticket_obj------',sell_ticket_obj
    try:
        sell_ticket_obj.status = 'inappropriate'
        sell_ticket_obj.updation_date=datetime.now()
        sell_ticket_obj.deleted_date=datetime.now()
        sell_ticket_obj.save()

        d_date = sell_ticket_obj.deleted_date.strftime("%B %d, %Y  %I:%M%P")
        print '-------d date-----',d_date
    except:
        pass
    data = {'success': 'true','d_date':d_date,'ticket_event_id':request.GET.get('ticket_event_id')}
    return HttpResponse(json.dumps(data), content_type='application/json')


def re_activate_ticket_event(request):
    print '---------post id--------',request.GET.get('ticket_event_id')
    sell_ticket_obj = SellTicket.objects.get(sellticket_id=request.GET.get('ticket_event_id'))
    print '------post_obj------',sell_ticket_obj
    try:
        sell_ticket_obj.status = 'appropriate'
        sell_ticket_obj.updated_date=datetime.now()
        sell_ticket_obj.save()

        d_date = sell_ticket_obj.updated_date.strftime("%B %d, %Y  %I:%M %P")
        print '-------d date-----',d_date
    except:
        pass
    data = {'success': 'true','d_date':d_date,'ticket_event_id':request.GET.get('ticket_event_id')}
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def ticket_resell_home(request):
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
                    #ticket_list = SellTicket.objects.filter(country_id=request.GET.get('cntry_val'))
                    state_list = State.objects.filter(country_id=request.GET.get('cntry_val'))
                    print '--------state list------',state_list
                    city_obj = City_Place.objects.filter(state_id__in = state_list)
                    cntry_name = ' India'
                if request.GET.get('cntry_val') =='2':
                    print '------in uae--------'
                    #ticket_list = SellTicket.objects.filter(country_id=request.GET.get('cntry_val'))
                    state_list = State.objects.filter(country_id=request.GET.get('cntry_val'))
                    print '--------state list------',state_list
                    city_obj = City_Place.objects.filter(state_id__in = state_list)
                    cntry_name = ' UAE'
            else:
                print '-------in else-----'
                pass
                # post_list = PostDetails.objects.all()
                # print '........post_details list...ALL....',post_list
                # city_obj = City_Place.objects.all()
                # print '--------city_name_obj obj id------',city_obj
                # cntry_name=''
            for c_obj in city_obj:
                city_id = c_obj
                print '............city_id...............',city_id
                #country_name = city_id.state_id.country_id.country_name
                country_name = cntry_name

                total_tickets_count = str(SellTicket.objects.filter(city_id = city_id).count())

                current_date = datetime.now()
                year = current_date.year
                month = current_date.month
                day = current_date.day

                past_date = datetime(year, month, day)

                todays_tickets_count = str(SellTicket.objects.filter(city_id = city_id,created_date__range=[past_date,datetime.now()]).count())
                print '-------------todays_posts_count------------',todays_tickets_count

                if SellTicket.objects.filter(city_id = city_id):
                    print '----------in if ---------'
                    tk_details= SellTicket.objects.filter(city_id = city_id).latest('sellticket_id')

                    print '....LIST BY CITY PARTICULAR....',tk_details
                    city_name = tk_details.city_id.city_id.city_name
                    city_id = tk_details.city_id
                    city_image = SERVER_URL + tk_details.city_id.city_image.url
                    #country_name = tk_details.country_id.country_name
                    country_name = cntry_name

                    description = tk_details.event_name
                    print '---------description------',description

                    event_date = tk_details.start_date

                    user_name = tk_details.user_id.consumer_full_name
                    print '----------user name------',user_name
                    if tk_details.user_id.consumer_profile_pic:
                        user_pic = SERVER_URL + tk_details.user_id.consumer_profile_pic.url
                        print '----------user_pic---------',user_pic
                    else:
                        user_pic = ''

                    creation_date = tk_details.created_date.strftime("%d %b.%y - %I:%M%P")
                    print '----------creation date------',creation_date


                    tid = tk_details.sellticket_id
                    print '----pid------',tid
                    file = SERVER_URL + tk_details.image_one.url


                    post_data = {
                        'city_name':city_name,
                        'city_id':city_id,
                        'city_image':city_image,
                        'country_name':country_name,
                        'description':description,
                        'event_date':event_date,
                        'todays_tickets_count':todays_tickets_count,
                        'user_name':user_name,
                        'user_pic':user_pic,
                        'creation_date':creation_date,
                        'total_tickets_count':total_tickets_count,
                        'file':file,
                        'ticket_id':tid,
                    }
                    final_list.append(post_data)

                else :
                    print '----------in else ---------'
                    city_name = city_id.city_id.city_name
                    print '--------city_name---else-----',city_name
                    city_id = city_id
                    city_image = SERVER_URL + city_id.city_image.url

                    post_data = {
                        'city_name':city_name,
                        'city_id':city_id,
                        'city_image':city_image,
                        'country_name':country_name,
                        'todays_tickets_count':todays_tickets_count,
                        'total_tickets_count':total_tickets_count,
                        'cl_details':'no',
                    }
                    final_list.append(post_data)

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
    return render(request,'Ticket_Resell/ticket-resell-home.html',data)



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