from django.db import models
from django.contrib.auth.models import User
from django.template import RequestContext
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth import logout
from django.contrib.auth import login
#from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_control
from django.contrib import auth

#from constants import AppUserConstants, ExceptionLabel
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.template import RequestContext
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf

# importing mysqldb and system packages
import MySQLdb, sys
from django.db.models import Q
from django.db.models import F
from django.db import transaction

import csv
import json
#importing exceptions
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError

from datetime import datetime
import uuid
from django.db.models.signals import class_prepared
# Create your models here.
status = (
    ('1','1'),
    ('0','0'),   
)

USER_IMAGES_PATH ='images/user_images/' 
COMPANY_LOGO_PATH ='images/user_images/' 

class ConsumerProfile(User):
    consumer_id                        =       models.AutoField(primary_key=True, editable=False)
    consumer_full_name                 =       models.CharField(max_length=100,default=None,blank=True,null=True)
    consumer_contact_no                =       models.CharField(blank=True,null=True,max_length=200,default=None)
    consumer_email_id                  =       models.CharField(blank=True,null=True,max_length=100,default=None)
    consumer_status                    =       models.CharField(default="1",null=True,max_length=100, choices=status)
    consumer_created_date              =       models.DateTimeField(null=True,blank=True)
    consumer_created_by                =       models.CharField(max_length=100,null=True,blank=True)
    consumer_updated_by                =       models.CharField(max_length=100,null=True,blank= True)
    consumer_updated_date              =       models.DateTimeField(null=True,blank=True)
    sign_up_source                     =       models.CharField(max_length=20,null=True,blank= True) 
    consumer_profile_pic               =       models.ImageField("Image",upload_to=USER_IMAGES_PATH,max_length=500, default=None)
    device_token                       =       models.CharField(max_length=20,null=True,blank= True)  
    online                             =       models.CharField(default="1",null=True,max_length=100, choices=status) 
    last_time_login                    =       models.DateTimeField(default=datetime.now,null=True,blank=True)
        

    def __unicode__(self):
        return unicode(self.consumer_id)
    
class Consumer_Feedback(models.Model):
    feedback_id                        =  models.AutoField(primary_key=True, editable=False)
    consumer_id                        =  models.ForeignKey(ConsumerProfile,null=True,blank=True)
    consumer_feedback                  =  models.CharField(max_length=1000,null=True,blank=True)    
    
    def __unicode__(self):
        return unicode(self.feedback_id)  

class State(models.Model):
    state_id        =       models.AutoField(primary_key=True, editable=False)
    state_name      =       models.CharField(max_length=500,null=True,blank=True)
    creation_date   =       models.DateTimeField(null=True,blank=True)
    created_by      =       models.CharField(max_length=500,null=True,blank=True)
    updated_by      =       models.CharField(max_length=500,null=True,blank= True)
    updation_date   =       models.DateTimeField(null=True,blank=True)
    state_status    =       models.CharField(max_length=15,null=True,blank=True,default="1",choices=status)

    def __unicode__(self):
        return unicode(self.state_name)

class City(models.Model):
    city_id         =       models.AutoField(primary_key=True, editable=False)
    city_name       =       models.CharField(max_length=100,null=True,blank=True)
    state_id        =       models.ForeignKey(State,blank=True)
    creation_date   =       models.DateTimeField(null=True,blank=True)
    created_by      =       models.CharField(max_length=500,null=True,blank=True)
    updated_by      =       models.CharField(max_length=500,null=True,blank= True)
    updation_date   =       models.DateTimeField(null=True,blank=True)
    city_status     =       models.CharField(max_length=10,default="1",blank=True,null=True,choices=status)

    def __unicode__(self):
        return unicode(self.city_id)
    

class City_Place(models.Model):
    city_place_id         =       models.AutoField(primary_key=True, editable=False)
    city_name       =       models.CharField(max_length=100,null=True,blank=True)
    state_id        =       models.ForeignKey(State,blank=True)
    about_city      =       models.CharField(max_length=1000,null=True,blank=True)
    city_image      =       models.FileField(upload_to=USER_IMAGES_PATH, max_length=500, null=True, blank=True)
    climate         =       models.CharField(max_length=500,null=True,blank=True)
    language        =       models.CharField(max_length=100,null=True,blank=True)
    population      =       models.CharField(max_length=100,null=True,blank=True)
    time_zone       =       models.CharField(max_length=100,null=True,blank=True)
    creation_date   =       models.DateTimeField(null=True,blank=True)
    created_by      =       models.CharField(max_length=500,null=True,blank=True)
    updated_by      =       models.CharField(max_length=500,null=True,blank= True)
    updation_date   =       models.DateTimeField(null=True,blank=True)
    city_status     =       models.CharField(max_length=10,default="1",blank=True,null=True,choices=status)

    def __unicode__(self):
        return unicode(self.city_place_id)
    

class Places(models.Model):
    place_id                    =           models.AutoField(primary_key=True)
    place_name                  =           models.CharField(max_length=250,default=None,blank=True,null=True)
    place_image                 =           models.FileField(upload_to=USER_IMAGES_PATH, max_length=500, null=True, blank=True)
    city_place_id               =           models.ForeignKey(City_Place,blank=True,null=True)
    place_type                  =           models.CharField(max_length=30,default=None,blank=True,null=True)
    created_date                =           models.DateTimeField(default=datetime.now,null=True,blank=True)
    created_by                  =           models.CharField(max_length=30,default=None,blank=True,null=True)
    updated_date                =           models.DateTimeField(default=datetime.now,null=True,blank=True)
    updated_by                  =           models.CharField(max_length=30,default=None,blank=True,null=True)

    def __unicode__(self):
        return unicode(self.place_id)    


class Pincode(models.Model):
    pincode_id                 =            models.AutoField(primary_key=True)
    pincode                     =           models.CharField(max_length=250,default=None,blank=True,null=True)
    city_id                     =           models.ForeignKey(City,blank=True,null=True)
    created_date                =           models.DateTimeField(default=datetime.now,null=True,blank=True)
    created_by                  =           models.CharField(max_length=30,default=None,blank=True,null=True)
    updated_date                =           models.DateTimeField(default=datetime.now,null=True,blank=True)
    updated_by                  =           models.CharField(max_length=30,default=None,blank=True,null=True)
    pincode_status             =            models.CharField(max_length=10,default="1",choices=status,blank=True,null=True)

    def __unicode__(self):
        return unicode(self.pincode)

class UserRole(models.Model):
    role_id             	=       models.AutoField(primary_key=True, editable=False)
    role_name           	=       models.CharField(max_length=25)
    role_status           	=       models.CharField(max_length=15,null=True,blank=True,default="1",choices=status)
    role_created_date       =       models.DateTimeField(null=True,blank=True)
    role_created_by         =       models.CharField(max_length=30,null=True,blank=True)
    role_updated_by         =       models.CharField(max_length=30,null=True,blank= True)
    role_updated_date       =       models.DateTimeField(null=True,blank=True)
    def __unicode__(self):
        return unicode(self.role_name)

class UserProfile(User):
    user_id                        =       models.AutoField(primary_key=True, editable=False)
    user_name                      =       models.CharField(max_length=100,default=None,blank=True,null=True)
    user_contact_no                =       models.CharField(blank=True,null=True,max_length=200,default=None)
    usre_email_id                  =       models.CharField(blank=True,null=True,max_length=100,default=None)
    user_role                 	   =       models.ForeignKey(UserRole,blank=True,null=True)
    user_status                    =       models.CharField(default="1",null=True,max_length=100, choices=status);
    user_created_date              =       models.DateTimeField(null=True,blank=True)
    user_created_by                =       models.CharField(max_length=100,null=True,blank=True)
    user_updated_by                =       models.CharField(max_length=100,null=True,blank= True)
    user_updated_date              =       models.DateTimeField(null=True,blank=True)


    def __unicode__(self):
        return unicode(self.user_name)

class Category(models.Model):
    category_id                 =       models.AutoField(primary_key=True, editable=False)
    category_name               =       models.CharField(max_length=30)
    category_status             =       models.CharField(max_length=15,null=True,blank=True,default="1",choices=status)
    category_created_date       =       models.DateTimeField(null=True,blank=True)
    category_created_by         =       models.CharField(max_length=30,null=True,blank=True)
    category_updated_by         =       models.CharField(max_length=30,null=True,blank= True)
    category_updated_date       =       models.DateTimeField(null=True,blank=True)
    has_category                =       models.ForeignKey('self',null='True',blank='True')
    level                =       models.CharField(max_length=30,null=True,blank= True)
 
    def __unicode__(self):
        return unicode(self.category_id)        
    
class PhoneCategory(models.Model):
    phone_category_id                 =       models.AutoField(primary_key=True, editable=False)
    phone_category_name           	  =       models.CharField(max_length=15)
    phone_category_status             =       models.CharField(max_length=15,null=True,blank=True,default="1",choices=status)
    phone_category_created_date       =       models.DateTimeField(null=True,blank=True)
    phone_category_created_by         =       models.CharField(max_length=30,null=True,blank=True)
    phone_category_updated_by         =       models.CharField(max_length=30,null=True,blank= True)
    phone_category_updated_date       =       models.DateTimeField(null=True,blank=True)
    def __unicode__(self):
        return unicode(self.phone_category_name)
    

class Currency(models.Model):
    currency_id = models.AutoField(primary_key=True)
    currency = models.CharField(max_length=150, null=True)
    status = models.CharField(max_length=150, null=True, default=None, choices=status)
    Currency_created_by = models.CharField(max_length=150, null=True)
    Currency_created_date = models.DateTimeField(null=True)
    Currency_updated_by = models.CharField(max_length=150, null=True)
    Currency_updated_date = models.DateTimeField(null=True)

    def __unicode__(self):
        return unicode(self.currency)

class Supplier(User):
    supplier_id                        =       models.AutoField(primary_key=True, editable=False)
    business_name                =       models.CharField(max_length=100,default=None,blank=True,null=True)
    phone_no                =       models.CharField(blank=True,null=True,max_length=200,default=None)
    secondary_phone_no                  =       models.CharField(blank=True,null=True,max_length=100,default=None)
    supplier_email                  =       models.CharField(blank=True,null=True,max_length=100,default=None)
    secondary_email                  =       models.CharField(blank=True,null=True,max_length=100,default=None)
    logo                      =      models.ImageField(upload_to=COMPANY_LOGO_PATH,default=None,null=True,blank=True)
    address1                  =       models.CharField(blank=True,null=True,max_length=100,default=None)
    address2                  =       models.CharField(blank=True,null=True,max_length=100,default=None)
    city                      =       models.ForeignKey(City,blank=True,null=True)
    state                     =       models.ForeignKey(State,blank=True,null=True)
    pincode                     =       models.ForeignKey(Pincode,blank=True,null=True)
    business_details                  =       models.CharField(blank=True,null=True,max_length=10000,default=None)
    contact_person              = models.CharField(blank=True,null=True,max_length=100,default=None)
    contact_no                = models.CharField(blank=True,null=True,max_length=100,default=None)
    contact_email                = models.CharField(blank=True,null=True,max_length=100,default=None)
    supplier_status                    =       models.CharField(default="1",null=True,max_length=100, choices=status);
    supplier_created_date              =       models.DateTimeField(null=True,blank=True)
    supplier_created_by                =       models.CharField(max_length=100,null=True,blank=True)
    supplier_updated_by                =       models.CharField(max_length=100,null=True,blank= True)
    supplier_updated_date              =       models.DateTimeField(null=True,blank=True)

    def __unicode__(self):
        return unicode(self.contact_email)
    
    
class Advert(models.Model):
    advert_id                   = models.AutoField(primary_key=True, editable=False)
    supplier_id                 = models.ForeignKey(Supplier,blank=True,null=True)
    category_id                 = models.ForeignKey(Category,blank=True,null=True)
    status                      = models.CharField(max_length=150, null=True, default="1", choices=status)
    advert_name                 = models.CharField(max_length=50,blank=True,null=True)
    website                     = models.CharField(max_length=50,blank=True,null=True)
    latitude                    = models.CharField(max_length=50,blank=True,null=True)
    longitude                   = models.CharField(max_length=50,blank=True,null=True)
    short_description           = models.CharField(max_length=5000,blank=True,null=True)
    product_description         = models.CharField(max_length=5000,blank=True,null=True)
    discount_description        = models.CharField(max_length=5000,blank=True,null=True)
    currency_id                 = models.ForeignKey(Currency,blank=True,null=True)
    product_price               = models.CharField(max_length=50,blank=True,null=True)
    display_image               = models.FileField(upload_to=USER_IMAGES_PATH, max_length=500, null=True, blank=True)
    address_line_1              = models.CharField(max_length=50,blank=True,null=True)
    address_line_2              = models.CharField(max_length=50,blank=True,null=True)
    state_id                    = models.ForeignKey(State,blank=True,null=True)
    city_id                     = models.ForeignKey(City,blank=True,null=True)
    pincode_id                  = models.ForeignKey(Pincode,blank=True,null=True)
    area                        = models.CharField(max_length=50,blank=True,null=True) 
    landmark                    = models.CharField(max_length=50,blank=True,null=True)
    email_primary               = models.CharField(max_length=50,blank=True,null=True)
    email_secondary             = models.CharField(max_length=50,blank=True,null=True)
    property_market_rate        = models.CharField(max_length=50,blank=True,null=True)
    possesion_status            = models.CharField(max_length=50,blank=True,null=True)
    date_of_delivery             = models.CharField(max_length=50,blank=True,null=True)
    any_other_details             = models.CharField(max_length=5000,blank=True,null=True)    
    distance_frm_railway_station = models.CharField(max_length=50,blank=True,null=True)
    distance_frm_railway_airport = models.CharField(max_length=50,blank=True,null=True)    
    creation_date               = models.DateTimeField(null=True,blank=True)
    created_by                  = models.CharField(max_length=500,null=True,blank=True)
    updated_by                  = models.CharField(max_length=500,null=True,blank= True)
    updation_date               = models.DateTimeField(null=True,blank=True)
    
    def __unicode__(self):
        return unicode(self.advert_id)
    

class PhoneNo(models.Model):
    phone_no_id                 = models.AutoField(primary_key=True, editable=False)
    phone_category_id           = models.ForeignKey(PhoneCategory,blank=True,null=True)
    advert_id                   = models.ForeignKey(Advert,blank=True,null=True)
    phone_no                    = models.CharField(max_length=50,blank=True,null=True)   
    creation_date               = models.DateTimeField(null=True,blank=True)
    created_by                  = models.CharField(max_length=500,null=True,blank=True)
    updated_by                  = models.CharField(max_length=500,null=True,blank= True)
    updation_date               = models.DateTimeField(null=True,blank=True)
    
    def __unicode__(self):
        return unicode(self.phone_no)   
    
        
class AdvertImage(models.Model):
    advert_image_id             = models.AutoField(primary_key=True, editable=False)
    advert_id                   = models.ForeignKey(Advert,blank=True,null=True)
    advert_image                = models.FileField(upload_to=USER_IMAGES_PATH, max_length=500, null=True, blank=True)
    creation_date               = models.DateTimeField(null=True,blank=True)
    created_by                  = models.CharField(max_length=500,null=True,blank=True)
    updated_by                  = models.CharField(max_length=500,null=True,blank= True)
    updation_date               = models.DateTimeField(null=True,blank=True)
    
    def __unicode__(self):
        return unicode(self.advert_image_id)
    
class WorkingHours(models.Model):
    working_hr_id              = models.AutoField(primary_key=True, editable=False)
    advert_id                  = models.ForeignKey(Advert,blank=True,null=True)
    day                        = models.CharField(max_length=50,blank=True,null=True) 
    start_time                 = models.CharField(max_length=50,blank=True,null=True) 
    end_time                   = models.CharField(max_length=50,blank=True,null=True)
    creation_date               = models.DateTimeField(null=True,blank=True)
    created_by                  = models.CharField(max_length=500,null=True,blank=True)
    updated_by                  = models.CharField(max_length=500,null=True,blank= True)
    updation_date               = models.DateTimeField(null=True,blank=True)
    
    def __unicode__(self):
        return unicode(self.working_hr_id)
    
    
class Advert_Video(models.Model):
    advert_video_id             = models.AutoField(primary_key=True, editable=False)
    advert_id                   = models.ForeignKey(Advert,blank=True,related_name='advert_videos',null=True)
    advert_video_name           = models.FileField(upload_to=USER_IMAGES_PATH, max_length=500, null=True, blank=True)
    creation_date               = models.DateTimeField(null=True,blank=True)
    created_by                  = models.CharField(max_length=500,null=True,blank=True)
    updated_by                  = models.CharField(max_length=500,null=True,blank= True)
    updation_date               = models.DateTimeField(null=True,blank=True)
    
    def __unicode__(self):
        return unicode(self.advert_video_id)
    

class Amenities(models.Model):
    amenity_id                 = models.AutoField(primary_key=True, editable=False)
    advert_id                  = models.ForeignKey(Advert,blank=True,null=True)
    amenity                    = models.CharField(max_length=50,blank=True,null=True) 
    creation_date               = models.DateTimeField(null=True,blank=True)
    created_by                  = models.CharField(max_length=500,null=True,blank=True)
    updated_by                  = models.CharField(max_length=500,null=True,blank= True)
    updation_date               = models.DateTimeField(null=True,blank=True)
    
    def __unicode__(self):
        return unicode(self.amenity_id)

class AdditionalAmenities(models.Model):
    extra_amenity_id                 = models.AutoField(primary_key=True, editable=False)
    advert_id                  = models.ForeignKey(Advert,related_name='add_ame',blank=True,null=True)
    extra_amenity                    = models.CharField(max_length=50,blank=True,null=True) 
    creation_date               = models.DateTimeField(null=True,blank=True)
    created_by                  = models.CharField(max_length=500,null=True,blank=True)
    updated_by                  = models.CharField(max_length=500,null=True,blank= True)
    updation_date               = models.DateTimeField(null=True,blank=True)
    
    def __unicode__(self):
        return unicode(self.extra_amenity_id)
    
    
class NearByAttraction(models.Model):
    attraction_id                 = models.AutoField(primary_key=True, editable=False)
    advert_id                  = models.ForeignKey(Advert,blank=True,null=True)
    attraction                    = models.CharField(max_length=50,blank=True,null=True) 
    creation_date               = models.DateTimeField(null=True,blank=True)
    created_by                  = models.CharField(max_length=500,null=True,blank=True)
    updated_by                  = models.CharField(max_length=500,null=True,blank= True)
    updation_date               = models.DateTimeField(null=True,blank=True)
    
    def __unicode__(self):
        return unicode(self.attraction)
    

class NearestShopping(models.Model):
    shopping_id                 = models.AutoField(primary_key=True, editable=False)
    advert_id                   = models.ForeignKey(Advert,blank=True,null=True)
    shop_name                   = models.CharField(max_length=50,blank=True,null=True) 
    distance_frm_property       = models.CharField(max_length=50,blank=True,null=True) 
    creation_date               = models.DateTimeField(null=True,blank=True)
    created_by                  = models.CharField(max_length=500,null=True,blank=True)
    updated_by                  = models.CharField(max_length=500,null=True,blank= True)
    updation_date               = models.DateTimeField(null=True,blank=True)
    
    def __unicode__(self):
        return unicode(self.shop_name)
    
    
class NearestSchool(models.Model):
    school_id                 = models.AutoField(primary_key=True, editable=False)
    advert_id                   = models.ForeignKey(Advert,blank=True,null=True)
    school_name                 = models.CharField(max_length=50,blank=True,null=True) 
    distance_frm_property       = models.CharField(max_length=50,blank=True,null=True) 
    creation_date               = models.DateTimeField(null=True,blank=True)
    created_by                  = models.CharField(max_length=500,null=True,blank=True)
    updated_by                  = models.CharField(max_length=500,null=True,blank= True)
    updation_date               = models.DateTimeField(null=True,blank=True)
    
    def __unicode__(self):
        return unicode(self.school_name)
    

class NearestHospital(models.Model):
    hospital_id                 = models.AutoField(primary_key=True, editable=False)
    advert_id                   = models.ForeignKey(Advert,blank=True,null=True)
    hospital_name                   = models.CharField(max_length=50,blank=True,null=True) 
    distance_frm_property       = models.CharField(max_length=50,blank=True,null=True) 
    creation_date               = models.DateTimeField(null=True,blank=True)
    created_by                  = models.CharField(max_length=500,null=True,blank=True)
    updated_by                  = models.CharField(max_length=500,null=True,blank= True)
    updation_date               = models.DateTimeField(null=True,blank=True)
    
    def __unicode__(self):
        return unicode(self.hospital_name) 


class Advert_Category_Map(models.Model):
    adv_cat_id                  =       models.AutoField(primary_key=True, editable=False)
    advert_id                   =       models.ForeignKey(Advert,blank=True,null=True)  
    category_id                 =       models.ForeignKey(Category,blank=True,null=True)
    category_level              =       models.CharField(max_length=30,null=True,blank= True)

    def __unicode__(self):
        return unicode(self.adv_cat_id)    




class PremiumService(models.Model):
    premium_service_id                 =       models.AutoField(primary_key=True, editable=False)
    premium_service_name               =       models.CharField(max_length=30)
    no_of_days                         =        models.CharField(max_length=30)
    start_date = models.CharField(max_length=30,blank=True,null=True)
    end_date = models.CharField(max_length=30,blank=True,null=True)
    supplier                      =       models.ForeignKey(Supplier,blank=True,null=True)    
    premium_service_status             =       models.CharField(max_length=15,null=True,blank=True,default="1",choices=status)
    premium_service_created_date       =       models.DateTimeField(null=True,blank=True)
    premium_service_created_by         =       models.CharField(max_length=30,null=True,blank=True)
    premium_service_updated_by         =       models.CharField(max_length=30,null=True,blank= True)
    premium_service_updated_date       =       models.DateTimeField(null=True,blank=True)
    def __unicode__(self):
        return unicode(self.premium_service_id)


class ServiceRateCard(models.Model):
    service_rate_card_id                 =       models.AutoField(primary_key=True, editable=False)
    service_name               =       models.CharField(max_length=30)
    duration = models.CharField(max_length=30,blank=True,null=True)
    cost = models.CharField(max_length=30,blank=True,null=True)
    service_rate_card_status             =       models.CharField(max_length=15,null=True,blank=True,default="1",choices=status)
    service_rate_card_created_date       =       models.DateTimeField(null=True,blank=True)
    service_rate_card_created_by         =       models.CharField(max_length=30,null=True,blank=True)
    service_rate_card_updated_by         =       models.CharField(max_length=30,null=True,blank= True)
    service_rate_card_updated_date       =       models.DateTimeField(null=True,blank=True)
    def __unicode__(self):
        return unicode(self.service_rate_card_id)


class AdvertRateCard(models.Model):
    advert_rate_card_id                 =       models.AutoField(primary_key=True, editable=False)
    advert_service_name               =       models.CharField(max_length=30)
    duration = models.CharField(max_length=30,blank=True,null=True)
    cost = models.CharField(max_length=30,blank=True,null=True)
    advert_rate_card_status             =       models.CharField(max_length=15,null=True,blank=True,default="1",choices=status)
    advert_rate_card_created_date       =       models.DateTimeField(null=True,blank=True)
    advert_rate_card_created_by         =       models.CharField(max_length=30,null=True,blank=True)
    advert_rate_card_updated_by         =       models.CharField(max_length=30,null=True,blank= True)
    advert_rate_card_updated_date       =       models.DateTimeField(null=True,blank=True)
    def __unicode__(self):
        return unicode(self.advert_rate_card_id)


class Business(models.Model):
    business_id                 =       models.AutoField(primary_key=True, editable=False)
    supplier                      =       models.ForeignKey(Supplier,blank=True,null=True)
    category             =       models.ForeignKey(Category,blank=True,null=True)
    service_rate_card_id             =       models.ForeignKey(ServiceRateCard,blank=True,null=True)
    duration               =       models.CharField(max_length=30)
    transaction_code               =       models.CharField(max_length=30,blank=True,null=True)
    start_date = models.CharField(max_length=30,blank=True,null=True)
    end_date = models.CharField(max_length=30,blank=True,null=True)
    business_created_date       =       models.DateTimeField(null=True,blank=True)
    business_created_by         =       models.CharField(max_length=30,null=True,blank=True)
    business_updated_by         =       models.CharField(max_length=30,null=True,blank= True)
    business_updated_date       =       models.DateTimeField(null=True,blank=True)
    is_active       =      models.CharField(max_length=2,null=True,blank=True)
    def __unicode__(self):
        return unicode(self.business_id)




class Tax(models.Model):
    tax_id=models.AutoField(primary_key=True)
    tax_type=models.CharField(max_length=50,default=None,null=True,blank=True)
    tax_rate=models.IntegerField(max_length=5,null=True,blank=True)
    def __unicode__(self):
        return unicode(self.tax_id)


class PaymentDetail(models.Model):
    payment_id                 =       models.AutoField(primary_key=True, editable=False)
    payment_code               =       models.CharField(max_length=30)
    payment_mode               =        models.CharField(max_length=30)
    paid_amount         =       models.CharField(max_length=30,null=True,blank=True)
    payable_amount         =       models.CharField(max_length=30,null=True,blank=True)
    total_amount         =       models.CharField(max_length=30,null=True,blank=True)
    tax_type             =       models.ForeignKey(Tax,null=True,blank=True)    
    payment_created_date       =       models.DateTimeField(null=True,blank=True)
    payment_created_by         =       models.CharField(max_length=30,null=True,blank=True)
    payment_updated_by         =       models.CharField(max_length=30,null=True,blank= True)
    payment_updated_date       =       models.DateTimeField(null=True,blank=True)
    note = models.CharField(max_length=30,null=True,blank=True)
    supplier                      =       models.ForeignKey(Supplier,blank=True,null=True)
    def __unicode__(self):
        return unicode(self.payment_id)


class CategoryCityMap(models.Model):
    map_id                 = models.AutoField(primary_key=True, editable=False)
    city_place_id                  = models.ForeignKey(City_Place,blank=True,null=True)
    category_id                    = models.ForeignKey(Category,blank=True,null=True) 
    sequence                = models.CharField(max_length=500,null=True,blank=True)
    creation_date               = models.DateTimeField(null=True,blank=True)
    created_by                  = models.CharField(max_length=500,null=True,blank=True)
    updated_by                  = models.CharField(max_length=500,null=True,blank= True)
    updation_date               = models.DateTimeField(null=True,blank=True)
    
    def __unicode__(self):
        return unicode(self.map_id)
    
    
class AdvertLike(models.Model):
    id                 = models.AutoField(primary_key=True, editable=False)
    user_id                  = models.ForeignKey(ConsumerProfile,blank=True,null=True)
    advert_id                    = models.ForeignKey(Advert,blank=True,null=True) 
    creation_date               = models.DateTimeField(null=True,blank=True)
    
    def __unicode__(self):
        return unicode(self.id)   


class AdvertSubscriptionMap(models.Model):
    id                 = models.AutoField(primary_key=True, editable=False)
    business_id                  = models.ForeignKey(Business,blank=True,null=True)
    advert_id                    = models.ForeignKey(Advert,blank=True,null=True) 
    
    def __unicode__(self):
        return unicode(self.id)     
