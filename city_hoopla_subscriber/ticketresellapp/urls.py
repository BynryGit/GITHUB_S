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
ticketresell_urlpatterns = patterns('',
## Ticket Resell

    url(r'^ticket-resell-home/', 'ticketresellapp.views.ticket_resell_home',name='ticket_resell_home'),
    url(r'^ticket-resell-feed/', 'ticketresellapp.views.ticket_resell_feed',name='ticket_resell_feed'),     
    url(r'^deactivate-ticket-event/', 'ticketresellapp.views.deactivate_ticket_event',name='deactivate_ticket_event'),
    url(r'^re-activate-ticket-event/', 'ticketresellapp.views.re_activate_ticket_event',name='re_activate_ticket_event'),  
    url(r'^deactivate-ticket/', 'ticketresellapp.views.deactivate_ticket',name='deactivate_ticket'),   
    url(r'^view-comments/', 'ticketresellapp.views.view_comments',name='view_comments'),           
       
)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
