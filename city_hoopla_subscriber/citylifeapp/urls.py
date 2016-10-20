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
citylife_urlpatterns = patterns('',
## CITY LIFE

    url(r'^city-dashboard/', 'citylifeapp.views.city_dashboard',name='city_dashboard'),
    url(r'^city-life/', 'citylifeapp.views.city_life',name='city_life'),
    url(r'^category-life/', 'citylifeapp.views.category_life',name='category_life'),
    url(r'^get-city-countrybase/', 'citylifeapp.views.get_city_countrybase',name='get_city_countrybase'),
    url(r'^save-category-citylife/', 'citylifeapp.views.save_category_citylife',name='save_category_citylife'),
    url(r'^citylife-cat/', 'citylifeapp.views.citylife_cat',name='citylife_cat'),
    url(r'^delete-citylife-cat/', 'citylifeapp.views.delete_citylife_cat',name='delete_citylife_cat'),             
       
)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
