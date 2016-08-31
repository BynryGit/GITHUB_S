
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
#importing exceptions
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


SERVER_URL = "http://52.40.205.128"   

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_subscriber(request):
	if not request.user.is_authenticated():
		return redirect('backoffice')
	else:	
	    state_list = State.objects.filter(state_status='1').order_by('state_name')
	    tax_list = Tax.objects.all()
	    category_list = Category.objects.filter(category_status='1').order_by('category_name')
	    
	    #service_list = ServiceRateCard.objects.filter(service_rate_card_status='1').order_by('service_name')
	    #advert_service_list = AdvertRateCard.objects.filter(advert_rate_card_status='1').order_by('advert_service_name')
	    service_list = ServiceRateCard.objects.filter(service_rate_card_status='1').values('service_name').distinct()    
	    advert_service_list, item_ids = [], []
	    for item in AdvertRateCard.objects.filter(advert_rate_card_status='1'):
	        if item.advert_service_name not in item_ids:
	            advert_service_list.append(str(item.advert_rate_card_id))
	            item_ids.append(item.advert_service_name)

	    advert_service_list = AdvertRateCard.objects.filter(advert_rate_card_id__in=advert_service_list,advert_rate_card_status='1')        
	    
	    #data = {'username':request.session['login_user'],'tax_list':tax_list,'state_list':state_list,'category_list':category_list}
	    data = {'username':request.session['login_user'],'advert_service_list':advert_service_list,'service_list':service_list,'tax_list':tax_list,'state_list':state_list,'category_list':category_list}
	    return render(request,'Admin/add_supplier.html',data)       

@csrf_exempt
def save_supplier(request):
	try:
	    supplier_obj = Supplier(
	    	business_name = request.POST.get('business_name'),
	    	phone_no = request.POST.get('phone_no'),
	    	secondary_phone_no = request.POST.get('sec_phone_no'),
	    	supplier_email = request.POST.get('email'),	
	    	secondary_email = request.POST.get('sec_email'),
	    	address1 = request.POST.get('address1'),
	    	address2 = request.POST.get('address2'),
	    	city = City.objects.get(city_id=request.POST.get('city')),
	    	state = State.objects.get(state_id=request.POST.get('state')),
	    	pincode = Pincode.objects.get(pincode=request.POST.get('pincode')),
	    	business_details = request.POST.get('business'),
	    	contact_person = request.POST.get('user_name'),
	    	contact_email = request.POST.get('user_email'),
	    	contact_no = request.POST.get('user_contact_no'),
	    	username = request.POST.get('user_email'),
	    	supplier_status='1'
	    	)
	    supplier_obj.save()
	    supplier_add_mail(supplier_obj)
	    try:
	    	supplier_obj.logo = request.FILES['logo']
	    except:
	    	pass
	    data={
			'success':'true',
			'message':"Supplier added successfully"
		}
	except Exception, e:
		data={
			'success':'false',
			'message':str(e)
		}
	return HttpResponse(json.dumps(data),content_type='application/json')    


@csrf_exempt
def save_service(request):
	try:
		serv_obj = ServiceRateCard.objects.get(service_name=request.POST.get('service'),duration=request.POST.get('selected_duration'))		
		try:
			premium_service_list = request.POST.get('premium_service')
			no_of_days_list = request.POST.get('premium_day_list')
			if(premium_service_list):

				final_data = check_subscription(premium_service_list,no_of_days_list)
				if final_data['success']=='true':				
					chars= string.digits
					pwdSize = 8
					password = ''.join(random.choice(chars) for _ in range(pwdSize))
					supplier_obj = Supplier.objects.get(username = request.POST.get('user_email'))
					business_obj = Business(
						category = Category.objects.get(category_name=request.POST.get('category')),
						service_rate_card_id = ServiceRateCard.objects.get(service_name=request.POST.get('service'),duration=request.POST.get('selected_duration')),
						duration = request.POST.get('selected_duration'),
						start_date = request.POST.get('duration_start_date'),
						end_date = request.POST.get('duration_end_date'),
						supplier= supplier_obj,
						transaction_code = "TID" + str(password),
						is_active = 0
					)
					business_obj.save()
					premium_service_list = request.POST.get('premium_service')
					if(premium_service_list!=['']):
						premium_service_list = str(premium_service_list).split(',')
						no_of_days_list = request.POST.get('premium_day')
						no_of_days_list = str(no_of_days_list).split(',')
						start_date_list = request.POST.get('premium_start_date')
						start_date_list = str(start_date_list).split(',')

						end_date_list = request.POST.get('premium_end_date')
						end_date_list = str(end_date_list).split(',')
						zipped_wk = zip(premium_service_list,no_of_days_list,start_date_list,end_date_list)
						save_working_hours(zipped_wk,business_obj)
					supplier_add_service_mail(business_obj)
					data={
						'success':'true',
						'message':"Supplier added successfully",
						'transaction_code': str(business_obj.transaction_code),
						'subscriber_id': str(supplier_obj.supplier_id)

					}
				else:
				 	data={
				 		'success':'false',
				 		'message':final_data['message']
				 	}	
			else:
				chars= string.digits
				pwdSize = 8
				password = ''.join(random.choice(chars) for _ in range(pwdSize))
				supplier_obj = Supplier.objects.get(username = request.POST.get('user_email'))
				business_obj = Business(
					category = Category.objects.get(category_name=request.POST.get('category')),
					service_rate_card_id = ServiceRateCard.objects.get(service_name=request.POST.get('service'),duration=request.POST.get('selected_duration')),
					duration = request.POST.get('selected_duration'),
					start_date = request.POST.get('duration_start_date'),
					end_date = request.POST.get('duration_end_date'),
					supplier= supplier_obj,
					transaction_code = "TID" + str(password),
					is_active = 0
				)
				business_obj.save()	
				supplier_add_service_mail(business_obj)
				data={
						'success':'true',
						'message':"Supplier added successfully",
						'transaction_code': str(business_obj.transaction_code),
						'subscriber_id': str(supplier_obj.supplier_id)

					}
		except Exception, e:
			data={
				'success':'false',
				'message':str(e)
			}
	except:
		data={
				'success':'false',
				'message':'Package ' + str(request.POST.get('service')) + ' ' +'(' + str(request.POST.get('selected_duration')) + ' Days)' + ' not available' 
			}		
	return HttpResponse(json.dumps(data),content_type='application/json')

@csrf_exempt
def edit_service(request):
	try:
		serv_obj = ServiceRateCard.objects.get(service_name=request.POST.get('service'),duration=request.POST.get('selected_duration'))
		try:
			supplier_obj = Supplier.objects.get(username = request.POST.get('user_email'))
			premium_service_list = request.POST.get('premium_service')
			no_of_days_list = request.POST.get('premium_day_list')
			if(premium_service_list):
				final_data = check_subscription(premium_service_list,no_of_days_list)
				if final_data['success']=='true':
					try:		
						business_obj = Business.objects.get(supplier=supplier_obj)
						business_obj.category = Category.objects.get(category_name=request.POST.get('category')) 
						business_obj.service_rate_card_id = ServiceRateCard.objects.get(service_name=request.POST.get('service'),duration=request.POST.get('selected_duration'))
						business_obj.duration = request.POST.get('selected_duration')
						business_obj.start_date = request.POST.get('duration_start_date')
						business_obj.end_date = request.POST.get('duration_end_date')
						business_obj.save()
					except:
						chars= string.digits
						pwdSize = 8
						password = ''.join(random.choice(chars) for _ in range(pwdSize))
						business_obj = Business(
						category = Category.objects.get(category_name=request.POST.get('category')),
						service_rate_card_id = ServiceRateCard.objects.get(service_name=request.POST.get('service'),duration=request.POST.get('selected_duration')),
						duration = request.POST.get('selected_duration'),
						start_date = request.POST.get('duration_start_date'),
						end_date = request.POST.get('duration_end_date'),
						supplier= supplier_obj,
						transaction_code = "TID" + str(password),
						is_active = 0
						)
					business_obj.save()
					premium_service_obj = PremiumService.objects.filter(business_id=business_obj).delete()
					premium_service_list = request.POST.get('premium_service')
					premium_service_list = str(premium_service_list).split(',')
					no_of_days_list = request.POST.get('premium_day_list')
					no_of_days_list = str(no_of_days_list).split(',')
					start_date_list = request.POST.get('premium_start_date')
					start_date_list = str(start_date_list).split(',')
					end_date_list = request.POST.get('premium_end_date')
					end_date_list = str(end_date_list).split(',')
					zipped_wk = zip(premium_service_list,no_of_days_list,start_date_list,end_date_list)
					save_working_hours(zipped_wk,business_obj)
					data={
						'success':'true',
						'message':"Supplier profile edited successfully",
						'transaction_code' : str(business_obj.transaction_code),
						'subscriber_id': str(supplier_obj.supplier_id)
					}
					supplier_edit_service_mail(business_obj)
				else:
				 	data={
				 		'success':'false',
				 		'message':final_data['message']
				 	}	
			else:
				premium_service_obj = PremiumService.objects.filter(business_id=business_obj).delete()
				try:		
					business_obj = Business.objects.get(supplier=supplier_obj)
					business_obj.category = Category.objects.get(category_name=request.POST.get('category')) 
					business_obj.service_rate_card_id = ServiceRateCard.objects.get(service_name=request.POST.get('service'),duration=request.POST.get('selected_duration'))
					business_obj.duration = request.POST.get('selected_duration')
					business_obj.start_date = request.POST.get('duration_start_date')
					business_obj.end_date = request.POST.get('duration_end_date')
					business_obj.save()
				except:
					chars= string.digits
					pwdSize = 8
					password = ''.join(random.choice(chars) for _ in range(pwdSize))
					business_obj = Business(
					category = Category.objects.get(category_name=request.POST.get('category')),
					service_rate_card_id = ServiceRateCard.objects.get(service_name=request.POST.get('service'),duration=request.POST.get('selected_duration')),
					duration = request.POST.get('selected_duration'),
					start_date = request.POST.get('duration_start_date'),
					end_date = request.POST.get('duration_end_date'),
					supplier= supplier_obj,
					transaction_code = "TID" + str(password),
					is_active = 0
					)
					business_obj.save()	
				data={
						'success':'true',
						'message':"Supplier profile edited successfully",
						'transaction_code' : str(business_obj.transaction_code),
						'subscriber_id': str(supplier_obj.supplier_id)
				}	
		except Exception, e:
			data={
				'success':'false',
				'message':str(e)
			}
	except:
		data={
				'success':'false',
				'message':'Package ' + str(request.POST.get('service')) + ' ' +'(' + str(request.POST.get('selected_duration')) + ' Days)' + ' not available' 
			}
	return HttpResponse(json.dumps(data),content_type='application/json')




def save_working_hours(zipped_wk,business_obj):
    try:
        for wk_serv,wk_day,strt_tm,end_tm in zipped_wk:
            wk_obj = PremiumService(
            business_id = business_obj,
            premium_service_name=wk_serv,
            no_of_days=wk_day,
            start_date=strt_tm,
            end_date=end_tm,
            premium_service_status='1',
            premium_service_created_date=datetime.now(),
            premium_service_created_by="Admin",
            premium_service_updated_by="Admin",
            premium_service_updated_date=datetime.now()
            )
            wk_obj.save()
            data = {'success': 'true'}
        
    except Exception, e:
        print 'Exception ', e    
    return HttpResponse(json.dumps(data), content_type='application/json')	    

    

@csrf_exempt
def register_supplier(request):
	try:
		supplier_obj = Supplier.objects.get(username = request.POST.get('user_email'))
		chars= string.digits
		pwdSize = 8
		password = ''.join(random.choice(chars) for _ in range(pwdSize))
		business_obj =  Business.objects.get(supplier_id=str(supplier_obj.supplier_id))	

		payment_obj = PaymentDetail(
			business_id = business_obj,
			note = request.POST.get('note'),
			payment_mode = request.POST.get('payment_mode'),
			paid_amount = request.POST.get('paid_amount'),
			payable_amount = request.POST.get('payable_amount'),
			total_amount = request.POST.get('generated_amount'),
			tax_type = Tax.objects.get(tax_type=request.POST.get('selected_tax_type')),
			payment_code = "PMID" + str(password)
			)
		payment_obj.save()
		data={
		'success':'true',
		'message':"Supplier added successfully",
		'payment_code': str(payment_obj.payment_code),
		'user_id':str(supplier_obj.supplier_id)
			}
		supplier_add_payment_mail(payment_obj)

	except Exception, e:
		data={
				'success':'false',
				'message':str(e)
		}
	print '=========data============',data	
	return HttpResponse(json.dumps(data),content_type='application/json')

@csrf_exempt
def get_amount(request):
	try:
		premium_service_list = request.POST.get('premium_service_list')
		premium_service_list = str(premium_service_list).split(',')

		premium_day = request.POST.get('premium_day')
		premium_day = str(premium_day).split(',')

		zipped_wk = zip(premium_service_list,premium_day)
		rate_card_obj = ServiceRateCard.objects.get(service_name=request.POST.get('service'),duration=request.POST.get('duration'))
		final_cost = int(rate_card_obj.cost)
		if zipped_wk!=[('', '')]:

			for serv,day in zipped_wk:
				service_rate_card_obj = AdvertRateCard.objects.get(advert_service_name=serv,duration=day)
				final_cost = int(final_cost)+int(service_rate_card_obj.cost)

		data={
				'success':'true',
				'cost': str(final_cost)
		}
	except Exception, e:
		data={
			'success':'false',
			'message':str(e)
		}
	return HttpResponse(json.dumps(data),content_type='application/json')    

def view_subscriber_list(request):
	try:
		data = {}
		final_list = []
		try:
			user_list = Supplier.objects.all()
			for user_obj in user_list:
				user_id = str(user_obj.supplier_id)
				business_name = user_obj.business_name
				user_name = user_obj.contact_person
				usre_email_id = user_obj.contact_email
				user_contact_no = user_obj.contact_no
				user_city = user_obj.city.city_name
				# try:
				# 	subscription_obj = Business.objects.get(supplier=user_obj)
				# 	subscription = str(subscription_obj.service_rate_card_id.service_name)
				# 	category = str(subscription_obj.category.category_name)
				# 	subscription_start_date = subscription_obj.start_date
				# 	subscription_end_date = subscription_obj.end_date
				# except Exception,e:
				# 	subscription = '---'
				# 	category = '---'
				# 	subscription_start_date = '---'
				# 	subscription_end_date = '---'
				subscription = '---'
				category = '---'
				subscription_start_date = '---'
				subscription_end_date = '---'
				subscription_obj = Business.objects.filter(supplier=user_obj)
				print '=========len==========',len(subscription_obj)
				if len(subscription_obj)<=1:
					edit = '<a  id="'+str(user_id)+'" title="Edit" class="edit" style="padding: 8px;" data-toggle="modal;" href="/edit-subscriber/?user_id='+str(user_id)+'"><i class="fa fa-pencil"></i></a>'
				else:
					edit = '<a  id="'+str(user_id)+'" title="Edit" class="edit" style="padding: 8px;" data-toggle="modal;" href="/edit-subscriber-detail/?user_id='+str(user_id)+'"><i class="fa fa-pencil"></i></a>'

				

				if user_obj.supplier_status == '1':
					status= 'Active'
					advert = '<a  id="'+str(user_id)+'"  style="text-align: center; padding: 8px;" title="Advert" class="edit" data-toggle="modal" onclick="check_advert(this.id)" ><i class="fa fa-shopping-cart"></i></a>'
					#edit = '<a  id="'+str(user_id)+'" title="Edit" class="edit" style="padding: 8px;" data-toggle="modal;" href="/edit-subscriber/?user_id='+str(user_id)+'"><i class="fa fa-pencil"></i></a>'
					delete = '<a  id="'+str(user_id)+'" onclick="delete_user_detail(this.id)" style="padding: 8px;"  title="Delete"  ><i class="fa fa-trash"></i></a>'
					actions =  advert + edit + delete
				else:
					status = 'Inactive'
					active = '<a  id="'+str(user_id)+'" onclick="active_subscriber(this.id);" style="text-align: center;letter-spacing: 5px;width:15%;" title="Activate" class="edit" data-toggle="modal" ><i class="fa fa-repeat"></i></a>'
					actions =  active
		
					
				list = {'subscriber_category':category,
						'subscription_end_date':subscription_end_date,
						'subscription_start_date':subscription_start_date,
						'subscriber_subscription':subscription,
						'subscriber_city':user_city,
						'subscriber_id':user_id,
						'business_name':business_name,
						'subscriber_name':user_name,
						'actions':actions,
						'usre_email_id':user_contact_no+', '+usre_email_id,
						'user_contact_no':user_contact_no,
						'status':status}
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
def delete_subscriber(request):
        try:
            user_obj = Supplier.objects.get(supplier_id=request.POST.get('user_id'))
            user_obj.supplier_status = '0'
            user_obj.save()
            supplier_inactive_mail(user_obj)
            data = {'message': 'User Inactivated Successfully', 'success':'true'}

        except IntegrityError as e:
          print e
        except Exception,e:
            print e
        print "Final Data: ",data
        return HttpResponse(json.dumps(data), content_type='application/json')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_subscriber(request):
	if not request.user.is_authenticated():
		return redirect('backoffice')
	else:	
		state_list = State.objects.filter(state_status='1').order_by('state_name')
		category_list = Category.objects.filter(category_status='1').order_by('category_name')
		tax_list = Tax.objects.all()
		subscriber_obj = Supplier.objects.get(supplier_id=request.GET.get('user_id'))
		business_name = subscriber_obj.business_name
		phone_no = subscriber_obj.phone_no
		secondary_phone_no = subscriber_obj.secondary_phone_no
		supplier_email = subscriber_obj.supplier_email
		secondary_email = subscriber_obj.secondary_email
		try:
	 		display_image = SERVER_URL + subscriber_obj.logo.url
	 		file_name = str(subscriber_obj.logo)[19:]
	 	except:
	 		display_image = ''
	 		file_name = ''

		address1 = subscriber_obj.address1
		address2 = subscriber_obj.address2
		state = subscriber_obj.state
		city_list = City.objects.filter(state_id=state,city_status='1') 
		city = subscriber_obj.city
		pincode_list = Pincode.objects.filter(city_id=city,pincode_status='1')
		pincode = subscriber_obj.pincode
		business_details = subscriber_obj.business_details
		contact_person = subscriber_obj.contact_person
		contact_no = subscriber_obj.contact_no
		contact_email = subscriber_obj.contact_email
		duration_list = {}
		category = ''
		duration = 0
		start_date = ''
		end_date = ''
		subscription = ''
		service_list = []
		payment_mode = ''
		note = ''
		paid_amount = ''
		payable_amount = ''
		total_amount = ''
		tax_type = '0'
		service_code = ''
		service_rate_card_list = ServiceRateCard.objects.filter(service_rate_card_status='1').values('service_name').distinct()

		try:
			business_obj = Business.objects.get(supplier=subscriber_obj)
			category = business_obj.category.category_name
			subscription = business_obj.service_rate_card_id.service_name
			duration = business_obj.duration
			if duration=='3':
				duration_list = {3}
			elif duration=='7':
				duration_list = {3,7}
			elif duration=='30':
				duration_list = {3,7,30}
			elif duration=='90':
				duration_list = {3,7,30,90}
			elif duration=='180':
				duration_list = {3,7,30,90,180}

			start_date = business_obj.start_date
			end_date = business_obj.end_date
			premium_service_list = PremiumService.objects.filter(business_id=business_obj)
			for service in premium_service_list:
			 	service_list = {'service':service}
		except Exception,e:
			pass

		#advert_service_list = AdvertRateCard.objects.filter(advert_rate_card_status='1').order_by('advert_service_name')
	        #advert_service_list = AdvertRateCard.objects.filter(advert_rate_card_status='1').values('advert_service_name','advert_rate_card_id').distinct()
	        advert_service_list, item_ids = [], []
	        for item in AdvertRateCard.objects.filter(advert_rate_card_status='1'):
	            if item.advert_service_name not in item_ids:
	                advert_service_list.append(str(item.advert_rate_card_id))
	                item_ids.append(item.advert_service_name)

	        advert_service_list = AdvertRateCard.objects.filter(advert_rate_card_id__in=advert_service_list)        

		advert_length = len(advert_service_list)
		final_advert_list = []
		for advert in advert_service_list:
			#advert_rate_card_id = str(advert)
			#advert_service_name = advert.advert_service_name
	                advert_rate_card_id = str(advert.advert_rate_card_id)
	                advert_service_name = advert.advert_service_name
			try:
				premium_service_obj = PremiumService.objects.get(business_id=business_obj,premium_service_name=advert.advert_service_name)			
				advert_start_date = premium_service_obj.start_date
				advert_end_date = premium_service_obj.end_date
				advert_days = premium_service_obj.no_of_days
				status = 'true'
			
			except:
				advert_start_date = ''
				advert_end_date = ''
				advert_days = ''
				status = 'false'
			advert_list = {'advert_rate_card_id':advert_rate_card_id,'advert_service_name':advert_service_name,'advert_start_date':advert_start_date,'advert_end_date':advert_end_date,'advert_days':advert_days,'status':status}
			final_advert_list.append(advert_list)

		try:
			payement_obj = PaymentDetail.objects.get(business_id=business_obj)
			payment_mode = payement_obj.payment_mode
			note = payement_obj.note
			paid_amount = payement_obj.paid_amount
			payable_amount = payement_obj.payable_amount
			total_amount = payement_obj.total_amount
			tax_type = payement_obj.tax_type
		except Exception, e:
			print '=---------exception==============',e
			pass	

		data = {'username':request.session['login_user'],'duration_list':sorted(duration_list),'service_rate_card_list':service_rate_card_list,'advert_length':advert_length,'final_advert_list':final_advert_list,'service_list':service_list,'user_pincode':pincode,'category_list':category_list,'service_code':service_code,'file_name':file_name,'display_image':display_image,'tax_list':tax_list,'tax_type':tax_type,'payable_amount':payable_amount,'total_amount':total_amount,'paid_amount':paid_amount,'note':note,'payment_mode':payment_mode,'service_list':service_list,'end_date':end_date,'start_date':start_date,'duration':duration,'subscriber_category':category,'subscription':subscription,'pincode_list':pincode_list,'city_list':city_list,'state':state,'city':city,'state_list':state_list,'contact_email':contact_email,'contact_no':contact_no,'contact_person':contact_person,'business_details':business_details,'address2':address2,'address1':address1,'secondary_email':secondary_email,'supplier_email':supplier_email,'business_name':business_name,'phone_no':phone_no,'secondary_phone_no':secondary_phone_no}
		#print '================data=============',data
		return render(request,'Admin/edit-subscriber.html',data)   


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_subscriber_detail(request):
	if not request.user.is_authenticated():
		return redirect('backoffice')
	else:	
		state_list = State.objects.filter(state_status='1').order_by('state_name')
		category_list = Category.objects.filter(category_status='1').order_by('category_name')
		tax_list = Tax.objects.all()
		subscriber_obj = Supplier.objects.get(supplier_id=request.GET.get('user_id'))
		business_name = subscriber_obj.business_name
		phone_no = subscriber_obj.phone_no
		secondary_phone_no = subscriber_obj.secondary_phone_no
		supplier_email = subscriber_obj.supplier_email
		secondary_email = subscriber_obj.secondary_email
		try:
	 		display_image = SERVER_URL + subscriber_obj.logo.url
	 		file_name = str(subscriber_obj.logo)[19:]
	 	except:
	 		display_image = ''
	 		file_name = ''

		address1 = subscriber_obj.address1
		address2 = subscriber_obj.address2
		state = subscriber_obj.state
		city_list = City.objects.filter(state_id=state,city_status='1') 
		city = subscriber_obj.city
		pincode_list = Pincode.objects.filter(city_id=city,pincode_status='1')
		pincode = subscriber_obj.pincode
		business_details = subscriber_obj.business_details
		contact_person = subscriber_obj.contact_person
		contact_no = subscriber_obj.contact_no
		contact_email = subscriber_obj.contact_email
		data = {'username':request.session['login_user'],'user_pincode':pincode,'file_name':file_name,'display_image':display_image,'pincode_list':pincode_list,'city_list':city_list,'state':state,'city':city,'state_list':state_list,'contact_email':contact_email,'contact_no':contact_no,'contact_person':contact_person,'business_details':business_details,'address2':address2,'address1':address1,'secondary_email':secondary_email,'supplier_email':supplier_email,'business_name':business_name,'phone_no':phone_no,'secondary_phone_no':secondary_phone_no}
		return render(request,'Admin/edit-subscriber-detail.html',data)   

@csrf_exempt
def update_subscriber(request):
	try:
		supplier_obj = Supplier.objects.get(username=request.POST.get('user_email'))
		supplier_obj.business_name = request.POST.get('business_name')
		supplier_obj.phone_no = request.POST.get('phone_no')
		supplier_obj.secondary_phone_no = request.POST.get('sec_phone_no')
		supplier_obj.supplier_email = request.POST.get('email')
		supplier_obj.secondary_email = request.POST.get('sec_email')
		supplier_obj.address1 = request.POST.get('address1')
		supplier_obj.address2 = request.POST.get('address2')
		supplier_obj.city = City.objects.get(city_id=request.POST.get('city'))
		supplier_obj.state = State.objects.get(state_id=request.POST.get('state'))
		supplier_obj.pincode = Pincode.objects.get(pincode=request.POST.get('pincode'))
		supplier_obj.business_details = request.POST.get('business')
		supplier_obj.contact_person = request.POST.get('user_name')
		supplier_obj.contact_email = request.POST.get('user_email')
		supplier_obj.contact_no = request.POST.get('user_contact_no')
		supplier_obj.save()
		try:
			supplier_obj.logo = request.FILES['logo']
		except:
			pass
		supplier_obj.save()
		supplier_edit_mail(supplier_obj)

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
def check_advert(request):
	try:
		supplier_obj = Supplier.objects.get(supplier_id=request.POST.get('user_id'))
		service_obj = Business.objects.filter(supplier=supplier_obj)

		data={
			'success':'true',
		}
	except Exception, e:
		print e
		data={
			'success':'false',
		}
	return HttpResponse(json.dumps(data),content_type='application/json') 



@csrf_exempt
def update_subscriber_detail(request):
	try:
		supplier_obj = Supplier.objects.get(username = request.POST.get('user_email'))
		business_obj = Business.objects.get(supplier_id=supplier_obj)
		try:
			payment_obj = PaymentDetail.objects.get(business_id = business_obj)
			payment_obj.note = request.POST.get('note')
			payment_obj.payment_mode = request.POST.get('payment_mode')
			if(request.POST.get('paid_amount')!='None'):
				payment_obj.paid_amount = request.POST.get('paid_amount')
			else:
				payment_obj.paid_amount = ''
			payment_obj.payable_amount = request.POST.get('payable_amount')
			payment_obj.total_amount = request.POST.get('generated_amount')
			try:
				payment_obj.tax_type = Tax.objects.get(tax_type=request.POST.get('selected_tax_type'))
			except:
				pass
			payment_obj.save()
		except:
			chars= string.digits
			pwdSize = 8
			password = ''.join(random.choice(chars) for _ in range(pwdSize))
			business_obj =  Business.objects.get(supplier_id=str(supplier_obj.supplier_id))	

			payment_obj = PaymentDetail(
			business_id = business_obj,
			note = request.POST.get('note'),
			payment_mode = request.POST.get('payment_mode'),
			paid_amount = request.POST.get('paid_amount'),
			payable_amount = request.POST.get('payable_amount'),
			total_amount = request.POST.get('generated_amount'),
			tax_type = Tax.objects.get(tax_type=request.POST.get('selected_tax_type')),
			payment_code = "PMID" + str(password)
			)
			payment_obj.save()	
		data={
		'success':'true',
		'message':"Supplier added successfully",
 		'payment_code': str(payment_obj.payment_code),
 		'user_id':str(supplier_obj.supplier_id)
		}
		supplier_edit_payment_mail(payment_obj)
	except Exception, e:
		data={
				'success':'false',
				'message':str(e)
		}

	return HttpResponse(json.dumps(data),content_type='application/json')


# def check_subscription(premium_service_list,premium_day):	
# 	premium_service_list = premium_service_list
# 	premium_service_list = str(premium_service_list).split(',')

# 	premium_day = premium_day
# 	premium_day = str(premium_day).split(',')
# 	zipped_wk = zip(premium_service_list,premium_day)
	
# 	try:
# 		for serv,day in zipped_wk:
# 			service_rate_card_obj = AdvertRateCard.objects.get(advert_service_name=serv,duration=day)

# 		data={
# 				'success':'true',
# 		}
# 		return 'true'
# 	except Exception,e:
# 		print '========e-------------',e	
# 		data={
# 				'success':'false',
# 				'message':''
# 		}
# 		return 'false'   

def check_subscription(premium_service_list,premium_day):
	premium_service_list = premium_service_list
	premium_service_list = str(premium_service_list).split(',')

	premium_day = premium_day
	premium_day = str(premium_day).split(',')
	zipped_wk = zip(premium_service_list,premium_day)
	service_list= []
	duration_list= []

	false_status = 0	

	for serv,day in zipped_wk:
		try:
			service_rate_card_obj = AdvertRateCard.objects.get(advert_service_name=serv,duration=day)

		except Exception,e:
			service_list.append(str(serv))
			duration_list.append(day)
			false_status = 1
	if false_status == 0:
		data={
 				'success':'true',
 		}
 	else:
		zipped_list = zip(service_list,duration_list)
		message = "Package "
 		for i,j in zipped_list:
 			message = message + str(i) + " " + "("+str(j)+" Days)" + ", "  
		

		message = message[:-2] + ' not available'

		data={
 				'success':'false',
 				'message':message
 			}
	return data 		
			


def supplier_add_mail(supplier_obj):
	gmail_user =  "cityhoopla2016"
	gmail_pwd =  "cityhoopla@2016"
	FROM = 'CityHoopla Admin: <cityhoopla2016@gmail.com>'
	TO = ['cityhoopla2016@gmail.com']
	try:
		TEXT = "Hi Admin,\nSubscriber " + str(supplier_obj.contact_person) + " "+ "with Business " + str(supplier_obj.business_name)+ " " +"has been added successfully.\nTo view complete details visit portal and follow - Customers -> Subscribers"+'\n\n'+ "Thank You,"+'\n'+"CityHoopla Team"
		SUBJECT = "Subscriber Added Successfully!"
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

def supplier_add_service_mail(business_obj):
	gmail_user =  "cityhoopla2016"
	gmail_pwd =  "cityhoopla@2016"
	FROM = 'CityHoopla Admin: <cityhoopla2016@gmail.com>'
	TO = ['cityhoopla2016@gmail.com']
	#pdb.set_trace()
	try:
		TEXT = "Hi Admin,\nSubscriber " + str(business_obj.supplier.contact_person) + " "+ "with Business " + str(business_obj.supplier.business_name)+ " " +"has been added successfully.\nTransaction ID "+ str(business_obj.transaction_code) + " for this transaction has been generated successfully.\nTo view complete details visit portal and follow - Customers -> Subscribers"+'\n\n'+ "Thank You,"+'\n'+"CityHoopla Team"
		SUBJECT = "Subscriber Added Successfully!"
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


def supplier_add_payment_mail(payment_obj):
	gmail_user =  "cityhoopla2016"
	gmail_pwd =  "cityhoopla@2016"
	FROM = 'CityHoopla Admin: <cityhoopla2016@gmail.com>'
	TO = ['cityhoopla2016@gmail.com']
	business_obj = Business.objects.get(business_id=str(payment_obj.business_id.business_id))
	supplier_id = Supplier.objects.get(supplier_id=str(business_obj.supplier_id))
	#pdb.set_trace()
	try:
		TEXT = "Hi Admin,\nSubscriber " + str(supplier_id.contact_person) + " "+ "with Business " + str(supplier_id.business_name)+ " " +"has been added successfully.\nPayment ID"+ str(payment_obj.payment_code) + " for this payment has been generated successfully. \nTo view complete details visit portal and follow - Customers -> Subscribers" +'\n\n'+ "Thank You,"+'\n'+"CityHoopla Team"
		SUBJECT = "Subscriber Added Successfully!"
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

def supplier_edit_mail(supplier_obj):
	gmail_user =  "cityhoopla2016"
	gmail_pwd =  "cityhoopla@2016"
	FROM = 'CityHoopla Admin: <cityhoopla2016@gmail.com>'
	TO = ['cityhoopla2016@gmail.com']
	try:
		TEXT = "Hi Admin,\nSubscriber " + str(supplier_obj.contact_person) + " "+ "with Business " + str(supplier_obj.business_name)+ " " +"has been updated successfully.\nTo view complete details visit portal and follow - Customers -> Subscribers"+'\n\n'+ "Thank You,"+'\n'+"CityHoopla Team"
		SUBJECT = "Subscriber Updated Successfully!"
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

def supplier_edit_service_mail(business_obj):
	gmail_user =  "cityhoopla2016"
	gmail_pwd =  "cityhoopla@2016"
	FROM = 'CityHoopla Admin: <cityhoopla2016@gmail.com>'
	TO = ['cityhoopla2016@gmail.com']
	#pdb.set_trace()
	try:
		TEXT = "Hi Admin,\nSubscriber " + str(business_obj.supplier.contact_person) + " "+ "with Business " + str(business_obj.supplier.business_name)+ " " +"has been updated successfully. \nTransaction ID "+ str(business_obj.transaction_code) + " for this transaction has been generated successfully.\nTo view complete details visit portal and follow - Customers -> Subscribers"+'\n\n'+ "Thank You,"+'\n'+"CityHoopla Team"
		SUBJECT = "Subscriber Updated Successfully!"
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


def supplier_edit_payment_mail(payment_obj):
	gmail_user =  "cityhoopla2016"
	gmail_pwd =  "cityhoopla@2016"
	FROM = 'CityHoopla Admin: <cityhoopla2016@gmail.com>'
	TO = ['cityhoopla2016@gmail.com']
	business_obj = Business.objects.get(business_id=str(payment_obj.business_id.business_id))
	supplier_id = Supplier.objects.get(supplier_id=str(business_obj.supplier_id))
	#pdb.set_trace()
	try:
		TEXT = "Hi Admin,\nSubscriber " + str(supplier_id.contact_person) + " "+ "with Business " + str(supplier_id.business_name)+ " " +"has been updated successfully.\nPayment ID"+ str(payment_obj.payment_code) + " for this payment has been generated successfully.\nTo view complete details visit portal and follow - Customers -> Subscribers" +'\n\n'+"Thank You,"+'\n'+"CityHoopla Team"
		SUBJECT = "Subscriber Updated Successfully!"
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

def supplier_inactive_mail(user_obj):
	gmail_user =  "cityhoopla2016"
	gmail_pwd =  "cityhoopla@2016"
	FROM = 'CityHoopla Admin: <cityhoopla2016@gmail.com>'
	TO = ['cityhoopla2016@gmail.com']
	#pdb.set_trace()
	try:
		TEXT = "Hi Admin,\nSubscriber " + str(user_obj.contact_person) + " "+ "with Business " + str(user_obj.business_name)+ " " +"deactivated successfully.\n\nThank You,"+'\n'+"CityHoopla Team"
		SUBJECT = "Subscriber Deactivated Successfully!"
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
def active_subscriber(request):
        try:
            subscriber_obj = Supplier.objects.get(supplier_id=request.POST.get('subscriber_id'))
            subscriber_obj.supplier_status = '1'
            subscriber_obj.save()
            supplier_activate_mail(subscriber_obj)
            data = {'message': 'Subscriber activated Successfully', 'success':'true'}

        except IntegrityError as e:
          print e
        except Exception,e:
            print e
        return HttpResponse(json.dumps(data), content_type='application/json')
       
def supplier_activate_mail(user_obj):
	gmail_user =  "cityhoopla2016"
	gmail_pwd =  "cityhoopla@2016"
	FROM = 'CityHoopla Admin: <cityhoopla2016@gmail.com>'
	TO = ['cityhoopla2016@gmail.com']
	#pdb.set_trace()
	try:
		TEXT = "Hi Admin,\nSubscriber " + str(user_obj.contact_person) + " "+ "with Business " + str(user_obj.business_name)+ " " +"activated successfully.\n\nThank You,"+'\n'+"CityHoopla Team"
		SUBJECT = "Subscriber Activated Successfully!"
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
