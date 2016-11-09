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
citystar_urlpatterns = patterns('',
    # #City star New Urls
    url(r'^citystar/', 'citystarapp.views.citystar',name='citystar'),
    url(r'^starhome/', 'citystarapp.views.starhome',name='starhome'),   
    url(r'^citystar_home/', 'citystarapp.views.citystar_home',name='citystar_home'), 
    url(r'^add_citystar/', 'citystarapp.views.add_citystar',name='add_citystar'),
    url(r'^edit_citystar/', 'citystarapp.views.edit_citystar',name='edit_citystar'),
    url(r'^update_citystar/', 'citystarapp.views.update_citystar',name='update_citystar'),
    url(r'^search_starcity/', 'citystarapp.views.search_starcity',name='search_starcity'),
    url(r'^uploaded-images/', 'citystarapp.views.uploaded_images',name='uploaded_images'),
    url(r'^activate_citystar/', 'citystarapp.views.activate_citystar',name='activate_citystar'),
    url(r'^addcitystar/', 'citystarapp.views.addcitystar',name='addcitystar'),
    url(r'^viewstarprofile/', 'citystarapp.views.viewstarprofile',name='viewstarprofile'),
    url(r'^save-citystar/', 'citystarapp.views.save_citystar',name='save-citystar'),
    url(r'^search-star/', 'citystarapp.views.search_star',name='search-star'),     
    url(r'^upload-star-image/', 'citystarapp.views.upload_star_image',name='upload_star_image'),        
    url(r'^remove-star-image/', 'citystarapp.views.remove_star_image',name='remove_star_image'),
    url(r'^get_star_dates/', 'citystarapp.views.get_star_dates',name='get_star_dates'),
       
)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
