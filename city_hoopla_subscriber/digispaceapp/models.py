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
import django
# Create your models here.
status = (
    ('1','1'),
    ('0','0'),   
)

preference_status = (
    ('true','true'),
    ('false','false'),
)

flag = (
    ('true','true'),
    ('false','false'),
)

like_dislike = (
    ('like', 'like'),
    ('dislike', 'dislike'),
)

post_status = (
    ('unread', 'unread'),
    ('appropriate', 'appropriate'),
    ('inappropriate', 'inappropriate'),
    ('deleted','deleted'),
)

post_mood = (
    ('positive', 'positive'),
    ('negative', 'negative'),
)

app_user = (
    ('register', 'register'),
    ('guest', 'guest'),
)

city_star_status = (
    ('current', 'current'),
    ('default', 'default'),
    ('expired', 'expired'),
    ('active', 'active'),
    ('deactivated', 'deactivated'),
)


comment_status = (
    ('read','read'),
    ('unread','unread'),   
)


USER_IMAGES_PATH ='images/user_images/' 
COMPANY_LOGO_PATH ='images/user_images/' 
CATEGORY_PATH ='images/user_images/'
STAR_IMAGES_PATH ='images/user_images/'
ADVERT_IMAGES_PATH ='images/advert_images/'
CITYLIFE_FILE_PATH = 'images/citylife_files/'

class Operator(User):
    operator_id                        =       models.AutoField(primary_key=True, editable=False)
    operator_name                      =       models.CharField(max_length=100,default=None,blank=True,null=True)
    operator_email_id                  =       models.CharField(blank=True,null=True,max_length=100,default=None)
    operator_status                    =       models.CharField(default="1",null=True,max_length=100, choices=status);
    user_created_date              =       models.DateTimeField(null=True,blank=True)
    user_created_by                =       models.CharField(max_length=100,null=True,blank=True)
    user_updated_by                =       models.CharField(max_length=100,null=True,blank= True)
    user_updated_date              =       models.DateTimeField(null=True,blank=True)

    def __unicode__(self):
        return unicode(self.operator_id)

class Country(models.Model):
    country_id      =       models.AutoField(primary_key=True, editable=False)
    country_name    =       models.CharField(max_length=500,null=True,blank=True)
    creation_date   =       models.DateTimeField(default=datetime.now,null=True,blank=True)
    created_by      =       models.CharField(max_length=500,null=True,blank=True)
    updated_by      =       models.CharField(max_length=500,null=True,blank= True)
    updation_date   =       models.DateTimeField(default=datetime.now,null=True,blank=True)
    country_status    =       models.CharField(max_length=15,null=True,blank=True,default="1",choices=status)

    def __unicode__(self):
        return unicode(self.country_name) 

class Currency(models.Model):
    currency_id = models.AutoField(primary_key=True)
    currency = models.CharField(max_length=150, null=True)
    country_id =models.ForeignKey(Country,blank=True)
    status = models.CharField(max_length=150, null=True, default="1", choices=status)
    created_by = models.CharField(max_length=150,blank= True, null=True)
    created_date = models.DateTimeField(null=True,blank= True)
    updated_by = models.CharField(max_length=150,blank= True, null=True)
    updated_date = models.DateTimeField(null=True,blank= True)

    def __unicode__(self):
        return unicode(self.currency)


class State(models.Model):
    state_id        =       models.AutoField(primary_key=True, editable=False)
    state_name      =       models.CharField(max_length=500,null=True,blank=True)
    country_id        =       models.ForeignKey(Country,blank=True)
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
        return unicode(self.city_name)
    

class City_Place(models.Model):
    city_place_id   =       models.AutoField(primary_key=True, editable=False)
    city_id         =       models.ForeignKey(City,blank=True)
    country_id      =       models.ForeignKey(Country,blank=True,null=True)
    state_id        =       models.ForeignKey(State,blank=True)
    currency        =       models.CharField(max_length=500,null=True,blank=True)
    about_city      =       models.CharField(max_length=50000,null=True,blank=True)
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

class ConsumerProfile(User):
    consumer_id                        =       models.AutoField(primary_key=True, editable=False)
    city_place_id                      =       models.ForeignKey(City_Place,blank=True,null=True)
    consumer_full_name                 =       models.CharField(max_length=100,default=None,blank=True,null=True)
    consumer_contact_no                =       models.CharField(blank=True,null=True,max_length=200,default=None)
    consumer_email_id                  =       models.CharField(blank=True,null=True,max_length=100,default=None)
    consumer_status                    =       models.CharField(default="1",null=True,max_length=100, choices=status)
    consumer_created_date              =       models.DateTimeField(null=True,blank=True)
    consumer_created_by                =       models.CharField(max_length=100,null=True,blank=True)
    consumer_updated_by                =       models.CharField(max_length=100,null=True,blank= True)
    consumer_otp                       =       models.CharField(max_length=100,null=True,blank= True)
    consumer_updated_date              =       models.DateTimeField(null=True,blank=True)
    sign_up_source                     =       models.CharField(max_length=20,null=True,blank= True) 
    consumer_profile_pic               =       models.ImageField("Image",upload_to=USER_IMAGES_PATH,max_length=500, default=None)
    device_token                       =       models.CharField(max_length=20,null=True,blank= True)  
    online                             =       models.CharField(default="1",null=True,max_length=100, choices=status) 
    last_time_login                    =       models.DateTimeField(default=datetime.now,null=True,blank=True)
    latitude                           =       models.FloatField(blank=True, null=True, max_length=20, default=None)
    longitude                          =       models.FloatField(blank=True, null=True, max_length=20, default=None)
    consumer_area                      =       models.CharField(max_length=100, default=None, blank=True, null=True)
    user_verified                      =       models.CharField(default="false", null=True, max_length=100, choices=flag)
    notification_status                =       models.CharField(default="true", null=True, max_length=100, choices=flag)
    push_review_status                 =       models.CharField(default="true", null=True, max_length=100, choices=flag)
    push_post_status                   =       models.CharField(default="true", null=True, max_length=100, choices=flag)
    push_social_status                 =       models.CharField(default="true", null=True, max_length=100, choices=flag)
    email_review_status                =       models.CharField(default="true", null=True, max_length=100, choices=flag)
    newsletter_status                  =       models.CharField(default="true", null=True, max_length=100, choices=flag)
    email_social_status                =       models.CharField(default="true", null=True, max_length=100, choices=flag)
    no_of_login                        =       models.CharField(max_length=100, default=None, blank=True, null=True)
    consumer_type                      =       models.CharField(default="register", null=True, max_length=100, choices=app_user)
        

    def __unicode__(self):
        return unicode(self.consumer_id)
    
class Consumer_Feedback(models.Model):
    feedback_id                        =  models.AutoField(primary_key=True, editable=False)
    consumer_id                        =  models.ForeignKey(ConsumerProfile,null=True,blank=True)
    consumer_feedback                  =  models.CharField(max_length=1000,null=True,blank=True)    
    
    def __unicode__(self):
        return unicode(self.feedback_id) 


class Places(models.Model):
    place_id                    =           models.AutoField(primary_key=True)
    place_name                  =           models.CharField(max_length=50000,default=None,blank=True,null=True)
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
    role_id                 =       models.AutoField(primary_key=True, editable=False)
    role_name               =       models.CharField(max_length=25)
    role_status             =       models.CharField(max_length=15,null=True,blank=True,default="1",choices=status)
    role_created_date       =       models.DateTimeField(null=True,blank=True)
    role_created_by         =       models.CharField(max_length=30,null=True,blank=True)
    role_updated_by         =       models.CharField(max_length=30,null=True,blank= True)
    role_updated_date       =       models.DateTimeField(null=True,blank=True)
    def __unicode__(self):
        return unicode(self.role_id)

class Privileges(models.Model):
    privilege_id            =       models.AutoField(primary_key=True, editable=False)
    role_id                 =       models.ForeignKey(UserRole,related_name='userroleid',blank=True,null=True)
    privilage               =       models.CharField(blank=True,null=True,max_length=100,default=None)
    created_date            =           models.DateTimeField(default=datetime.now,null=True,blank=True)
    created_by              =           models.CharField(max_length=30,default=None,blank=True,null=True)
    updated_date            =           models.DateTimeField(default=datetime.now,null=True,blank=True)
    updated_by              =           models.CharField(max_length=30,default=None,blank=True,null=True)

    def __unicode__(self):
        return unicode(self.privilege_id)

class UserProfile(User):
    user_id                        =       models.AutoField(primary_key=True, editable=False, blank=True)
    user_first_name                =       models.CharField(max_length=100,default=None,blank=True,null=True)
    user_last_name                 =       models.CharField(max_length=100,default=None,blank=True,null=True)
    user_contact_no                =       models.CharField(blank=True,null=True,max_length=200,default=None)
    usre_email_id                  =       models.CharField(blank=True,null=True,max_length=100,default=None)
    user_role                      =       models.ForeignKey(UserRole,blank=True,null=True)
    user_status                    =       models.CharField(default="1",null=True,max_length=100, choices=status);
    user_created_date              =       models.DateTimeField(null=True,blank=True)
    user_created_by                =       models.CharField(max_length=100,null=True,blank=True)
    user_updated_by                =       models.CharField(max_length=100,null=True,blank= True)
    user_updated_date              =       models.DateTimeField(null=True,blank=True)
    city_place_id                  =       models.ForeignKey(City_Place, blank=True, null=True)


    def __unicode__(self):
        return unicode(self.usre_email_id)

class Category(models.Model):
    category_id                 =       models.AutoField(primary_key=True, editable=False)
    category_name               =       models.CharField(max_length=30)
    category_color              =       models.CharField(max_length=30,null=True,blank=True)
    category_image              =       models.ImageField(upload_to=CATEGORY_PATH, default=None, null=True, blank=True)
    category_status             =       models.CharField(max_length=15,null=True,blank=True,default="1",choices=status)
    category_created_date       =       models.DateTimeField(null=True,blank=True)
    category_created_by         =       models.CharField(max_length=30,null=True,blank=True)
    category_updated_by         =       models.CharField(max_length=30,null=True,blank= True)
    category_updated_date       =       models.DateTimeField(null=True,blank=True)
 
    def __unicode__(self):
        return unicode(self.category_id)


class CategoryLevel1(models.Model):
    category_id = models.AutoField(primary_key=True, editable=False)
    parent_category_id = models.ForeignKey(Category, blank=True, null=True)
    category_name = models.CharField(max_length=30)
    category_status = models.CharField(max_length=15, null=True, blank=True, default="1", choices=status)
    category_created_date = models.DateTimeField(null=True, blank=True)
    category_created_by = models.CharField(max_length=30, null=True, blank=True)
    category_updated_by = models.CharField(max_length=30, null=True, blank=True)
    category_updated_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.category_id)



class CategoryLevel2(models.Model):
    category_id = models.AutoField(primary_key=True, editable=False)
    parent_category_id = models.ForeignKey(CategoryLevel1, blank=True, null=True)
    category_name = models.CharField(max_length=30)
    category_status = models.CharField(max_length=15, null=True, blank=True, default="1", choices=status)
    category_created_date = models.DateTimeField(null=True, blank=True)
    category_created_by = models.CharField(max_length=30, null=True, blank=True)
    category_updated_by = models.CharField(max_length=30, null=True, blank=True)
    category_updated_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.category_id)


class CategoryLevel3(models.Model):
    category_id = models.AutoField(primary_key=True, editable=False)
    parent_category_id = models.ForeignKey(CategoryLevel2, blank=True, null=True)
    category_name = models.CharField(max_length=30)
    category_status = models.CharField(max_length=15, null=True, blank=True, default="1", choices=status)
    category_created_date = models.DateTimeField(null=True, blank=True)
    category_created_by = models.CharField(max_length=30, null=True, blank=True)
    category_updated_by = models.CharField(max_length=30, null=True, blank=True)
    category_updated_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.category_id)

class CategoryLevel4(models.Model):
    category_id = models.AutoField(primary_key=True, editable=False)
    parent_category_id = models.ForeignKey(CategoryLevel3, blank=True, null=True)
    category_name = models.CharField(max_length=30)
    category_status = models.CharField(max_length=15, null=True, blank=True, default="1", choices=status)
    category_created_date = models.DateTimeField(null=True, blank=True)
    category_created_by = models.CharField(max_length=30, null=True, blank=True)
    category_updated_by = models.CharField(max_length=30, null=True, blank=True)
    category_updated_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.category_id)

class CategoryLevel5(models.Model):
    category_id = models.AutoField(primary_key=True, editable=False)
    parent_category_id = models.ForeignKey(CategoryLevel4, blank=True, null=True)
    category_name = models.CharField(max_length=30)
    category_status = models.CharField(max_length=15, null=True, blank=True, default="1", choices=status)
    category_created_date = models.DateTimeField(null=True, blank=True)
    category_created_by = models.CharField(max_length=30, null=True, blank=True)
    category_updated_by = models.CharField(max_length=30, null=True, blank=True)
    category_updated_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.category_id) 
    
class PhoneCategory(models.Model):
    phone_category_id                 =       models.AutoField(primary_key=True, editable=False)
    phone_category_name               =       models.CharField(max_length=15)
    phone_category_status             =       models.CharField(max_length=15,null=True,blank=True,default="1",choices=status)
    phone_category_created_date       =       models.DateTimeField(null=True,blank=True)
    phone_category_created_by         =       models.CharField(max_length=30,null=True,blank=True)
    phone_category_updated_by         =       models.CharField(max_length=30,null=True,blank= True)
    phone_category_updated_date       =       models.DateTimeField(null=True,blank=True)
    def __unicode__(self):
        return unicode(self.phone_category_name)
    

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
    country_id =models.ForeignKey(Country,blank=True,null=True)
    city_place_id                     = models.ForeignKey(City_Place,blank=True,null=True)
    area                  =       models.CharField(blank=True,null=True,max_length=100,default=None)
    # city                      =       models.ForeignKey(City,blank=True,null=True)
    state                     =       models.ForeignKey(State,blank=True,null=True)
    pincode                     =       models.ForeignKey(Pincode,blank=True,null=True)
    business_details                  =       models.CharField(blank=True,null=True,max_length=10000,default=None)
    contact_person              = models.CharField(blank=True,null=True,max_length=100,default=None)
    contact_no                = models.CharField(blank=True,null=True,max_length=100,default=None)
    contact_email                = models.CharField(blank=True,null=True,max_length=100,default=None)
    supplier_status                    =       models.CharField(default="1",null=True,max_length=100, choices=status);
    supplier_created_date              =       models.DateTimeField(null=True,blank=True,default=django.utils.timezone.now)
    supplier_created_by                =       models.CharField(max_length=100,null=True,blank=True)
    supplier_updated_by                =       models.CharField(max_length=100,null=True,blank= True)
    supplier_updated_date              =       models.DateTimeField(null=True,blank=True)
    notification_status = models.CharField(default="true", null=True, max_length=100, choices=preference_status)
    reminders_status = models.CharField(default="true", null=True, max_length=100, choices=preference_status)
    discounts_status = models.CharField(default="true", null=True, max_length=100, choices=preference_status)
    request_call_back_status = models.CharField(default="true", null=True, max_length=100, choices=preference_status)
    no_call_status = models.CharField(default="true", null=True, max_length=100, choices=preference_status)
    sales_person_name                  =       models.ForeignKey(UserProfile,blank=True,null=True)
    sales_person_contact_number        =       models.CharField(blank=True,null=True,max_length=100,default=None)
    sales_person_email                 =       models.CharField(blank=True,null=True,max_length=100,default=None)
    title                               =       models.CharField(blank=True,null=True,max_length=50,default=None)
    parent_supplier_id = models.ForeignKey('self', blank=True, null=True)


    def __unicode__(self):
        return unicode(self.supplier_id)
    
    
class Advert(models.Model):
    advert_id                   = models.AutoField(primary_key=True, editable=False)
    supplier_id                 = models.ForeignKey(Supplier,blank=True,null=True)
    category_id = models.ForeignKey(Category, blank=True, null=True)
    category_level_1 = models.ForeignKey(CategoryLevel1, blank=True, null=True)
    category_level_2 = models.ForeignKey(CategoryLevel2, blank=True, null=True)
    category_level_3 = models.ForeignKey(CategoryLevel3, blank=True, null=True)
    category_level_4 = models.ForeignKey(CategoryLevel4, blank=True, null=True)
    category_level_5 = models.ForeignKey(CategoryLevel5, blank=True, null=True)
    status                      = models.CharField(max_length=150, null=True, default="1", choices=status)
    advert_name                 = models.CharField(max_length=50,blank=True,null=True)
    contact_name                = models.CharField(max_length=50,blank=True,null=True)
    contact_no                  = models.CharField(max_length=50,blank=True,null=True)
    website                     = models.CharField(max_length=50,blank=True,null=True)
    latitude                    = models.CharField(max_length=50,blank=True,null=True)
    longitude                   = models.CharField(max_length=50,blank=True,null=True)
    short_description           = models.CharField(max_length=5000,blank=True,null=True)
    product_description         = models.CharField(max_length=5000,blank=True,null=True)
    discount_description        = models.CharField(max_length=5000,blank=True,null=True)
    country_id =models.ForeignKey(Country,blank=True,null=True)
    currency                    = models.CharField(max_length=50,blank=True,null=True)
    # product_price               = models.CharField(max_length=50,blank=True,null=True)
    display_image               = models.FileField(upload_to=USER_IMAGES_PATH, max_length=500, null=True, blank=True)
    advert_image               = models.FileField(upload_to=ADVERT_IMAGES_PATH, max_length=500, null=True, blank=True)
    advert_slider_image         = models.FileField(upload_to=ADVERT_IMAGES_PATH, max_length=500, null=True, blank=True)
    address_line_1              = models.CharField(max_length=50,blank=True,null=True)
    address_line_2              = models.CharField(max_length=50,blank=True,null=True)
    state_id                    = models.ForeignKey(State,blank=True,null=True)
    city_place_id                     = models.ForeignKey(City_Place,blank=True,null=True)
    pincode_id                  = models.ForeignKey(Pincode,blank=True,null=True)
    area                        = models.CharField(max_length=50,blank=True,null=True) 
    landmark                    = models.CharField(max_length=50,blank=True,null=True)
    email_primary               = models.CharField(max_length=50,blank=True,null=True)
    email_secondary             = models.CharField(max_length=50,blank=True,null=True)
    property_market_rate        = models.CharField(max_length=50,blank=True,null=True)
    possesion_status            = models.CharField(max_length=50,blank=True,null=True)
    other_projects              = models.CharField(max_length=5000,blank=True,null=True)
    date_of_delivery             = models.CharField(max_length=50,blank=True,null=True)
    any_other_details             = models.CharField(max_length=5000,blank=True,null=True)  
    speciality                  = models.CharField(max_length=5000,blank=True,null=True)
    happy_hour_offer            = models.CharField(max_length=5000,blank=True,null=True)
    course_duration                  = models.CharField(max_length=5000,blank=True,null=True)
    affilated_to                  = models.CharField(max_length=5000,blank=True,null=True)
    facility                  = models.CharField(max_length=5000,blank=True,null=True) 
    image_video_space_used      = models.CharField(max_length=200,blank=True,null=True)  
    distance_frm_railway_station = models.CharField(max_length=50,blank=True,null=True)
    distance_frm_railway_airport = models.CharField(max_length=50,blank=True,null=True)    
    creation_date               = models.DateTimeField(null=True,blank=True,default=django.utils.timezone.now)
    created_by                  = models.CharField(max_length=500,null=True,blank=True)
    updated_by                  = models.CharField(max_length=500,null=True,blank= True)
    updation_date               = models.DateTimeField(null=True,blank=True)
    advert_views                = models.CharField(max_length=10,null=True,blank=True)
    keywords                    = models.CharField(max_length=1000, blank=True, null=True)
    other_amenity                    = models.CharField(max_length=500,blank=True,null=True)
    title                       =       models.CharField(blank=True,null=True,max_length=50,default=None)
    discount_start_date         =  models.CharField(blank=True,null=True,max_length=50,default=None)
    discount_end_date         =  models.CharField(blank=True,null=True,max_length=50,default=None)
    
    def __unicode__(self):
        return unicode(self.advert_id)

class Product(models.Model):
    product_id                  = models.AutoField(primary_key=True, editable=False)
    advert_id                   = models.ForeignKey(Advert,blank=True,null=True)
    product_name                = models.CharField(max_length=50,blank=True,null=True)   
    product_price               = models.CharField(max_length=50,blank=True,null=True)
    creation_date               = models.DateTimeField(null=True,blank=True)
    created_by                  = models.CharField(max_length=500,null=True,blank=True)
    updated_by                  = models.CharField(max_length=500,null=True,blank= True)
    updation_date               = models.DateTimeField(null=True,blank=True)
    
    def __unicode__(self):
        return unicode(self.product_id)
    

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
    



# class AdditionalAmenities(models.Model):
#     extra_amenity_id                 = models.AutoField(primary_key=True, editable=False)
#     advert_id                  = models.ForeignKey(Advert,related_name='add_ame',blank=True,null=True)
#     extra_amenity                    = models.CharField(max_length=50,blank=True,null=True) 
#     creation_date               = models.DateTimeField(null=True,blank=True)
#     created_by                  = models.CharField(max_length=500,null=True,blank=True)
#     updated_by                  = models.CharField(max_length=500,null=True,blank= True)
#     updation_date               = models.DateTimeField(null=True,blank=True)
    
#     def __unicode__(self):
#         return unicode(self.extra_amenity_id)
    
    
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

class RateCard(models.Model):
    rate_card_id = models.AutoField(primary_key=True, editable=False)
    city_place_id = models.ForeignKey(City_Place, blank=True, null=True)
    service_name = models.CharField(max_length=30)
    cost_for_3_days = models.CharField(max_length=30, blank=True, null=True)
    cost_for_7_days = models.CharField(max_length=30, blank=True, null=True)
    cost_for_30_days = models.CharField(max_length=30, blank=True, null=True)
    cost_for_90_days = models.CharField(max_length=30, blank=True, null=True)
    cost_for_180_days = models.CharField(max_length=30, blank=True, null=True)
    rate_card_status = models.CharField(max_length=15, null=True, blank=True, default="1", choices=status)
    rate_card_created_date = models.DateTimeField(null=True, blank=True)
    rate_card_created_by = models.CharField(max_length=30, null=True, blank=True)
    rate_card_updated_by = models.CharField(max_length=30, null=True, blank=True)
    rate_card_updated_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.rate_card_id)

class CategoryWiseRateCard(models.Model):
    rate_card_id = models.AutoField(primary_key=True, editable=False)
    city_place_id = models.ForeignKey(City_Place, blank=True, null=True)
    service_name = models.CharField(max_length=30)
    category_id = models.CharField(max_length=30)
    category_level = models.CharField(max_length=30)
    cost_for_3_days = models.CharField(max_length=30, blank=True, null=True)
    cost_for_7_days = models.CharField(max_length=30, blank=True, null=True)
    cost_for_30_days = models.CharField(max_length=30, blank=True, null=True)
    cost_for_90_days = models.CharField(max_length=30, blank=True, null=True)
    cost_for_180_days = models.CharField(max_length=30, blank=True, null=True)
    rate_card_status = models.CharField(max_length=15, null=True, blank=True, default="1", choices=status)
    rate_card_created_date = models.DateTimeField(null=True, blank=True)
    rate_card_created_by = models.CharField(max_length=30, null=True, blank=True)
    rate_card_updated_by = models.CharField(max_length=30, null=True, blank=True)
    rate_card_updated_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.rate_card_id)

class TelephoneEnquiryRateCard(models.Model):
    rate_card_id = models.AutoField(primary_key=True, editable=False)
    city_place_id = models.ForeignKey(City_Place, blank=True, null=True)
    service_name = models.CharField(max_length=30)
    cost_for_3_days = models.CharField(max_length=30, blank=True, null=True)
    cost_for_7_days = models.CharField(max_length=30, blank=True, null=True)
    cost_for_30_days = models.CharField(max_length=30, blank=True, null=True)
    cost_for_90_days = models.CharField(max_length=30, blank=True, null=True)
    cost_for_180_days = models.CharField(max_length=30, blank=True, null=True)
    rate_card_status = models.CharField(max_length=15, null=True, blank=True, default="1", choices=status)
    rate_card_created_date = models.DateTimeField(null=True, blank=True)
    rate_card_created_by = models.CharField(max_length=30, null=True, blank=True)
    rate_card_updated_by = models.CharField(max_length=30, null=True, blank=True)
    rate_card_updated_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.rate_card_id) 

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
    business_id = models.AutoField(primary_key=True, editable=False)
    city_place_id = models.ForeignKey(City_Place,blank=True,null=True)
    supplier = models.ForeignKey(Supplier, blank=True, null=True)
    category = models.ForeignKey(Category, blank=True, null=True)
    category_level_1 = models.ForeignKey(CategoryLevel1, blank=True, null=True)
    category_level_2 = models.ForeignKey(CategoryLevel2, blank=True, null=True)
    category_level_3 = models.ForeignKey(CategoryLevel3, blank=True, null=True)
    category_level_4 = models.ForeignKey(CategoryLevel4, blank=True, null=True)
    category_level_5 = models.ForeignKey(CategoryLevel5, blank=True, null=True)
    service_rate_card_id = models.ForeignKey(ServiceRateCard, blank=True, null=True)
    duration = models.CharField(max_length=30)
    transaction_code = models.CharField(max_length=30, blank=True, null=True)
    start_date = models.CharField(max_length=30, blank=True, null=True)
    end_date = models.CharField(max_length=30, blank=True, null=True)
    business_created_date = models.DateTimeField(default=datetime.now, null=True, blank=True)
    business_created_by = models.CharField(max_length=30, null=True, blank=True)
    business_updated_by = models.CharField(max_length=30, null=True, blank=True)
    business_updated_date = models.DateTimeField(default=datetime.now, null=True, blank=True)
    is_active = models.CharField(max_length=2, default='1', null=True, blank=True)
    country_id =models.ForeignKey(Country,blank=True,null=True)
    state_id                    = models.ForeignKey(State,blank=True,null=True)

    def __unicode__(self):
        return unicode(self.business_id)

class CategorywiseAmenity(models.Model):
    categorywise_amenity_id = models.AutoField(primary_key=True, editable=False)
    amenity    = models.CharField(max_length=50, blank=True, null=True)
    category = models.ForeignKey(Category, blank=True, null=True)
    category_level_1 = models.ForeignKey(CategoryLevel1, blank=True, null=True)
    category_level_2 = models.ForeignKey(CategoryLevel2, blank=True, null=True)
    category_level_3 = models.ForeignKey(CategoryLevel3, blank=True, null=True)
    category_level_4 = models.ForeignKey(CategoryLevel4, blank=True, null=True)
    category_level_5 = models.ForeignKey(CategoryLevel5, blank=True, null=True)
    status                      = models.CharField(max_length=150, null=True, default="1", choices=status)
    creation_date               = models.DateTimeField(null=True,blank=True)
    created_by                  = models.CharField(max_length=500,null=True,blank=True)
    updated_by                  = models.CharField(max_length=500,null=True,blank= True)
    updation_date               = models.DateTimeField(null=True,blank=True)

    def __unicode__(self):
        return unicode(self.categorywise_amenity_id)


class Amenities(models.Model):
    amenity_id                 = models.AutoField(primary_key=True, editable=False)
    advert_id                  = models.ForeignKey(Advert,blank=True,null=True)
    categorywise_amenity_id    = models.ForeignKey(CategorywiseAmenity,blank=True,null=True)
    creation_date               = models.DateTimeField(null=True,blank=True)
    created_by                  = models.CharField(max_length=500,null=True,blank=True)
    updated_by                  = models.CharField(max_length=500,null=True,blank= True)
    updation_date               = models.DateTimeField(null=True,blank=True)
    
    def __unicode__(self):
        return unicode(self.amenity_id)

class PremiumService(models.Model):
    premium_service_id = models.AutoField(primary_key=True, editable=False)
    premium_service_name = models.CharField(max_length=30)
    city_place_id = models.ForeignKey(City_Place, blank=True, null=True)
    no_of_days = models.CharField(max_length=30)
    category_id = models.CharField(max_length=10, blank=True, null=True)
    category_level = models.CharField(max_length=10, blank=True, null=True)
    start_date = models.CharField(max_length=30, blank=True, null=True)
    end_date = models.CharField(max_length=30, blank=True, null=True)
    business_id = models.ForeignKey(Business, blank=True, null=True)
    premium_service_status = models.CharField(max_length=15, null=True, blank=True, default="1", choices=status)
    premium_service_created_date = models.DateTimeField(default=datetime.now, null=True, blank=True)
    premium_service_created_by = models.CharField(max_length=30, null=True, blank=True)
    premium_service_updated_by = models.CharField(max_length=30, null=True, blank=True)
    premium_service_updated_date = models.DateTimeField(default=datetime.now, null=True, blank=True)

    def __unicode__(self):
        return unicode(self.premium_service_id) 

class EnquiryService(models.Model):
    enquiry_service_id = models.AutoField(primary_key=True, editable=False)
    enquiry_service_name = models.CharField(max_length=30)
    city_place_id = models.ForeignKey(City_Place, blank=True, null=True)
    no_of_days = models.CharField(max_length=30)
    category_id = models.CharField(max_length=10, blank=True, null=True)
    category_level = models.CharField(max_length=10, blank=True, null=True)
    start_date = models.CharField(max_length=30, blank=True, null=True)
    end_date = models.CharField(max_length=30, blank=True, null=True)
    business_id = models.ForeignKey(Business, blank=True, null=True)
    enquiry_service_status = models.CharField(max_length=15, null=True, blank=True, default="1", choices=status)
    enquiry_service_created_date = models.DateTimeField(default=datetime.now, null=True, blank=True)
    enquiry_service_created_by = models.CharField(max_length=30, null=True, blank=True)
    enquiry_service_updated_by = models.CharField(max_length=30, null=True, blank=True)
    enquiry_service_updated_date = models.DateTimeField(default=datetime.now, null=True, blank=True)

    def __unicode__(self):
        return unicode(self.enquiry_service_id)

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
    bank_name                  =      models.CharField(max_length=50,null=True,blank=True)
    branch_name                =    models.CharField(max_length=50,null=True,blank=True)
    cheque_number              =    models.CharField(max_length=50,null=True,blank=True)
    paid_amount         =       models.CharField(max_length=30,null=True,blank=True)
    payable_amount         =       models.CharField(max_length=30,null=True,blank=True)
    total_amount         =       models.CharField(max_length=30,null=True,blank=True)
    tax_type             =       models.ForeignKey(Tax,null=True,blank=True)    
    payment_created_date       =  models.DateTimeField(null=True,blank=True,default=django.utils.timezone.now)
    payment_created_by         =       models.CharField(max_length=30,null=True,blank=True)
    payment_updated_by         =       models.CharField(max_length=30,null=True,blank= True)
    payment_updated_date       =       models.DateTimeField(null=True,blank=True)
    note = models.CharField(max_length=5000,null=True,blank=True)
    business_id                      =       models.ForeignKey(Business,blank=True,null=True)

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

class AdvertReview(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user_id = models.ForeignKey(ConsumerProfile, blank=True, null=True)
    advert_id = models.ForeignKey(Advert, blank=True, null=True)
    ratings = models.CharField(max_length=10,null=True, blank=True)
    review = models.CharField(max_length=500, null=True, blank=True)
    creation_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.id)

class AdvertView(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user_id = models.ForeignKey(ConsumerProfile, blank=True, null=True)
    advert_id = models.ForeignKey(Advert, blank=True, null=True)
    creation_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.id)


class AdvertCallbacks(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user_id = models.ForeignKey(ConsumerProfile, blank=True, null=True)
    advert_id = models.ForeignKey(Advert, blank=True, null=True)
    creation_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.id)


class AdvertCallsMade(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user_id = models.ForeignKey(ConsumerProfile, blank=True, null=True)
    advert_id = models.ForeignKey(Advert, blank=True, null=True)
    creation_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.id)


class AdvertShares(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user_id = models.ForeignKey(ConsumerProfile, blank=True, null=True)
    advert_id = models.ForeignKey(Advert, blank=True, null=True)
    creation_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.id)

class AdvertFavourite(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user_id = models.ForeignKey(ConsumerProfile, blank=True, null=True)
    advert_id = models.ForeignKey(Advert, blank=True, null=True)
    creation_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.id)

class AdvertSubscriptionMap(models.Model):
    id                 = models.AutoField(primary_key=True, editable=False)
    business_id                  = models.ForeignKey(Business,blank=True,null=True)
    advert_id                    = models.ForeignKey(Advert,blank=True,null=True) 
    
    def __unicode__(self):
        return unicode(self.id)    

class CouponCode(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user_id = models.ForeignKey(ConsumerProfile, blank=True, null=True)
    advert_id = models.ForeignKey(Advert, blank=True, null=True)
    coupon_code = models.CharField(max_length=20, null=True, blank=True)
    creation_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.id) 

class SellTicket(models.Model):
    sellticket_id = models.AutoField(primary_key=True, editable=False)
    user_id = models.ForeignKey(ConsumerProfile, blank=True, null=True)
    event_name = models.CharField(max_length=50, null=True, blank=True)
    event_venue = models.CharField(max_length=50, null=True, blank=True)
    start_date = models.CharField(null=True, max_length=50, blank=True)
    start_time = models.CharField(max_length=50, null=True, blank=True)
    select_activation_date = models.CharField(max_length=50, null=True, blank=True)
    #select_deactivation_date = models.CharField(max_length=50, null=True, blank=True)
    other_comments = models.CharField(max_length=5000, null=True, blank=True)
    city_id = models.ForeignKey(City_Place, blank=True,null=True)
    country_id = models.ForeignKey(Country, blank=True,null=True)
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    image_one = models.ImageField("Image", upload_to=USER_IMAGES_PATH, max_length=500, default=None)
    image_two = models.ImageField("Image", upload_to=USER_IMAGES_PATH, max_length=500, default=None)
    image_three = models.ImageField("Image", upload_to=USER_IMAGES_PATH, max_length=500, default=None)
    image_four = models.ImageField("Image", upload_to=USER_IMAGES_PATH, max_length=500, default=None)
    created_date = models.DateTimeField(default=datetime.now, null=True, blank=True)
    sellticket_views = models.CharField(max_length=10, null=True, blank=True)
    status = models.CharField(max_length=15, null=True, blank=True, default="unread", choices=post_status)
    updated_date = models.DateTimeField(null=True, blank=True)
    deleted_date = models.DateTimeField(null=True, blank=True)    

    def __unicode__(self):
        return unicode(self.sellticket_id)

class SellTicketDetails(models.Model):
    sell_ticket_detail_id = models.AutoField(primary_key=True, editable=False)
    sellticket_id = models.ForeignKey(SellTicket, blank=True, null=True)
    ticket_class = models.CharField(max_length=50, null=True, blank=True)
    no_of_tickets = models.CharField(max_length=50, null=True, blank=True)
    original_price = models.CharField(max_length=50, null=True, blank=True)
    asking_price = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=150, null=True, default="1", choices=status)
    created_date = models.DateTimeField(default=datetime.now, null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    deleted_date = models.DateTimeField(null=True, blank=True)
    
    def __unicode__(self):
        return unicode(self.sell_ticket_detail_id)

class SellTicketLike(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user_id = models.ForeignKey(ConsumerProfile, blank=True, null=True)
    sellticket_id = models.ForeignKey(SellTicket, blank=True, null=True)
    creation_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.id)


class SellTicketFavourite(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user_id = models.ForeignKey(ConsumerProfile, blank=True, null=True)
    sellticket_id = models.ForeignKey(SellTicket, blank=True, null=True)
    creation_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.id)


class SellTicketReview(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user_id = models.ForeignKey(ConsumerProfile, blank=True, null=True)
    sellticket_id = models.ForeignKey(SellTicket, blank=True, null=True)
    review = models.CharField(max_length=500, null=True, blank=True)
    ratings = models.CharField(max_length=10, null=True, blank=True)
    creation_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.id)

class SellTicketView(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user_id = models.ForeignKey(ConsumerProfile, blank=True, null=True)
    sellticket_id = models.ForeignKey(SellTicket, blank=True, null=True)
    creation_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.id)

class SellTicketShares(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user_id = models.ForeignKey(ConsumerProfile, blank=True, null=True)
    sellticket_id = models.ForeignKey(SellTicket, blank=True, null=True)
    creation_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.id)

class CallerDetails(models.Model):
    CallerID                        =       models.AutoField(primary_key=True, editable=False)
    first_name                      =       models.CharField(max_length=100,default=None,blank=True,null=True)
    last_name                      =       models.CharField(max_length=100,default=None,blank=True,null=True)
    IncomingTelNo                =       models.CharField(blank=True,null=True,max_length=200,default=None)
    TelNo                =       models.CharField(blank=True,null=True,max_length=200,default=None)
    email                =       models.CharField(blank=True,null=True,max_length=200,default=None)
    CallerArea                  =       models.CharField(blank=True,null=True,max_length=100,default=None)
    CallerPincode                      =       models.ForeignKey(Pincode,blank=True,null=True)
    CallerCity                      =       models.ForeignKey(City,blank=True,null=True)
    caller_created_date              =       models.DateTimeField(null=True,blank=True)
    caller_created_by                =       models.CharField(max_length=100,null=True,blank=True)
    caller_updated_by                =       models.CharField(max_length=100,null=True,blank= True)
    caller_updated_date              =       models.DateTimeField(null=True,blank=True)

    def __unicode__(self):
        return unicode(self.CallerID)

class EnquiryDetails(models.Model):
    EnquiryID                        =       models.AutoField(primary_key=True, editable=False)
    CallerID                =       models.ForeignKey(CallerDetails,blank=True,null=True)
    enquiryFor                  =       models.CharField(blank=True,null=True,max_length=100,default=None)
    SelectedArea                     =       models.CharField(max_length=100,default=None,blank=True,null=True)
    SelectedPincode                      =       models.ForeignKey(Pincode,blank=True,null=True)
    SelectedCity                      =       models.ForeignKey(City,blank=True,null=True)
    category_id = models.ForeignKey(Category, blank=True, null=True)
    subcategory_id1 = models.ForeignKey(CategoryLevel1, blank=True, null=True)
    subcategory_id2 = models.ForeignKey(CategoryLevel2, blank=True, null=True)
    created_date              =       models.DateTimeField(null=True,blank=True)
    created_by                =       models.CharField(max_length=100,null=True,blank=True)
    updated_by                =       models.CharField(max_length=100,null=True,blank= True)
    updated_date              =       models.DateTimeField(null=True,blank=True)

    def __unicode__(self):
        return unicode(self.EnquiryID)

class CallInfo(models.Model):
    UCID                        =       models.CharField(max_length=100,default=None,blank=True,null=True)
    CallerID                      =       models.CharField(max_length=100,default=None,blank=True,null=True)
    CalledNo                      =       models.CharField(max_length=100,default=None,blank=True,null=True)
    CallStartTime                =       models.DateTimeField(null=True,blank=True)
    DialStartTime                =       models.DateTimeField(null=True,blank=True)
    DialEndTime                  =       models.DateTimeField(null=True,blank=True)
    DisconnectType                      =       models.CharField(max_length=100,default=None,blank=True,null=True)
    CallStatus                      =       models.CharField(max_length=100,default=None,blank=True,null=True)
    CallDuration                      =       models.CharField(max_length=100,default=None,blank=True,null=True)
    CallType                      =       models.CharField(max_length=100,default=None,blank=True,null=True)
    AudioRecordingURL                      =       models.URLField(default=None,blank=True,null=True)
    DialedNumber                      =       models.CharField(max_length=100,default=None,blank=True,null=True)
    Department                      =       models.CharField(max_length=100,default=None,blank=True,null=True)
    CallBackParam                      =       models.CharField(max_length=100,default=None,blank=True,null=True)
    Extn                      =       models.CharField(max_length=100,default=None,blank=True,null=True)


    def __unicode__(self):
        return unicode(self.CallerID)

#---------------------city star---------------

class CityStarDetails(models.Model):
    citystarID = models.AutoField(primary_key=True, editable=False)
    title = models.CharField(max_length=10, default=None, blank=True, null=True)
    name = models.CharField(max_length=100, default=None, blank=True, null=True)
    address1 = models.CharField(blank=True, null=True, max_length=400, default=None)
    address2 = models.CharField(blank=True, null=True, max_length=400, default=None)
    phone = models.CharField(blank=True, null=True, max_length=100, default=None)
    email = models.CharField(blank=True, null=True, max_length=100, default=None)
    education = models.CharField(blank=True, null=True, max_length=100, default=None)
    age = models.CharField(blank=True, null=True, max_length=100, default=None)
    experience = models.CharField(blank=True, null=True, max_length=100, default=None)
    summary = models.CharField(blank=True, null=True, max_length=1000, default=None)
    occupation = models.CharField(blank=True, null=True, max_length=200, default=None)
    description = models.CharField(blank=True, null=True, max_length=5000, default=None)
    achievements = models.CharField(blank=True, null=True, max_length=500, default=None)
    image = models.FileField(upload_to=STAR_IMAGES_PATH, max_length=500, null=True, blank=True)
    city = models.ForeignKey(City_Place, blank=True, null=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(default="active", max_length=100, null=True, blank=True, choices=city_star_status)
    likes = models.CharField(max_length=100, null=True, blank=True)
    views = models.CharField(max_length=100, null=True, blank=True)
    shares = models.CharField(max_length=100, null=True, blank=True)
    creation_date = models.DateTimeField(null=True, blank=True)
    creation_by = models.CharField(max_length=100, null=True, blank=True)
    updation_date = models.DateTimeField(null=True, blank=True)
    updation_by = models.CharField(max_length=100, null=True, blank=True)

    def __unicode__(self):
        return unicode(self.citystarID)

class CityStar_Like(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user_id = models.ForeignKey(ConsumerProfile, blank=True, null=True)
    citystarID = models.ForeignKey(CityStarDetails, blank=True, null=True)
    creation_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.id)

class CityStar_View(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user_id = models.ForeignKey(ConsumerProfile, blank=True, null=True)
    citystarID = models.ForeignKey(CityStarDetails, blank=True, null=True)
    creation_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.id)


class StarImage(models.Model):
    star_image_id = models.AutoField(primary_key=True, editable=False)
    star_id = models.ForeignKey(CityStarDetails, blank=True, null=True)
    star_image = models.FileField(upload_to=STAR_IMAGES_PATH, max_length=500, null=True, blank=True)
    creation_date = models.DateTimeField(null=True, blank=True)
    created_by = models.CharField(max_length=500, null=True, blank=True)
    updated_by = models.CharField(max_length=500, null=True, blank=True)
    updation_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.star_image_id)


#################  ......CITY LIFE...... ######################

class citylife_category(models.Model):
    category_id = models.AutoField(primary_key=True, editable=False)
    category_name = models.CharField(max_length=50, blank=True, null=True)
    city_id = models.ForeignKey(City_Place, blank=True, null=True)
    creation_date = models.DateTimeField(null=True, blank=True)
    creation_by = models.CharField(max_length=500, null=True, blank=True)
    status = models.CharField(max_length=15, null=True, blank=True, default="1", choices=status)

    def __unicode__(self):
        return unicode(self.category_id)

class PostDetails(models.Model):
    post_id = models.AutoField(primary_key=True, editable=False)
    citylife_category = models.ForeignKey(citylife_category, blank=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    user_id = models.ForeignKey(ConsumerProfile, blank=True, null=True)
    area = models.CharField(max_length=50, blank=True, null=True)    
    mood = models.CharField(default="positive", max_length=100, null=True, blank=True, choices=post_mood)
    #mood = models.CharField(max_length=100, blank=True, null=True)
    share = models.CharField(default="0", max_length=100, null=True, blank=True)
    city_id = models.ForeignKey(City_Place, blank=True)
    country_id = models.ForeignKey(Country, blank=True)
    status = models.CharField(max_length=15, null=True, blank=True, default="unread", choices=post_status)
    post_status = models.CharField(max_length=150, null=True, default="unread", choices=comment_status)
    creation_date = models.DateTimeField(null=True, blank=True)
    creation_by = models.CharField(max_length=500, null=True, blank=True)
    updated_by = models.CharField(max_length=500, null=True, blank=True)
    updation_date = models.DateTimeField(null=True, blank=True)
    deleted_date = models.DateTimeField(null=True, blank=True)    
    
    def __unicode__(self):
        return unicode(self.post_id)

class PostFile(models.Model):
    post_file_id = models.AutoField(primary_key=True, editable=False)
    post_id = models.ForeignKey(PostDetails, blank=True, null=True)
    post_file = models.FileField(upload_to=CITYLIFE_FILE_PATH, max_length=500, null=True, blank=True)
    file_width = models.CharField(max_length=500, null=True, blank=True)
    file_height = models.CharField(max_length=500, null=True, blank=True)
    creation_date = models.DateTimeField(null=True, blank=True)
    created_by = models.CharField(max_length=500, null=True, blank=True)
    updated_by = models.CharField(max_length=500, null=True, blank=True)
    updation_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.post_file_id)


class PostMood(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user_id = models.ForeignKey(ConsumerProfile, blank=True, null=True)
    post_id = models.ForeignKey(PostDetails, blank=True, null=True)
    status = models.CharField(default="like", max_length=100, null=True, blank=True, choices=like_dislike)
    creation_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.id)


class PostComments(models.Model):
    comment_id = models.AutoField(primary_key=True, editable=False)
    user_id = models.ForeignKey(ConsumerProfile, blank=True, null=True)
    post_id = models.ForeignKey(PostDetails, blank=True, null=True)
    comment = models.CharField(max_length=500, null=True, blank=True)
    status = models.CharField(max_length=150, null=True, default="1", choices=status)
    comment_status = models.CharField(max_length=150, null=True, default="unread", choices=comment_status)
    creation_date = models.DateTimeField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    deleted_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.comment_id)

class PostReplys(models.Model):
    reply_id = models.AutoField(primary_key=True, editable=False)
    user_id = models.ForeignKey(ConsumerProfile, blank=True, null=True)
    comment_id = models.ForeignKey(PostComments, blank=True, null=True)
    reply = models.CharField(max_length=500, null=True, blank=True)
    status = models.CharField(max_length=150, null=True, default="1", choices=status)
    creation_date = models.DateTimeField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    deleted_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.reply_id)

class LikeDislikeComment(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user_id = models.ForeignKey(ConsumerProfile, blank=True, null=True)
    comment_id = models.ForeignKey(PostComments, blank=True, null=True)
    status = models.CharField(default="like", max_length=100, null=True, blank=True, choices=like_dislike)
    creation_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.id)

class LikeDislikeReply(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user_id = models.ForeignKey(ConsumerProfile, blank=True, null=True)
    reply_id = models.ForeignKey(PostReplys, blank=True, null=True)
    status = models.CharField(default="like", max_length=100, null=True, blank=True, choices=like_dislike)
    creation_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.id)

class PostView(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user_id = models.ForeignKey(ConsumerProfile, blank=True, null=True)
    post_id = models.ForeignKey(PostDetails, blank=True, null=True)
    creation_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.id)


class PostFavourite(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user_id = models.ForeignKey(ConsumerProfile, blank=True, null=True)
    post_id = models.ForeignKey(PostDetails, blank=True, null=True)
    creation_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.id)
