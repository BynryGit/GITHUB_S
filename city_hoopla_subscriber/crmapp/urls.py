from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls import patterns, include, url
from django.contrib import admin
from digispaceapp import views
from django.conf.urls.static import static
from DigiSpace import settings
from mobileapp.mobile_urls import mobileapp_urlpattern


#from django.views.generic import direct_to_template
from django.views.generic import TemplateView
crm_urlpatterns = patterns('',
    # #CRM New Urls
    
    url(r'^crm_details/', 'crmapp.views.crm_details',name='crm_details'),
    url(r'^get-consumer-detail/', 'crmapp.views.get_consumer_detail',name='get_consumer_detail'),
    url(r'^new_consumer/', 'crmapp.views.new_consumer',name='new_consumer'),
    url(r'^save_consumer_details/', 'crmapp.views.save_consumer_details',name='save_consumer_details'),   
#    url(r'^enquiry_search_results/', 'crmapp.views.enquiry_search_results',name='enquiry_search_results'),
    url(r'^get-pincode-list/', 'crmapp.views.get_pincode_list',name='get_pincode_list'),
    url(r'^save-enquiry-details/', 'crmapp.views.save_enquiry_details',name='save_enquiry_details'),
    url(r'^send_subscriber_details/', 'crmapp.views.send_subscriber_details',name='send_subscriber_details'),
    url(r'^send_consumer_details/', 'crmapp.views.send_consumer_details',name='send_consumer_details'),
    url(r'^search_details/', 'crmapp.views.search_details',name='search_details'),

    url(r'^callinfo/', 'crmapp.views.caller_details_api',name='caller_details_api'),

)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
