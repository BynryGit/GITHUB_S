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

# importing mysqldb and system packages
import MySQLdb, sys
from django.db.models import Q
from django.db.models import F
from django.db import transaction
import pdb
import csv
import json
# importing exceptions
from django.db import IntegrityError

import operator
from django.db.models import Q
from datetime import date, timedelta

# HTTP Response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
import string
import random
from django.views.decorators.cache import cache_control
import urllib2

# SERVER_URL = "http://192.168.0.180:9888"   

SERVER_URL = "http://52.66.133.35"


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_rate_card(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        rate_card_obj = RateCard.objects.all()
        city_list = City_Place.objects.all().exclude(city_place_id__in=[rate_card.city_place_id.city_place_id for rate_card in rate_card_obj])
        data = {'username': request.session['login_user'], 'city_list': city_list}
        return render(request, 'Admin/add_rate_card.html', data)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_rate_card(request):
    if not request.user.is_authenticated():
        return redirect('backoffice')
    else:
        cat_list = []
        category_id = ''
        label_id = ''
        city_id = request.GET.get('city_id')
        city_list = City_Place.objects.filter(city_place_id=city_id)
        cat_city_obj = CategoryCityMap.objects.filter(city_place_id=city_id)
        for objs in cat_city_obj:
            cat_obj = Category.objects.get(category_id=str(objs.category_id))
            if cat_obj.category_name != 'Event Ticket Resale':
                cat_data = {'cat_id': str(cat_obj.category_id), 'cat_name': cat_obj.category_name}
                cat_list.append(cat_data)
        rate_card_obj = RateCard.objects.filter(city_place_id=city_id, rate_card_status='1')
        if rate_card_obj:
            for rate_card in rate_card_obj:
                if rate_card.service_name == "Advert Slider":
                    advert_slider_data = {
                        '3days': str("%0.2f" % float(rate_card.cost_for_3_days)),
                        '7days': str("%0.2f" % float(rate_card.cost_for_7_days)),
                        '30days': str("%0.2f" % float(rate_card.cost_for_30_days)),
                        '90days': str("%0.2f" % float(rate_card.cost_for_90_days)),
                        '180days': str("%0.2f" % float(rate_card.cost_for_180_days))
                    }
                else:
                    top_advert_data = {
                        '3days': str("%0.2f" % float(rate_card.cost_for_3_days)),
                        '7days': str("%0.2f" % float(rate_card.cost_for_7_days)),
                        '30days': str("%0.2f" % float(rate_card.cost_for_30_days)),
                    }
        else:
            advert_slider_data = {
                '3days': "0.00",
                '7days': "0.00",
                '30days': "0.00",
                '90days': "0.00",
                '180days': "0.00"
            }
            top_advert_data = {
                '3days': "0.00",
                '7days': "0.00",
                '30days': "0.00",
            }
        telephone_rate_list = []
        telephone_rate_card_obj = TelephoneEnquiryRateCard.objects.filter(city_place_id=city_id, rate_card_status='1')
        if telephone_rate_card_obj:
            for telephone_rate_card in telephone_rate_card_obj:
                telephone_rate_data = {
                    'service_name': telephone_rate_card.service_name,
                    '3days': str("%0.2f" % float(telephone_rate_card.cost_for_3_days)),
                    '7days': str("%0.2f" % float(telephone_rate_card.cost_for_7_days)),
                    '30days': str("%0.2f" % float(telephone_rate_card.cost_for_30_days)),
                    '90days': str("%0.2f" % float(telephone_rate_card.cost_for_90_days)),
                    '180days': str("%0.2f" % float(telephone_rate_card.cost_for_180_days))
                }
                telephone_rate_list.append(telephone_rate_data)
        else:
            telephone_rate_cards = ['Platinum', 'Diamond', 'Gold', 'Silver', 'Bronze', 'Value']
            for telephone_rate_card in telephone_rate_cards:
                telephone_rate_data = {
                    'service_name': telephone_rate_card,
                    '3days': "0.00",
                    '7days': "0.00",
                    '30days': "0.00",
                    '90days': "0.00",
                    '180days': "0.00"
                }
                telephone_rate_list.append(telephone_rate_data)
        catwise_rate_card_obj = CategoryWiseRateCard.objects.filter(city_place_id=city_id, rate_card_status='1')
        if catwise_rate_card_obj:
            cat_id = catwise_rate_card_obj[0].category_id
            cat_lvl = catwise_rate_card_obj[0].category_level
            if cat_lvl == '1':
                category_id_1 = CategoryLevel1.objects.get(category_id=cat_id)
                category_id = category_id_1.parent_category_id.category_id
                label_id = "label_" + str(category_id_1)
            if cat_lvl == '2':
                category_id_2 = CategoryLevel2.objects.get(category_id = cat_id)
                category_id_1 = category_id_2.parent_category_id.category_id
                category_id = category_id_2.parent_category_id.parent_category_id.category_id
                label_id = "label_" + str(category_id_1) +"_"+ str(category_id_2)
            if cat_lvl == '3':
                category_id_3 = CategoryLevel3.objects.get(category_id=cat_id)
                category_id_2 = category_id_3.parent_category_id.category_id
                category_id_1 = category_id_3.parent_category_id.parent_category_id.category_id
                category_id = category_id_3.parent_category_id.parent_category_id.parent_category_id.category_id
                label_id = "label_" + str(category_id_1) + "_" + str(category_id_2) + "_" + str(category_id_3)
            if cat_lvl == '4':
                category_id_4 = CategoryLevel4.objects.get(category_id=cat_id)
                category_id_3 = category_id_4.parent_category_id.category_id
                category_id_2 = category_id_4.parent_category_id.parent_category_id.category_id
                category_id_1 = category_id_4.parent_category_id.parent_category_id.parent_category_id.category_id
                category_id = category_id_4.parent_category_id.parent_category_id.parent_category_id.parent_category_id.category_id
                label_id = "label_" + str(category_id_1) + "_" + str(category_id_2) + "_" + str(category_id_3) + "_" + str(category_id_4)
            if cat_lvl == '4':
                category_id_5 = CategoryLevel5.objects.get(category_id=cat_id)
                category_id_4 = category_id_5.parent_category_id.category_id
                category_id_3 = category_id_5.parent_category_id.parent_category_id.category_id
                category_id_2 = category_id_5.parent_category_id.parent_category_id.parent_category_id.category_id
                category_id_1 = category_id_5.parent_category_id.parent_category_id.parent_category_id.parent_category_id.category_id
                category_id = category_id_5.parent_category_id.parent_category_id.parent_category_id.parent_category_id.parent_category_id.category_id
                label_id = "label_" + str(category_id_1) + "_" + str(category_id_2) + "_" + str(category_id_3) + "_" + str(category_id_4) + "_" + str(category_id_5)

        data = {
            'username': request.session['login_user'], 'city_list': city_list,
            'advert_slider_data':advert_slider_data, 'top_advert_data':top_advert_data,
            'cat_list':cat_list,'telephone_rate_list':telephone_rate_list,
            'category_id':category_id,'label_id':label_id
        }
        return render(request, 'Admin/edit_rate_card.html', data)

def get_subcategory_ratecard(request):
    try:
        rate_card_list = []
        category_id = request.GET.get('category_id')
        category_level = request.GET.get('category_level')
        cat_rate_obj = CategoryWiseRateCard.objects.filter(rate_card_status='1',category_id=category_id, category_level=category_level)
        if cat_rate_obj:
            for rate_card in cat_rate_obj:
                if rate_card.service_name == "Subscription":
                    sub_3days = str( "%0.2f" % float(rate_card.cost_for_3_days))
                    sub_7days = str( "%0.2f" % float(rate_card.cost_for_7_days))
                    sub_30days = str( "%0.2f" % float(rate_card.cost_for_30_days))
                    sub_90days = str( "%0.2f" % float(rate_card.cost_for_90_days))
                    sub_180days = str( "%0.2f" % float(rate_card.cost_for_180_days))
                if rate_card.service_name == "No.1 Listing":
                    no1_3days = str("%0.2f" % float(rate_card.cost_for_3_days))
                    no1_7days = str("%0.2f" % float(rate_card.cost_for_7_days))
                    no1_30days = str("%0.2f" % float(rate_card.cost_for_30_days))
                    no1_90days = str("%0.2f" % float(rate_card.cost_for_90_days))
                    no1_180days = str("%0.2f" % float(rate_card.cost_for_180_days))
                if rate_card.service_name == "No.2 Listing":
                    no2_3days = str("%0.2f" % float(rate_card.cost_for_3_days))
                    no2_7days = str("%0.2f" % float(rate_card.cost_for_7_days))
                    no2_30days = str("%0.2f" % float(rate_card.cost_for_30_days))
                    no2_90days = str("%0.2f" % float(rate_card.cost_for_90_days))
                    no2_180days = str("%0.2f" % float(rate_card.cost_for_180_days))
                if rate_card.service_name == "No.3 Listing":
                    no3_3days = str("%0.2f" % float(rate_card.cost_for_3_days))
                    no3_7days = str("%0.2f" % float(rate_card.cost_for_7_days))
                    no3_30days = str("%0.2f" % float(rate_card.cost_for_30_days))
                    no3_90days = str("%0.2f" % float(rate_card.cost_for_90_days))
                    no3_180days = str("%0.2f" % float(rate_card.cost_for_180_days))
        else:
            sub_3days = ""
            sub_7days = ""
            sub_30days = ""
            sub_90days = ""
            sub_180days = ""
            no1_3days = ""
            no1_7days = ""
            no1_30days = ""
            no1_90days = ""
            no1_180days = ""
            no2_3days = ""
            no2_7days = ""
            no2_30days = ""
            no2_90days = ""
            no2_180days = ""
            no3_3days = ""
            no3_7days = ""
            no3_30days = ""
            no3_90days = ""
            no3_180days = ""
        data = {
            'success': 'true',
            'sub_3days':sub_3days,
            'sub_7days':sub_7days,
            'sub_30days':sub_30days,
            'sub_90days':sub_90days,
            'sub_180days':sub_180days,
            'no1_3days':no1_3days,
            'no1_7days':no1_7days,
            'no1_30days':no1_30days,
            'no1_90days':no1_90days,
            'no1_180days':no1_180days,
            'no2_3days':no2_3days,
            'no2_7days':no2_7days,
            'no2_30days':no2_30days,
            'no2_90days':no2_90days,
            'no2_180days':no2_180days,
            'no3_3days':no3_3days,
            'no3_7days':no3_7days,
            'no3_30days':no3_30days,
            'no3_90days':no3_90days,
            'no3_180days':no3_180days
        }
    except Exception, e:
        print e
        data = {
            'success': 'false',
        }
    return HttpResponse(json.dumps(data), content_type='application/json')

def delete_rate_card(request):
    try:
        city_id = request.GET.get('city_id')
        city_obj = City_Place.objects.get(city_place_id = city_id)
        rate_card_obj = RateCard.objects.filter(city_place_id=city_id,rate_card_status='1')
        for rate_card in rate_card_obj:
            rate_card.rate_card_status = '0'
            rate_card.save()
        cat_rate_obj = CategoryWiseRateCard.objects.filter(city_place_id=city_id,rate_card_status='1')
        for cat_rate in cat_rate_obj:
            cat_rate.rate_card_status = '0'
            cat_rate.save()
        cat_rate_obj = TelephoneEnquiryRateCard.objects.filter(city_place_id=city_id, rate_card_status='1')
        for cat_rate in cat_rate_obj:
            cat_rate.rate_card_status = '0'
            cat_rate.save()
        data = {
            'success': 'true',
            'message': "Rate card for "+city_obj.city_id.city_name+" deactivated successfully"
        }
    except Exception, e:
        print e
        data = {
            'success': 'false',
            'message': e
        }
    return HttpResponse(json.dumps(data), content_type='application/json')

def activate_rate_card(request):
    try:
        city_id = request.GET.get('city_id')
        city_obj = City_Place.objects.get(city_place_id = city_id)
        rate_card_obj = RateCard.objects.filter(city_place_id=city_id,rate_card_status='0')
        for rate_card in rate_card_obj:
            rate_card.rate_card_status = '1'
            rate_card.save()
        cat_rate_obj = CategoryWiseRateCard.objects.filter(city_place_id=city_id,rate_card_status='0')
        for cat_rate in cat_rate_obj:
            cat_rate.rate_card_status = '1'
            cat_rate.save()
        cat_rate_obj = TelephoneEnquiryRateCard.objects.filter(city_place_id=city_id, rate_card_status='0')
        for cat_rate in cat_rate_obj:
            cat_rate.rate_card_status = '1'
            cat_rate.save()
        data = {
            'success': 'true',
            'message': "Rate card for "+city_obj.city_id.city_name+" activated successfully"
        }
    except Exception, e:
        print e
        data = {
            'success': 'false',
            'message': e
        }
    return HttpResponse(json.dumps(data), content_type='application/json')

def get_city_category_list(request):
    try:
        cat_list = []
        cat_city_obj = CategoryCityMap.objects.filter(city_place_id=request.GET.get('city_id'))
        for objs in cat_city_obj:
            cat_obj = Category.objects.get(category_id=str(objs.category_id))
            if cat_obj.category_name != 'Event Ticket Resale':
                cat_data = {'cat_id': str(cat_obj.category_id), 'cat_name': cat_obj.category_name}
                cat_list.append(cat_data)
        data = {
            'success': 'true',
            'message': "Service already exist",
            'cat_list': cat_list
        }
    except Exception, e:
        print e
        data = {
            'success': 'false',
            'message': "Service added successfully"
        }
    return HttpResponse(json.dumps(data), content_type='application/json')


def get_category_ratecard(request):
    try:
        rate_card_list = []
        category_id = request.GET.get('category_id')
        category_level = request.GET.get('category_level')
        category_name = request.GET.get('category_name')
        cat_rate_obj = CategoryWiseRateCard.objects.filter(category_id=category_id, category_level=category_level,rate_card_status='1')
        rate_card_str = ''
        if cat_rate_obj:
            text = category_name
            flag = 1
            for rate_card in cat_rate_obj:
                rate_card_str = rate_card_str + '<tr>' \
                                                '<td class="table_th_3"><label>' + rate_card.service_name + '</label></td>' \
                                                '<td class="table_th_2_1"><label>' + str( "%0.2f" % float(rate_card.cost_for_3_days)) + '</label></td>' \
                                                '<td class="table_th_2_1"><label>' + str( "%0.2f" % float(rate_card.cost_for_7_days)) + '</label></td>' \
                                                '<td class="table_th_2_1"><label>' + str( "%0.2f" % float(rate_card.cost_for_30_days)) + '</label></td>' \
                                                '<td class="table_th_2_1"><label>' + str( "%0.2f" % float(rate_card.cost_for_90_days)) + '</label></td>' \
                                                '<td class="table_th_2_1"><label>' + str( "%0.2f" % float(rate_card.cost_for_180_days)) + '</label></td>' \
                                                '</tr>'
        else:
            text = category_name + 'is not added'
            flag = 0
        data = {
            'success': 'true',
            'rate_card_str': rate_card_str,
            'text': text,
            'flag': flag
        }
    except Exception, e:
        print e
        data = {
            'success': 'false',
        }
    return HttpResponse(json.dumps(data), content_type='application/json')


def get_city_ratecard(request):
    try:
        rate_card_list = []
        cat_list = []
        city_id = request.GET.get('city_id')
        rate_card_obj = RateCard.objects.filter(city_place_id=city_id,rate_card_status='1')
        telephone_rate_card_obj = TelephoneEnquiryRateCard.objects.filter(city_place_id=city_id,rate_card_status='1')
        city_obj = City_Place.objects.get(city_place_id=city_id)
        city_detail = city_obj.city_id.city_name + ' Rate Card (in ' + city_obj.currency + ')'
        rate_card_str = ''
        telephone_rate_card_str = ''

        cat_city_obj = CategoryCityMap.objects.filter(city_place_id=request.GET.get('city_id'))
        for objs in cat_city_obj:
            cat_obj = Category.objects.get(category_id=str(objs.category_id))
            if cat_obj.category_name != 'Event Ticket Resale':
                cat_data = {'cat_id': str(cat_obj.category_id), 'cat_name': cat_obj.category_name}
                cat_list.append(cat_data)

        if rate_card_obj:
            for rate_card in rate_card_obj:
                if rate_card.service_name == "Advert Slider":
                    rate_card_str = rate_card_str + '<tr>' \
                                                    '<td class="table_th_1"><label>' + rate_card.service_name + '</label></td>' \
                                                    '<td class="table_th"><label>' + str( "%0.2f" % float(rate_card.cost_for_3_days)) + '</label></td>' \
                                                    '<td class="table_th"><label>' + str( "%0.2f" % float(rate_card.cost_for_7_days)) + '</label></td>' \
                                                    '<td class="table_th"><label>' + str( "%0.2f" % float(rate_card.cost_for_30_days)) + '</label></td>' \
                                                    '<td class="table_th"><label>' + str( "%0.2f" % float(rate_card.cost_for_90_days)) + '</label></td>' \
                                                    '<td class="table_th"><label>' + str( "%0.2f" % float(rate_card.cost_for_180_days)) + '</label></td>' \
                                                    '</tr>'
                else:
                    rate_card_str = rate_card_str + '<tr>' \
                                                    '<td class="table_th_1"><label>' + rate_card.service_name + '</label></td>' \
                                                    '<td class="table_th"><label>' + str( "%0.2f" % float(rate_card.cost_for_3_days)) + '</label></td>' \
                                                    '<td class="table_th"><label>' + str( "%0.2f" % float(rate_card.cost_for_7_days)) + '</label></td>' \
                                                    '<td class="table_th"><label>' + str( "%0.2f" % float(rate_card.cost_for_30_days)) + '</label></td>' \
                                                    '<td class="table_th"><label>' + rate_card.cost_for_90_days + '</label></td>' \
                                                    '<td class="table_th"><label>' + rate_card.cost_for_180_days + '</label></td>' \
                                                    '</tr>'
        else:
            rate_card_str = '<tr>' \
                            '<td class="table_th_1"><label>Advert Slider</label></td>' \
                            '<td class="table_th"><label>0.00</label></td>' \
                            '<td class="table_th"><label>0.00</label></td>' \
                            '<td class="table_th"><label>0.00</label></td>' \
                            '<td class="table_th"><label>0.00</label></td>' \
                            '<td class="table_th"><label>0.00</label></td>' \
                            '</tr>' \
                            '<tr>' \
                            '<td class="table_th_1"><label>Top Advert</label></td>' \
                            '<td class="table_th"><label>0.00</label></td>' \
                            '<td class="table_th"><label>0.00</label></td>' \
                            '<td class="table_th"><label>0.00</label></td>' \
                            '<td class="table_th"><label>N/A</label></td>' \
                            '<td class="table_th"><label>N/A</label></td>' \
                            '</tr>'
        if telephone_rate_card_obj:
            for telephone_rate_card in telephone_rate_card_obj:
                telephone_rate_card_str = telephone_rate_card_str + '<tr>' \
                                                '<td class="table_th_1"><label>' + telephone_rate_card.service_name + '</label></td>' \
                                                                                                            '<td class="table_th"><label>' + str(
                    "%0.2f" % float(telephone_rate_card.cost_for_3_days)) + '</label></td>' \
                                                                  '<td class="table_th"><label>' + str(
                    "%0.2f" % float(telephone_rate_card.cost_for_7_days)) + '</label></td>' \
                                                                  '<td class="table_th"><label>' + str(
                    "%0.2f" % float(telephone_rate_card.cost_for_30_days)) + '</label></td>' \
                                                                   '<td class="table_th"><label>' + str(
                    "%0.2f" % float(telephone_rate_card.cost_for_90_days)) + '</label></td>' \
                                                                   '<td class="table_th"><label>' + str(
                    "%0.2f" % float(telephone_rate_card.cost_for_180_days)) + '</label></td>' \
                                                                    '</tr>'
        else:
            telephone_rate_cards = ['Platinum', 'Diamond', 'Gold', 'Silver', 'Bronze', 'Value']
            for telephone_rate_card in telephone_rate_cards:
                telephone_rate_card_str = telephone_rate_card_str + '<tr>' \
                    '<td class="table_th_1"><label>' + telephone_rate_card+ '</label></td>' \
                    '<td class="table_th"><label>0.00</label></td>' \
                    '<td class="table_th"><label>0.00</label></td>' \
                    '<td class="table_th"><label>0.00</label></td>' \
                    '<td class="table_th"><label>0.00</label></td>' \
                    '<td class="table_th"><label>0.00</label></td>' \
                    '</tr>'
        data = {
            'success': 'true',
            'cat_list': cat_list,
            'city_detail': city_detail,
            'premium_text': rate_card_str,
            'telephone_text': telephone_rate_card_str
        }
    except Exception, e:
        print e
        data = {
            'success': 'false',
        }
    return HttpResponse(json.dumps(data), content_type='application/json')


def get_all_category_list(request):
    try:
        cat_obj = Category.objects.get(category_id=request.GET.get('category_id'))
        cat_l1_obj = CategoryLevel1.objects.filter(parent_category_id=str(cat_obj.category_id))
        cat_str = ''
        i = 0
        for cat_l1 in cat_l1_obj:
            i = int(i) + 1
            level_name = "level_" + str(i)
            cat_l2_obj = CategoryLevel2.objects.filter(parent_category_id=str(cat_l1.category_id))
            if cat_l2_obj:
                icon = 'fa-minus-square'
                click_function = ''
                flag_click = "onclick=collapse_div('" + level_name + "',this)"
                cursor_style = ''
            else:
                icon = ''
                label_id = "id='label_"+str(cat_l1.category_id)+"'"
                click_function = label_id+"onclick='showTable(this," + str(cat_l1.category_id) + ",1)'"
                flag_click = ''
                cursor_style = "style='cursor: pointer;'"
            cat_str = cat_str + "<div class='col-lg-12 padding_left0'>" \
                                "<div class='col-lg-1' style='padding:0px;'>" \
                                "<a class='fa " + icon + "' " + flag_click + "></a></div>" \
                                                                             "<div class='col-lg-11'><label " + cursor_style + " class='label_item' " + click_function + ">" + cat_l1.category_name + "</label>" \
                                                                                                                                                                                                      "</div></div>"
            j = 0
            for cat_l2 in cat_l2_obj:
                j = int(j) + 1
                level_name_1 = "level_" + str(i) + "_" + str(j)
                cat_l3_obj = CategoryLevel3.objects.filter(parent_category_id=str(cat_l2.category_id))
                if cat_l3_obj:
                    icon = 'fa-minus-square'
                    click_function = ''
                    flag_click = "onclick=collapse_div('" + level_name_1 + "',this)"
                    cursor_style = ''
                else:
                    icon = ''
                    label_id = "id='label_" + str(cat_l1.category_id) + "_"+str(cat_l2.category_id)+"'"
                    click_function = label_id+"onclick='showTable(this," + str(cat_l2.category_id) + ",2)'"
                    flag_click = ''
                    cursor_style = "style='cursor: pointer;'"
                cat_str = cat_str + "<div class='row col_div " + level_name + "' style='margin-left: 6.33333%;'>" \
                                                                              "<div class='col-lg-12 padding_left0'>" \
                                                                              "<div class='col-lg-1' style='padding:0px;'>" \
                                                                              "<a class='fa " + icon + "' " + flag_click + "></a></div>" \
                                                                                                                           "<div class='col-lg-11'><label " + cursor_style + " class='label_item' " + click_function + ">" + cat_l2.category_name + "</label>" \
                                                                                                                                                                                                                                                    "</div></div>"
                k = 0
                for cat_l3 in cat_l3_obj:
                    k = int(k) + 1
                    level_name_2 = "level_" + str(i) + "_" + str(j) + "_" + str(k)
                    cat_l4_obj = CategoryLevel4.objects.filter(parent_category_id=str(cat_l3.category_id))
                    if cat_l4_obj:
                        icon = 'fa-minus-square'
                        click_function = ''
                        flag_click = "onclick=collapse_div('" + level_name_2 + "',this)"
                        cursor_style = ''
                    else:
                        icon = ''
                        label_id = "id='label_" + str(cat_l1.category_id) + "_" + str(cat_l2.category_id) + "_" + str(cat_l3.category_id) +"'"
                        click_function = label_id+"onclick='showTable(this," + str(cat_l3.category_id) + ",3)'"
                        flag_click = ''
                        cursor_style = "style='cursor: pointer;'"
                    cat_str = cat_str + "<div class='row col_div " + level_name_1 + "' style='margin-left: 6.33333%;'>" \
                                                                                    "<div class='col-lg-12 padding_left0'>" \
                                                                                    "<div class='col-lg-1' style='padding:0px;'>" \
                                                                                    "<a class='fa " + icon + "' " + flag_click + "></a></div>" \
                                                                                                                                 "<div class='col-lg-11'><label " + cursor_style + " class='label_item' " + click_function + ">" + cat_l3.category_name + "</label>" \
                                                                                                                                                                                                                                                          "</div></div>"
                    l = 0
                    for cat_l4 in cat_l4_obj:
                        l = int(l) + 1
                        level_name_3 = "level_" + str(i) + "_" + str(j) + "_" + str(k) + "_" + str(l)
                        cat_l5_obj = CategoryLevel5.objects.filter(parent_category_id=str(cat_l4.category_id))
                        if cat_l5_obj:
                            icon = 'fa-minus-square'
                            click_function = ''
                            flag_click = "onclick=collapse_div('" + level_name_3 + "',this)"
                            cursor_style = ''
                        else:
                            icon = ''
                            label_id = "id='label_" + str(cat_l1.category_id) + "_" + str(
                                cat_l2.category_id) + "_" + str(cat_l3.category_id) + "_" + str(cat_l4.category_id) + "'"
                            click_function = label_id + "onclick='showTable(this," + str(cat_l4.category_id) + ",4)'"
                            flag_click = ''
                            cursor_style = "style='cursor: pointer;'"
                        cat_str = cat_str + "<div class='row col_div " + level_name_2 + "' style='margin-left: 6.33333%;'>" \
                                                                                        "<div class='col-lg-12 padding_left0'>" \
                                                                                        "<div class='col-lg-1' style='padding:0px;'>" \
                                                                                        "<a class='fa " + icon + "' " + flag_click + "></a></div>" \
                                                                                                                                     "<div class='col-lg-11'><label " + cursor_style + " class='label_item' " + click_function + " >" + cat_l4.category_name + "</label>" \
                                                                                                                                                                                                                                                               "</div></div>"
                        for cat_l5 in cat_l5_obj:
                            label_id = "id='label_" + str(cat_l1.category_id) + "_" + str(
                                cat_l2.category_id) + "_" + str(cat_l3.category_id) + "_" + str(
                                cat_l4.category_id) + "_" + str(cat_l3.category_id) + "'"
                            cursor_style = "style='cursor: pointer;'"
                            cat_str = cat_str + "<div class='row col_div " + level_name_3 + "' style='margin-left: 6.33333%;'>" \
                                                                                            "<div class='col-lg-12 padding_left0'>" \
                                                                                            "<div class='col-lg-1' style='padding:0px;'>" \
                                                                                            "<a class='fa '></a></div>" \
                                                                                            "<div class='col-lg-11'><label " + cursor_style + " class='label_item' "+label_id+" onclick='showTable(this," + str(
                                cat_l5.category_id) + ",5)'>" + cat_l5.category_name + "</label>" \
                                                                                       "</div></div>"
                            cat_str = cat_str + '</div>'
                        cat_str = cat_str + '</div>'
                    cat_str = cat_str + '</div>'
                cat_str = cat_str + '</div>'
            cat_str = cat_str + '</div>'
        data = {
            'success': 'true',
            'message': "Service already exist",
            'cat_str': cat_str
        }
    except Exception, e:
        print e
        data = {
            'success': 'false',
            'message': "Service added successfully"
        }
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def save_prem_sevice_ratecard(request):
    try:
        city_id = request.POST.get('city_id')
        service_name_list = request.POST.getlist('prem_service_name')

        days_3_list = request.POST.getlist('3_days_price')
        days_7_list = request.POST.getlist('7_days_price')
        days_30_list = request.POST.getlist('30_days_price')
        days_90_list = request.POST.getlist('90_days_price')
        days_180_list = request.POST.getlist('180_days_price')
        rate_card_obj = RateCard.objects.filter(rate_card_status='1', city_place_id=city_id)
        if rate_card_obj:
            data = {
                'success': 'false',
                'message': "Premium Service Rate card already exist for selected city"
            }
        else:
            i = 0
            for service_name in service_name_list:
                rate_card_obj = RateCard()
                rate_card_obj.city_place_id = City_Place.objects.get(city_place_id=city_id)
                rate_card_obj.service_name = service_name
                rate_card_obj.cost_for_3_days = str(days_3_list[i])
                rate_card_obj.cost_for_7_days = str(days_7_list[i])
                rate_card_obj.cost_for_30_days = str(days_30_list[i])
                rate_card_obj.cost_for_90_days = str(days_90_list[i])
                rate_card_obj.cost_for_180_days = str(days_180_list[i])
                rate_card_obj.rate_card_created_by = request.session['login_user']
                rate_card_obj.rate_card_created_date = datetime.utcnow()
                rate_card_obj.save()
                i = i + 1
            data = {
                'success': 'true',
                'message': "Premium Service Rate card added successfully"
            }
    except Exception, e:
        print "Exception:", e
        data = {
            'success': 'false',
            'message': e
        }
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def save_telephone_sevice_ratecard(request):
    try:
        city_id = request.POST.get('city_id')
        service_name_list = request.POST.getlist('prem_service_name')

        days_3_list = request.POST.getlist('3_days_price')
        days_7_list = request.POST.getlist('7_days_price')
        days_30_list = request.POST.getlist('30_days_price')
        days_90_list = request.POST.getlist('90_days_price')
        days_180_list = request.POST.getlist('180_days_price')
        rate_card_obj = TelephoneEnquiryRateCard.objects.filter(rate_card_status='1', city_place_id=city_id)
        if rate_card_obj:
            data = {
                'success': 'false',
                'message': "Telephone Enquiry Premium Service Rate card already exist for selected city"
               #'message': "Telephone Enquiry Premium Service Rate card updated successfully",
            }
        else:
            i = 0
            for service_name in service_name_list:
                rate_card_obj = TelephoneEnquiryRateCard()
                rate_card_obj.city_place_id = City_Place.objects.get(city_place_id=city_id)
                rate_card_obj.service_name = service_name
                rate_card_obj.cost_for_3_days = str(days_3_list[i])
                rate_card_obj.cost_for_7_days = str(days_7_list[i])
                rate_card_obj.cost_for_30_days = str(days_30_list[i])
                rate_card_obj.cost_for_90_days = str(days_90_list[i])
                rate_card_obj.cost_for_180_days = str(days_180_list[i])
                rate_card_obj.rate_card_created_by = request.session['login_user']
                rate_card_obj.rate_card_created_date = datetime.utcnow()
                rate_card_obj.save()
                i = i + 1
            data = {
                'success': 'true',
                'message': "Telephone Enquiry Premium Service Rate card added successfully",
            }
    except Exception, e:
        print "Exception:", e
        data = {
            'success': 'false',
            'message': e
        }
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def update_prem_sevice_ratecard(request):
    try:
        city_id = request.POST.get('city_id')
        #service_name_list = request.POST.getlist('prem_service_name')
        service_name_list = ["Advert Slider","Top Advert"]
        days_3_list = request.POST.getlist('3_days_price')
        days_7_list = request.POST.getlist('7_days_price')
        days_30_list = request.POST.getlist('30_days_price')
        days_90_list = request.POST.getlist('90_days_price')
        days_180_list = request.POST.getlist('180_days_price')
        rate_card_list = RateCard.objects.filter(rate_card_status='1', city_place_id=city_id)
        if rate_card_list:
            i = 0
            for rate_card_obj in rate_card_list:
                rate_card_obj.cost_for_3_days = str(days_3_list[i])
                rate_card_obj.cost_for_7_days = str(days_7_list[i])
                rate_card_obj.cost_for_30_days = str(days_30_list[i])
                rate_card_obj.cost_for_90_days = str(days_90_list[i])
                rate_card_obj.cost_for_180_days = str(days_180_list[i])
                rate_card_obj.rate_card_updated_by = request.session['login_user']
                rate_card_obj.rate_card_updated_date = datetime.utcnow()
                rate_card_obj.save()
                i = i + 1
        else:
            i = 0
            for service_name in service_name_list:
                rate_card_obj = RateCard()
                rate_card_obj.city_place_id = City_Place.objects.get(city_place_id=city_id)
                rate_card_obj.service_name = service_name
                rate_card_obj.cost_for_3_days = str(days_3_list[i])
                rate_card_obj.cost_for_7_days = str(days_7_list[i])
                rate_card_obj.cost_for_30_days = str(days_30_list[i])
                rate_card_obj.cost_for_90_days = str(days_90_list[i])
                rate_card_obj.cost_for_180_days = str(days_180_list[i])
                rate_card_obj.rate_card_created_by = request.session['login_user']
                rate_card_obj.rate_card_created_date = datetime.utcnow()
                rate_card_obj.rate_card_updated_by = request.session['login_user']
                rate_card_obj.rate_card_updated_date = datetime.utcnow()
                rate_card_obj.save()
                i = i + 1

        rate_card_obj = RateCard.objects.filter(city_place_id=city_id, rate_card_status='1')
        for rate_card in rate_card_obj:
            if rate_card.service_name == "Advert Slider":
                as_3days = str("%0.2f" % float(rate_card.cost_for_3_days))
                as_7days = str("%0.2f" % float(rate_card.cost_for_7_days))
                as_30days = str("%0.2f" % float(rate_card.cost_for_30_days))
                as_90days = str("%0.2f" % float(rate_card.cost_for_90_days))
                as_180days = str("%0.2f" % float(rate_card.cost_for_180_days))
            else:
                ta_3days = str("%0.2f" % float(rate_card.cost_for_3_days))
                ta_7days = str("%0.2f" % float(rate_card.cost_for_7_days))
                ta_30days = str("%0.2f" % float(rate_card.cost_for_30_days))

        data = {
            'success': 'true',
            'message': "Premium Service Rate card updated successfully",
            'as_3days':as_3days,
            'as_7days':as_7days,
            'as_30days':as_30days,
            'as_90days':as_90days,
            'as_180days':as_180days,
            'ta_3days':ta_3days,
            'ta_7days':ta_7days,
            'ta_30days':ta_30days,
        }
    except Exception, e:
        print "Exception:", e
        data = {
            'success': 'false',
            'message': e
        }
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def update_telephone_sevice_ratecard(request):
    try:
        city_id = request.POST.get('city_id')
        #service_name_list = request.POST.getlist('prem_service_name')
        service_name_list = ['Platinum','Diamond','Gold','Silver','Bronze','Value']
        days_3_list = request.POST.getlist('3_days_price')
        days_7_list = request.POST.getlist('7_days_price')
        days_30_list = request.POST.getlist('30_days_price')
        days_90_list = request.POST.getlist('90_days_price')
        days_180_list = request.POST.getlist('180_days_price')
        rate_card_list = TelephoneEnquiryRateCard.objects.filter(rate_card_status='1', city_place_id=city_id)
        if rate_card_list:
            i = 0
            for rate_card_obj in rate_card_list:
                rate_card_obj.cost_for_3_days = str(days_3_list[i])
                rate_card_obj.cost_for_7_days = str(days_7_list[i])
                rate_card_obj.cost_for_30_days = str(days_30_list[i])
                rate_card_obj.cost_for_90_days = str(days_90_list[i])
                rate_card_obj.cost_for_180_days = str(days_180_list[i])
                rate_card_obj.rate_card_updated_by = request.session['login_user']
                rate_card_obj.rate_card_updated_date = datetime.utcnow()
                rate_card_obj.save()
                i = i + 1
        else:
            i = 0
            for service_name in service_name_list:
                rate_card_obj = TelephoneEnquiryRateCard()
                rate_card_obj.city_place_id = City_Place.objects.get(city_place_id=city_id)
                rate_card_obj.service_name = service_name
                rate_card_obj.cost_for_3_days = str(days_3_list[i])
                rate_card_obj.cost_for_7_days = str(days_7_list[i])
                rate_card_obj.cost_for_30_days = str(days_30_list[i])
                rate_card_obj.cost_for_90_days = str(days_90_list[i])
                rate_card_obj.cost_for_180_days = str(days_180_list[i])
                rate_card_obj.rate_card_created_by = request.session['login_user']
                rate_card_obj.rate_card_created_date = datetime.utcnow()
                rate_card_obj.rate_card_updated_by = request.session['login_user']
                rate_card_obj.rate_card_updated_date = datetime.utcnow()
                rate_card_obj.save()
                i = i + 1

        rate_card_obj = TelephoneEnquiryRateCard.objects.filter(city_place_id=city_id, rate_card_status='1')
        # for rate_card in rate_card_obj:
        #     if rate_card.service_name == "Advert Slider":
        #         as_3days = str("%0.2f" % float(rate_card.cost_for_3_days))
        #         as_7days = str("%0.2f" % float(rate_card.cost_for_7_days))
        #         as_30days = str("%0.2f" % float(rate_card.cost_for_30_days))
        #         as_90days = str("%0.2f" % float(rate_card.cost_for_90_days))
        #         as_180days = str("%0.2f" % float(rate_card.cost_for_180_days))
        #     else:
        #         ta_3days = str("%0.2f" % float(rate_card.cost_for_3_days))
        #         ta_7days = str("%0.2f" % float(rate_card.cost_for_7_days))
        #         ta_30days = str("%0.2f" % float(rate_card.cost_for_30_days))

        data = {
            'success': 'true',
            'message': "Telephone Enquiry Premium Service Rate card updated successfully",
            # 'as_3days':as_3days,
            # 'as_7days':as_7days,
            # 'as_30days':as_30days,
            # 'as_90days':as_90days,
            # 'as_180days':as_180days,
            # 'ta_3days':ta_3days,
            # 'ta_7days':ta_7days,
            # 'ta_30days':ta_30days,
        }
    except Exception, e:
        print "Exception:", e
        data = {
            'success': 'false',
            'message': e
        }
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def save_cat_wise_ratecard(request):
    try:
        city_id = request.POST.get('city_id')
        category_id = request.POST.get('category_id')
        category_level = request.POST.get('category_level')
        #service_name_list = request.POST.getlist('service_name')
        service_name_list = ["Subscription","No.1 Listing","No.2 Listing","No.3 Listing"]
        days_3_list = request.POST.getlist('3_days_price')
        days_7_list = request.POST.getlist('7_days_price')
        days_30_list = request.POST.getlist('30_days_price')
        days_90_list = request.POST.getlist('90_days_price')
        days_180_list = request.POST.getlist('180_days_price')
        rate_card_obj = CategoryWiseRateCard.objects.filter(rate_card_status='1', city_place_id=city_id,
                                                            category_id=category_id, category_level=category_level)
        if rate_card_obj:
            data = {
                'success': 'false',
                'message': "Service Rate card already exist for selected category"
            }
        else:
            i = 0
            for service_name in service_name_list:
                rate_card_obj = CategoryWiseRateCard()
                rate_card_obj.city_place_id = City_Place.objects.get(city_place_id=city_id)
                rate_card_obj.service_name = service_name
                rate_card_obj.category_id = category_id
                rate_card_obj.category_level = category_level
                rate_card_obj.cost_for_3_days = str(days_3_list[i])
                rate_card_obj.cost_for_7_days = str(days_7_list[i])
                rate_card_obj.cost_for_30_days = str(days_30_list[i])
                rate_card_obj.cost_for_90_days = str(days_90_list[i])
                rate_card_obj.cost_for_180_days = str(days_180_list[i])
                rate_card_obj.rate_card_created_by = request.session['login_user']
                rate_card_obj.rate_card_created_date = datetime.utcnow()
                rate_card_obj.save()
                i = i + 1
            data = {
                'success': 'true',
                'message': "Service Rate card add successfully"
            }
    except Exception, e:
        print "Exception:", e
        data = {
            'success': 'false',
            'message': e
        }
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def update_cat_wise_ratecard(request):
    try:
        city_id = request.POST.get('city_id')
        category_id = request.POST.get('category_id')
        category_level = request.POST.get('category_level')
        #service_name_list = request.POST.getlist('service_name')
        service_name_list = ["Subscription","No.1 Listing","No.2 Listing","No.3 Listing"]
        days_3_list = request.POST.getlist('3_days_price')
        days_7_list = request.POST.getlist('7_days_price')
        days_30_list = request.POST.getlist('30_days_price')
        days_90_list = request.POST.getlist('90_days_price')
        days_180_list = request.POST.getlist('180_days_price')
        rate_card_list = CategoryWiseRateCard.objects.filter(rate_card_status='1', city_place_id=city_id,
                                                            category_id=category_id, category_level=category_level)
        if rate_card_list:
            i = 0
            for rate_card_obj in rate_card_list:
                rate_card_obj.city_place_id = City_Place.objects.get(city_place_id=city_id)
                rate_card_obj.cost_for_3_days = str(days_3_list[i])
                rate_card_obj.cost_for_7_days = str(days_7_list[i])
                rate_card_obj.cost_for_30_days = str(days_30_list[i])
                rate_card_obj.cost_for_90_days = str(days_90_list[i])
                rate_card_obj.cost_for_180_days = str(days_180_list[i])
                rate_card_obj.rate_card_updated_by = request.session['login_user']
                rate_card_obj.rate_card_updated_date = datetime.utcnow()
                rate_card_obj.save()
                i = i + 1
        else:
            i = 0
            for service_name in service_name_list:
                rate_card_obj = CategoryWiseRateCard()
                rate_card_obj.city_place_id = City_Place.objects.get(city_place_id=city_id)
                rate_card_obj.service_name = service_name
                rate_card_obj.category_id = category_id
                rate_card_obj.category_level = category_level
                rate_card_obj.cost_for_3_days = str(days_3_list[i])
                rate_card_obj.cost_for_7_days = str(days_7_list[i])
                rate_card_obj.cost_for_30_days = str(days_30_list[i])
                rate_card_obj.cost_for_90_days = str(days_90_list[i])
                rate_card_obj.cost_for_180_days = str(days_180_list[i])
                rate_card_obj.rate_card_created_by = request.session['login_user']
                rate_card_obj.rate_card_created_date = datetime.utcnow()
                rate_card_obj.rate_card_updated_by = request.session['login_user']
                rate_card_obj.rate_card_updated_date = datetime.utcnow()
                rate_card_obj.save()
                i = i + 1

        rate_card_list = CategoryWiseRateCard.objects.filter(rate_card_status='1', city_place_id=city_id,
                                                             category_id=category_id, category_level=category_level)
        for rate_card in rate_card_list:
            if rate_card.service_name == "Subscription":
                sub_3days = str("%0.2f" % float(rate_card.cost_for_3_days))
                sub_7days = str("%0.2f" % float(rate_card.cost_for_7_days))
                sub_30days = str("%0.2f" % float(rate_card.cost_for_30_days))
                sub_90days = str("%0.2f" % float(rate_card.cost_for_90_days))
                sub_180days = str("%0.2f" % float(rate_card.cost_for_180_days))
            if rate_card.service_name == "No.1 Listing":
                no1_3days = str("%0.2f" % float(rate_card.cost_for_3_days))
                no1_7days = str("%0.2f" % float(rate_card.cost_for_7_days))
                no1_30days = str("%0.2f" % float(rate_card.cost_for_30_days))
                no1_90days = str("%0.2f" % float(rate_card.cost_for_90_days))
                no1_180days = str("%0.2f" % float(rate_card.cost_for_180_days))
            if rate_card.service_name == "No.2 Listing":
                no2_3days = str("%0.2f" % float(rate_card.cost_for_3_days))
                no2_7days = str("%0.2f" % float(rate_card.cost_for_7_days))
                no2_30days = str("%0.2f" % float(rate_card.cost_for_30_days))
                no2_90days = str("%0.2f" % float(rate_card.cost_for_90_days))
                no2_180days = str("%0.2f" % float(rate_card.cost_for_180_days))
            if rate_card.service_name == "No.3 Listing":
                no3_3days = str("%0.2f" % float(rate_card.cost_for_3_days))
                no3_7days = str("%0.2f" % float(rate_card.cost_for_7_days))
                no3_30days = str("%0.2f" % float(rate_card.cost_for_30_days))
                no3_90days = str("%0.2f" % float(rate_card.cost_for_90_days))
                no3_180days = str("%0.2f" % float(rate_card.cost_for_180_days))
        data = {
            'success': 'true',
            'message': "Service Rate card updated successfully",
            'sub_3days': sub_3days,
            'sub_7days': sub_7days,
            'sub_30days': sub_30days,
            'sub_90days': sub_90days,
            'sub_180days': sub_180days,
            'no1_3days': no1_3days,
            'no1_7days': no1_7days,
            'no1_30days': no1_30days,
            'no1_90days': no1_90days,
            'no1_180days': no1_180days,
            'no2_3days': no2_3days,
            'no2_7days': no2_7days,
            'no2_30days': no2_30days,
            'no2_90days': no2_90days,
            'no2_180days': no2_180days,
            'no3_3days': no3_3days,
            'no3_7days': no3_7days,
            'no3_30days': no3_30days,
            'no3_90days': no3_90days,
            'no3_180days': no3_180days
        }
    except Exception, e:
        print "Exception:", e
        data = {
            'success': 'false',
            'message': e
        }
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def add_service(request):
    try:
        rate_card_obj = ServiceRateCard.objects.get(service_name=request.POST.get('service'),
                                                    duration=request.POST.get('duration'))

        data = {
            'success': 'false',
            'message': "Service already exist"
        }
    except Exception, e:
        card_obj = ServiceRateCard(
            service_name=request.POST.get('service'),
            duration=request.POST.get('duration'),
            cost=request.POST.get('price'),
            service_rate_card_status='1',
            service_rate_card_created_date=datetime.now(),
            service_rate_card_updated_date=datetime.now(),
            service_rate_card_created_by='Admin',
            service_rate_card_updated_by='Admin'
        )
        card_obj.save()

    add_service_sms(card_obj)
    rate_card_add_mail(card_obj)

    data = {
        'success': 'true',
        'message': "Service added successfully"
    }
    return HttpResponse(json.dumps(data), content_type='application/json')


def add_service_sms(card_obj):
    authkey = "118994AIG5vJOpg157989f23"
    # user_obj = Supplier.objects.get(supplier_id=su_id)
    #    contact_no = user_obj.contact_no
    #    print '---------contact_no------',contact_no

    mobiles = "+919403884595"
    message = "Hi Admin,\n Service Rate Card has been added successfully"
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
    print "sagar"


def service_list(request):
    print "===IN SERVICE LIST"
    try:
        data = {}
        final_list = []
        try:
            service_list = ServiceRateCard.objects.all()
            for service_obj in service_list:
                service_name = service_obj.service_name
                duration = str(service_obj.duration) + " Days"
                price = service_obj.cost
                if service_obj.service_rate_card_status == '1':
                    # edit = '<a class="col-md-offset-2 col-md-1" id="'+str(role_id)+'" onclick="edit_user_role(this.id);" style="text-align: center;letter-spacing: 5px;width:15%;" title="Edit" class="edit" data-toggle="modal" href="#edit_subscription"><i class="fa fa-pencil"></i></a>'
                    edit = '<a class="col-md-2" id="' + str(
                        service_obj.service_rate_card_id) + '" onclick="edit_service(this.id);" style="text-align: center;letter-spacing: 5px;width:15%;" title="Edit" class="edit" data-toggle="modal" ><i class="fa fa-pencil"></i></a>'
                    delete = '<a id="' + str(
                        service_obj) + '" onclick="inactive_service(this.id)" style="text-align: center;letter-spacing: 5px;width:15%;" title="Delete"  ><i class="fa fa-trash"></i></a>'
                    status = 'Active'
                    actions = edit + delete
                else:
                    status = 'Inactive'
                    active = '<a class="col-md-2" id="' + str(
                        service_obj) + '" onclick="active_service(this.id);" style="text-align: center;letter-spacing: 5px;width:15%;" title="Activate" class="edit" data-toggle="modal" href="#edit_subscription"><i class="fa fa-repeat"></i></a>'
                    actions = active
                list = {'status': status, 'service_name': service_name, 'actions': actions, 'duration': duration,
                        'price': price}
                final_list.append(list)
            data = {'success': 'true', 'data': final_list}
        except IntegrityError as e:
            print e
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def delete_service(request):
    try:
        service_obj = ServiceRateCard.objects.get(service_rate_card_id=request.POST.get('service_id'))
        service_obj.service_rate_card_status = '0'
        service_obj.save()
        #delete_service_sms(service_obj)
        #rate_card_delete_mail(service_obj)
        data = {'message': 'Service Inactivated Successfully', 'success': 'true'}

    except IntegrityError as e:
        print e
    except Exception, e:
        print e
    return HttpResponse(json.dumps(data), content_type='application/json')


def delete_service_sms(card_obj):
    authkey = "118994AIG5vJOpg157989f23"
    # user_obj = Supplier.objects.get(supplier_id=su_id)
    #    contact_no = user_obj.contact_no
    #    print '---------contact_no------',contact_no

    mobiles = "+919403884595"
    message = "Hi Admin,\n Service Rate Card has been deactivated successfully"
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
    print "sagar"


@csrf_exempt
def active_service(request):
    try:
        service_obj = ServiceRateCard.objects.get(service_rate_card_id=request.POST.get('service_id'))
        service_obj.service_rate_card_status = '1'
        service_obj.save()
        rate_card_activate_mail(service_obj)
        data = {'message': 'Service activated Successfully', 'success': 'true'}

    except IntegrityError as e:
        print e
    except Exception, e:
        print e
    print "Final Data: ", data
    return HttpResponse(json.dumps(data), content_type='application/json')


def rate_card_activate_mail(rate_card_obj):
    gmail_user = "cityhoopla2016"
    gmail_pwd = "cityhoopla@2016"
    FROM = 'CityHoopla Admin <cityhoopla2016@gmail.com>'
    TO = ['cityhoopla2016@gmail.com']
    try:
        TEXT = "Hi Admin,\nService Rate Card " + str(
            rate_card_obj.service_name) + " " + " has been activated successfully.\nTo view complete details visit portal and follow - Rate Card -> Service\n\nThank You," + '\n' + "CityHoopla Team"
        SUBJECT = "Service Rate Card Activated Successfully!"
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException, e:
        print e


def rate_card_add_mail(rate_card_obj):
    gmail_user = "cityhoopla2016"
    gmail_pwd = "cityhoopla@2016"
    FROM = 'CityHoopla Admin <cityhoopla2016@gmail.com>'
    TO = ['cityhoopla2016@gmail.com']
    try:
        TEXT = "Hi Admin,\nService Rate Card " + str(
            rate_card_obj.service_name) + " " + " has been added successfully.\nTo view complete details visit portal and follow - Rate Card -> Service\n\nThank You," + '\n' + "CityHoopla Team"
        SUBJECT = "Service Rate Card Added Successfully!"
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException, e:
        print e


def rate_card_delete_mail(rate_card_obj):
    gmail_user = "cityhoopla2016"
    gmail_pwd = "cityhoopla@2016"
    FROM = 'CityHoopla Admin <cityhoopla2016@gmail.com>'
    TO = ['cityhoopla2016@gmail.com']
    # pdb.set_trace()
    try:
        TEXT = "Hi Admin,\nService Rate Card " + str(
            rate_card_obj.service_name) + " " + "deactivated successfully.\n\nThank You," + '\n' + "CityHoopla Team"
        SUBJECT = "Service Rate Card Deactivated Successfully!"
        # server = smtplib.SMTP_SSL()
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()

        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException, e:
        print e
    return 1


@csrf_exempt
def add_premium_service(request):
    try:
        rate_card_obj = AdvertRateCard.objects.get(advert_service_name=request.POST.get('premium_service'),
                                                   duration=request.POST.get('premium_duration'))

        data = {
            'success': 'false',
            'message': "Service already exist"
        }
    except Exception, e:
        card_obj = AdvertRateCard(
            advert_service_name=request.POST.get('premium_service'),
            duration=request.POST.get('premium_duration'),
            cost=request.POST.get('premium_price'),
            advert_rate_card_status='1',
            advert_rate_card_created_date=datetime.now(),
            advert_rate_card_updated_date=datetime.now(),
            advert_rate_card_created_by='Admin',
            advert_rate_card_updated_by='Admin'
        )
        card_obj.save()

    add_premium_service_sms(card_obj)
    premium_rate_card_add_mail(card_obj)

    data = {
        'success': 'true',
        'message': "Service added successfully"
    }
    return HttpResponse(json.dumps(data), content_type='application/json')


def add_premium_service_sms(card_obj):
    authkey = "118994AIG5vJOpg157989f23"
    # user_obj = Supplier.objects.get(supplier_id=su_id)
    #    contact_no = user_obj.contact_no
    #    print '---------contact_no------',contact_no

    mobiles = "+919403884595"
    message = "Hi Admin,\n Premium Service Rate Card has been added successfully"
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
    print "sagar"


def premium_service_list(request):
    try:
        data = {}
        final_list = []
        try:
            premium_service_list = AdvertRateCard.objects.all()
            for service_obj in premium_service_list:
                service_name = service_obj.advert_service_name
                duration = str(service_obj.duration) + " Days"
                price = service_obj.cost
                if service_obj.advert_rate_card_status == '1':
                    edit = '<a class="col-md-2" id="' + str(
                        service_obj.advert_rate_card_id) + '" onclick="edit_premium_service(this.id);" style="text-align: center;letter-spacing: 5px;width:15%;" title="Edit" class="edit" data-toggle="modal" ><i class="fa fa-pencil"></i></a>'
                    delete = '<a id="' + str(
                        service_obj) + '" onclick="inactive_premium_service(this.id)" style="text-align: center;letter-spacing: 5px;width:15%;" title="Delete"  ><i class="fa fa-trash"></i></a>'
                    status = 'Active'
                    actions = edit + delete
                else:
                    status = 'Inactive'
                    active = '<a class="col-md-2" id="' + str(
                        service_obj) + '" onclick="active_premium_service(this.id);" style="text-align: center;letter-spacing: 5px;width:15%;" title="Activate" class="edit" data-toggle="modal" href="#edit_subscription"><i class="fa fa-repeat"></i></a>'
                    actions = active
                list = {'status': status, 'service_name': service_name, 'actions': actions, 'duration': duration,
                        'price': price}
                final_list.append(list)
            data = {'success': 'true', 'data': final_list}
        except IntegrityError as e:
            print e
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time'}
    except MySQLdb.OperationalError, e:
        print e
    except Exception, e:
        print 'Exception ', e
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def delete_premium_service(request):
    try:
        service_obj = AdvertRateCard.objects.get(advert_rate_card_id=request.POST.get('premium_service_id'))
        service_obj.advert_rate_card_status = '0'
        service_obj.save()
        premium_rate_card_delete_mail(service_obj)
        delete_premium_service_sms(service_obj)
        data = {'message': 'Service Inactivated Successfully', 'success': 'true'}

    except IntegrityError as e:
        print e
    except Exception, e:
        print e
    return HttpResponse(json.dumps(data), content_type='application/json')


def delete_premium_service_sms(card_obj):
    authkey = "118994AIG5vJOpg157989f23"
    # user_obj = Supplier.objects.get(supplier_id=su_id)
    #    contact_no = user_obj.contact_no
    #    print '---------contact_no------',contact_no

    mobiles = "+919403884595"
    message = "Hi Admin,\n Premium Service Rate Card has been deactivated successfully"
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
    print "sagar"


def premium_rate_card_add_mail(rate_card_obj):
    gmail_user = "cityhoopla2016"
    gmail_pwd = "cityhoopla@2016"
    FROM = 'CityHoopla Admin <cityhoopla2016@gmail.com>'
    TO = ['cityhoopla2016@gmail.com']
    try:
        TEXT = "Hi Admin,\nPremium Service Rate Card " + str(
            rate_card_obj.advert_service_name) + " " + " has been added successfully.\nTo view complete details visit portal and follow - Rate Card -> Premium Service\n\nThank You," + '\n' + "CityHoopla Team"
        SUBJECT = "Premium Service Rate Card Added Successfully!"
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException, e:
        print e


def premium_rate_card_delete_mail(rate_card_obj):
    gmail_user = "cityhoopla2016"
    gmail_pwd = "cityhoopla@2016"
    FROM = 'CityHoopla Admin <cityhoopla2016@gmail.com>'
    TO = ['cityhoopla2016@gmail.com']
    # pdb.set_trace()
    try:
        TEXT = "Hi Admin,\nService Rate Card " + str(
            rate_card_obj.advert_service_name) + " " + "deactivated successfully.\n\nThank You," + '\n' + "CityHoopla Team"
        SUBJECT = "Premium Service Rate Card Deactivated Successfully!"
        # server = smtplib.SMTP_SSL()
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()

        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException, e:
        print e
    return 1


@csrf_exempt
def active_premium_service(request):
    try:
        service_obj = AdvertRateCard.objects.get(advert_rate_card_id=request.POST.get('premium_service_id'))
        service_obj.advert_rate_card_status = '1'
        service_obj.save()
        advert_rate_card_activate_mail(service_obj)
        data = {'message': 'Premium Service activated Successfully', 'success': 'true'}

    except IntegrityError as e:
        print e
    except Exception, e:
        print e
    print "Final Data: ", data
    return HttpResponse(json.dumps(data), content_type='application/json')


def advert_rate_card_activate_mail(rate_card_obj):
    gmail_user = "cityhoopla2016"
    gmail_pwd = "cityhoopla@2016"
    FROM = 'CityHoopla Admin <cityhoopla2016@gmail.com>'
    TO = ['cityhoopla2016@gmail.com']
    try:
        TEXT = "Hi Admin,\nAdvert Rate Card " + str(
            rate_card_obj.advert_service_name) + " " + " has been activated successfully.\nTo view complete details visit portal and follow - Rate Card ->Premium Service\n\nThank You," + '\n' + "CityHoopla Team"
        SUBJECT = "Premium Service Rate Card Activated Successfully!"
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException, e:
        print e


@csrf_exempt
def edit_service(request):
    try:
        data = {}
        final_list = []
        try:
            if request.method == "GET":
                print request
                service_obj = ServiceRateCard.objects.get(service_rate_card_id=request.GET.get('service_id'))

                data = {'success': 'true', 'service': service_obj.service_name,
                        'rate_card_service_id': str(service_obj.service_rate_card_id),
                        'duration': str(service_obj.duration), 'price': str(service_obj.cost)}
                print "=====Service Info====", data
        except IntegrityError as e:
            print e
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time'}

    except MySQLdb.OperationalError, e:
        print e

    except Exception, e:
        print 'Exception ', e
    print data
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def edit_premium_service(request):
    try:
        data = {}
        final_list = []
        try:
            if request.method == "GET":
                print request
                service_obj = AdvertRateCard.objects.get(advert_rate_card_id=request.GET.get('service_id'))

                data = {'success': 'true', 'service': service_obj.advert_service_name,
                        'premium_rate_card_service_id': str(service_obj.advert_rate_card_id),
                        'duration': str(service_obj.duration), 'price': str(service_obj.cost)}
                print "=====Service Info====", data
        except IntegrityError as e:
            print e
            data = {'success': 'false', 'message': 'Error in  loading page. Please try after some time'}

    except MySQLdb.OperationalError, e:
        print e

    except Exception, e:
        print 'Exception ', e
    print data
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def update_service(request):
    try:
        print request.POST
        data = {}
        service_obj = request.POST.get('service_name')
        service_rate_card_id = request.POST.get('rate_card_service_id')
        try:
            service_object = ServiceRateCard.objects.get(service_name=request.POST.get('service'),
                                                         duration=request.POST.get('duration'),
                                                         service_rate_card_status=1)
            if (str(service_rate_card_id) == str(service_object)):
                service_object = ServiceRateCard.objects.get(service_name=request.POST.get('service'),
                                                             duration=request.POST.get('duration'),
                                                             service_rate_card_status=1)
                service_object.service_name = request.POST.get('service')
                service_object.duration = request.POST.get('duration')
                service_object.cost = request.POST.get('price')
                service_object.service_rate_card_status = '1'
                service_object.service_rate_card_updated_date = datetime.now()
                service_object.service_rate_card_updated_by = 'Admin'
                service_object.save()

                data = {'success': 'true'}
                update_service_rate_card(service_object)
                update_service_sms(service_object)
            else:
                data = {'success': 'false'}
        except:
            service_object = ServiceRateCard.objects.get(service_rate_card_id=service_rate_card_id)
            service_object.service_name = request.POST.get('service')
            service_object.duration = request.POST.get('duration')
            service_object.cost = request.POST.get('price')
            service_object.service_rate_card_status = '1'
            service_object.service_rate_card_updated_date = datetime.now()
            service_object.service_rate_card_updated_by = 'Admin'
            service_object.save()
            update_service_rate_card(service_object)
            update_service_sms(service_object)
            data = {
                'success': 'true',
            }
    except Exception, e:
        data = {
            'success': 'false',
            'message': str(e)
        }
    print '========data====================', data
    return HttpResponse(json.dumps(data), content_type='application/json')


def update_service_sms(card_obj):
    authkey = "118994AIG5vJOpg157989f23"
    # user_obj = Supplier.objects.get(supplier_id=su_id)
    #    contact_no = user_obj.contact_no
    #    print '---------contact_no------',contact_no

    mobiles = "+919403884595"
    message = "Hi Admin,\n Service Rate Card has been updated successfully"
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
    print "sagar"


def update_service_rate_card(rate_card_obj):
    gmail_user = "cityhoopla2016"
    gmail_pwd = "cityhoopla@2016"
    FROM = 'CityHoopla Admin <cityhoopla2016@gmail.com>'
    TO = ['cityhoopla2016@gmail.com']
    # pdb.set_trace()
    try:
        TEXT = "Hi Admin,\nService Rate Card " + str(
            rate_card_obj.service_name) + " " + "updated successfully.\nTo view complete details visit portal and follow - Rate Card -> Service\n\nThank You," + '\n' + "CityHoopla Team"
        SUBJECT = "Service Rate Card Updated Successfully!"
        # server = smtplib.SMTP_SSL()
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()

        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException, e:
        print e
    return 1


@csrf_exempt
def update_premium_service(request):
    # pdb.set_trace()
    print "========In update Premium Service"
    try:
        print request.POST
        data = {}
        service_obj = request.POST.get('premium_service')
        advert_rate_card_id = request.POST.get('premium_rate_card_service_id')
        print "===advert_rate_card_id", advert_rate_card_id
        try:
            print "IN TRY OF UPDATE"
            service_object = AdvertRateCard.objects.get(advert_service_name=request.POST.get('premium_service'),
                                                        duration=request.POST.get('premium_duration'),
                                                        advert_rate_card_status=1)
            print "====service_object", service_object
            if (str(advert_rate_card_id) == str(service_object)):
                print "=====IN IF"
                service_object = AdvertRateCard.objects.get(advert_service_name=request.POST.get('premium_service'),
                                                            duration=request.POST.get('premium_duration'),
                                                            advert_rate_card_status=1)
                service_object.advert_service_name = request.POST.get('premium_service')
                service_object.duration = request.POST.get('premium_duration')
                service_object.cost = request.POST.get('premium_price')
                service_object.advert_rate_card_status = '1'
                service_object.advert_rate_card_updated_date = datetime.now()
                service_object.advert_rate_card_updated_by = 'Admin'
                service_object.save()
                update_premium_service_sms(service_object)
                update_advert_rate_card(service_object)
                data = {'success': 'true'}
            else:
                print '======in else======='
                data = {'success': 'false'}
        except:
            print "IN EXCEPTION"
            service_object = AdvertRateCard.objects.get(advert_rate_card_id=advert_rate_card_id)
            service_object.advert_service_name = request.POST.get('premium_service')
            service_object.duration = request.POST.get('premium_duration')
            service_object.cost = request.POST.get('premium_price')
            service_object.advert_rate_card_status = '1'
            service_object.advert_rate_card_updated_date = datetime.now()
            service_object.advert_rate_card_updated_by = 'Admin'
            service_object.save()
            update_premium_service_sms(service_object)
            update_advert_rate_card(service_object)
            data = {
                'success': 'true',
            }
    except Exception, e:
        data = {
            'success': 'false',
            'message': str(e)
        }
    print '========data====================', data
    return HttpResponse(json.dumps(data), content_type='application/json')


def update_premium_service_sms(card_obj):
    authkey = "118994AIG5vJOpg157989f23"
    # user_obj = Supplier.objects.get(supplier_id=su_id)
    #    contact_no = user_obj.contact_no
    #    print '---------contact_no------',contact_no

    mobiles = "+919403884595"
    message = "Hi Admin,\n Premium Service Rate Card has been updated successfully"
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
    print "sagar"


def update_advert_rate_card(rate_card_obj):
    gmail_user = "cityhoopla2016"
    gmail_pwd = "cityhoopla@2016"
    FROM = 'CityHoopla Admin <cityhoopla2016@gmail.com>'
    TO = ['cityhoopla2016@gmail.com']
    # pdb.set_trace()
    try:
        TEXT = "Hi Admin,\nAdvert Rate Card " + str(
            rate_card_obj.advert_service_name) + " " + "updated successfully.\nTo view complete details visit portal and follow - Rate Card ->Premium Service\n\nThank You," + '\n' + "CityHoopla Team"
        SUBJECT = "Premium Service Rate Card Updated Successfully!"
        # server = smtplib.SMTP_SSL()
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()

        server.login(gmail_user, gmail_pwd)
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        server.sendmail(FROM, TO, message)
        server.quit()
    except SMTPException, e:
        print e
    return 1
